"""
    TranSPHIRE is supposed to help with the cryo-EM data collection
    Copyright (C) 2017 Markus Stabrin

    This program is free software: you can redistribute it and/or modify
    it under the terms of the GNU General Public License as published by
    the Free Software Foundation, either version 3 of the License, or
    (at your option) any later version.

    This program is distributed in the hope that it will be useful,
    but WITHOUT ANY WARRANTY; without even the implied warranty of
    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
    GNU General Public License for more details.

    You should have received a copy of the GNU General Public License
    along with this program.  If not, see <http://www.gnu.org/licenses/>.
"""
import numpy as np
import json
import pexpect as pe
import time
import os
import shutil
import re
import glob
import copy as cp
from PyQt5.QtCore import QObject, pyqtSignal, pyqtSlot
import multiprocessing as mp
import multiprocessing.managers
import queue

from . import transphire_utils as tu


class MyManager(multiprocessing.managers.BaseManager):
    pass
MyManager.register('LifoQueue', queue.LifoQueue)


class ProcessWorker(QObject):
    """
    Setup and start worker threads

    Inherits from:
    QObject

    Buttons:
    None

    Signals:
    sig_start - Connected to the run method to start the process (settings|object)
    sig_finished - Emitted, if run method finishes (No objects)
    sig_error - Emitted, if an error occured (text|str)
    sig_status - Emitted to change the status (text|str, device|str, color|str)
    sig_notification - Emitted to send a notification (text|str)
    sig_plot_ctf - Emitted to plot ctf information (ctf_name|str, ctf_settings|object, settings|object)
    sig_plot_motion - Emitted to plot motion information (motion_name|str, motion_settings|object, settings|object)
    sig_plot_picking - Emitted to plot picking information (picking_name|str, picking_settings|str, settings|object)
    """
    sig_set_project_directory = pyqtSignal(str, str, str)
    sig_start = pyqtSignal(object, object)
    sig_finished = pyqtSignal()
    sig_error = pyqtSignal(str)
    sig_status = pyqtSignal(str, object, str, str)
    sig_notification = pyqtSignal(str)
    signal_plot = pyqtSignal(object)

    def __init__(self, password, content_process, mount_directory, parent=None):
        """
        Initialize object variables.

        Arguments:
        password - Sudo password
        content_process - Pipeline content
        mount_directory - Folder containing the mount points
        parent - Parent widget (default None)

        Return:
        None
        """
        super(ProcessWorker, self).__init__(parent)
        # Variables
        self.password = password
        self.content_process = content_process
        self.mount_directory = mount_directory
        self.stop = None
        self.abort = None
        self.settings = {}
        self.idx_number = 0
        self.idx_values = 1

        # Events
        self.sig_start.connect(self.run)

    def emit_plot_signals(self, folder_list, monitor):
        settings_emit = []
        for name_no_feedback, name, prog_type, folder in self.settings['plot_emit']:
            try:
                settings_emit.append([
                    name,
                    name_no_feedback,
                    folder,
                    self.settings,
                    self.settings['Copy'][prog_type],
                    ])
            except KeyError:
                pass

        self.signal_plot.emit(settings_emit)

    @pyqtSlot(object, object)
    def run(self, settings, restart_dict):
        """
        Start the process.

        Arguments:
        settings - Transphire settings

        Return:
        None
        """
        # Set settings
        self.abort = False
        self.sig_error.emit('NEW SESSION: {}'.format('Monitor' if settings['Monitor'] else 'Start'))

        content_process = cp.deepcopy(self.content_process)
        settings['copy_software_meta'] = True
        if settings['Input']['Input frames extension'] in ('dm4'):
            settings['Output extension'] = 'mrc'
        else:
            settings['Output extension'] = settings['Input']['Input frames extension']

        # Set paths
        settings['software_meta_tar'] = os.path.join(
            settings['tar_folder'], 'Software_meta.tar'
            )

        picking_name = settings['Copy']['Picking'] 
        if picking_name not in ('False', 'Later'):
            settings[picking_name]['--threshold_old'] = settings[picking_name]['--threshold']
            value = settings[picking_name]['--weights']
            try:
                if '|||' in value:
                    external_log, local_key = value.split('|||')
                    with open(settings[external_log], 'r') as read:
                        log_data = json.load(read)
                    try:
                        set_value = log_data[settings['current_set']][picking_name][local_key]['new_file']
                    except KeyError:
                        set_value = value
                else:
                    set_value = value
            except TypeError:
                set_value = value
            settings[picking_name]['--weights_old'] = set_value

        self.settings = settings
        self.sig_set_project_directory.emit(self.settings['project_folder'], self.settings['log_folder'], self.settings['error_folder'])

        manager_lifo = MyManager()
        manager_lifo.start()
        manager = mp.Manager()
        typ_dict = {}
        share_dict = {}
        bad_dict = {}
        queue_dict = {}
        full_content = []
        for entry in content_process:
            for process in entry:
                for key in process:
                    if 'WIDGETS' in key:
                        continue
                    process[key][self.idx_values]['group'], process[key][self.idx_values]['aim'] = \
                        process[key][self.idx_values]['group'].split(';')
                    process[key][self.idx_values]['aim'] = process[key][self.idx_values]['aim'].split(',')
                    share_dict[key] = manager.list()
                    bad_dict[key] = manager.list()
                    queue_dict[key] = manager_lifo.LifoQueue()
                    #queue_dict[key] = manager.Queue()
                    typ_dict[key] = manager.dict({
                        'file_number': 0,
                        'spot': False,
                        'lost_input_meta': False,
                        'lost_input_frames': False,
                        'lost_work': False,
                        'lost_backup': False,
                        'lost_hdd': False,
                        'full_transphire': False,
                        'full_work': False,
                        'full_backup': False,
                        'full_hdd': False,
                        'unknown_error': False,
                        'delay_error': False,
                        'is_error': False,
                        'queue_list_time': 0.0,
                        'tar_idx': 0,
                        'max_running': int(self.settings['Pipeline'][key]),
                        'running': 0,
                        'do_update_count': 0,
                        'queue_list': manager.list(),
                        'queue_list_lock': manager.Lock(),
                        'queue_lock': manager.Lock(),
                        'save_lock': manager.Lock(),
                        'count_lock': manager.Lock(),
                        'error_lock': manager.Lock(),
                        'bad_lock': manager.Lock(),
                        'share_lock': manager.Lock(),
                        'write_lock': manager.Lock(),
                        'spot_dict': manager.dict(self.fill_spot_dict()),
                        'settings_file': '{0}/updated_settings_{1}.txt'.format(
                            self.settings['log_folder'],
                            key
                            ),
                        'number_file': '{0}/last_filenumber_{1}.txt'.format(
                            self.settings['log_folder'],
                            key
                            ),
                        'save_file': '{0}/Queue_{1}'.format(
                            self.settings['queue_folder'], key
                            ),
                        'done_file': '{0}/Queue_{1}_done'.format(
                            self.settings['queue_folder'], key
                            ),
                        'feedback_lock_file': '{0}/Queue_{1}_feedback_lock'.format(
                            self.settings['queue_folder'], key
                            ),
                        'list_file': '{0}/Queue_{1}_list'.format(
                            self.settings['queue_folder'], key
                            ),
                        'error_file': '{0}/Queue_{1}_error'.format(
                            self.settings['error_folder'], key
                            ),
                        })

                    full_content.append([key, process[key]])

        # Queue communication dictionary
        queue_com = {
            'log': manager.Queue(),
            'status': manager.Queue(),
            'notification': manager.Queue(),
            'error': manager.Queue(),
            'info': manager.Queue(),
            }

        # Set stop variable to the return value of the pre_check
        if settings['Monitor']:
            self.stop = False
            self.emit_plot_signals([], monitor=True)
            self.run_monitor(
                typ_dict=typ_dict,
                queue_com=queue_com,
                full_content=full_content,
                )
        else:
            self.stop = bool(self.pre_check_programs())
            self.run_process(
                typ_dict=typ_dict,
                queue_com=queue_com,
                share_dict=share_dict,
                bad_dict=bad_dict,
                queue_dict=queue_dict,
                content_process=content_process,
                full_content=full_content,
                manager=manager,
                restart_dict=restart_dict,
                )

        self.sig_finished.emit()

    def run_monitor(
            self,
            typ_dict,
            queue_com,
            full_content
        ):
        """
        Run the TranSPHIRE monitor process.

        Arguments:
        typ_dict - Dictionary for the queue types
        queue_com - Dictionary for queue communication

        Returns:
        None
        """
        def check_int(number):
            try:
                int(number)
            except:
                return False
            else:
                return True

        while True:
            if self.stop:
                text = 'Not monitoring'
                color = tu.get_color('white')
            else:
                text = 'Monitoring'
                color = tu.get_color('Running')
            for entry in full_content:
                name = entry[0]
                key = '_'.join([key for key in name.split('_') if not check_int(key)])
                try:
                    with open(typ_dict[key]['save_file']) as read:
                        nr_do = len([line for line in read.readlines() if line.strip()])
                except FileNotFoundError:
                    nr_do = 0
                try:
                    with open(typ_dict[key]['done_file']) as read:
                        nr_done = len([line for line in read.readlines() if line.strip()])
                except FileNotFoundError:
                    nr_done = 0
                queue_com['status'].put([
                    text,
                    [
                        nr_do,
                        nr_done
                        ],
                    name,
                    color
                    ])
            try:
                self.check_queue(queue_com=queue_com)
            except BrokenPipeError:
                pass

            if self.stop:
                break
            else:
                time.sleep(3)

    def run_process(self,
            typ_dict,
            queue_com,
            share_dict,
            bad_dict,
            queue_dict,
            content_process,
            full_content,
            manager,
            restart_dict,
        ):
        """
        Run the TranSPHIRE process.

        Arguments:
        typ_dict - Dictionary for the queue types
        queue_com - Dictionary for queue communication

        Returns:
        None
        """
        # Set default values for folder list and thread list
        folder_list = ['stack_folder', 'meta_folder']
        use_threads_list = ['Meta', 'Find', 'Import']

        data_frame = tu.DataFrame(manager, self.settings['data_frame'])

        # Decide if one will use copy to hdd
        self.settings['Copy']['Copy_to_hdd'] = self.settings['Copy']['Copy to hdd']
        if self.settings['Copy']['Copy to hdd'] != 'False':
            if self.settings['Copy']['Copy to hdd'] == 'Later':
                pass
            else:
                try:
                    for folder in glob.glob('{0}/*'.format(self.settings['copy_to_hdd_folder_feedback_0'])):
                        if not os.path.ismount(folder):
                            try:
                                os.listdir(folder)
                            except PermissionError:
                                pass
                            else:
                                self.sig_error.emit(
                                    'HDD not mounted or not well unmounted!' +
                                    'Please remount if you want to use HDD'
                                    )
                                return None
                        else:
                            pass
                except FileNotFoundError:
                    self.sig_error.emit(
                        'HDD not mounted or not well unmounted!' +
                        'Please remount if you want to use HDD!'
                        )
                    return None
            use_threads_list.append('Copy_to_hdd')
        else:
            pass

        names = [
            entry.replace('_entries', '')
            for entry in self.settings['Copy']
            if entry.endswith('_entries') and
            entry.replace('_entries', '').replace('_', ' ') in self.settings['Copy']
            ]
        for entry in names:
            if 'copy_to_' in entry.lower():
                # Fill folder list and threads list
                for name in ['work', 'backup']:
                    short_name = 'Copy_to_{0}'.format(name)
                    long_name = 'Copy to {0}'.format(name)
                    folder_name = '{0}_folder_feedback_0'.format(short_name.lower())
                    user_name = '{0}_user'.format(short_name)
                    self.settings['Copy'][short_name] = \
                        self.settings['Copy'][long_name]

                    if self.settings['Copy'][long_name] != 'False':
                        if self.settings['Copy'][long_name] == 'Later':
                            pass
                        elif not os.path.ismount(self.settings[folder_name]):
                            try:
                                os.listdir(self.settings[folder_name])
                            except PermissionError:
                                pass
                            except FileNotFoundError:
                                self.sig_error.emit(
                                    '{0} folder {1} not mounted!'.format(
                                        name,
                                        self.settings['Copy'][long_name]
                                        )
                                    )
                                return None
                            except OSError as err:
                                if 'Required key' in str(err):
                                    self.sig_error.emit(
                                        '\n'.join([
                                            '{0} folder {1} no longer mounted! '.format(
                                                name,
                                                self.settings['Copy'][long_name]
                                                ),
                                            'Use kinit to refresh the key'
                                            ])
                                        )
                                    return None
                                else:
                                    print(
                                        '\n'.join([
                                            'Unknown Error occured!',
                                            'Please contact the TranSPHIRE authors!'
                                            ])
                                    )
                                    raise
                            else:
                                self.sig_error.emit(
                                    '{0} folder {1} not mounted!'.format(
                                        name,
                                        self.settings['Copy'][long_name]
                                        )
                                    )
                                return None

                        else:
                            pass
                        try:
                            self.settings[user_name] = self.settings[
                                'user_{0}'.format(
                                    self.settings['Copy'][long_name].replace(' ', '_')
                                    )
                                ]
                        except KeyError:
                            self.sig_error.emit('{0} needs remount! '.format(name))
                            return None
                        use_threads_list.append(short_name)
                    else:
                        pass

            elif 'ctf' == entry.lower():
                # Set CTF settings
                if self.settings['Copy']['CTF'] != 'False':
                    folder_list.append('ctf_folder_feedback_0')
                    use_threads_list.append('CTF')
                    ctf_name = self.settings['Copy']['CTF']
                    try:
                        if self.settings[ctf_name]['Use movies'] == 'True':
                            self.settings['Copy']['CTF_frames'] = 'True'
                            self.settings['Copy']['CTF_sum'] = 'False'
                        else:
                            self.settings['Copy']['CTF_frames'] = 'False'
                            self.settings['Copy']['CTF_sum'] = 'True'
                    except KeyError:
                        self.settings['Copy']['CTF_frames'] = 'False'
                        self.settings['Copy']['CTF_sum'] = 'True'
                else:
                    self.settings['Copy']['CTF_frames'] = 'False'
                    self.settings['Copy']['CTF_sum'] = 'False'
            else:
                if self.settings['Copy'][entry] != 'False':
                    folder_list.append('{0}_folder_feedback_0'.format(entry.lower()))
                    use_threads_list.append(entry)
                else:
                    pass

        # Fill different dictionarys with process information
        gpu_mutex_dict = dict([
            ('{0}_{1}'.format(idx, idx_2), [manager.RLock(), mp.Value('i', 0)])
            if idx_2 != -1
            else
            (str(idx), [manager.RLock(), mp.Value('i', 0)])
            for idx in range(10)
            for idx_2 in range(-1, 10)
            ])

        # Shared dictionary
        shared_dict = {
            'share': share_dict,
            'bad': bad_dict,
            'queue': queue_dict,
            'global_update_lock': manager.Lock(),
            'translate_lock': manager.Lock(),
            'ctf_star_lock': manager.Lock(),
            'ctf_partres_lock': manager.Lock(),
            'motion_star_lock': manager.Lock(),
            'motion_star_relion3_lock': manager.Lock(),
            'motion_txt_lock': manager.Lock(),
            'gpu_lock': gpu_mutex_dict,
            'gpu_lock_lock': manager.Lock(),
            'data_frame_lock': manager.Lock(),
            'typ': typ_dict,
            }

        keep_list = [
            self.settings['set_folder_raw'],
            self.settings['tar_folder'],
            self.settings['meta_folder'],
            self.settings['stack_folder'],
            ]
        try:
            restart_feedback = restart_dict['feedback']
        except KeyError:
            restart_feedback = False

        if restart_feedback:
            try:
                shutil.move(
                    os.path.join(self.settings['project_folder'], '000_Feedback_results'),
                    self.settings['restart_backup_folder'],
                    )
            except FileNotFoundError:
                pass
            try:
                shutil.move(
                    self.settings['feedback_file'],
                    self.settings['restart_backup_folder'],
                    )
            except FileNotFoundError:
                pass
        else:
            keep_list.append('000_Feedback_results')
            try:
                with open(self.settings['feedback_file'], 'r') as read:
                    content = read.read().strip()
                    self.settings['do_feedback_loop'] = int(content)
            except FileNotFoundError:
                pass

        self.settings['is_superres'] = mp.Value('i', 2)
        self.settings['do_feedback_loop'] = mp.Value('i', self.settings['do_feedback_loop'])
        if self.settings['do_feedback_loop'].value == 0:
            status = 'Done'
            color = 'Finished'
        else:
            status = 'Running'
            color = 'Running'
        queue_com['status'].put([
            '{0:02d}|{1:02d}'.format(
                int(self.settings['Output']['Number of feedbacks']) - self.settings['do_feedback_loop'].value,
                int(self.settings['Output']['Number of feedbacks'])
                ),
            [status],
            'Feedbacks',
            tu.get_color(color)
            ])
        with open(self.settings['feedback_file'], 'w') as write:
            write.write(str(self.settings['do_feedback_loop'].value))

        # Fill process queues
        for entry in content_process:
            for process in entry:
                for key in process:
                    if 'WIDGETS' in key:
                        continue
                    elif process[key][1]['name'].startswith('Copy_to'):
                        continue
                    self.prefill_queue(
                        shared_dict=shared_dict,
                        entry=process[key][1],
                        restart_dict=restart_dict,
                        keep_list=keep_list,
                        )
        for entry in content_process:
            for process in entry:
                for key in process:
                    if 'WIDGETS' in key:
                        continue
                    elif not process[key][1]['name'].startswith('Copy_to'):
                        continue
                    self.prefill_queue(
                        shared_dict=shared_dict,
                        entry=process[key][1],
                        restart_dict=restart_dict,
                        keep_list=keep_list,
                        )
        queue_com['info'].put('Current settings saved to: {0}'.format(self.settings['set_folder']))
        self.check_queue(queue_com=queue_com)

        # Unlock the Class2d queue in case of a TranSPHIRE crash during 2D classification
        try:
            with open(shared_dict['typ']['Class2d']['feedback_lock_file'], 'r') as read:
                in_feedback = '1' in read.read()

            if in_feedback and shared_dict['queue']['Select2d'].empty() and shared_dict['queue']['Train2d'].empty():
                with open(shared_dict['typ']['Class2d']['feedback_lock_file'], 'w') as write:
                    write.write('0')
        except FileNotFoundError:
            pass

        self.emit_plot_signals(folder_list=folder_list, monitor=False)

        # Define file number and check if file already exists
        if self.settings['Output']['Rename micrographs'] == 'True':
            try:
                with open(shared_dict['typ']['Find']['number_file'], 'r') as read:
                    shared_dict['typ']['Find']['file_number'] = int(read.readline())
            except FileNotFoundError:
                shared_dict['typ']['Find']['file_number'] = int(self.settings['Output']['Start number']) - 1
                message = '{0}: New run detected - Set start number to {1}\n'.format(
                    'Find',
                    self.settings['Output']['Start number'],
                    )
            else:
                if self.settings['Output']['Start number'] != '0' and \
                        int(self.settings['Output']['Start number']) > int(shared_dict['typ']['Find']['file_number']):
                    message = '{0}: Filenumber {1} provided and larger than last file_number {2}!\nContinue with {1}\n'.format(
                        'Find',
                        self.settings['Output']['Start number'],
                        shared_dict['typ']['Find']['file_number'],
                        )
                    shared_dict['typ']['Find']['file_number'] = int(self.settings['Output']['Start number']) - 1

                elif self.settings['Output']['Start number'] != '0' and \
                        int(self.settings['Output']['Start number']) <= int(shared_dict['typ']['Find']['file_number']):
                    self.stop = True
                    message = '{0}: Filenumber {1} provided and smaller equals the last file_number {2}!\nPlease adjust the Start number to a valid, i.e. not used yet, value or 0\n'.format(
                        'Find',
                        self.settings['Output']['Start number'],
                        shared_dict['typ']['Find']['file_number'],
                        )
                elif self.settings['Output']['Start number'] == '0':
                    message = '{0}: Continue run detected! Continue with file number: {1}'.format(
                        'Find',
                        shared_dict['typ']['Find']['file_number'],
                        )
                else:
                    self.stop = True
                    message = 'Unreachable code! Please contact the TranSPHIRE authors.'
            queue_com['error'].put(message)
            queue_com['notification'].put(message)
                

        #####
#
#        shared_dict['typ']['Find']['file_number'] = int(self.settings['Output']['Start number']) - 1
#
#        if self.settings['Output']['Rename micrographs'] == 'True':
#            new_name = '{0}/{1}{2:0{3}d}{4}'.format(
#                self.settings['meta_folder'],
#                self.settings['Output']['Rename prefix'],
#                shared_dict['typ']['Find']['file_number']+1,
#                len(self.settings['Output']['Estimated mic number']),
#                self.settings['Output']['Rename suffix']
#                )
#
#            if os.path.exists('{0}_krios_sum.mrc'.format(new_name)):
#                old_filenumber = shared_dict['typ']['Find']['file_number']
#                try:
#                    with open(shared_dict['typ']['Find']['number_file'], 'r') as read:
#                        shared_dict['typ']['Find']['file_number'] = int(read.readline())
#                except FileNotFoundError:
#                    shared_dict['typ']['Find']['file_number'] = 0
#                if self.settings['Output']['Increment number'] == 'True':
#                    message = '{0}: Filenumber {1} already exists!\n'.format(
#                        'Find',
#                        old_filenumber+1
#                        ) + \
#                        'Last one used: {0} - Continue with {1}'.format(
#                            shared_dict['typ']['Find']['file_number'],
#                            shared_dict['typ']['Find']['file_number']+1
#                            )
#                    queue_com['error'].put(message)
#                    queue_com['notification'].put(message)
#                else:
#                    self.stop = True
#                    message = '{0}: Filenumber {1} already exists!\n'.format(
#                        'Find',
#                        old_filenumber+1
#                        ) + \
#                        'Check Startnumber! Last one used: {0}'.format(shared_dict['typ']['Find']['file_number'])
#                    queue_com['error'].put(message)
#                    queue_com['notification'].put(message)
#            else:
#                pass
#        else:
#            pass

        # Start threads
        thread_list = []
        use_threads_set = set(use_threads_list)
        for key, settings_content in full_content:
            
            content_settings = settings_content[self.idx_values]
            number = self.settings['Pipeline'][key]
            names = None
            if (key == 'Find' and number != '1') or (key == 'Meta' and number != '1'):
                self.stop = True
                message = 'Find and Meta are not allowed to have more than 1 process running!'
                queue_com['error'].put(message)
                queue_com['notification'].put(message)
                names = [key]
            elif number == '1':
                names = [key]
            else:
                names = ['{0}_{1}'.format(key, idx) for idx in range(int(number))]
            assert names is not None, (key, names, number)

            for name in names:
                thread_obj = ProcessThread(
                    shared_dict=shared_dict,
                    name=name,
                    content_settings=content_settings,
                    queue_com=queue_com,
                    settings=self.settings,
                    mount_directory=self.mount_directory,
                    password=self.password,
                    use_threads_set=use_threads_set,
                    stop=mp.Value('i', self.stop),
                    abort=mp.Value('i', self.abort),
                    has_finished=mp.Value('i', 0),
                    data_frame=data_frame,
                    parent=self,
                    )
                thread = mp.Process(target=self.run_in_parallel, args=(thread_obj,))
                thread.start()
                thread_list.append([thread, name, content_settings, thread_obj])
            self.check_queue(queue_com=queue_com)
        time.sleep(1)

        # Run until the user stops the processes
        if not self.stop:
            while True:
                try:
                    self.check_queue(queue_com=queue_com)
                except BrokenPipeError:
                    pass
                if self.stop:
                    break
                else:
                    pass
                time.sleep(3)
        else:
            self.check_queue(queue_com=queue_com)

        # Indicate to stop all processes
        for key, settings_content in full_content:
            typ = settings_content[self.idx_values]['name']
            size = shared_dict['queue'][typ].qsize()
            self.sig_status.emit(
                'Stopping',
                [size, shared_dict['typ'][typ]['file_number']],
                key,
                tu.get_color('Stopped')
                )
        self.check_queue(queue_com=queue_com)

        # Send the stop signals to all threads
        for _, _, _, thread_obj in thread_list:
            thread_obj.stop.value = True
            thread_obj.abort.value = self.abort

        for _, name, _, thread_obj in thread_list:
            queue_com['log'].put('Waiting for {0} to finish!'.format(name))
            while not thread_obj.has_finished.value:
                time.sleep(1)
                self.check_queue(queue_com=queue_com)

        queue_com['status'].put([
            '{0:02d}|{1:02d}'.format(
                int(self.settings['Output']['Number of feedbacks']) - self.settings['do_feedback_loop'].value,
                int(self.settings['Output']['Number of feedbacks'])
                ),
            ['Not running'],
            'Feedbacks',
            tu.get_color('white')
            ])
        queue_com['log'].put('All done!')
        self.check_queue(queue_com=queue_com)

        final_sizes = []
        for key, settings_content in full_content:
            typ = settings_content[self.idx_values]['name']
            size = shared_dict['queue'][typ].qsize()
            final_sizes.append([key, size, typ])

        # Wait for all threads to finish
        for thread, name, _, thread_obj in thread_list:
            thread.join()
            del thread_obj
        time.sleep(0.1)

        for key, size, typ in final_sizes:
            self.sig_status.emit(
                '00|{0:02d}'.format(shared_dict['typ'][typ]['max_running']),
                [size, shared_dict['typ'][typ]['file_number']],
                key,
                tu.get_color('white')
                )
        time.sleep(1)

    @staticmethod
    def run_in_parallel(thread_obj):
        thread_obj.run()

    def pre_check_programs(self):
        """
        Check, if all programs the user wants to use are available.

        Arguments:
        None

        Return:
        True, if programs exist, else False
        """
        default_unique_types = tu.get_unique_types()
        error = False
        check_files = []
        for entry in default_unique_types:
            if entry == 'Compress':
                continue
            check_files.append(['Path', self.settings['Copy'][entry]])

        check_files.append(['Path', 'IMOD header'])

        try:
            if self.settings['Copy']['Train2d'] not in ('False', 'Later'):
                check_files.append(['Path', 'cryolo_gui.py'])
                check_files.append(['Path', 'cryolo_evaluation.py'])
                check_files.append(['Path', 'sp_pipe.py'])
            else:
                pass
        except KeyError:
            pass

        try:
            if self.settings['Copy']['Select2d'] not in ('False', 'Later'):
                check_files.append(['Path', 'sp_header.py'])
            else:
                pass
        except KeyError:
            pass

        try:
            if self.settings['Copy']['Class2d'] not in ('False', 'Later'):
                check_files.append(['Path', 'e2bdb.py'])
                check_files.append(['Path', 'mpirun'])
            else:
                pass
        except KeyError:
            pass

        try:
            if self.settings['Copy']['Auto3d'] not in ('False', 'Later'):
                check_files.append(['Path', 'sp_pipe.py'])
            else:
                pass
        except KeyError:
            pass

        try:
            if [entry for entry in map(lambda x: x not in ('False', 'Later'), ['Class2d', 'CTF', 'Extract', 'Picking', 'Select2d']) if entry]:
                check_files.append(['Path', 'e2proc2d.py'])
            else:
                pass
        except KeyError:
            pass

        if self.settings['Copy']['Compress'] == 'Compress cmd':
            check_files.append([self.settings['Copy']['Compress'], '--command_compress_path'])
            check_files.append([self.settings['Copy']['Compress'], '--command_uncompress_path'])
        else:
            pass

        for typ, name in check_files:
            if name != 'False' and name != 'Later':
                try:
                    is_file = os.path.isfile(self.settings[typ][name])
                except KeyError:
                    self.sig_error.emit(
                        '{0} path not valid or disabled (Advanced, Rare)! Please adjust it!'.format(name)
                        )
                    error = True
                else:
                    if shutil.which(self.settings[typ][name]) is not None:
                        pass
                    elif not is_file:
                        self.sig_error.emit(
                            '{0} path not valid or disabled (Advanced, Rare)! Please adjust it!'.format(name)
                            )
                        error = True
                    else:
                        pass
            else:
                pass

        ctf_name = self.settings['Copy']['CTF']
        motion_name = self.settings['Copy']['Motion']
        try:
            if self.settings[ctf_name]['Use movies'] and motion_name in ('Later', 'False'):
                self.sig_error.emit('Cannot automatically adjust the pixel size for the CTF output files in case of binned micrographs. Remember to adjust it manually if necessary.')
        except KeyError:
            pass

        train2d_name = self.settings['Copy']['Train2d']
        select2d_name = self.settings['Copy']['Select2d']
        class2d_name = self.settings['Copy']['Class2d']
        extract_name = self.settings['Copy']['Extract']
        if int(self.settings['Output']['Number of feedbacks']) != 0:
            if 'Later' in (train2d_name, select2d_name, extract_name, class2d_name):
                self.sig_error.emit('Number of feedbacks provided and Extract, Class2d, Select2d, or Train2d set to Later. Remember that particle extraction and subsequent runs will stall until a Extract, Class2d, Select2d, or Train2d  program is provided.')
            if 'False' in (train2d_name, select2d_name, extract_name, class2d_name):
                self.sig_error.emit('Number of feedbacks provided and Extract, Class2d, Select2d, or Train2d set to False. This is not possible, because the program will stall infinitely.')
                error = True

        auto3d_name = self.settings['Copy']['Auto3d']
        if auto3d_name not in ('False', 'Later'):
            if self.settings['Copy']['Class2d'] in ('False') and \
                    not self.settings[auto3d_name]['input_volume']:
                self.sig_error.emit('An input volume needs to be provided to Auto3d if no 2D classification should be performed!')
                error = True

            if self.settings[auto3d_name]['Use SSH'] == 'True':
                if self.settings['Copy']['Copy to work'] != 'False' and self.settings['Copy']['Copy to work'] != 'Later':
                    device_name = [
                        entry
                        for entry in self.settings['Mount'][self.settings['Copy']['Copy to work']]['IP'].split('/') if entry.strip()
                        ][0]
                    ssh_command = 'ssh -o "StrictHostKeyChecking no" {0}@{1} ls'.format(
                        self.settings[auto3d_name]['SSH username'],
                        device_name
                        )

                    child = pe.spawnu(ssh_command)
                    try:
                        expect_idx = child.expect(
                            [
                                "{0}@{1}'s password:".format(self.settings[auto3d_name]['SSH username'], device_name),
                                pe.EOF
                                ],
                            timeout=20
                            )
                    except pe.exceptions.TIMEOUT:
                        self.sig_error.emit('TIMEOUT: SSH "ls" command failed! Username or Password in Auto3d might be wrong or Copy to work is not consistent!!')
                        error = True

                    if error:
                        pass
                    elif expect_idx == 0 and self.settings[auto3d_name]['Need SSH password'] == 'True':
                        child.sendline(self.settings[auto3d_name]['SSH password'])
                    elif expect_idx == 1 and self.settings[auto3d_name]['Need SSH password'] == 'True':
                        self.sig_error.emit('SSH password provided, but not needed. Please check if passwordless authentification is enabled for this mount point.')
                        error = True
                    elif expect_idx == 0 and self.settings[auto3d_name]['Need SSH password'] == 'False':
                        self.sig_error.emit('SSH password expected, but none provided!')
                        error = True
                    elif expect_idx == 1 and self.settings[auto3d_name]['Need SSH password'] == 'False':
                        pass

                    try:
                        child.expect(pe.EOF, timeout=20)
                    except pe.exceptions.TIMEOUT:
                        self.sig_error.emit('TIMEOUT Password: SSH ls command failed! Username or Password in Auto3d might be wrong or Copy to work is not consistent!!')
                        error = True
                else:
                    self.sig_error.emit('"Copy to work" not specified for Auto3d ssh command.')
                    error = True
        return error

    def check_queue(self, queue_com):
        """
        Check the content of the queues and react accordingly.

        Arguments:
        queue_com

        Return:
        None
        """
        for key in queue_com:
            while not queue_com[key].empty():
                if key == 'status':
                    status, numbers, device, color = queue_com['status'].get()
                    self.sig_status.emit(status, numbers, device, color)
                elif key == 'notification':
                    notification = queue_com['notification'].get()
                    self.sig_notification.emit(notification)
                elif key == 'error':
                    error = queue_com['error'].get()
                    self.sig_error.emit(error)
                elif key == 'info':
                    error = queue_com['info'].get()
                    self.sig_error.emit(error)
                elif key == 'log':
                    log = queue_com['log'].get()
                    try:
                        with open(os.path.join(self.settings['log_folder'], 'sys_log.txt'), 'a+') as write:
                            write.write('{0}\n'.format(log))
                    except FileNotFoundError:
                        pass
                else:
                    print(
                        'Processworker - check_queue:',
                        key,
                        ' Not known!',
                        ' Unreachable code!',
                        ' Please contact the TranSPHIRE authors'
                        )

    def fill_spot_dict(self):
        """
        Fill the spot dictionary.

        Arguments:
        None

        Return:
        Spot dictionary
        """
        dictionary = {}
        spot_file = self.settings['spot_file']
        try:
            with open(spot_file, 'r') as read:
                lines = [line.rstrip() for line in read.readlines()]
            for line in lines:
                key, number = line.split('\t')
                dictionary[key] = number
        except FileNotFoundError:
            with open(spot_file, 'w') as write:
                write.write('')
        return dictionary

    def prefill_queue(self, shared_dict, entry, restart_dict, keep_list):
        """
        Prefill the queues for continue mode

        Arguments:
        shared_dict - Shared dictionary
        entry - Name of the queue process

        Return:
        None
        """
        key = entry['name']
        share = entry['group']
        shared_dict_typ = shared_dict['typ'][key]
        number_file = shared_dict_typ['number_file']
        settings_file = shared_dict_typ['settings_file']
        feedback_lock_file = shared_dict_typ['feedback_lock_file']
        save_file = shared_dict_typ['save_file']
        done_file = shared_dict_typ['done_file']
        list_file = shared_dict_typ['list_file']
        share_list = shared_dict['share'][share]
        queue = shared_dict['queue'][key]
        queue_list = shared_dict_typ['queue_list']

        if self.settings["Input"]["Software"] == "Just Stack":
            self.settings['copy_software_meta'] = False

        check_state = 0
        try:
            check_state = restart_dict[key]
        except KeyError:
            pass

        prepend_list = []
        if key.startswith('Copy_to'):
            for root, _, files in os.walk(self.settings['set_folder']):
                for entry in files:
                    prepend_list.append(os.path.join(root, entry))

        if check_state in (1, 2):
            try:
                shutil.move(
                    feedback_lock_file,
                    self.settings['restart_backup_folder'],
                    )
            except FileNotFoundError:
                pass
            try:
                shutil.move(
                    self.settings['{}_folder_feedback_{}'.format(key.lower(), self.settings['do_feedback_loop'].value)],
                    self.settings['restart_backup_folder'],
                    )
            except FileNotFoundError:
                pass
            try:
                shutil.move(
                    self.settings['{}_folder_feedback_0'.format(key.lower())],
                    self.settings['restart_backup_folder'],
                    )
            except FileNotFoundError:
                pass
            except shutil.Error:
                pass
            try:
                shutil.move(
                    number_file,
                    self.settings['restart_backup_folder'],
                    )
            except FileNotFoundError:
                pass
            if restart_dict['feedback']:
                try:
                    shutil.move(
                        settings_file,
                        self.settings['restart_backup_folder'],
                        )
                except FileNotFoundError:
                    pass

            special_cases = ('Extract', 'Train2d', 'CTF')
            lines = []
            if check_state == 2 or key in special_cases:
                for entry in (save_file, done_file):
                    if os.path.exists(entry):
                        with open(entry, 'r') as read:
                            lines.extend([line.strip() for line in read.readlines() if line.strip()])
                    else:
                        with open(entry, 'w'):
                            pass

            remove_patterns = []
            if check_state in (1, 2) and key == 'CTF':
                if restart_dict['Motion'] != 0:
                    remove_patterns = [
                        '^CTF_sum',
                        ]

            elif check_state == 1 and key == 'Extract':
                if restart_dict['Picking'] == 1 and restart_dict['CTF'] == 1:
                    # Reset Motion correction and therefore picking and CTF
                    remove_patterns = [
                        '.*',
                        ]
                elif restart_dict['Picking'] == 2 and restart_dict['CTF'] == 2:
                    # Reset Picking and CTF but not motion correction
                    remove_patterns = [
                        '.*\.box',
                        '.*partres.txt',
                        ]
                elif restart_dict['Picking'] == 1:
                    assert False, 'Picking cannot be 1 without CTF be 1'
                elif restart_dict['CTF'] == 1:
                    assert False, 'Picking cannot be 1 without CTF be 1'
                elif restart_dict['Picking'] == 2:
                    # Only reset picking
                    remove_patterns = [
                        '.*\.box',
                        ]
                elif restart_dict['CTF'] == 2:
                    # Only reset CTF
                    remove_patterns = [
                        '.*partres.txt',
                        ]

            elif check_state == 1 and key == 'Train2d':
                if restart_dict['Motion'] == 2:
                    remove_patterns = [
                        '.*'
                        ]
                else:
                    remove_patterns = [
                        '.*\.hdf'
                        ]

            for pattern in remove_patterns:
                lines = sorted([entry for entry in lines if re.search(pattern, entry) is None])

            with open(save_file, 'w') as write:
                write.write('\n'.join(sorted(lines)) + '\n')
            for line in lines:
                share_list.append(line.split('|||')[-1])
                queue.put(line)

            with open(done_file, 'w'):
                pass
            with open(list_file, 'w'):
                pass

        elif check_state == 0:
            try:
                keep_list.append(os.path.basename(self.settings['{}_folder_feedback_0'.format(key.lower())]))
            except KeyError:
                pass
            if os.path.exists(save_file):
                with open(save_file, 'r') as read:
                    lines = [line.strip() for line in read.readlines() if line.strip()]

                if key.startswith('Copy_to'):
                    if '000_Feedback_results' in keep_list:
                        keep_feedback = True
                    else:
                        keep_feedback = False

                    good_lines = []
                    for line in lines:
                        if os.path.dirname(line) == self.settings['project_folder']:
                            good_lines.append(line)
                        else:
                            for entry in keep_list:
                                if entry in line:
                                    if '000_Feedback_results' in line and not keep_feedback:
                                        pass
                                    else:
                                        good_lines.append(line)
                    lines = [entry for entry in np.unique(good_lines) if os.path.exists(entry)]
                    with open(save_file, 'w') as write:
                        write.write('\n'.join(lines) + '\n')

                for line in lines:
                    if self.settings['software_meta_tar'] in line:
                        self.settings['copy_software_meta'] = False
                    else:
                        pass
                    share_list.append(line.split('|||')[-1])
                    queue.put(line)
            else:
                with open(save_file, 'w'):
                    pass

            if os.path.exists(done_file):
                with open(done_file, 'r') as read:
                    lines = [line.strip() for line in read.readlines() if line.strip()]
                    shared_dict_typ['file_number'] = len(lines)
                for line in lines:
                    if self.settings['software_meta_tar'] in line:
                        self.settings['copy_software_meta'] = False
                    else:
                        pass
            else:
                with open(done_file, 'w'):
                    pass

            if os.path.exists(list_file):
                with open(list_file, 'r') as read:
                    lines = [line.strip() for line in read.readlines() if line.strip()]
                for line in lines:
                    if line:
                        queue_list.append(line)
                    if self.settings['software_meta_tar'] in line:
                        self.settings['copy_software_meta'] = False
                    else:
                        pass
            else:
                with open(list_file, 'w'):
                    pass

            # Tar index
            if not queue_list:
                tar_files = glob.glob(os.path.join(
                    self.settings['tar_folder'],
                    '{0}_*.tar'.format(key)
                    ))
                if tar_files:
                    shared_dict_typ['tar_idx'] = max([int(re.search('{0}_.*([0-9]{{6}})\.tar'.format(re.escape(key)), entry).group(1)) for entry in tar_files]) + 1
                else:
                    shared_dict_typ['tar_idx'] = 0
            else:
                try:
                    shared_dict_typ['tar_idx'] = max([int(re.search('{0}_.*([0-9]{{6}})\.tar'.format(re.escape(key)), entry).group(1)) for entry in queue_list if re.search('{0}_.*([0-9]{{6}})\.tar'.format(re.escape(key)), entry)])
                except ValueError:
                    pass


        if prepend_list:
            with open(save_file, 'a') as append:
                append.write('\n'.join(prepend_list) + '\n')
            for entry in prepend_list:
                share_list.append(entry.split('|||')[-1])
                queue.put(entry)

from .processthread import ProcessThread
