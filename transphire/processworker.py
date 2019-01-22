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
import os
import re
import glob
import copy as cp
import queue as qu
try:
    from PyQt4.QtCore import QObject, pyqtSignal, pyqtSlot, QThread, QMutex
except ImportError:
    from PyQt5.QtCore import QObject, pyqtSignal, pyqtSlot, QThread, QMutex
from transphire.processthread import ProcessThread
from transphire import transphire_utils as tu


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
    sig_start = pyqtSignal(object)
    sig_finished = pyqtSignal()
    sig_error = pyqtSignal(str)
    sig_status = pyqtSignal(str, object, str, str)
    sig_notification = pyqtSignal(str)
    sig_plot_ctf = pyqtSignal(str, object, object, str)
    sig_plot_motion = pyqtSignal(str, object, object, str)
    sig_plot_picking = pyqtSignal(str, object, object, str)

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
        self.settings = {}

        # Events
        self.sig_start.connect(self.run)

    def emit_plot_signals(self):
        # Set CTF settings
        self.settings['CTF_folder'] = {}
        for entry in self.settings['Copy']['CTF_entries']:
            self.settings['CTF_folder'][entry] = os.path.join(
                self.settings['project_folder'],
                entry.replace(' ', '_')
                )
            self.sig_plot_ctf.emit(
                entry,
                self.settings['CTF_folder'][entry],
                self.settings,
                self.settings['Copy']['CTF']
                )

        # Set Motion settings
        self.settings['Motion_folder'] = {}
        for entry in self.settings['Copy']['Motion_entries']:
            self.settings['Motion_folder'][entry] = os.path.join(
                self.settings['project_folder'],
                entry.replace(' ', '_')
                )
            self.sig_plot_motion.emit(
                entry,
                self.settings['Motion_folder'][entry],
                self.settings,
                self.settings['Copy']['Motion']
                )

        # Set Picking settings
        self.settings['Picking_folder'] = {}
        for entry in self.settings['Copy']['Picking_entries']:
            self.settings['Picking_folder'][entry] = os.path.join(
                self.settings['project_folder'],
                entry.replace(' ', '_')
                )
            self.sig_plot_picking.emit(
                entry,
                self.settings['Picking_folder'][entry],
                self.settings,
                self.settings['Copy']['Picking']
                )

    @pyqtSlot(object)
    def run(self, settings):
        """
        Start the process.

        Arguments:
        settings - Transphire settings

        Return:
        None
        """
        # Set settings
        self.settings = settings
        content_process = cp.deepcopy(self.content_process)
        self.settings['copy_software_meta'] = True
        if self.settings['General']['Input extension'] in ('dm4'):
            self.settings['Output extension'] = 'mrc'
        else:
            self.settings['Output extension'] = self.settings['General']['Input extension']

        # Set paths
        self.settings['stack_folder'] = os.path.join(
            self.settings['project_folder'], 'Stack'
            )
        self.settings['meta_folder'] = os.path.join(
            self.settings['project_folder'], 'Meta'
            )
        self.settings['software_meta_folder'] = os.path.join(
            self.settings['project_folder'], 'Software_meta'
            )
        self.settings['software_meta_tar'] = os.path.join(
            self.settings['tar_folder'], 'Software_meta.tar'
            )
        self.settings['motion_folder'] = os.path.join(
            self.settings['motion_folder'],
            self.settings['Copy']['Motion'].replace(' ', '_')
            )
        self.settings['scratch_motion_folder'] = os.path.join(
            self.settings['scratch_folder'],
            self.settings['Copy']['Motion'].replace(' ', '_')
            )
        self.settings['ctf_folder'] = os.path.join(
            self.settings['ctf_folder'],
            self.settings['Copy']['CTF'].replace(' ', '_')
            )
        self.settings['picking_folder'] = os.path.join(
            self.settings['picking_folder'],
            self.settings['Copy']['Picking'].replace(' ', '_')
            )
        self.settings['compress_folder'] = os.path.join(
            self.settings['compress_folder'], 'Compress'
            )
        self.settings['Copy_hdd_folder'] = os.path.join(
            self.settings['Copy_hdd_folder'], 'HDD'
            )
        self.settings['Copy_work_folder'] = os.path.join(
            self.settings['Copy_work_folder'],
            self.settings['Copy']['Copy to work'].replace(' ', '_')
            )
        self.settings['Copy_backup_folder'] = os.path.join(
            self.settings['Copy_backup_folder'],
            self.settings['Copy']['Copy to backup'].replace(' ', '_')
            )

        typ_dict = {}
        wait_dict = {}
        share_dict = {}
        bad_dict = {}
        queue_dict = {}
        full_content = []
        idx_number = 0
        idx_values = 1
        for entry in content_process:
            for process in entry:
                for key in process:
                    process[key][idx_values]['group'], process[key][idx_values]['aim'] = \
                        process[key][idx_values]['group'].split(';')
                    process[key][idx_values]['aim'] = process[key][idx_values]['aim'].split(',')
                    wait_dict[key] = False
                    share_dict[key] = []
                    bad_dict[key] = []
                    queue_dict[key] = qu.Queue()
                    typ_dict[key] = {
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
                        'queue_list_time': 0,
                        'tar_idx': 0,
                        'queue_list': [],
                        'queue_lock': QMutex(),
                        'save_lock': QMutex(),
                        'count_lock': QMutex(),
                        'error_lock': QMutex(),
                        'bad_lock': QMutex(),
                        'share_lock': QMutex(),
                        'spot_dict': self.fill_spot_dict(),
                        'number_file': '{0}/last_filenumber.txt'.format(
                            self.settings['project_folder']
                            ),
                        'save_file': '{0}/Queue_{1}'.format(
                            self.settings['queue_folder'], key
                            ),
                        'done_file': '{0}/Queue_{1}_done'.format(
                            self.settings['queue_folder'], key
                            ),
                        'list_file': '{0}/Queue_{1}_list'.format(
                            self.settings['queue_folder'], key
                            ),
                        'error_file': '{0}/Queue_{1}_error'.format(
                            self.settings['error_folder'], key
                            ),
                        }

                    if process[key][idx_number] == '1':
                        full_content.append([key, process[key]])
                    else:
                        for idx in range(int(process[key][idx_number])):
                            full_content.append(
                                ['{0}_{1}'.format(key, idx+1), process[key]]
                                )

        # Queue communication dictionary
        queue_com = {
            'status': qu.Queue(),
            'notification': qu.Queue(),
            'error': qu.Queue(),
            }

        # Set stop variable to the return value of the pre_check
        if settings['Monitor']:
            self.stop = False
            self.emit_plot_signals()
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
                idx_values=idx_values,
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
                color = 'white'
            else:
                text = 'Monitoring'
                color = 'lightgreen'
            for entry in full_content:
                name = entry[0]
                key = '_'.join([key for key in name.split('_') if not check_int(key)])
                with open(typ_dict[key]['save_file']) as read:
                    nr_do = len([line for line in read.readlines() if line.strip()])
                with open(typ_dict[key]['done_file']) as read:
                    nr_done = len([line for line in read.readlines() if line.strip()])
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
                QThread.sleep(3)

    def run_process(self,
            typ_dict,
            queue_com,
            share_dict,
            bad_dict,
            queue_dict,
            content_process,
            full_content,
            idx_values,
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

        # Fill folder list and threads list
        for name in ['work', 'backup']:
            short_name = 'Copy_{0}'.format(name)
            long_name = 'Copy to {0}'.format(name)
            folder_name = '{0}_folder'.format(short_name)
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

        # Decide if one will use copy to HDD
        self.settings['Copy']['Copy_hdd'] = self.settings['Copy']['Copy to HDD']
        if self.settings['Copy']['Copy to HDD'] != 'False':
            if self.settings['Copy']['Copy to HDD'] == 'Later':
                pass
            else:
                try:
                    for folder in glob.glob('{0}/*'.format(self.settings['Copy_hdd_folder'])):
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
            use_threads_list.append('Copy_hdd')
        else:
            pass

        # Set CTF settings
        if self.settings['Copy']['CTF'] != 'False':
            folder_list.append('ctf_folder')
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

        # Set Compress settings
        if self.settings['Copy']['Compress'] != 'False':
            folder_list.append('compress_folder')
            use_threads_list.append('Compress')
        else:
            pass

        # Set Motion settings
        if self.settings['Copy']['Motion'] != 'False':
            folder_list.append('motion_folder')
            use_threads_list.append('Motion')
        else:
            pass

        # Set Picking settings
        if self.settings['Copy']['Picking'] != 'False':
            folder_list.append('picking_folder')
            use_threads_list.append('Picking')
        else:
            pass

        # Create output directories
        for entry in folder_list:
            try:
                tu.mkdir_p(self.settings[entry])
            except PermissionError:
                continue
            except OSError as err:
                print(str(err))
                self.sig_error.emit(str(err))
                return None

        self.emit_plot_signals()

        # Fill different dictionarys with process information
        gpu_mutex_dict = dict([(str(idx), [QMutex(), 0]) for idx in range(99)])

        # Shared dictionary
        shared_dict = {
            'share': share_dict,
            'bad': bad_dict,
            'queue': queue_dict,
            'translate_lock': QMutex(),
            'ctf_star_lock': QMutex(),
            'ctf_partres_lock': QMutex(),
            'motion_star_lock': QMutex(),
            'motion_star_relion3_lock': QMutex(),
            'motion_txt_lock': QMutex(),
            'gpu_lock': gpu_mutex_dict,
            'gpu_lock_lock': QMutex(),
            'typ': typ_dict,
            }

        # Fill process queues
        for entry in content_process:
            for process in entry:
                for key in process:
                    self.prefill_queue(
                        shared_dict=shared_dict,
                        entry=process[key][1]
                        )

        # Define file number and check if file already exists
        shared_dict['typ']['Import']['file_number'] = int(self.settings['General']['Start number']) - 1

        if self.settings['General']['Rename micrographs'] == 'True':
            new_name = '{0}/{1}{2:0{3}d}{4}'.format(
                self.settings['meta_folder'],
                self.settings['General']['Rename prefix'],
                shared_dict['typ']['Import']['file_number']+1,
                len(self.settings['General']['Estimated mic number']),
                self.settings['General']['Rename suffix']
                )

            if os.path.exists('{0}.jpg'.format(new_name)):
                old_filenumber = shared_dict['typ']['Import']['file_number']
                with open(shared_dict['typ']['Import']['number_file'], 'r') as read:
                    shared_dict['typ']['Import']['file_number'] = int(read.readline())
                if self.settings['General']['Increment number'] == 'True':
                    message = '{0}: Filenumber {1} already exists!\n'.format(
                        'Import',
                        old_filenumber
                        ) + \
                        'Last one used: {0} - Continue with {1}'.format(
                            shared_dict['typ']['Import']['file_number'],
                            shared_dict['typ']['Import']['file_number']+1
                            )
                    queue_com['error'].put(message)
                    queue_com['notification'].put(message)
                else:
                    self.stop = True
                    message = '{0}: Filenumber {1} already exists!\n'.format(
                        'Import',
                        old_filenumber
                        ) + \
                        'Check Startnumber! Last one used: {0}'.format(shared_dict['typ']['Import']['file_number'])
                    queue_com['error'].put(message)
                    queue_com['notification'].put(message)
            else:
                pass
        else:
            pass

        # Start threads
        thread_list = []
        use_threads_set = set(use_threads_list)
        for key, settings_content in full_content:
            content_settings = settings_content[idx_values]
            thread = ProcessThread(
                shared_dict=shared_dict,
                name=key,
                content_settings=content_settings,
                queue_com=queue_com,
                settings=self.settings,
                mount_directory=self.mount_directory,
                password=self.password,
                use_threads_set=use_threads_set,
                stop=self.stop,
                parent=self
                )
            thread.start()
            thread_list.append([thread, key, content_settings])
            QThread.sleep(1)

        # Run until the user stops the processes
        while True:
            try:
                self.check_queue(queue_com=queue_com)
            except BrokenPipeError:
                pass
            if self.stop:
                break
            else:
                pass
            QThread.sleep(3)

        # Indicate to stop all processes
        for key, settings_content in full_content:
            typ = settings_content[idx_values]['name']
            size = shared_dict['queue'][typ].qsize()
            self.sig_status.emit(
                'Stopping',
                [size, shared_dict['typ'][typ]['file_number']],
                key,
                '#ff5c33'
                )

        # Send the stop signals to all threads
        for thread, name, setting in thread_list:
            thread.stop = True

        # Wait for all threads to finish
        for thread, name, setting in thread_list:
            typ = setting['name']
            print('Waiting for', name, 'to finish!')
            while thread.is_running:
                QThread.msleep(1000)
            thread.quit()
            print('Waiting for', name, 'thread to quit!')
            thread.wait()
            self.check_queue(queue_com=queue_com)
            size = shared_dict['queue'][typ].qsize()
            self.sig_status.emit(
                'Not running',
                [size, shared_dict['typ'][typ]['file_number']],
                name,
                'white'
                )

    def pre_check_programs(self):
        """
        Check, if all programs the user wants to use are available.

        Arguments:
        None

        Return:
        True, if programs exist, else False
        """
        error = False
        check_files = []
        check_files.append(self.settings['Copy']['Motion'])
        check_files.append(self.settings['Copy']['CTF'])
        check_files.append(self.settings['Copy']['Picking'])
        check_files.append('IMOD header')

        if self.settings['Copy']['Picking'] == 'crYOLO v1.0.4' or \
                self.settings['Copy']['Picking'] == 'crYOLO v1.0.5' or \
                self.settings['Copy']['Picking'] == 'crYOLO v1.1.0' or \
                self.settings['Copy']['Picking'] == 'crYOLO v1.2.1' or \
                self.settings['Copy']['Picking'] == 'crYOLO v1.2.2':
            if self.settings[self.settings['Copy']['Picking']]['Filter micrographs'] == 'True':
                check_files.append('e2proc2d.py')
            else:
                pass
        else:
            pass

        if self.settings['Copy']['Compress'] == 'True':
            check_files.append('IMOD mrc2tif')
        else:
            pass

        if len(self.settings['motion_frames']) > 1:
            check_files.append('SumMovie v1.0.2')
        else:
            pass

        for name in check_files:
            if name != 'False' and name != 'Later':
                try:
                    is_file = os.path.isfile(self.settings['Path'][name])
                except KeyError:
                    self.sig_error.emit(
                        '{0} path not valid or disabled (Advanced, Rare)! Please adjust it!'.format(name)
                        )
                    error = True
                else:
                    if not is_file:
                        self.sig_error.emit(
                            '{0} path not valid or disabled (Advanced, Rare)! Please adjust it!'.format(name)
                            )
                        error = True
                    else:
                        pass
            else:
                pass

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
        spot_file = os.path.join(self.settings['project_folder'], '.spot_dict')
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

    def prefill_queue(self, shared_dict, entry):
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
        save_file = shared_dict_typ['save_file']
        done_file = shared_dict_typ['done_file']
        list_file = shared_dict_typ['list_file']
        share_list = shared_dict['share'][share]
        queue = shared_dict['queue'][key]
        queue_list = shared_dict_typ['queue_list']

        if os.path.exists(save_file):
            with open(save_file, 'r') as read:
                lines = [line.rstrip() for line in read.readlines()]

            for line in lines:
                if self.settings['software_meta_tar'] in line:
                    self.settings['copy_software_meta'] = False
                else:
                    pass
                if line.startswith(self.settings['project_folder']):
                    share_list.append(line)
                    queue.put(line)
                else:
                    pass
        else:
            with open(save_file, 'w'):
                pass

        if os.path.exists(done_file):
            with open(done_file, 'r') as read:
                lines = [line.rstrip() for line in read.readlines()]
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
                lines = [line.rstrip() for line in read.readlines()]
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
                '{0}_*\.tar'.format(key)
                ))
            if tar_files:
                shared_dict_typ['tar_idx'] = max([int(re.match('{0}_([0-9]+)\.tar'.format(key), entry).group(1)) for entry in tar_files]) + 1
            else:
                shared_dict_typ['tar_idx'] = 0
        else:
            try:
                shared_dict_typ['tar_idx'] = max([int(re.match('{0}_([0-9]+)\.tar'.format(key), entry).group(1)) for entry in queue_list if re.match('{0}_([0-9]+)\.tar'.format(key), entry)])
            except ValueError:
                pass
