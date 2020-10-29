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
import signal
import time
import os
import re
import shutil
import traceback as tb
import glob
import json
import copy
import matplotlib
import matplotlib.pyplot
import threading
import tarfile
import subprocess as sp
import numpy as np
import pexpect as pe
import hyperspy.io_plugins.digital_micrograph as hidm

from . import transphire_utils as tu
from . import transphire_software as tus
from . import transphire_motion as tum
from . import transphire_ctf as tuc
from . import transphire_picking as tup
from . import transphire_extract as tue
from . import transphire_class2d as tuclass2d
from . import transphire_select2d as tselect2d
from . import transphire_train2d as ttrain2d


class ProcessThread(object):
    """
    Worker thread

    Inherits from:
    object

    Buttons:
    None

    Signals:
    None
    """

    def __init__(
            self,
            shared_dict,
            name,
            content_settings,
            queue_com,
            password,
            settings,
            mount_directory,
            use_threads_set,
            stop,
            abort,
            has_finished,
            data_frame,
            parent=None
            ):
        """
        Initialize object variables.

        Arguments:
        shared_dict - Dictionary containing shared information
        name - Name of the process
        content_settings - Settings for this process
        queue_com - Queue communication dictionary
        password - Sudo password
        settings - TranSPHIRE settings
        mount_directory - Directory for mount points
        use_threads_set - set of threads that are used
        stop - Value of the stop variable
        parent - Parent widget (default None)

        Return:
        None
        """
        super(ProcessThread, self).__init__()
        # Variables
        self.stop = stop
        self.abort = abort
        self.password = password
        self.shared_dict = shared_dict
        self.done = False
        self.content_settings = content_settings

        self.name = name
        self.typ = self.content_settings['name']
        self.run_this_thread = bool(self.typ in use_threads_set)

        self.queue_com = queue_com
        self.settings = settings
        self.mount_directory = mount_directory
        self.time_last = None
        self.time_last_error = None
        self.notification_send = None
        self.notification_time = float(self.settings['Notification']['Time until notification'])
        self.is_running = False
        self.data_frame = data_frame

        self.queue = shared_dict['queue'][self.content_settings['name']]
        self.shared_dict_typ = shared_dict['typ'][self.content_settings['name']]
        self.queue_lock = self.shared_dict_typ['queue_lock']
        try:
            self.prog_name = self.settings['Copy'][self.typ]
        except KeyError:
            self.prog_name = None

        try:
            self.later = bool(self.settings['Copy'][self.typ] == 'Later')
        except KeyError:
            self.later = False

        try:
            self.user = self.settings['{0}_user'.format(self.typ)]
        except KeyError:
            self.user = None

        self.queue_com['log'].put(tu.create_log('Starting', name))
        self.has_finished = has_finished
        self.disable_thread = False

        # This list saves the per process locks to prevent garbage collection
        self.GLOBAL_LOCKS = []

        if self.typ not in ('Motion', 'CTF'):
            try:
                for value in self.settings[self.prog_name].values():
                    try:
                        if '|||' in value:
                            external_log, local_key = value.split('|||')
                            with open(settings[external_log], 'r') as read:
                                log_data = json.load(read)
                            try:
                                set_value = log_data[self.settings['current_set']][self.prog_name][local_key]['new_file']
                            except KeyError:
                                continue
                            self.settings[self.prog_name][local_key] = set_value
                    except TypeError:
                        pass
            except KeyError:
                pass

    def wait(self, wait_time=10):
        for _ in range(int(wait_time)):
            time.sleep(1)
            if self.stop.value:
                break
        else:
            time.sleep(wait_time % 1)

    def run(self):
        """
        Run the thread.

        Arguments:
        None

        Return:
        None
        """
        # Replacing the Matplotlib Thread shared by all processes with its own lock to avoid a deadlock scenario.
        matplotlib.pyplot.switch_backend('AGG')
        lock = threading.RLock()
        matplotlib.backends.backend_agg.RendererAgg.lock = lock
        self.GLOBAL_LOCKS.append(lock)

        # Current time
        self.time_last = time.time()
        self.time_last_error = time.time()
        self.notification_send = False

        # Event loop
        while not self.stop.value:
            if self.shared_dict_typ['do_update_count'] != 0:
                self.queue_lock.acquire()
                try:
                    self.shared_dict_typ['do_update_count'] -= 1
                finally:
                    self.queue_lock.release()

                self.shared_dict['global_update_lock'].acquire()
                self.shared_dict['global_update_lock'].release()

            if self.done:
                while not self.stop.value:
                    self.queue_com['status'].put([
                        'Finished',
                        [],
                        self.typ,
                        tu.get_color('Finished')
                        ])
                    self.wait(10)
                continue
            else:
                pass

            if not self.run_this_thread:
                while not self.stop.value:
                    self.queue_com['status'].put([
                        'Skipped',
                        [self.queue.qsize()],
                        self.typ,
                        tu.get_color('Skipped')
                        ])
                    self.wait(10)
                continue
            else:
                pass

            if self.later:
                while not self.stop.value:
                    self.queue_com['status'].put([
                        'Later',
                        [self.queue.qsize()],
                        self.typ,
                        tu.get_color('Later')
                        ])
                    self.wait(10)
                continue
            else:
                pass

            if self.check_quota():
                pass
            else:
                self.queue_com['status'].put([
                    'Quota Error',
                    [self.queue.qsize()],
                    self.typ,
                    tu.get_color('Error')
                    ])
                self.wait(10)
                continue

            if self.check_connection():
                pass
            else:
                self.queue_com['status'].put([
                    'Connection Error',
                    [self.queue.qsize()],
                    self.typ,
                    tu.get_color('Error')
                    ])
                self.wait(10)
                continue

            if self.check_full():
                pass
            else:
                self.queue_com['status'].put([
                    'No space Error',
                    [self.queue.qsize()],
                    self.typ,
                    tu.get_color('Error')
                    ])
                self.wait(10)
                continue

            if self.shared_dict_typ['delay_error']:
                self.wait(10)
                self.shared_dict_typ['delay_error'] = False
                self.shared_dict_typ['is_error'] = False

            if self.shared_dict_typ['unknown_error']:
                time_diff = time.time() - self.time_last
                if self.typ == 'Find':
                    self.queue_com['status'].put([
                        'Unknown Error',
                        ['{0:.1f} min'.format(time_diff / 60)],
                        self.typ,
                        tu.get_color('Error')
                        ])
                else:
                    self.queue_com['status'].put([
                        'Unknown Error',
                        [
                            self.queue.qsize(),
                            self.shared_dict_typ['file_number'],
                            '{0:.1f} min'.format(time_diff / 60)
                            ],
                        self.typ,
                        tu.get_color('Error')
                        ])
                self.wait(10)
                self.shared_dict_typ['unknown_error'] = False
                self.shared_dict_typ['is_error'] = False
                continue
            else:
                pass

            # Start processes
            self.is_running = True
            if self.typ == 'Find':
                self.start_queue_find()
            elif self.typ == 'Meta':
                self.start_queue_meta()
            else:
                self.start_queue(clear_list=False)
            self.is_running = False

        if self.shared_dict_typ['queue_list']:
            if self.abort.value:
                pass
            elif self.later:
                pass
            elif not self.run_this_thread:
                pass
            else:
                self.is_running = True
                if self.typ not in ('Find', 'Meta', 'Extract'):
                    self.start_queue(clear_list=True)
                self.is_running = False

        # Print, if stopped
        if self.disable_thread:
            color = tu.get_color('Running')
        else:
            color = tu.get_color('Error')
        self.queue_com['status'].put([
            '{0:02d}|{1:02d}'.format(
                self.shared_dict_typ['running'],
                self.shared_dict_typ['max_running'],
                ),
            [
                self.queue.qsize(),
                self.shared_dict_typ['file_number']
                ],
            self.typ,
            color
            ])
        self.queue_com['log'].put(tu.create_log('Stopped', self.name))
        print(self.name, ': Stopped')
        self.has_finished.value = True
        self.GLOBAL_LOCKS.clear()

    def check_full(self):
        """
        Check, if the program got an no space error.

        Arguments:
        None

        Return:
        True, if there is a no space error, else False
        """
        copy_threads = [
            'full_work', 'full_backup', 'full_hdd', 'full_transphire'
            ]
        for name in copy_threads:
            if self.shared_dict_typ[name]:
                return False
            else:
                pass
        return True

    def check_quota(self):
        """
        Check, if the computer reached the quota limit.

        Arguments:
        None

        Return:
        True, if the computer did not hit the limit, else False
        """
        scratch_stop = float(self.settings['Notification']['Scratch quota stop (%)']) / 100
        project_stop = float(self.settings['Notification']['Project quota stop (%)']) / 100
        if self.typ in ['Copy_to_work', 'Copy_to_backup', 'Copy_to_hdd']:
            return True
        else:
            pass

        for stop, folder in zip(
                [project_stop, scratch_stop],
                ['project_folder', 'scratch_folder']
                ):
            try:
                total_quota = shutil.disk_usage(self.settings[folder]).total / 1e12
                used_quota = shutil.disk_usage(self.settings[folder]).used / 1e12
            except FileNotFoundError:
                self.stop.value = True
                message_error = '\n'.join([
                    '{0} no longer available!'.format(
                        folder.replace('_', ' ')
                        ),
                    '{0} is stopping now!'.format(self.name)
                    ])
                message_notification = '\n'.join([
                    'Folder no longer available!',
                    '{0} is stopping now!'.format(self.name)
                    ])
                self.queue_com['notification'].put(
                    message_notification
                    )
                self.queue_com['error'].put(
                    message_error
                    )
                return False
            if used_quota > (total_quota * stop):
                self.stop.value = True
                message_error = '\n'.join([
                    'Less than {0:.1f} Tb free on {1}!'.format(
                        total_quota * (1 - stop),
                        folder.replace('_', ' ')
                        ),
                    '{0} is stopping now!'.format(self.name)
                    ])
                message_notification = '\n'.join([
                    'Less than {0:.1f} Tb free!'.format(
                        total_quota * (1 - stop),
                        ),
                    '{0} is stopping now!'.format(self.name)
                    ])
                self.queue_com['notification'].put(message_notification)
                self.queue_com['error'].put(message_error)
                return False
            else:
                pass
        return True

    def check_connection(self):
        """
        Check, if the process got a lost connection error.

        Arguments:
        None

        Return:
        True, if the process did not get an error, else False
        """
        # List of processes and related folder names
        processes = [
            ['lost_input_frames', 'Input project path for frames'],
            ['lost_input_meta', 'Input project path for jpg'],
            ['lost_work', 'copy_to_work_folder_feedback_0'],
            ['lost_backup', 'copy_to_backup_folder_feedback_0'],
            ['lost_hdd', 'copy_to_hdd_folder_feedback_0']
            ]
        for process, folder in processes:
            if self.shared_dict_typ[process]:
                time_diff = time.time() - self.time_last
                if folder == 'Input project path for frames' or \
                        folder == 'Input project path for jpg':
                    output_folder = self.settings['Input'][folder]
                else:
                    output_folder = self.settings[folder]

                self.queue_com['status'].put([
                    'Lost connection',
                    ['{0:.1f} min'.format(time_diff / 60)],
                    self.typ,
                    tu.get_color('Error')
                    ])
                if self.typ == 'Motion' or \
                        self.typ == 'CTF' or \
                        self.typ == 'Compress':
                    # These processes do not have a mount point
                    return False
                elif self.mount_directory in output_folder:
                    if self.check_if_mounted(output_folder):
                        self.shared_dict_typ[process] = False
                        self.queue_com['notification'].put(''.join([
                            '{0} is connected again!'.format(self.name),
                            'If this message is occuring very often, ',
                            'please remount {0} or restart TranSPHIRE'.format(
                                self.name
                                )
                            ]))
                        if time.time() - self.time_last_error > 1800:
                            self.queue_com['error'].put(
                                '{0} is connected again!'.format(self.typ)
                                )
                            self.time_last_error = time.time()
                        else:
                            pass
                    else:
                        return False
                else:
                    pass
            else:
                pass

        return True

    @staticmethod
    def check_if_mounted(directory):
        """
        Check, if the mount point is still present.

        Arguments:
        directory - Directory to check.

        Return:
        True, if the mount point is still present, else False
        """
        folder_names = directory.split('/')
        # Return, if the process is not running.
        if folder_names[-1] == 'False' or folder_names[-1] == 'Later':
            return False
        else:
            pass

        for idx in range(1, len(folder_names)+1):
            current_dir = os.path.join(*folder_names[0:idx])
            if not current_dir:
                continue
            elif folder_names[0]:
                pass
            else:
                current_dir = '/{0}'.format(current_dir)

            if os.path.ismount(current_dir):
                return True
            else:
                try:
                    os.listdir(current_dir)
                except PermissionError:
                    return True
                else:
                    pass
        return False

    def reset_queue(self, aim=None, switch_feedback=False, remove_pattern='THIS IS A DUMMY PATTERN'):
        if aim is None:
            aim = self.typ

        self.shared_dict['typ'][aim]['queue_lock'].acquire()
        try:
            self.shared_dict['typ'][aim]['do_update_count'] = self.shared_dict['typ'][aim]['max_running'] - bool(self.typ == aim)
        finally:
            self.shared_dict['typ'][aim]['queue_lock'].release()

        while self.shared_dict['typ'][aim]['do_update_count'] != 0:
            self.wait(0.5)

        self.shared_dict['typ'][aim]['queue_lock'].acquire()
        try:
            while not self.shared_dict['queue'][aim].empty():
                self.shared_dict['queue'][aim].get()
            self.wait(1)

            with open(self.shared_dict['typ'][aim]['done_file'], 'r') as read:
                content_done = [line.strip() for line in read.readlines() if line.strip()]
            with open(self.shared_dict['typ'][aim]['save_file'], 'r') as read:
                content_save = [line.strip() for line in read.readlines() if line.strip()]

            if switch_feedback:
                tu.copy(
                    self.shared_dict['typ'][aim]['save_file'],
                    '{0}_folder_feedback_{1}'.format(self.shared_dict['typ'][aim]['save_file'], self.settings['do_feedback_loop'].value)
                    )
                tu.copy(
                    self.shared_dict['typ'][aim]['list_file'],
                    '{0}_folder_feedback_{1}'.format(self.shared_dict['typ'][aim]['list_file'], self.settings['do_feedback_loop'].value)
                    )
                tu.copy(
                    self.shared_dict['typ'][aim]['done_file'],
                    '{0}_folder_feedback_{1}'.format(self.shared_dict['typ'][aim]['done_file'], self.settings['do_feedback_loop'].value)
                    )

            pattern = re.compile(remove_pattern)
            combined_content = sorted([entry for entry in content_done + content_save if pattern.search(entry) is None])

            self.try_write(
                self.shared_dict['typ'][aim]['save_file'],
                'w',
                '{0}\n'.format('\n'.join(combined_content))
                )
            self.try_write(
                self.shared_dict['typ'][aim]['done_file'],
                'w',
                ''
                )
            self.try_write(
                self.shared_dict['typ'][aim]['list_file'],
                'w',
                ''
                )

            self.shared_dict['typ'][aim]['queue_list_lock'].acquire()
            try:
                self.shared_dict['typ'][aim]['queue_list_time'] = time.time()
                self.shared_dict['typ'][aim]['queue_list'][:] = []
            finally:
                self.shared_dict['typ'][aim]['queue_list_lock'].release()
            for entry in combined_content:
                assert entry, (aim, entry)
                self.shared_dict['queue'][aim].put(entry, block=False)

            self.shared_dict['typ'][aim]['file_number'] = 0

        finally:
            self.shared_dict['typ'][aim]['queue_lock'].release()

    def start_queue_meta(self):
        """
        Start copying meta files.

        Arguments:
        None

        Return:
        None
        """
        if not self.settings['copy_software_meta']:
            self.done = True
            return None
        else:
            pass
        folder = self.settings['Input']['Input project path for jpg']
        if folder:
            self.queue_com['status'].put([
                'Copy Metadata',
                [],
                self.typ,
                tu.get_color('Running')
                ])
            try:
                self.run_software_meta(directory=folder)
            except FileNotFoundError as e:
                print(e)
                self.stop.value = True
                message_notification = '\n'.join([
                    'Folder no longer available!',
                    '{0} is stopping now!'.format(self.name)
                    ])
                message_error = '\n'.join([
                    '{0} no longer available!'.format(folder),
                    '{0} is stopping now!'.format(self.name)
                    ])
                self.queue_com['notification'].put(
                    message_notification
                    )
                self.queue_com['error'].put(
                    message_error
                    )
        else:
            print('No search path specified')
        self.done = True

    def start_queue_find(self):
        """
        Start finding files to process.

        Arguments:
        None

        Return:
        None
        """
        time_diff = time.time() - self.time_last

        self.queue_com['status'].put([
            'Run',
            ['{0:.1f} min'.format(time_diff / 60)],
            self.typ,
            tu.get_color('Running')
            ])
        try:
            self.run_find()
        except FileNotFoundError:
            self.write_error(
                msg=tb.format_exc(),
                root_name=''
                )
            self.lost_connection(
                typ='lost_work'
                )
        except Exception:
            print('!!! UNKNOWN !!!\n')
            msg = tb.format_exc()
            self.write_error(
                msg=msg,
                root_name=''
                )
            if 'termios.error' not in msg:
                message_notification = '\n'.join([
                    'Unknown error occured in {0}!'.format(self.name),
                    'The process will continue, but check the error file!',
                    ])
                message_error = '\n'.join([
                    'Unknown error occured in {0}!'.format(self.name),
                    'The process will continue, but check the error file!',
                    '{0}'.format(self.shared_dict_typ['error_file'])
                    ])
                if time.time() - self.time_last_error > 1800:
                    self.queue_com['notification'].put(message_notification)
                    self.queue_com['error'].put(message_error)
                    self.time_last_error = time.time()
                else:
                    pass
                self.shared_dict_typ['unknown_error'] = True
                self.shared_dict_typ['is_error'] = True
            else:
                pass
        else:
            time_diff = time.time() - self.time_last
            if time_diff / 60 > self.notification_time and \
                    not self.notification_send:
                self.notification_send = True
                message = 'No new files from data collection in the last {0} Minutes!'.format(
                    self.notification_time
                    )
                self.queue_com['notification'].put(message)
                self.queue_com['error'].put(message)
        self.wait(20)

    def start_queue(self, clear_list):
        """
        Start pipeline processes.

        Arguments:
        None

        Return:
        None
        """
        self.queue_lock.acquire()
        error = False
        dummy = False
        try:

            try:
                with open(self.shared_dict_typ['feedback_lock_file'], 'r') as read:
                    if int(read.readline().strip()) == 1:
                        error = True
            except FileNotFoundError:
                pass

            if error:
                self.queue_com['status'].put([
                    'Pending feedback',
                    [
                        self.queue.qsize(),
                        self.shared_dict_typ['file_number']
                        ],
                    self.typ,
                    tu.get_color('Waiting')
                    ])
            elif clear_list:
                dummy = True
                self.shared_dict_typ['queue_list_time'] -= 60
            else:
                if self.queue.empty():
                    if self.shared_dict_typ['is_error']:
                        error = True
                    else:
                        if self.shared_dict_typ['running'] == 0:
                            color = tu.get_color('Waiting')
                        else:
                            color = tu.get_color('Running')
                        self.queue_com['status'].put([
                            '{0:02d}|{1:02d}'.format(
                                self.shared_dict_typ['running'],
                                self.shared_dict_typ['max_running'],
                                ),
                            [
                                self.queue.qsize(),
                                self.shared_dict_typ['file_number']
                                ],
                            self.typ,
                            color
                            ])
                        if not self.shared_dict_typ['queue_list']:
                            error = True
                        elif time.time() - self.shared_dict_typ['queue_list_time'] > 30:
                            dummy = True
                        else:
                            error = True
                else:
                    pass
        except Exception:
            error = True
        finally:
            self.queue_lock.release()

        if error:
            self.wait(5)
            return None
        else:
            pass

        # Get new file
        self.queue_lock.acquire()
        try:
            self.shared_dict_typ['running'] += 1
            if self.shared_dict_typ['running'] == 0:
                color = tu.get_color('Waiting')
            else:
                color = tu.get_color('Running')
            self.queue_com['status'].put([
                '{0:02d}|{1:02d}'.format(
                    self.shared_dict_typ['running'],
                    self.shared_dict_typ['max_running'],
                    ),
                [
                    self.queue.qsize(),
                    self.shared_dict_typ['file_number']
                    ],
                self.typ,
                color,
                ])
            if dummy:
                root_name = 'None'
            else:
                root_name = self.remove_from_queue()
        except Exception:
            self.shared_dict_typ['running'] -= 1
            if self.shared_dict_typ['running'] == 0:
                color = tu.get_color('Waiting')
            else:
                color = tu.get_color('Running')
            self.queue_com['status'].put([
                '{0:02d}|{1:02d}'.format(
                    self.shared_dict_typ['running'],
                    self.shared_dict_typ['max_running'],
                    ),
                [
                    self.queue.qsize(),
                    self.shared_dict_typ['file_number']
                    ],
                self.typ,
                color,
                ])
            return None
        finally:
            self.queue_lock.release()

        # Set for every process a method and the right lost_connection name
        method_dict = {
            'Import': {
                'method': self.run_import,
                'lost_connect': 'full_transphire'
                },
            'Motion': {
                'method': self.run_motion,
                'lost_connect': 'full_transphire'
                },
            'CTF': {
                'method': self.run_ctf,
                'lost_connect': 'full_transphire'
                },
            'Picking': {
                'method': self.run_picking,
                'lost_connect': 'full_transphire'
                },
            'Extract': {
                'method': self.run_extract,
                'lost_connect': 'full_transphire'
                },
            'Class2d': {
                'method': self.run_class2d,
                'lost_connect': 'full_transphire'
                },
            'Select2d': {
                'method': self.run_select2d,
                'lost_connect': 'full_transphire'
                },
            'Train2d': {
                'method': self.run_train2d,
                'lost_connect': 'full_transphire'
                },
            'Auto3d': {
                'method': self.run_auto3d,
                'lost_connect': 'full_transphire'
                },
            'Compress': {
                'method': self.run_compress,
                'lost_connect': 'full_transphire'
                },
            'Copy_to_work': {
                'method': self.run_copy_extern,
                'lost_connect': 'full_work'
                },
            'Copy_to_backup': {
                'method': self.run_copy_extern,
                'lost_connect': 'full_backup'
                },
            'Copy_to_hdd': {
                'method': self.run_copy_extern,
                'lost_connect': 'full_hdd'
                }
            }

        try:
            method_dict[self.typ]['method'](
                root_name=root_name,
                )
        except FileNotFoundError as err:
            if not dummy:
                self.add_to_queue(aim=self.typ, root_name=root_name)
            self.write_error(msg=tb.format_exc(), root_name=root_name)
            if 'Check Startnumber' in str(err):
                pass
            else:
                self.lost_connection(
                    typ='lost_input_meta'
                    )
                self.lost_connection(
                    typ='lost_input_frames'
                    )
            self.shared_dict_typ['delay_error'] = True
            self.shared_dict_typ['is_error'] = True
        except BlockingIOError:
            if not dummy:
                self.add_to_queue(aim=self.typ, root_name=root_name)
            print('!!! BlockingIOError !!! \n')
            msg = tb.format_exc()
            self.write_error(msg=msg, root_name=root_name)
            if 'termios.error' not in msg:
                message_notification = '\n'.join([
                    'BlockingIOError occured in {0}!'.format(self.name),
                    'The process will continue, but check the error file!',
                    ])
                message_error = '\n'.join([
                    'BlockingIOError occured in {0}!'.format(self.name),
                    'The process will continue, but check the error file!',
                    '{0}'.format(self.shared_dict_typ['error_file'])
                    ])
                if time.time() - self.time_last_error > 1800:
                    self.queue_com['notification'].put(message_notification)
                    self.queue_com['error'].put(message_error)
                    self.time_last_error = time.time()
                else:
                    pass
                self.shared_dict_typ['unknown_error'] = True
                self.shared_dict_typ['is_error'] = True
            else:
                pass
        except IOError:
            if not dummy:
                self.add_to_queue(aim=self.typ, root_name=root_name)
            self.write_error(msg=tb.format_exc(), root_name=root_name)
            if self.typ != 'Import':
                self.lost_connection(
                    typ=method_dict[self.typ]['lost_connect']
                    )
                self.shared_dict_typ['delay_error'] = True
                self.shared_dict_typ['is_error'] = True
        except UserWarning:
            if not dummy:
                self.add_to_queue(aim=self.typ, root_name=root_name)
            #self.write_error(msg=tb.format_exc(), root_name=root_name)
            self.stop.value = True
            self.abort.value = True
            self.disable_thread = True
            self.queue_lock.acquire()
            #if self.typ == 'Picking': print(self.name, 'User Error! Reduce Max running', 1)
            try:
                #if self.typ == 'Picking': print(self.name, 'User Error! Reduce Max running', 2)
                self.shared_dict_typ['max_running'] -= 1
            finally:
                self.queue_lock.release()
            #if self.typ == 'Picking': print(self.name, 'User Error! Reduce Max running', 3)
        except Exception:
            if not dummy:
                self.add_to_queue(aim=self.typ, root_name=root_name)
            print('!!! UNKNOWN !!! \n')
            msg = tb.format_exc()
            self.write_error(msg=msg, root_name=root_name)
            if 'termios.error' not in msg:
                message_notification = '\n'.join([
                    'Unknown error occured in {0}!'.format(self.name),
                    'The process will continue, but check the error file!',
                    ])
                message_error = '\n'.join([
                    'Unknown error occured in {0}!'.format(self.name),
                    'The process will continue, but check the error file!',
                    '{0}'.format(self.shared_dict_typ['error_file'])
                    ])
                if time.time() - self.time_last_error > 1800:
                    self.queue_com['notification'].put(message_notification)
                    self.queue_com['error'].put(message_error)
                    self.time_last_error = time.time()
                else:
                    pass
                self.shared_dict_typ['unknown_error'] = True
                self.shared_dict_typ['is_error'] = True
            else:
                pass
        else:
            if not dummy:
                self.remove_from_queue_file(root_name, self.shared_dict_typ['save_file'])

                self.queue_lock.acquire()
                try:
                    self.add_to_queue_file(
                        root_name=root_name,
                        file_name=self.shared_dict['typ'][self.typ]['done_file'],
                        )

                finally:
                    self.queue_lock.release()

                self.check_queue_files(root_name=root_name)

                self.queue_lock.acquire()
                try:
                    self.shared_dict_typ['file_number'] += 1
                finally:
                    self.queue_lock.release()

        #if self.typ == 'Picking': print(self.name, 'User Error! Reduce Max running', 4)
        self.queue_lock.acquire()
        try:
            #if self.typ == 'Picking': print(self.name, 'User Error! Reduce Max running', 5)
            self.shared_dict_typ['running'] -= 1
            if not self.shared_dict_typ['is_error']:
                #if self.typ == 'Picking': print(self.name, 'User Error! Reduce Max running', 6)
                if self.shared_dict_typ['running'] == 0:
                    color = tu.get_color('Waiting')
                else:
                    color = tu.get_color('Running')
                self.queue_com['status'].put([
                    '{0:02d}|{1:02d}'.format(
                        self.shared_dict_typ['running'],
                        self.shared_dict_typ['max_running'],
                        ),
                    [
                        self.queue.qsize(),
                        self.shared_dict_typ['file_number']
                        ],
                    self.typ,
                    color,
                    ])
        finally:
            self.queue_lock.release()
        #if self.typ == 'Picking': print(self.name, 'User Error! Reduce Max running', 7)

    def check_queue_files(self, root_name):
        if self.settings['Copy']['Compress'] in ('False', 'Later'):
            return

        basename = os.path.basename(os.path.splitext(root_name)[0])
        if self.settings['Input']['Input frames extension'] in ('dm4',):
            stack_extension = 'mrc'
        elif self.settings['Input']['Input frames extension'] in ('tiff', 'tif'):
            return
        else:
            stack_extension = self.settings['Input']['Input frames extension']

        stack_file = os.path.join(
            self.settings['stack_folder'],
            '{0}.{1}'.format(
                basename,
                stack_extension,
                )
            )
        compressed_file = os.path.join(
            self.settings['compress_folder_feedback_0'],
            '{0}.{1}'.format(
                basename,
                self.settings[self.settings['Copy']['Compress']]['--command_compress_extension'],
                )
            )

        delete_stack = True
        for key in self.shared_dict['typ']:
            self.shared_dict['typ'][key]['save_lock'].acquire()
            try:
                for name in ('save_file', 'list_file'):
                    with open(self.shared_dict['typ'][key][name]) as read:
                        reads = read.read()
                    if compressed_file in reads:
                        delete_stack = False
                    if stack_file in reads:
                        delete_stack = False
            finally:
                self.shared_dict['typ'][key]['save_lock'].release()

        if delete_stack:
            options = (
                ('Delete stack after compression?', stack_file),
                ('Delete compressed stack after copy?', compressed_file),
                )
            for option, file_to_delete in options:
                if self.settings['Copy'][option] == 'True':
                    try:
                        os.remove(file_to_delete)
                    except Exception:
                        pass

    def write_error(self, msg, root_name):
        """
        Write to error file.

        Arguments:
        msg - Message to send.
        root_name - File that was processed while the error occured.

        Return:
        None
        """
        self.shared_dict_typ['error_lock'].acquire()
        try:
            local = time.localtime()
            print('\n{0}/{1}/{2}-{3}:{4}:{5}\t'.format(*local[0:6]))
            print(root_name)
            print('New error message in error file: {0}'.format(
                self.shared_dict_typ['error_file']
                ))
            content = []
            content.append('{0}/{1}/{2}-{3}:{4}:{5}\t'.format(*local[0:6]))
            content.append('{0}\n'.format(self.typ))
            content.append('{0}\n'.format(root_name))
            if self.password:
                content.append(
                    '{0}\n\n\n'.format(
                        str(msg).replace(self.password, 'SUDOPASSWORD')
                        )
                    )
            else:
                content.append('{0}\n\n\n'.format(str(msg)))

            self.try_write(self.shared_dict_typ['error_file'], 'a', ''.join(content))
        finally:
            self.shared_dict_typ['error_lock'].release()

    def remove_from_queue(self):
        """
        Remove item from queue.

        Arguments:
        None

        Return:
        Name removed from the queue.
        """
        value = self.queue.get(block=False)
        return value

    def add_to_queue_file(self, root_name, file_name, allow_dublicate=False):
        """
        Add item to queue_file.

        Arguments:
        root_name - Name to add
        file_name - File to append to

        Return:
        Name removed from the queue.
        """
        is_present = False
        try:
            with open(file_name, 'r') as read:
                is_present = bool(re.search(r'^{0}$'.format(re.escape(root_name)), read.read(), re.MULTILINE))
        except FileNotFoundError:
            pass

        if not is_present or allow_dublicate:
            self.try_write(file_name, 'a', '{0}\n'.format(root_name))
        else:
            pass

    def all_in_queue_file(self, aim, root_name, lock=True):
        """
        Add item to queue.

        Arguments:
        aim - Aim queue
        root_name - Name to add

        Return:
        None
        """
        if lock:
            self.shared_dict['typ'][aim]['queue_list_lock'].acquire()
        matches = 0
        try:
            files = (
                self.shared_dict['typ'][aim]['list_file'],
                )
            for file_name in files:
                try:
                    with open(file_name, 'r') as read:
                        matches = re.findall(r'^.*{0}.*$'.format(re.escape(root_name)), read.read(), re.MULTILINE)
                except FileNotFoundError:
                    pass
        finally:
            if lock:
                self.shared_dict['typ'][aim]['queue_list_lock'].release()
        return matches

    def already_in_queue_file(self, aim, root_name):
        """
        Add item to queue.

        Arguments:
        aim - Aim queue
        root_name - Name to add

        Return:
        None
        """
        self.shared_dict['typ'][aim]['queue_lock'].acquire()
        self.shared_dict['typ'][aim]['queue_list_lock'].acquire()
        is_present = False
        try:
            files = (
                self.shared_dict['typ'][aim]['save_file'],
                self.shared_dict['typ'][aim]['list_file'],
                self.shared_dict['typ'][aim]['done_file'],
                )
            for file_name in files:
                try:
                    with open(file_name, 'r') as read:
                        if bool(re.search(r'{0}'.format(re.escape(root_name)), read.read(), re.MULTILINE)):
                            is_present = True
                except FileNotFoundError:
                    pass
        finally:
            self.shared_dict['typ'][aim]['queue_lock'].release()
            self.shared_dict['typ'][aim]['queue_list_lock'].release()
        return is_present

    def add_to_queue(self, aim, root_name, allow_dublicate=False):
        """
        Add item to queue.

        Arguments:
        aim - Aim queue
        root_name - Name to add

        Return:
        None
        """
        if isinstance(root_name, list):
            root_name_list = root_name
        else:
            root_name_list = [root_name]

        self.shared_dict['typ'][aim]['queue_lock'].acquire()
        try:
            for entry in root_name_list:
                self.shared_dict['queue'][aim].put(entry, block=False)
                self.add_to_queue_file(
                    root_name=entry,
                    file_name=self.shared_dict['typ'][aim]['save_file'],
                    allow_dublicate=allow_dublicate,
                    )
        finally:
            self.shared_dict['typ'][aim]['queue_lock'].release()

    def lost_connection(self, typ):
        """
        Handle lost connection errors.

        Arguments:
        typ - Typ of the error

        Return:
        None
        """
        if typ == 'Motion':
            message = ''.join([
                '{0}: An error occured! '.format(self.name),
                'MotionCor2 crashed or the PC is out of space ',
                'or SumMove/MotionCor2 path is not specified correctly! ',
                'MorionCor2 processes stopped! ',
                'It is possible that the PC needs to be rebooted! ',
                'Please check the error file!'
                ])
        else:
            message = ''.join([
                '{0}: An error occured!'.format(self.name),
                'Lost connection or target device out of space!',
                'Please check the error file!'
                ])
        self.shared_dict_typ[typ] = True
        message_notification = '{0} ({1}, {2})'.format(
            message,
            self.name,
            self.shared_dict_typ['error_file']
            )
        message_error = '{0} ({1})'.format(
            message,
            self.name,
            )
        if time.time() - self.time_last_error > 1800:
            self.queue_com['notification'].put(message_notification)
            self.queue_com['error'].put(message_error)
            self.time_last_error = time.time()
        else:
            pass

    def remove_from_queue_file(self, root_name, file_name, lock=True):
        """
        Remove the files from the queue file.

        Arguments:
        root_name - Name of the file to delete

        Return:
        None
        """
        if isinstance(root_name, list):
            root_name = set(root_name)
        else:
            root_name = set([root_name])
        if lock:
            self.queue_lock.acquire()
        try:
            useable_lines = []
            try:
                with open(file_name, 'r') as read:
                    lines = [line.strip() for line in read.readlines() if line.strip()]
            except FileNotFoundError:
                useable_lines = []
            else:
                for line in lines:
                    if line not in root_name:
                        useable_lines.append(line)
                    else:
                        pass

            self.try_write(file_name, 'w', '{0}\n'.format('\n'.join(useable_lines)))
        finally:
            if lock:
                self.queue_lock.release()

    def run_software_meta(self, directory):
        """
        Copy meta files produces by the collection software.

        Arguments:
        directory - Start directory for recursive search.

        Return:
        None
        """
        start_prog = time.time()
        self.queue_com['log'].put(tu.create_log(self.name, 'run_software_meta start'))
        file_list = []
        file_list = self.recursive_search(
            directory=directory,
            file_list=file_list,
            find_meta=True
            )

        if not file_list:
            self.queue_com['error'].put('No Meta data information found (Atlas & Co.)')
            self.queue_com['notification'].put('No Meta data information found (Atlas & Co.)')
        elif not self.stop.value:
            for entry in file_list:
                file_path = entry[len(directory)+1:]
                file_name = os.path.join(self.settings['software_meta_folder'], file_path)
                tu.mkdir_p(os.path.dirname(file_name))
                tu.copy(entry, file_name)
                # Add to queue

            folder_name = os.path.basename(self.settings['software_meta_folder'])
            tar_file = self.settings['software_meta_tar']
            with tarfile.open(tar_file, 'w') as tar:
                tar.add(self.settings['software_meta_folder'], arcname=folder_name)

            for aim in self.content_settings['aim']:
                *compare, aim_name = aim.split(':')
                var = True
                for typ in compare:
                    name = typ.split('!')[-1]
                    if typ.startswith('!'):
                        if self.settings['Copy'][name] == 'False':
                            continue
                        else:
                            var = False
                            break
                    else:
                        if not self.settings['Copy'][name] == 'False':
                            continue
                        else:
                            var = False
                            break
                if var:
                    self.add_to_queue(aim=aim_name, root_name=tar_file)
                else:
                    pass
        self.queue_com['log'].put(tu.create_log(self.name, 'run_software_meta stop', time.time() - start_prog))

    def run_find(self):
        """
        Find files

        Arguments:
        None

        Return:
        None
        """
        start_prog = time.time()
        self.queue_com['log'].put(tu.create_log(self.name, 'run_find start'))
        self.queue_lock.acquire()
        file_list = []
        try:
            file_list = self.recursive_search(
                directory=self.settings['Input']['Input project path for jpg'],
                file_list=file_list,
                find_meta=False
                )
        finally:
            self.queue_lock.release()

        if not self.stop.value:
            data = np.empty(
                len(file_list),
                dtype=[('root', '|U1200'), ('date', '<i8'), ('time', '<i8')]
                )

            for idx, root_name in enumerate(file_list):
                if self.stop.value:
                    break
                hole, grid_number, spot1, spot2, date, collect_time = \
                    tus.extract_time_and_grid_information(
                        root_name=root_name,
                        settings=self.settings,
                        queue_com=self.queue_com,
                        name=self.name
                        )
                del spot1, spot2, hole, grid_number
                data[idx]['root'] = root_name
                data[idx]['date'] = int(date)
                data[idx]['time'] = int(collect_time)

            data = np.sort(data, order=['date', 'time'])
            for root_name in data['root']:

                self.shared_dict_typ['count_lock'].acquire()
                try:
                    self.shared_dict_typ['file_number'] += 1

                    if self.settings['Output']['Rename micrographs'] == 'True':
                        new_name_meta = '{0}/{1}{2:0{3}.0f}{4}'.format(
                            self.settings['meta_folder'],
                            self.settings['Output']['Rename prefix'],
                            self.shared_dict_typ['file_number'],
                            len(self.settings['Output']['Estimated mic number']),
                            self.settings['Output']['Rename suffix']
                            )
                    else:
                        new_name_meta = os.path.join(
                            self.settings['meta_folder'],
                            root_name.split('/')[-1]
                            )

                    if os.path.exists('{0}_krios_sum.mrc'.format(new_name_meta)):
                        self.stop.value = True
                        message = '{0}: Filenumber {1} already exists!\n'.format(
                            self.name,
                            self.shared_dict_typ['file_number']
                            ) + \
                            'Check Startnumber! Last one used: {0}'.format(self.shared_dict_typ['file_number'])
                        self.queue_com['error'].put(message)
                        self.queue_com['notification'].put(message)
                    else:
                        self.try_write(self.shared_dict_typ['number_file'], 'w', str(self.shared_dict_typ['file_number']))
                finally:
                    self.shared_dict_typ['count_lock'].release()

                if self.stop.value:
                    break
                for aim in self.content_settings['aim']:
                    if self.stop.value:
                        break
                    *compare, aim_name = aim.split(':')
                    var = True
                    for typ in compare:
                        name = typ.split('!')[-1]
                        if typ.startswith('!'):
                            if self.settings['Copy'][name] == 'False':
                                continue
                            else:
                                var = False
                                break
                        else:
                            if not self.settings['Copy'][name] == 'False':
                                continue
                            else:
                                var = False
                                break
                    if self.stop.value:
                        break
                    elif var:
                        self.add_to_queue(
                            aim=aim_name,
                            root_name='{0}|||{1}|||{2}'.format(
                                self.shared_dict_typ['file_number'],
                                root_name,
                                self.settings['current_set']
                                )
                            )
                    else:
                        pass
        self.queue_com['log'].put(tu.create_log(self.name, 'run_find stop', time.time() - start_prog))

    def recursive_search(self, directory, file_list, find_meta):
        """
        Find files in a recursive search.

        directory - Directory to search files.
        file_list - List of files that have been found.
        find_meta - Find meta data flag.

        Returns:
        List of files found
        """
        if not os.path.exists(directory):
            raise FileNotFoundError('Find directory does not exist')
        else:
            pass

        files_in_dir = sorted(glob.glob('{0}/*'.format(directory)))

        for entry_dir in files_in_dir:
            if self.stop.value:
                break
            elif os.path.isdir(entry_dir):
                file_list = self.recursive_search(
                    directory=entry_dir,
                    file_list=file_list,
                    find_meta=find_meta
                    )
            elif self.settings["Input"]["Software"] == "Just Stack":
                if not entry_dir.endswith(self.settings['Input']['Input frames extension']):
                    continue
                root_name = os.path.splitext(entry_dir)[0]
                frames_root = root_name
                compare_name = frames_root
                frames = tus.find_frames(
                    frames_root=frames_root,
                    compare_name=compare_name,
                    settings=self.settings,
                    queue_com=self.queue_com,
                    name=self.name,
                    write_error=self.write_error
                    )

                if frames is None:
                    self.shared_dict_typ['bad_lock'].acquire()
                    try:
                        if root_name not in self.shared_dict['bad'][self.typ]:
                            self.shared_dict['bad'][self.typ].append(root_name)
                        else:
                            pass
                    finally:
                        self.shared_dict_typ['bad_lock'].release()
                    continue
                elif not frames:
                    continue
                elif self.already_in_translation_file(os.path.basename(root_name)):
                    self.shared_dict_typ['bad_lock'].acquire()
                    try:
                        if root_name not in self.shared_dict['bad'][self.typ]:
                            self.shared_dict['bad'][self.typ].append(root_name)
                        else:
                            pass
                    finally:
                        self.shared_dict_typ['bad_lock'].release()
                    continue
                elif self.already_in_queue_file('Import', os.path.basename(root_name)):
                    self.shared_dict_typ['bad_lock'].acquire()
                    try:
                        if root_name not in self.shared_dict['bad'][self.typ]:
                            self.shared_dict['bad'][self.typ].append(root_name)
                        else:
                            pass
                    finally:
                        self.shared_dict_typ['bad_lock'].release()
                    continue
                else:
                    pass

                self.shared_dict['typ'][self.content_settings['group']]['share_lock'].acquire()
                try:
                    if root_name in self.shared_dict['share'][self.content_settings['group']]:
                        continue
                    else:
                        self.time_last = time.time()
                        self.notification_send = False
                        file_list.append(root_name)
                        self.shared_dict['share'][self.content_settings['group']].append(
                            root_name
                            )
                finally:
                    self.shared_dict['typ'][self.content_settings['group']]['share_lock'].release()
            elif find_meta:
                if os.path.isfile(entry_dir) and 'Data' not in entry_dir and 'SurveyImages' not in entry_dir:
                    file_list.append(entry_dir)
                else:
                    continue
            elif os.path.isfile(entry_dir) and \
                    'Data' in entry_dir and \
                    (entry_dir.endswith('.jpg') or entry_dir.endswith('.gtg')):
                root_name = entry_dir[:-len('.jpg')]
                self.shared_dict_typ['bad_lock'].acquire()
                try:
                    if root_name in self.shared_dict['bad'][self.typ]:
                        continue
                    else:
                        pass
                finally:
                    self.shared_dict_typ['bad_lock'].release()

                if entry_dir.endswith('.jpg'):
                    frames_root = root_name.replace(
                        self.settings['Input']['Input project path for jpg'],
                        self.settings['Input']['Input project path for frames'],
                        )
                    compare_name = frames_root[:-len('_19911213_2019')]
                elif entry_dir.endswith('.gtg'):
                    frames_root = root_name
                    compare_name = frames_root
                else:
                    assert False

                frames = tus.find_frames(
                    frames_root=frames_root,
                    compare_name=compare_name,
                    settings=self.settings,
                    queue_com=self.queue_com,
                    name=self.name,
                    write_error=self.write_error
                    )
                if frames is None:
                    self.shared_dict_typ['bad_lock'].acquire()
                    try:
                        if root_name not in self.shared_dict['bad'][self.typ]:
                            self.shared_dict['bad'][self.typ].append(root_name)
                        else:
                            pass
                    finally:
                        self.shared_dict_typ['bad_lock'].release()
                    continue
                elif not frames:
                    continue
                elif self.already_in_translation_file(os.path.basename(root_name)):
                    self.shared_dict_typ['bad_lock'].acquire()
                    try:
                        if root_name not in self.shared_dict['bad'][self.typ]:
                            self.shared_dict['bad'][self.typ].append(root_name)
                        else:
                            pass
                    finally:
                        self.shared_dict_typ['bad_lock'].release()
                    continue
                elif self.already_in_queue_file('Import', os.path.basename(root_name)):
                    self.shared_dict_typ['bad_lock'].acquire()
                    try:
                        if root_name not in self.shared_dict['bad'][self.typ]:
                            self.shared_dict['bad'][self.typ].append(root_name)
                        else:
                            pass
                    finally:
                        self.shared_dict_typ['bad_lock'].release()
                    continue
                else:
                    pass

                self.shared_dict['typ'][self.content_settings['group']]['share_lock'].acquire()
                try:
                    if root_name in self.shared_dict['share'][self.content_settings['group']]:
                        continue
                    else:
                        self.time_last = time.time()
                        self.notification_send = False
                        file_list.append(root_name)
                        self.shared_dict['share'][self.content_settings['group']].append(
                            root_name
                            )
                finally:
                    self.shared_dict['typ'][self.content_settings['group']]['share_lock'].release()
            else:
                continue

        return file_list

    def run_import(self, root_name):
        """
        Import found files to em-transfer.

        root_name - Root name of file to copy.

        Returns:
        None
        """
        root_name_input = root_name
        start_prog = time.time()
        self.queue_com['log'].put(tu.create_log(self.name, 'run_import', root_name_input, 'start process'))
        root_name_raw = root_name
        number, root_name, set_name = root_name_raw.split('|||')
        number = int(number)
        frames_root = root_name.replace(
            self.settings['Input']['Input project path for jpg'],
            self.settings['Input']['Input project path for frames'],
            )
        frames, compare_name_frames, compare_name_meta = tus.find_related_frames_to_jpg(
            frames_root=frames_root,
            root_name=root_name,
            settings=self.settings,
            queue_com=self.queue_com,
            name=self.name
            )

        overall_file_size = 0
        for frame in frames:
            overall_file_size += os.path.getsize(frame)

        if frames:
            check_name = root_name.split('/')[-1]
            if self.already_in_translation_file(root_name=check_name):
                message = \
                    '{0}: In queue, but already copied! Skip!'.format(self.name)
                self.write_error(msg=message, root_name=root_name)
                self.queue_com['log'].put(tu.create_log(self.name, 'run_import', root_name_input, 'stop early 1'))
                return None
            else:
                pass
        else:
            message = '{0}: No frames found! If this appears very often, please restart TranSPHIRE.'.format(self.name)
            self.queue_com['notification'].put(message)
            self.write_error(msg=message, root_name=root_name)
            self.queue_com['log'].put(tu.create_log(self.name, 'run_import', root_name_input, 'stop early 2'))
            return None

        if overall_file_size > \
                shutil.disk_usage(self.settings['project_folder']).free:
            self.stop.value = True
            message = '{0}: Not enough space in project folder'.format(
                self.name
                )
            self.queue_com['notification'].put(message)
            raise IOError(message)
        else:
            pass

        self.shared_dict_typ['count_lock'].acquire()
        try:
            if self.settings['Output']['Rename micrographs'] == 'True':
                new_name_stack = '{0}/{1}{2:0{3}.0f}{4}'.format(
                    self.settings['stack_folder'],
                    self.settings['Output']['Rename prefix'],
                    number,
                    len(self.settings['Output']['Estimated mic number']),
                    self.settings['Output']['Rename suffix']
                    )
                new_name_meta = '{0}/{1}{2:0{3}.0f}{4}'.format(
                    self.settings['meta_folder'],
                    self.settings['Output']['Rename prefix'],
                    number,
                    len(self.settings['Output']['Estimated mic number']),
                    self.settings['Output']['Rename suffix']
                    )
            else:
                new_name_stack = os.path.join(
                    self.settings['stack_folder'],
                    root_name.split('/')[-1]
                    )
                new_name_meta = os.path.join(
                    self.settings['meta_folder'],
                    root_name.split('/')[-1]
                    )
        finally:
            self.shared_dict_typ['count_lock'].release()

        if os.path.exists('{0}_krios_sum.mrc'.format(new_name_meta)):
            self.stop.value = True
            if os.path.exists(self.shared_dict_typ['done_file']):
                self.queue_lock.acquire()
                try:
                    with open(self.shared_dict_typ['done_file'], 'r') as read:
                        self.shared_dict_typ['file_number'] = len(read.readlines())
                finally:
                    self.queue_lock.release()
            else:
                self.shared_dict_typ['file_number'] = int(
                    self.settings['Output']['Start number']
                    )
            message = '{0}: Filenumber {1} already exists!\n'.format(
                self.name,
                number
                ) + \
                'Check Startnumber! Last one used: {0}'.format(self.shared_dict_typ['file_number'])
            self.queue_com['notification'].put(message)
            raise FileNotFoundError(message)
        else:
            pass

        new_stack = '{0}.{1}'.format(
            new_name_stack,
            self.settings['Output extension']
            )

        command_raw = tus.get_copy_command_for_frames(
            settings=self.settings,
            queue_com=self.queue_com,
            name=self.name
            )

        command = "{0} '{1}' {2}".format(
            command_raw,
            "' '".join(frames),
            new_stack
            )

        log_file, err_file = self.run_command(
            root_name_input=root_name_input,
            command=command,
            log_prefix=new_name_stack,
            block_gpu=False,
            gpu_list=[],
            shell=True
            )

        tus.check_outputs(
            zero_list=[err_file],
            non_zero_list=[log_file, new_stack],
            exists_list=[],
            folder=self.settings['stack_folder'],
            command=command
            )

        meta_files, frame_files = tus.find_all_files(
            root_name=root_name,
            compare_name_frames=compare_name_frames,
            compare_name_meta=compare_name_meta,
            settings=self.settings,
            queue_com=self.queue_com,
            name=self.name
            )

        all_files = meta_files.union(frame_files)

        xml_file = None
        log_files = []
        for file_entry in all_files:
            extension = file_entry.split('.')[-1]
            is_xml = False
            if file_entry in frames:
                continue
            elif extension == 'mrc' and 'gain' in file_entry:
                name = '{0}_gain'.format(new_name_meta)
            elif extension == 'mrc':
                name = '{0}_krios_sum'.format(new_name_meta)
            elif extension == 'dm4' and 'gain' in file_entry:
                name = '{0}_gain'.format(new_name_meta)
            elif extension in ('xml', 'gtg') and file_entry in meta_files:
                is_xml = True
                name = new_name_meta
            elif extension == 'xml':
                name = '{0}_frames'.format(new_name_meta)
            else:
                name = new_name_meta

            new_file = '{0}.{1}'.format(name, extension)

            if is_xml:
                xml_file = new_file
            else:
                pass

            tu.copy(file_entry, new_file)
            log_files.append(new_file)
            self.try_write(log_file, 'a', '\ncp {0} {1}\n'.format(file_entry, new_file))

        tus.check_outputs(
            zero_list=[],
            non_zero_list=[],
            exists_list=log_files,
            folder=self.settings['meta_folder'],
            command='copy'
            )

        log_files.extend([log_file, err_file, new_stack])

        self.append_to_translate(
            root_name=root_name,
            new_name=new_name_meta,
            xml_file=xml_file
            )

        for aim in self.content_settings['aim']:
            *compare, aim_name = aim.split(':')
            var = True
            for typ in compare:
                name = typ.split('!')[-1]
                if typ.startswith('!'):
                    if self.settings['Copy'][name] == 'False':
                        continue
                    else:
                        var = False
                        break
                else:
                    if not self.settings['Copy'][name] == 'False':
                        continue
                    else:
                        var = False
                        break
            if var:
                if 'Compress' in compare or \
                        'Motion' in compare or \
                        'CTF' in compare:
                    string_list = []
                    if 'CTF' in compare:
                        string_list.append('CTF_frames')
                    string_list.extend([new_stack, set_name])

                    self.add_to_queue(aim=aim_name, root_name='|||'.join(string_list))
                else:
                    self.add_to_queue(
                        aim=aim_name,
                        root_name=[
                            entry
                            for entry in log_files
                            if ('Frames to' in compare[0] and '{}/'.format(self.settings['stack_folder']) in entry) or
                                ('Meta to' in compare[0] and '{}/'.format(self.settings['meta_folder']) in entry)
                            ]
                        )
            else:
                pass

        if self.settings['Copy']['Delete data after import?'] == 'True':
            for file_entry in all_files:
                try:
                    os.remove(file_entry)
                except IOError:
                    self.write_error(msg=tb.format_exc(), root_name=file_entry)
                    raise BlockingIOError('Cannot remove Frames!')
        else:
            pass

        self.wait(1)
        self.shared_dict['typ'][self.content_settings['group']]['share_lock'].acquire()
        try:
            self.shared_dict['share'][self.content_settings['group']].remove(root_name)
        except ValueError:
            pass
        finally:
            self.shared_dict['typ'][self.content_settings['group']]['share_lock'].release()

        self.queue_com['log'].put(tu.create_log(self.name, 'run_import', root_name_input, 'stop process', time.time() - start_prog))


    def already_in_translation_file(self, root_name):
        """
        Check, if the root_name already exists in the translation file.

        root_name - root_name

        Returns:
        True, if root_name in translation file.
        """
        check_list = []
        try:
            for name in ('translation_file', 'translation_file_bad'):
                self.shared_dict['translate_lock'].acquire()
                try:
                    content_translation_file = np.genfromtxt(
                        self.settings[name],
                        usecols=0,
                        dtype=str
                        )
                finally:
                    self.shared_dict['translate_lock'].release()
                check_list.append(bool(root_name in content_translation_file))
        except OSError:
            return False
        else:
            return bool([entry for entry in check_list if entry])

    def remove_from_translate(self, root_name):
        """
        Remove line from the translation file.

        root_name - Root name of the file to remove

        Returns:
        None
        """
        file_name = self.settings['translation_file']
        file_name_bad = self.settings['translation_file_bad']
        self.shared_dict['translate_lock'].acquire()
        try:
            with open(file_name, 'r') as read:
                good_lines = []
                bad_lines = []
                for line in read.readlines():
                    if root_name in line:
                        bad_lines.append(line)
                    else:
                        good_lines.append(line)

            self.try_write(file_name, 'w', ''.join(good_lines))

            self.try_write(file_name_bad, 'a', ''.join(bad_lines))

        finally:
            self.shared_dict['translate_lock'].release()

        self.file_to_distribute(file_name=file_name)
        self.file_to_distribute(file_name=file_name_bad)

    def file_to_distribute(self, file_name):
        for copy_name in ('work', 'hdd', 'backup'):
            copy_type = 'Copy_to_{0}'.format(copy_name.lower())
            if not self.settings['Copy']['Copy to {0}'.format(copy_name)] == 'False':
                self.add_to_queue(aim=copy_type, root_name=file_name)
            else:
                pass

    @staticmethod
    def get_gtg_info(xml_file, entries, first_entry):
        try:
            with open(xml_file, "rb") as read: 
                reader = hidm.DigitalMicrographReader(read) 
                reader.parse_file()
        except IOError as e:
            print(e)
        else:
            gtg_values = {
                '_pipeAlpha': ['Microscope Info', 'Stage Position', 'Stage Alpha'],
                '_pipeCoordX': ['Microscope Info', 'Stage Position', 'Stage X'],
                '_pipeCoordY': ['Microscope Info', 'Stage Position', 'Stage Y'],
                '_pipeCoordZ': ['Microscope Info', 'Stage Position', 'Stage Z'],

                '_pipeDefocusMicroscope': ['Latitude', 'Distance To Focus Position'],
                '_pipeAppliedDefocusMicroscope': ['Latitude', 'Intended Defocus'],
                #'_pipeDose': ['Latitude', 'Pixel Size'],
                '_pipePixelSize': ['Latitude', 'Pixel Size'],
                #'_pipeNrFractions': [r'.*<b:NumberOffractions>(.*?)</b:NumberOffractions>.*', r'<b:StartFrameNumber>'],

                '_pipeExposureTime': ['Acquisition', 'Parameters', 'Detector', 'exposure (s)'],
                'frame exposure': ['Acquisition', 'Parameters', 'High Level', 'Frame Exposure'],
                '_pipeHeight': ['Latitude', 'Image Size Y'],
                '_pipeWidth': ['Latitude', 'Image Size X'],
                }
            for key, value in gtg_values.items():
                temp = reader.tags_dict
                for idx, entry in enumerate(value):
                    if isinstance(temp[entry], dict):
                        temp = temp[entry]
                    else:
                        if key == 'frame exposure':
                            first_key = '_pipeNrFractions'
                            val = int(entries[-1] // temp[entry] + 0.5)
                        else:
                            first_key = key
                            val = temp[entry]
                        entries.append(val)
                        if first_entry:
                            first_entry.append('{0} #{1}'.format(first_key, idx+8))

    @staticmethod
    def get_xml_info(xml_file, entries, first_entry):
        try:
            with open(xml_file, 'r') as read:
                lines = read.read()
        except IOError:
            pass
        else:
            xml_values = {
                '_pipeCoordX': [r'.*<X>(.*?)</X>.*'], # https://regex101.com/r/tnWRzx/1/
                '_pipeCoordY': [r'.*<Y>(.*?)</Y>.*'], # https://regex101.com/r/tnWRzx/2/
                '_pipeCoordZ': [r'.*<Z>(.*?)</Z>.*'], # https://regex101.com/r/tnWRzx/3
                '_pipeVoltage': [r'.*<AccelerationVoltage>(.*?)</AccelerationVoltage>.*'], # https://regex101.com/r/tnWRzx/4
                '_pipeDefocusMicroscope': [r'.*<Defocus>(.*?)</Defocus>.*'], # https://regex101.com/r/tnWRzx/4/
                '_pipeAppliedDefocusMicroscope': [r'.*<a:Key>AppliedDefocus</a:Key><a:Value .*?>(.*?)</a:Value>.*'], # https://regex101.com/r/tnWRzx/5
                '_pipeDose': [r'.*<a:Key>Dose</a:Key><a:Value .*?>(.*?)</a:Value>.*'], # https://regex101.com/r/tnWRzx/6
                '_pipePhasePlate': [r'.*<a:Key>PhasePlateUsed</a:Key><a:Value .*?>(.*?)</a:Value>.*'], # https://regex101.com/r/tnWRzx/7/
                '_pipeSuperResolutionFactor': [r'.*<a:Key>SuperResolutionFactor</a:Key><a:Value .*?>(.*?)</a:Value>.*'], # https://regex101.com/r/tnWRzx/8
                '_pipePixelSize': [r'.*<pixelSize><x><numericValue>(.*?)</numericValue>.*'], # https://regex101.com/r/tnWRzx/9
                '_pipeNrFractions': [r'.*<b:NumberOffractions>(.*?)</b:NumberOffractions>.*', r'<b:StartFrameNumber>'], # https://regex101.com/r/tnWRzx/10
                '_pipeExposureTime': [r'.*<camera>.*?<ExposureTime>(.*?)</ExposureTime>.*'], # https://regex101.com/r/tnWRzx/11
                '_pipeHeight': [r'.*<ReadoutArea.*?<a:height>(.*?)</a:height>.*'], # https://regex101.com/r/tnWRzx/12
                '_pipeWidth': [r'.*<ReadoutArea.*?<a:width>(.*?)</a:width>.*'], # https://regex101.com/r/tnWRzx/13
                '_pipeBeamShiftX': [r'.*<BeamShift .*?><a:_x>(.*?)</a:_x>.*?</BeamShift>.*'], # https://regex101.com/r/tnWRzx/15
                '_pipeBeamShiftY': [r'.*<BeamShift .*?>.*?<a:_y>(.*?)</a:_y></BeamShift>.*'], # https://regex101.com/r/tnWRzx/14
                '_pipeBeamTiltX': [r'.*<BeamTilt .*?><a:_x>(.*?)</a:_x>.*?</BeamTilt>.*'], # https://regex101.com/r/tnWRzx/16
                '_pipeBeamTiltY': [r'.*<BeamTilt .*?>.*?<a:_y>(.*?)</a:_y></BeamTilt>.*'], # https://regex101.com/r/tnWRzx/17
                }
            idx = 0
            for xml_key, values in xml_values.items():
                for xml_value in values:
                    error = False
                    try:
                        extracted_value = re.match(xml_value, lines).group(1)
                    except AttributeError:
                        try:
                            extracted_value = len(re.findall(xml_value, lines))
                        except Exception:
                            extracted_value = None
                            error = True
                        else:
                            if extracted_value:
                                break
                            else:
                                extracted_value = None
                                error = True
                    else:
                        break

                entries.append(extracted_value)
                if first_entry:
                    first_entry.append('{0} #{1}'.format(xml_key, idx+8))
                else:
                    pass
                idx += 1

                if error:
                    print('Attribute {0} not present in the XML file, please contact the TranSPHIRE authors'.format(xml_key))
                else:
                    pass

    def append_to_translate(self, root_name, new_name, xml_file):
        """
        Write to the translation file.

        root_name - Root name of the file
        new_name - New name of the file
        xml_file - XML or GTG file that contains meta data information

        Returns:
        None
        """
        file_name = self.settings['translation_file']
        file_name_bad = self.settings['translation_file_bad']

        if os.path.exists(file_name):
            first_entry = []
        else:
            first_entry = [
                '',
                'data_transphire',
                '',
                'loop_',
                '_pipeRootName #1',
                '_pipeNewName #2',
                '_pipeHoleNumber #3',
                '_pipeSpotNumber #4',
                '_pipeDate #5',
                '_pipeTime #6',
                '_pipeGridNumber #7',
                ]

        try:
            hole, grid_number, spot1, spot2, date, time = \
                tus.extract_time_and_grid_information(
                    root_name=root_name,
                    settings=self.settings,
                    queue_com=self.queue_com,
                    name=self.name
                    )
            new_file = os.path.basename(new_name)

            key = '{0}{1}'.format(spot1, spot2)
            if key not in self.shared_dict_typ['spot_dict']:
                self.shared_dict_typ['spot'] += 1
                self.shared_dict_typ['spot_dict'][key] = \
                    self.shared_dict_typ['spot']
                self.try_write(self.settings['spot_file'], 'a', '{0}\t{1}\n'.format(
                        key,
                        self.shared_dict_typ['spot']
                        ))

            entries = [
                os.path.basename(root_name),
                new_file,
                hole,
                self.shared_dict_typ['spot_dict'][key],
                date,
                time,
                grid_number
                ]

            if xml_file is None:
                pass
            elif xml_file.endswith('xml'):
                self.get_xml_info(xml_file, entries, first_entry)
            elif xml_file.endswith('gtg'):
                self.get_gtg_info(xml_file, entries, first_entry)
            else:
                assert False, ('File not known:', xml_file)


        except ValueError:
            if first_entry:
                first_entry = [
                    '',
                    'data_transphire',
                    '',
                    'loop_',
                    '_pipeRootName #1',
                    '_pipeRootDir #2',
                    '_pipeNewName #3'
                    ]
            else:
                pass
            entries = [
                os.path.basename(root_name),
                os.path.dirname(root_name),
                new_name
                ]

        template = '{0}\n'
        if first_entry:
            content = [template.format('\n'.join(first_entry))]
        else:
            content = []
        content.append(template.format(
                '  '.join(
                    ['{0}'.format(entry) for entry in entries]
                    )
                ))
        self.try_write(file_name, 'a', ''.join(content))

        self.shared_dict['translate_lock'].acquire()
        try:
            if first_entry:
                self.try_write(file_name_bad, 'a', template.format('\n'.join(first_entry)))
        finally:
            self.shared_dict['translate_lock'].release()

        self.file_to_distribute(file_name=file_name)
        self.file_to_distribute(file_name=file_name_bad)

    def run_motion(self, root_name):
        """
        Do the motion correction.

        root_name - Root name of the micrograph.

        Returns:
        None
        """
        root_name_input = root_name
        start_prog = time.time()
        self.queue_com['log'].put(tu.create_log(self.name, 'run_motion', root_name_input, 'start process'))
        root_name, set_name = root_name.split('|||')
        if not os.path.isfile(root_name):
            compress_name = self.settings['Copy']['Compress']
            try:
                compress_extension = self.settings[compress_name]['--command_compress_extension']
            except KeyError:
                raise IOError('Compressed file and Stack file does not exist!')

            compressed_file_name = os.path.join(
                self.settings['compress_folder_feedback_0'],
                '{0}.{1}'.format(
                    tu.get_name(root_name[len(self.settings['stack_folder'])+1:]),
                    compress_extension
                    )
                )
            file_input = compressed_file_name
        else:
            file_input = root_name
        root_name, _ = os.path.splitext(file_input)
        file_dw_post_move = None
        file_stack = None
        queue_dict = {}
        do_subsum = bool(len(self.settings['motion_frames']) > 1)
        for motion_idx, key in enumerate(self.settings['motion_frames']):
            # The current settings that we work with
            motion_frames = copy.deepcopy(self.settings['motion_frames'][key])
            queue_dict[motion_idx] = {'log': [], 'sum': [], 'sum_dw': [], 'sum_dws': []}

            # Abort if frames out of range
            if int(self.settings['Input']['Number of frames']) == -1:
                pass
            elif motion_frames['first'] > \
                    int(self.settings['Input']['Number of frames']) or \
                    motion_frames['last'] > \
                    int(self.settings['Input']['Number of frames']):
                print('First:{0} Last:{1} not valid! Skip!\n'.format(
                    motion_frames['first'],
                    motion_frames['last']
                    ))
                continue
            else:
                pass

            # Create an unblur shift file
            tu.mkdir_p(self.settings['motion_folder_feedback_0'])
            file_shift = os.path.join(
                self.settings['motion_folder_feedback_0'],
                '.{0}_shift'.format(self.name)
                )

            # Rename the last frame
            if motion_frames['last'] == -1:
                do_dw = tum.get_motion_default(
                    settings=self.settings,
                    motion_frames=motion_frames,
                    queue_com=self.queue_com,
                    name=self.name
                    )
                zeros_list = [
                    '0.0' for i in range(
                        motion_frames['last'] - motion_frames['first'] - 1
                        )
                    ]
                self.try_write(file_shift, 'w', '{0}\n{0}\n'.format('\t'.join(zeros_list)))
            else:
                do_dw = False

            # Folder name for the current settings
            if do_dw:
                suffix = 'with_DW'
            else:
                suffix = 'without_DW'
            output_folder_name = '{0}_{1}_{2}'.format(
                motion_frames['first'],
                motion_frames['last'],
                suffix
                )
            output_logfile = '{0}_log'.format(output_folder_name)

            # Create the folders
            # Variables
            output_transfer_root = os.path.join(
                self.settings['motion_folder_feedback_0'],
                output_folder_name
                )
            output_transfer_log = os.path.join(
                self.settings['motion_folder_feedback_0'],
                output_logfile
                )
            # Scratch
            output_transfer_scratch_root = os.path.join(
                self.settings['scratch_motion_folder_feedback_0'],
                output_folder_name
                )
            output_transfer_log_scratch = os.path.join(
                self.settings['scratch_motion_folder_feedback_0'],
                output_logfile
                )

            output_dw = os.path.join(output_transfer_root, 'DW')
            output_dws = os.path.join(output_transfer_root, 'DWS')
            output_transfer = os.path.join(output_transfer_root, 'Non_DW')
            output_transfer_scratch = os.path.join(
                output_transfer_scratch_root,
                'Non_DW'
                )

            # Create folders if they do not exist
            tu.mkdir_p(output_transfer_root)
            tu.mkdir_p(output_transfer)
            tu.mkdir_p(output_transfer_log)
            tu.mkdir_p(output_transfer_scratch)
            tu.mkdir_p(output_transfer_log_scratch)

            # Remove the path from the name
            file_name = os.path.basename(root_name)

            # Scratch output
            file_output_scratch = os.path.join(
                output_transfer_scratch,
                '{0}.mrc'.format(file_name)
                )
            file_log_scratch = os.path.join(
                output_transfer_log_scratch,
                '{0}.mrc'.format(file_name)
                )

            # Project output
            file_output = os.path.join(
                output_transfer,
                '{0}.mrc'.format(file_name)
                )
            file_log = os.path.join(
                output_transfer_log,
                '{0}.mrc'.format(file_name)
                )
            file_frc = '{0}_frc.log'.format(
                file_log
                )

            non_zero_list_scratch = []
            zero_list_scratch = []
            non_zero_list = []
            zero_list = []

            # Create the commands
            if motion_idx == 0:
                # DW folder
                tu.mkdir_p(output_dw)
                tu.mkdir_p(output_dws)

                # Files
                file_stack = os.path.join(
                    output_transfer_scratch,
                    '{0}_Stk.mrc'.format(file_name)
                    )
                file_dw_post_move = os.path.join(
                    output_dw,
                    '{0}.mrc'.format(file_name)
                    )
                file_dws_post_move = os.path.join(
                    output_dws,
                    '{0}.mrc'.format(file_name)
                    )
                file_dws_pre_move = tum.get_dws_file_name(
                    output_transfer_scratch=output_transfer_scratch,
                    file_name=file_name,
                    settings=self.settings,
                    queue_com=self.queue_com,
                    name=self.name
                    )
                file_dw_pre_move = tum.get_dw_file_name(
                    output_transfer_scratch=output_transfer_scratch,
                    file_name=file_name,
                    settings=self.settings,
                    queue_com=self.queue_com,
                    name=self.name
                    )
                command, block_gpu, gpu_list, file_to_delete, shell = tum.get_motion_command(
                    file_input=file_input,
                    file_output_scratch=file_output_scratch,
                    file_log_scratch=file_log_scratch,
                    queue_com=self.queue_com,
                    name=self.name,
                    set_name=set_name,
                    settings=self.settings,
                    do_subsum=do_subsum
                    )

                file_stdout_scratch, file_stderr_scratch = self.run_command(
                    root_name_input=root_name_input,
                    command=command,
                    log_prefix=file_log_scratch,
                    block_gpu=block_gpu,
                    gpu_list=gpu_list,
                    shell=shell,
                    file_to_delete=file_to_delete,
                    )
                file_stdout = file_stdout_scratch.replace(
                    output_transfer_log_scratch,
                    output_transfer_log
                    )
                file_stderr = file_stderr_scratch.replace(
                    output_transfer_log_scratch,
                    output_transfer_log
                    )
                file_stdout_combine = file_stdout

                # Move DW file
                if do_dw:
                    non_zero_list_scratch.append(file_dw_pre_move)
                    non_zero_list.append(file_dw_post_move)
                    if os.path.exists(file_dws_pre_move):
                        non_zero_list_scratch.append(file_dws_pre_move)
                        non_zero_list.append(file_dws_post_move)
                else:
                    pass

            else:
                assert os.path.exists(file_stack)
                command, block_gpu, gpu_list = tum.create_sum_movie_command(
                    motion_frames=motion_frames,
                    file_input=file_stack,
                    file_output=file_output_scratch,
                    file_shift=file_shift,
                    file_frc=file_frc,
                    settings=self.settings,
                    queue_com=self.queue_com,
                    name=self.name
                    )

                file_stdout_scratch, file_stderr_scratch = self.run_command(
                    root_name_input=root_name_input,
                    command=command,
                    log_prefix=file_log_scratch,
                    block_gpu=block_gpu,
                    gpu_list=gpu_list,
                    shell=True
                    )
                file_stdout = file_stdout_scratch.replace(
                    output_transfer_log_scratch,
                    output_transfer_log
                    )
                file_stderr = file_stderr_scratch.replace(
                    output_transfer_log_scratch,
                    output_transfer_log
                    )

                non_zero_list.append(file_frc)
                for entry_temp in glob.glob('.SumMovie*'):
                    try:
                        os.remove(entry_temp)
                    except FileNotFoundError:
                        pass
                    except IOError:
                        pass

            non_zero_list_scratch.append(file_output_scratch)
            non_zero_list_scratch.append(file_stdout_scratch)
            zero_list_scratch.append(file_stderr_scratch)
            non_zero_list.append(file_output)
            non_zero_list.append(file_stdout)
            zero_list.append(file_stderr)

            # Sanity check
            log_files_scratch = glob.glob('{0}0*'.format(file_log_scratch))
            non_zero_list_scratch.extend(log_files_scratch)
            tus.check_outputs(
                zero_list=zero_list_scratch,
                non_zero_list=non_zero_list_scratch,
                exists_list=[],
                folder=output_transfer_log_scratch,
                command=command
                )

            if do_dw:
                if os.path.exists(file_dws_pre_move):
                    tu.copy(file_dws_pre_move, file_dws_post_move)
                    tus.check_outputs(
                        zero_list=[],
                        non_zero_list=[file_dws_post_move],
                        exists_list=[],
                        folder=self.settings['motion_folder_feedback_0'],
                        command='copy'
                        )
                tu.copy(file_dw_pre_move, file_dw_post_move)
                tus.check_outputs(
                    zero_list=[],
                    non_zero_list=[file_dw_post_move],
                    exists_list=[],
                    folder=self.settings['motion_folder_feedback_0'],
                    command='copy'
                    )

            if os.path.realpath(self.settings['scratch_motion_folder_feedback_0']) != \
                    os.path.realpath(self.settings['motion_folder_feedback_0']):
                tu.copy(file_output_scratch, file_output)
                tu.copy(file_stdout_scratch, file_stdout)
                tu.copy(file_stderr_scratch, file_stderr)
                for file_name_log in log_files_scratch:
                    name = os.path.basename(file_name_log)
                    new_name = os.path.join(output_transfer_log, name)
                    tu.copy(file_name_log, new_name)

                log_files = glob.glob('{0}0*'.format(file_log))
                non_zero_list.extend(log_files)
                tus.check_outputs(
                    zero_list=zero_list,
                    non_zero_list=non_zero_list,
                    exists_list=[],
                    folder=self.settings['motion_folder_feedback_0'],
                    command='copy'
                    )

                copied_files = zero_list_scratch + non_zero_list_scratch
                for file_entry in copied_files:
                    try:
                        os.remove(file_entry)
                    except IOError:
                        self.write_error(msg=tb.format_exc(), root_name=file_entry)
                        raise
            elif do_dw:
                try:
                    os.remove(file_dws_pre_move)
                except IOError:
                    pass
                try:
                    os.remove(file_dw_pre_move)
                except IOError:
                    pass
            else:
                pass

            queue_dict[motion_idx]['sum'].append(file_output)
            for file_name_log in glob.glob('{0}*'.format(file_log)):
                queue_dict[motion_idx]['log'].append(file_name_log)
            if do_dw:
                queue_dict[motion_idx]['sum_dw'].append(file_dw_post_move)
                if os.path.exists(file_dws_post_move):
                    queue_dict[motion_idx]['sum_dws'].append(file_dws_post_move)
            else:
                pass

        try:
            file_for_jpg = queue_dict[0]['sum_dw'][0]
        except IndexError:
            file_for_jpg = queue_dict[0]['sum'][0]

        import_name = tu.get_name(file_for_jpg)
        data, data_original = tu.get_function_dict()[self.prog_name]['plot_data'](
            self.prog_name,
            self.prog_name,
            self.settings,
            self.settings['motion_folder_feedback_0'],
            import_name
            )

        mask = np.in1d(
                np.array(np.char.rsplit(data['file_name'], '/', 1).tolist())[:, -1],
                [os.path.basename(queue_dict[0]['sum'][0])]
                )

        tum.create_jpg_file(
            file_for_jpg,
            data_original[mask],
            self.settings,
            )

        warnings, skip_list = tus.check_for_outlier(
            dict_name='Motion',
            data=data,
            file_name=queue_dict[0]['sum'][0],
            settings=self.settings
            )

        if skip_list:
            self.remove_from_translate(os.path.basename(root_name))
        else:
            pass

        for warning in skip_list:
            self.send_out_of_range_error(warning, root_name, 'skip')

        for warning in warnings:
            self.send_out_of_range_error(warning, root_name, 'warning')

        data = data[mask]
        data_original = data_original[mask]

        if data.shape[0] != 0:
            sum_file = queue_dict[0]['sum'][0]
            try:
                dw_file = queue_dict[0]['sum_dw'][0]
            except IndexError:
                dw_file = None

            output_combine = tum.combine_motion_outputs(
                data=data,
                data_original=data_original,
                settings=self.settings,
                queue_com=self.queue_com,
                shared_dict=self.shared_dict,
                name=self.name,
                log_file=file_stdout_combine,
                sum_file=sum_file,
                dw_file=dw_file,
                stack_file=file_input,
                set_name=set_name,
                )
            output_name_mic_combined = output_combine[0]
            output_name_star_combined = output_combine[1]
            output_name_star_relion3_combined = output_combine[2]
            output_name_mic = output_combine[3]
            output_name_star = output_combine[4]
            output_name_star_relion3 = output_combine[5]
            star_files_relion3_meta = output_combine[6]

            combine_list = [
                [self.shared_dict['motion_txt_lock'], output_name_mic, output_name_mic_combined],
                [self.shared_dict['motion_star_lock'], output_name_star, output_name_star_combined],
                [self.shared_dict['motion_star_relion3_lock'], output_name_star_relion3, output_name_star_relion3_combined],
                ]
            self.create_combines(combine_list)

            self.file_to_distribute(file_name=star_files_relion3_meta)
        else:
            pass

        if skip_list:
            pass
        else:
            for motion_idx in queue_dict:
                for aim in self.content_settings['aim']:
                    *compare, aim_name = aim.split(':')
                    var = True
                    for typ in compare:
                        name = typ.split('!')[-1]
                        if typ.startswith('!'):
                            if self.settings['Copy'][name] == 'False':
                                continue
                            else:
                                var = False
                                break
                        else:
                            if not self.settings['Copy'][name] == 'False':
                                continue
                            else:
                                var = False
                                break
                    if var:
                        sum_files = queue_dict[motion_idx]['sum']
                        log_files = queue_dict[motion_idx]['log']
                        sum_dw_files = queue_dict[motion_idx]['sum_dw']
                        sum_dws_files = queue_dict[motion_idx]['sum_dws']
                        if '!Compress' in compare:
                            if motion_idx == 0:
                                self.add_to_queue(aim=aim_name, root_name=file_input)
                            else:
                                pass
                        elif 'Compress' in compare:
                            if motion_idx == 0:
                                self.add_to_queue(aim=aim_name, root_name=file_input)
                            else:
                                pass
                        elif 'Extract' in compare or 'Train2d' in compare:
                            if motion_idx == 0:
                                if sum_dw_files:
                                    dw_file = sum_dw_files[0]
                                else:
                                    dw_file = sum_files[0]
                                self.add_to_queue(
                                    aim=aim_name,
                                    root_name=dw_file
                                    )
                            else:
                                pass
                        elif 'CTF' in compare or 'Picking' in compare:

                            if motion_idx == 0:
                                sum_file = sum_files[0]
                                if sum_dw_files:
                                    dw_file = sum_dw_files[0]
                                else:
                                    dw_file = 'None'

                                string_list = []
                                if 'CTF' in compare:
                                    string_list.append('CTF_sum')
                                string_list.extend([sum_file, dw_file, file_input])
                                self.add_to_queue(
                                    aim=aim_name,
                                    root_name=';;;'.join(string_list)
                                    )
                            else:
                                pass
                        else:
                            self.add_to_queue(aim=aim_name, root_name=sum_files+log_files+sum_dw_files+sum_dws_files)
                    else:
                        pass

        if do_subsum:
            os.remove(file_stack)
        else:
            pass
        self.queue_com['log'].put(tu.create_log(self.name, 'run_motion', root_name_input, 'stop process', time.time() - start_prog))

    def run_ctf(self, root_name):
        """
        Run CTF estimation.

        root_name - name of the file to process.

        Returns:
        None
        """
        root_name_input = root_name
        start_prog = time.time()
        self.queue_com['log'].put(tu.create_log(self.name, 'run_ctf', root_name_input, 'start process'))
        ctf_mode = None
        if '|||' in root_name:
            ctf_mode, root_name_raw, set_name = root_name.split('|||')
            root_name = root_name_raw
        else:
            set_name = None
            root_name_raw = root_name
        # Split is file_sum, file_dw_sum, file_frames
        try:
            ctf_mode, file_sum, file_dw, file_input = root_name.split(';;;')
        except ValueError:
            file_input = root_name
            file_sum = root_name
            file_dw = 'None'

        assert ctf_mode is not None, ctf_mode
        if self.settings['Copy'][ctf_mode] != 'True':
            self.queue_com['log'].put(tu.create_log(self.name, 'run_ctf', root_name_input, 'stop early 1'))
            return None

        try:
            if self.settings[self.settings['Copy']['CTF']]['Use movies'] == 'True':
                if not os.path.isfile(file_input):
                    compress_name = self.settings['Copy']['Compress']
                    try:
                        compress_extension = self.settings[compress_name]['--command_compress_extension']
                    except KeyError:
                        raise IOError('Compressed file and Stack file does not exist!')

                    compressed_file_name = os.path.join(
                        self.settings['compress_folder_feedback_0'],
                        '{0}.{1}'.format(
                            tu.get_name(root_name[len(self.settings['stack_folder'])+1:]),
                            compress_extension
                            )
                        )
                    file_input = compressed_file_name
                    file_sum = file_input
                else:
                    file_input = file_input
                root_name, _ = os.path.splitext(file_input)
            else:
                root_name, _ = os.path.splitext(file_sum)
        except KeyError:
            root_name, _ = os.path.splitext(file_sum)

        # New name
        file_name = os.path.basename(root_name)
        new_name = os.path.join(
            self.settings['ctf_folder_feedback_0'],
            '{0}.mrc'.format(file_name)
            )

        # Create the command
        command, check_files, block_gpu, gpu_list, shell = tuc.get_ctf_command(
            file_sum=file_sum,
            file_input=file_input,
            new_name=new_name,
            settings=self.settings,
            queue_com=self.queue_com,
            set_name=set_name,
            name=self.name
            )

        # Log files
        log_prefix = os.path.join(
            self.settings['ctf_folder_feedback_0'],
            file_name
            )

        log_file, err_file = self.run_command(
            root_name_input=root_name_input,
            command=command,
            log_prefix=log_prefix,
            block_gpu=block_gpu,
            gpu_list=gpu_list,
            shell=shell
            )

        zero_list = [err_file]
        non_zero_list = [log_file]
        non_zero_list.extend(check_files)

        root_path = os.path.join(os.path.dirname(root_name), file_name)
        log_files, copied_log_files = tuc.find_logfiles(
            root_path=root_path,
            file_name=file_name,
            settings=self.settings,
            queue_com=self.queue_com,
            name=self.name
            )

        try:
            log_files.remove(err_file)
            copied_log_files.remove(err_file)
        except ValueError:
            pass

        tus.check_outputs(
            zero_list=zero_list,
            non_zero_list=non_zero_list+log_files,
            exists_list=[],
            folder=self.settings['ctf_folder_feedback_0'],
            command=command
            )

        for old_file, new_file in zip(log_files, copied_log_files):
            if os.path.realpath(old_file) != os.path.realpath(new_file):
                tu.copy(old_file, new_file)
            else:
                pass

        tus.check_outputs(
            zero_list=[],
            non_zero_list=copied_log_files,
            exists_list=[],
            folder=self.settings['ctf_folder_feedback_0'],
            command=command
            )

        for old_file, new_file in zip(log_files, copied_log_files):
            if os.path.realpath(old_file) != os.path.realpath(new_file):
                os.remove(old_file)
            else:
                pass

        copied_log_files.extend(non_zero_list)
        copied_log_files.extend(zero_list)
        copied_log_files = list(set(copied_log_files))

        tuc.create_jpg_file(
            file_sum,
            self.settings,
            self.settings['Copy']['CTF'],
            )

        import_name = tu.get_name(file_sum)
        data, data_orig = tu.get_function_dict()[self.prog_name]['plot_data'](
            self.prog_name,
            self.prog_name,
            self.settings,
            self.settings['ctf_folder_feedback_0'],
            import_name
            )

        try:
            warnings, skip_list = tus.check_for_outlier(
                dict_name='CTF',
                data=data,
                file_name=file_sum,
                settings=self.settings
                )
        except ValueError:
            raise IOError('{0} - Please check, if {0} can be executed outside of TranSPHIRE'.format(self.settings['Copy']['CTF']))

        if skip_list:
            self.remove_from_translate(os.path.basename(root_name))
        else:
            pass

        for warning in skip_list:
            self.send_out_of_range_error(warning, root_name, 'skip')

        for warning in warnings:
            self.send_out_of_range_error(warning, root_name, 'warning')

        mask = np.in1d(
            np.array(
                np.char.rsplit(
                    np.array(
                        np.char.rsplit(
                            data['file_name'],
                            '/',
                            1
                            ).tolist()
                        )[:, -1],
                    '.',
                    1
                    ).tolist()
                )[:,0],
            np.char.rsplit(np.char.rsplit(
                file_sum,
                '/',
                1
                ).tolist()[-1], '.', 1).tolist()[0]
            )
        data = data[mask]
        data_orig = data_orig[mask]

        # Combine output files
        output_name_partres_comb, output_name_star_comb, output_name_partres, output_name_star = tuc.combine_ctf_outputs(
            data=data,
            data_orig=data_orig,
            root_path=root_path,
            file_name=file_name,
            settings=self.settings,
            queue_com=self.queue_com,
            shared_dict=self.shared_dict,
            name=self.name,
            sum_file=file_sum,
            dw_file=file_dw,
            )

        combine_list = [
            [self.shared_dict['ctf_partres_lock'], output_name_partres, output_name_partres_comb],
            [self.shared_dict['ctf_star_lock'], output_name_star, output_name_star_comb],
            ]
        self.create_combines(combine_list)

        if skip_list:
            pass
        else:
            # Add to queue
            for aim in self.content_settings['aim']:
                *compare, aim_name = aim.split(':')
                var = True
                for typ in compare:
                    name = typ.split('!')[-1]
                    if typ.startswith('!'):
                        if self.settings['Copy'][name] == 'False':
                            continue
                        else:
                            var = False
                            break
                    else:
                        if not self.settings['Copy'][name] == 'False':
                            continue
                        else:
                            var = False
                            break
                if var:
                    if '!Compress' in compare or 'Compress' in compare:
                        self.add_to_queue(aim=aim_name, root_name=file_input)
                    elif 'Picking' in compare:
                        self.add_to_queue(aim=aim_name, root_name=root_name_raw)
                    elif 'Extract' in compare:
                        self.add_to_queue(aim=aim_name, root_name=output_name_partres)
                    else:
                        self.add_to_queue(aim=aim_name, root_name=copied_log_files)
                else:
                    pass
        self.queue_com['log'].put(tu.create_log(self.name, 'run_ctf', root_name_input, 'stop process', time.time() - start_prog))

    def run_extract(self, root_name):
        """
        Run Particle extraction.

        root_name - name of the file to process.

        Returns:
        None
        """
        root_name_input = root_name
        if root_name == 'None':
            self.shared_dict_typ['queue_list_lock'].acquire()
            try:
                self.shared_dict_typ['queue_list_time'] = time.time() * 100
                self.shared_dict_typ['queue_list'][:] = []
            finally:
                self.shared_dict_typ['queue_list_lock'].release()
            return None

        folder_name = 'extract_folder_feedback_{0}'.format(self.settings['do_feedback_loop'].value)

        start_prog = time.time()
        self.queue_com['log'].put(tu.create_log(self.name, 'run_extract', root_name_input, 'start process'))

        self.shared_dict_typ['queue_list_lock'].acquire()
        try:
            self.add_to_queue_file(
                root_name=root_name,
                file_name=self.shared_dict_typ['list_file'],
                )
            file_name = tu.get_name(tu.get_name(tu.get_name(root_name)))
            matches_in_queue = self.all_in_queue_file(self.typ, file_name, lock=False)
            if len(matches_in_queue) != 3:
                self.queue_com['log'].put(tu.create_log(self.name, 'run_extract', root_name_input, 'stop early 1'))
                return None
        finally:
            self.shared_dict_typ['queue_list_lock'].release()

        # Create the command
        output_dir = os.path.join(self.settings[folder_name], file_name)
        tmp_matches = matches_in_queue[:]
        file_ctf = [entry for entry in tmp_matches if 'partres.txt' in entry][0]
        tmp_matches.remove(file_ctf)
        file_box = [entry for entry in tmp_matches if '.box' in entry][0]
        tmp_matches.remove(file_box)
        file_sum = [entry for entry in tmp_matches if '.mrc' in entry][0]
        tmp_matches.remove(file_sum)
        assert not tmp_matches, (tmp_matches, matches_in_queue, file_ctf, file_box, file_sum, output_dir)

        command, check_files, block_gpu, gpu_list, shell = tue.get_extract_command(
            file_sum=file_sum,
            file_box=file_box,
            file_ctf=file_ctf,
            output_dir=output_dir,
            settings=self.settings,
            queue_com=self.queue_com,
            name=self.name
            )

        # Log files
        log_prefix = os.path.join(
                self.settings[folder_name],
                file_name
                )

        log_file, err_file = self.run_command(
            root_name_input=root_name_input,
            command=command,
            log_prefix=log_prefix,
            block_gpu=block_gpu,
            gpu_list=gpu_list,
            shell=shell
            )

        zero_list = [err_file]
        non_zero_list = [log_file]
        non_zero_list.extend(check_files)

        log_files, copied_log_files = tue.find_logfiles(
            root_path=output_dir,
            settings=self.settings,
            queue_com=self.queue_com,
            name=self.name
            )

        tus.check_outputs(
            zero_list=zero_list,
            non_zero_list=non_zero_list,
            exists_list=log_files,
            folder=self.settings[folder_name],
            command=command
            )

        n_particles = tue.get_particle_number(
            log_file,
            self.settings,
            queue_com=self.queue_com,
            name=self.name
            )

        try:
            log_files.remove(err_file)
            copied_log_files.remove(err_file)
        except ValueError:
            pass

        for old_file, new_file in zip(log_files, copied_log_files):
            if os.path.realpath(old_file) != os.path.realpath(new_file):
                os.remove(old_file)
            else:
                pass

        copied_log_files.extend(non_zero_list)
        copied_log_files.extend(zero_list)
        copied_log_files = list(set(copied_log_files))

        tue.create_jpg_file(file_name, self.settings[folder_name])

        skip_list = False
        if skip_list:
            pass
        else:
            # Add to queue
            for aim in self.content_settings['aim']:
                *compare, aim_name = aim.split(':')
                var = True
                for typ in compare:
                    name = typ.split('!')[-1]
                    if typ.startswith('!'):
                        if self.settings['Copy'][name] == 'False':
                            continue
                        else:
                            var = False
                            break
                    else:
                        if not self.settings['Copy'][name] == 'False':
                            continue
                        else:
                            var = False
                            break
                if var:
                    if 'Class2d' in compare:
                        self.add_to_queue(
                            aim=aim_name,
                            root_name=[
                                '|||'.join([n_particles, entry])
                                for entry in copied_log_files
                                if '.bdb' in entry and not entry.endswith('data.bdb')
                                ]
                            )

                    elif 'Auto3d' in compare:
                        self.add_to_queue(
                            aim=aim_name,
                            root_name=[
                                '|||'.join([n_particles, 'bdb:{0}'.format(entry.replace('EMAN2DB/', '').replace('.bdb', ''))])
                                for entry in copied_log_files
                                if '.bdb' in entry and not entry.endswith('data.bdb')
                                ]
                            )

                    else:
                        self.add_to_queue(aim=aim_name, root_name=copied_log_files)
                else:
                    pass

        self.remove_from_queue_file(matches_in_queue, self.shared_dict_typ['list_file'])
        self.queue_com['log'].put(tu.create_log(self.name, 'run_extract', root_name_input, 'stop process', time.time() - start_prog))

    def run_train2d(self, root_name):
        """
        Run Particle extraction.

        root_name - name of the file to process.

        Returns:
        None
        """
        root_name_input = root_name
        if root_name == 'None':
            self.shared_dict_typ['queue_list_lock'].acquire()
            try:
                self.shared_dict_typ['queue_list_time'] = time.time() * 100
                self.shared_dict_typ['queue_list'][:] = []
            finally:
                self.shared_dict_typ['queue_list_lock'].release()
            return None

        folder_name = 'train2d_folder_feedback_{0}'.format(self.settings['do_feedback_loop'].value)

        start_prog = time.time()
        self.queue_com['log'].put(tu.create_log(self.name, 'run_train2d', root_name_input, 'start process'))

        error = False
        matches_in_queue = []
        all_logs = []
        if root_name.endswith('_good.hdf'):

            isac_folder, particle_stack, class_average_file = root_name.split('|||')
            file_name = tu.get_name(isac_folder)
            log_prefix = os.path.join(self.settings[folder_name], file_name)

            command, check_files, block_gpu, gpu_list, shell, stack_name = ttrain2d.create_substack_command(
                class_average_name=class_average_file,
                input_stack=particle_stack,
                isac_dir=isac_folder,
                output_dir=log_prefix,
                settings=self.settings,
                )
            all_logs.append(stack_name)

            log_file, err_file = self.run_command(
                root_name_input=root_name_input,
                command=command,
                log_prefix='{0}_substack'.format(log_prefix),
                block_gpu=block_gpu,
                gpu_list=gpu_list,
                shell=shell
                )
            all_logs.append(err_file)
            all_logs.append(log_file)

            zero_list = [err_file]
            non_zero_list = [log_file]
            non_zero_list.extend(check_files)

            tus.check_outputs(
                zero_list=zero_list,
                non_zero_list=non_zero_list,
                exists_list=[],
                folder=self.settings[folder_name],
                command=command
                )

            command, check_files, block_gpu, gpu_list, shell, box_dir = ttrain2d.create_restack_command(
                stack_name=stack_name,
                output_dir=log_prefix,
                settings=self.settings,
                )
            used_box_name = 'centered' if self.settings[self.settings['Copy']['Train2d']]['Use centered'] == 'True' else 'original'
            box_dir = os.path.join(box_dir, used_box_name)

            log_file, err_file = self.run_command(
                root_name_input=root_name_input,
                command=command,
                log_prefix='{0}_restack'.format(log_prefix),
                block_gpu=block_gpu,
                gpu_list=gpu_list,
                shell=shell
                )
            for entry in sorted(glob.glob(os.path.join(box_dir, '*'))):
                all_logs.append(entry)
            all_logs.append(err_file)
            all_logs.append(log_file)

            zero_list = [err_file]
            non_zero_list = [log_file]
            non_zero_list.extend(check_files)

            tus.check_outputs(
                zero_list=zero_list,
                non_zero_list=non_zero_list,
                exists_list=[],
                folder=self.settings[folder_name],
                command=command
                )
            new_box_dir = box_dir.replace('/BOX/{}'.format(used_box_name), '/BOX/renamed')
            tu.mkdir_p(new_box_dir)

            n_max_micrographs = int(self.settings[self.settings['Copy']['Train2d']]['Maximum micrographs'])

            for file_name in sorted(np.random.permutation(glob.glob(os.path.join(box_dir, '*')))[:n_max_micrographs]):
                tu.symlink_rel(
                    file_name,
                    file_name.replace(box_dir, new_box_dir).replace('_{}.box'.format(used_box_name), '.box')
                    )
                all_logs.append(file_name.replace(box_dir, new_box_dir).replace('_{}.box'.format(used_box_name), '.box'))

            self.shared_dict_typ['queue_list_lock'].acquire()
            try:
                self.try_write(self.shared_dict_typ['number_file'], 'w', log_prefix)
                for entry in sorted(glob.glob(os.path.join(new_box_dir, '*'))):
                    self.add_to_queue_file(
                        root_name=entry,
                        file_name=self.shared_dict_typ['list_file'],
                        )
                    matches = self.all_in_queue_file(self.typ, tu.get_name(entry), lock=False)
                    if len(matches) != 2:
                        error = True
                    elif error:
                        pass
                    else:
                        matches_in_queue.extend(matches)
            finally:
                self.shared_dict_typ['queue_list_lock'].release()

        else:
            self.shared_dict_typ['queue_list_lock'].acquire()
            try:
                self.add_to_queue_file(
                    root_name=root_name,
                    file_name=self.shared_dict_typ['list_file'],
                    )
                with open(self.shared_dict_typ['list_file']) as read:
                    box_files = [line.strip() for line in read.readlines() if line.strip() and '.box' in line]
                if not box_files:
                    error = True
                else:                
                    with open(self.shared_dict_typ['number_file'], 'r') as read:
                        log_prefix = read.read().strip()

                for entry in box_files:
                    matches = self.all_in_queue_file(self.typ, tu.get_name(entry), lock=False)
                    if len(matches) != 2:
                        error = True
                        break
                    else:
                        matches_in_queue.extend(matches)
            finally:
                self.shared_dict_typ['queue_list_lock'].release()

        if error:
            self.queue_com['log'].put(tu.create_log(self.name, 'run_train2d', root_name_input, 'stop early 1', time.time() - start_prog))
            return None


        # Create the command
        tmp_matches = matches_in_queue[:]
        sum_folder = np.unique([os.path.dirname(entry) for entry in tmp_matches if '.mrc' in entry]).tolist()[0]
        box_folder = np.unique([os.path.dirname(entry) for entry in tmp_matches if '.box' in entry]).tolist()[0]

        command, check_files, block_gpu, gpu_list, shell, new_model, new_config = ttrain2d.create_train_command(
            sum_folder=sum_folder,
            box_folder=box_folder,
            output_dir=log_prefix,
            name=self.name,
            settings=self.settings,
            )

        log_file, err_file = self.run_command(
            root_name_input=root_name_input,
            command=command,
            log_prefix='{0}_train'.format(log_prefix),
            block_gpu=block_gpu,
            gpu_list=gpu_list,
            shell=shell
            )
        all_logs.append(new_model)
        all_logs.append(new_config)
        all_logs.append(log_file)
        all_logs.append(err_file)

        zero_list = []
        non_zero_list = [err_file, log_file, new_model, new_config]
        non_zero_list.extend(check_files)

        tus.check_outputs(
            zero_list=zero_list,
            non_zero_list=non_zero_list,
            exists_list=[],
            folder=self.settings[folder_name],
            command=command
            )

        self.shared_dict['global_update_lock'].acquire()
        try:
            for aim in ('Picking', 'Extract', 'Class2d', 'Select2d', 'Train2d'):
                if aim in ('Picking'):
                    remove_pattern = 'THIS IS A DUMMY PATTERN!'
                elif aim in ('Extract'):
                    remove_pattern = '.*\.box'
                elif aim in ('Train2d'):
                    remove_pattern = '.*\.hdf'
                else:
                    remove_pattern = '.*'
                self.reset_queue(
                    aim=aim,
                    switch_feedback=True,
                    remove_pattern=remove_pattern,
                    )

            new_threshold = None
            if self.settings['do_feedback_loop'].value == 1 and self.settings[self.settings['Copy']['Picking']]['--filament'] == 'False' and tu.is_higher_version(self.settings['Copy']['Train2d'], '1.5.8'):
                command, check_files, block_gpu, gpu_list, shell = ttrain2d.create_eval_command(new_config, new_model, log_file, self.settings, self.name)
                if command is not None:
                    log_file, err_file = self.run_command(
                        root_name_input=root_name_input,
                        command=command,
                        log_prefix='{0}_evaluation'.format(log_prefix),
                        block_gpu=block_gpu,
                        gpu_list=gpu_list,
                        shell=shell
                        )
                    all_logs.append(log_file)
                    all_logs.append(err_file)

                    zero_list = []
                    non_zero_list = [err_file, log_file]
                    non_zero_list.extend(check_files)

                    tus.check_outputs(
                        zero_list=zero_list,
                        non_zero_list=non_zero_list,
                        exists_list=[],
                        folder=self.settings[folder_name],
                        command=command
                        )

                    try:
                        with open(log_file, 'r') as read:
                            new_threshold = re.search('^.*according F2 statistic: (.*)$', read.read(), re.M).group(1).strip() # https://regex101.com/r/ZvTGaw
                    except Exception:
                        message = 'Could not find F2 score in the output file: {0}!'.format(log_file)
                        self.queue_com['error'].put(message)
                        raise

            elif self.settings['do_feedback_loop'].value == 1 and self.settings[self.settings['Copy']['Picking']]['--filament'] == 'True' and tu.is_higher_version(self.settings['Copy']['Train2d'], '1.5.8'):
                new_threshold = 0.3

            if new_threshold is None:
                threshold = self.settings[self.settings['Copy']['Picking']]['--threshold_old']
            else:
                threshold = new_threshold

            self.shared_dict['typ']['Picking']['queue_list_lock'].acquire()
            try:
                self.try_write(self.shared_dict['typ']['Picking']['settings_file'], 'w', '|||'.join([new_model, new_config, str(threshold)]))
            finally:
                self.shared_dict['typ']['Picking']['queue_list_lock'].release()

            skip_list = False
            if skip_list:
                pass
            else:
                # Add to queue
                for aim in self.content_settings['aim']:
                    *compare, aim_name = aim.split(':')
                    var = True
                    for typ in compare:
                        name = typ.split('!')[-1]
                        if typ.startswith('!'):
                            if self.settings['Copy'][name] == 'False':
                                continue
                            else:
                                var = False
                                break
                        else:
                            if not self.settings['Copy'][name] == 'False':
                                continue
                            else:
                                var = False
                                break
                    if var:
                        self.add_to_queue(aim=aim_name, root_name=all_logs)
                    else:
                        pass

            #self.remove_from_queue_file(matches_in_queue, self.shared_dict_typ['list_file'])
            for type_name in ('Extract', 'Class2d'):
                self.shared_dict['typ'][type_name]['queue_lock'].acquire()
                try:
                    self.try_write(self.shared_dict['typ'][type_name]['feedback_lock_file'], 'w', '0')
                finally:
                    self.shared_dict['typ'][type_name]['queue_lock'].release()

            with self.settings['do_feedback_loop'].get_lock():
                self.settings['do_feedback_loop'].value -= 1

            self.try_write(self.settings['feedback_file'], 'w', str(self.settings['do_feedback_loop'].value))

            if self.settings['do_feedback_loop'].value == 0:
                self.queue_com['status'].put([
                    '{0:02d}|{1:02d}'.format(
                        int(self.settings['Output']['Number of feedbacks']) - self.settings['do_feedback_loop'].value,
                        int(self.settings['Output']['Number of feedbacks'])
                        ),
                    ['Done'],
                    'Feedbacks',
                    tu.get_color('Finished')
                    ])
            else:
                self.queue_com['status'].put([
                    '{0:02d}|{1:02d}'.format(
                        int(self.settings['Output']['Number of feedbacks']) - self.settings['do_feedback_loop'].value,
                        int(self.settings['Output']['Number of feedbacks'])
                        ),
                    ['Running'],
                    'Feedbacks',
                    tu.get_color('Running')
                    ])
        finally:
            self.shared_dict['global_update_lock'].release()

        self.queue_com['log'].put(tu.create_log(self.name, 'run_train2d', root_name_input, 'stop process', time.time() - start_prog))



    def run_class2d(self, root_name):
        root_name_input = root_name
        start_prog = time.time()
        self.queue_com['log'].put(tu.create_log(self.name, 'run_class2d', root_name_input, 'start process'))

        folder_name = 'class2d_folder_feedback_{0}'.format(self.settings['do_feedback_loop'].value)

        self.shared_dict_typ['queue_list_lock'].acquire()
        try:
            try:
                with open(self.shared_dict_typ['number_file'], 'r') as read:
                    try:
                        old_index = read.read().strip()
                        old_index = int(old_index)
                    except ValueError:
                        old_index = -1
            except FileNotFoundError:
                old_index = -1

            if root_name != 'None':
                self.shared_dict_typ['queue_list'].append(root_name)
                self.add_to_queue_file(
                    root_name=root_name,
                    file_name=self.shared_dict_typ['list_file'],
                    )
                self.queue_com['log'].put(tu.create_log(self.name, 'run_class2d', root_name_input, 'stop early 1', time.time() - start_prog))
                return None

            lines_to_use = []
            final_lines_to_use = []
            total_n = 0
            n_particles_to_check = int(self.settings[self.prog_name]['Nr. Particles'])

            for line in self.shared_dict_typ['queue_list']:
                lines_to_use.append(line)
                n_particles, stack_name = line.split('|||')
                total_n += int(n_particles)
                if total_n >= n_particles_to_check:
                    final_lines_to_use = lines_to_use
                    break

            if not final_lines_to_use:
                self.queue_com['log'].put(tu.create_log(self.name, 'run_class2d', root_name_input, 'stop early 2', time.time() - start_prog))
                self.shared_dict_typ['queue_list_time'] = time.time()
                return None

            try:
                with open(self.shared_dict['typ']['Class2d']['feedback_lock_file'], 'r') as read:
                    if '1' in read.read():
                        self.queue_com['log'].put(tu.create_log(self.name, 'run_class2d', root_name_input, 'stop early 3', time.time() - start_prog))
                        self.shared_dict_typ['queue_list_time'] = time.time()
                        return None
            except FileNotFoundError:
                pass

            current_idx = old_index + 1
            self.try_write(self.shared_dict_typ['number_file'], 'w', str(current_idx))

            for entry in final_lines_to_use:
                self.shared_dict_typ['queue_list'].remove(entry)

            if self.settings['do_feedback_loop'].value:
                for type_name in ('Extract', 'Class2d'):
                    self.shared_dict['typ'][type_name]['queue_lock'].acquire()
                    try:
                        self.try_write(self.shared_dict['typ'][type_name]['feedback_lock_file'], 'w', '1')
                    finally:
                        self.shared_dict['typ'][type_name]['queue_lock'].release()
        finally:
            self.shared_dict_typ['queue_list_lock'].release()

        try:
            file_name = '{0:03d}'.format(current_idx)
            command, check_files, block_gpu, gpu_list, shell, new_stack = tuclass2d.create_stack_combine_command(
                class2d_name=self.prog_name,
                file_names=[entry.strip().split('|||')[1] for entry in final_lines_to_use if entry.strip()],
                file_name=file_name,
                output_dir=self.settings[folder_name],
                settings=self.settings,
                queue_com=self.queue_com,
                name=self.name,
                )

            # Log files
            log_prefix = os.path.join(
                    self.settings[folder_name],
                    '{0}_combine'.format(file_name)
                    )

            log_file, err_file = self.run_command(
                root_name_input=root_name_input,
                command=command,
                log_prefix=log_prefix,
                block_gpu=block_gpu,
                gpu_list=gpu_list,
                shell=shell
                )

            command, check_files, block_gpu, gpu_list, shell = tuclass2d.create_class2d_command(
                class2d_name=self.prog_name,
                stack_name=new_stack,
                file_name=file_name,
                output_dir=self.settings[folder_name],
                settings=self.settings,
                queue_com=self.queue_com,
                name=self.name,
                )

            # Log files
            log_prefix = os.path.join(
                    self.settings[folder_name],
                    '{0}'.format(file_name)
                    )

            log_file, err_file = self.run_command(
                root_name_input=root_name_input,
                command=command,
                log_prefix=log_prefix,
                block_gpu=block_gpu,
                gpu_list=gpu_list,
                shell=shell
                )

            zero_list = [err_file]
            non_zero_list = [log_file]
            non_zero_list.extend(check_files)

            log_files, copied_log_files = tuclass2d.find_logfiles(
                root_path=os.path.join(self.settings[folder_name], file_name),
                settings=self.settings,
                queue_com=self.queue_com,
                name=self.name
                )

            tus.check_outputs(
                zero_list=zero_list,
                non_zero_list=non_zero_list,
                exists_list=log_files,
                folder=self.settings[folder_name],
                command=command
                )

            try:
                log_files.remove(err_file)
                copied_log_files.remove(err_file)
            except ValueError:
                pass

            for old_file, new_file in zip(log_files, copied_log_files):
                if os.path.realpath(old_file) != os.path.realpath(new_file):
                    os.remove(old_file)
                else:
                    pass

            copied_log_files.extend(non_zero_list)
            copied_log_files.extend(zero_list)
            copied_log_files = list(set(copied_log_files))

            tuclass2d.create_jpg_file(
                file_name,
                self.settings[folder_name],
                )

        except Exception:
            self.shared_dict_typ['queue_list_lock'].acquire()
            try:
                self.shared_dict_typ['queue_list'].extend(final_lines_to_use)
                self.try_write(self.shared_dict['typ'][self.typ]['feedback_lock_file'], 'w', '0')
            finally:
                self.shared_dict_typ['queue_list_lock'].release()
            self.queue_com['log'].put(tu.create_log(self.name, 'run_auto3d', root_name_input, 'stop early 4', time.time() - start_prog))
            raise
        else:
            self.queue_com['notification'].put(
                'New class averages arrived. :)'
                )
            skip_list = False
            if skip_list:
                pass
            else:
                # Add to queue
                for aim in self.content_settings['aim']:
                    *compare, aim_name = aim.split(':')
                    var = True
                    for typ in compare:
                        name = typ.split('!')[-1]
                        if typ.startswith('!'):
                            if self.settings['Copy'][name] == 'False':
                                continue
                            else:
                                var = False
                                break
                        else:
                            if not self.settings['Copy'][name] == 'False':
                                continue
                            else:
                                var = False
                                break
                    if var:
                        if 'Select2d' in compare:
                            self.add_to_queue(aim=aim_name, root_name='|||'.join([log_prefix, new_stack]))
                        elif 'Auto3d' in compare:
                            self.add_to_queue(
                                aim=aim_name,
                                root_name='|||'.join([
                                    str(self.settings['do_feedback_loop'].value),
                                    log_prefix,
                                    new_stack,
                                    check_files[0]
                                    ])
                                )
                        else:
                            self.add_to_queue(aim=aim_name, root_name=copied_log_files)
                    else:
                        pass

            self.shared_dict_typ['queue_list_lock'].acquire()
            try:
                self.remove_from_queue_file(final_lines_to_use, self.shared_dict_typ['list_file'])
            finally:
                self.shared_dict_typ['queue_list_lock'].release()

        finally:
            self.shared_dict_typ['queue_list_lock'].acquire()
            try:
                self.shared_dict_typ['queue_list_time'] = time.time()
            finally:
                self.shared_dict_typ['queue_list_lock'].release()

        self.queue_com['log'].put(tu.create_log(self.name, 'run_class2d', root_name_input, 'stop process', time.time() - start_prog))

    def run_select2d(self, root_name):
        """
        Run Particle extraction.

        root_name - name of the file to process.

        Returns:
        None
        """
        root_name_input = root_name
        if root_name == 'None':
            self.shared_dict_typ['queue_list_lock'].acquire()
            try:
                self.shared_dict_typ['queue_list_time'] = time.time() * 100
                self.shared_dict_typ['queue_list'][:] = []
            finally:
                self.shared_dict_typ['queue_list_lock'].release()
            return None

        root_name_raw = root_name
        # Input is ISAC_DIR|||STACK_NAME
        root_name, _ = root_name.split('|||')

        folder_name = 'select2d_folder_feedback_{0}'.format(self.settings['do_feedback_loop'].value)

        start_prog = time.time()
        self.queue_com['log'].put(tu.create_log(self.name, 'run_select_2d', root_name_input, 'start process'))
        file_name = tu.get_name(tu.get_name(tu.get_name(root_name)))

        # Create the command
        output_dir = os.path.join(self.settings[folder_name], file_name)

        command, check_files, block_gpu, gpu_list, shell = tselect2d.get_select2d_command(
            file_input=root_name,
            output_dir=output_dir,
            settings=self.settings,
            queue_com=self.queue_com,
            name=self.name
            )

        # Log files
        log_prefix = os.path.join(
                self.settings[folder_name],
                file_name
                )

        log_file, err_file = self.run_command(
            root_name_input=root_name_input,
            command=command,
            log_prefix=log_prefix,
            block_gpu=block_gpu,
            gpu_list=gpu_list,
            shell=shell
            )

        zero_list = []
        non_zero_list = [log_file, err_file]
        non_zero_list.extend(check_files)

        log_files, copied_log_files = tselect2d.find_logfiles(
            root_path=output_dir,
            settings=self.settings,
            queue_com=self.queue_com,
            name=self.name
            )

        tus.check_outputs(
            zero_list=zero_list,
            non_zero_list=non_zero_list,
            exists_list=log_files,
            folder=self.settings[folder_name],
            command=command
            )

        try:
            log_files.remove(err_file)
            copied_log_files.remove(err_file)
        except ValueError:
            pass

        for old_file, new_file in zip(log_files, copied_log_files):
            if os.path.realpath(old_file) != os.path.realpath(new_file):
                os.remove(old_file)
            else:
                pass

        copied_log_files.extend(non_zero_list)
        copied_log_files.extend(zero_list)
        copied_log_files = list(set(copied_log_files))

        tselect2d.create_jpg_file(file_name, self.settings[folder_name])

        skip_list = False
        if skip_list:
            pass
        else:
            # Add to queue
            for aim in self.content_settings['aim']:
                *compare, aim_name = aim.split(':')
                var = True
                for typ in compare:
                    name = typ.split('!')[-1]
                    if typ.startswith('!'):
                        if self.settings['Copy'][name] == 'False':
                            continue
                        else:
                            var = False
                            break
                    else:
                        if not self.settings['Copy'][name] == 'False':
                            continue
                        else:
                            var = False
                            break
                if var:
                    if self.settings['do_feedback_loop'].value and 'Train2d' in compare:
                        self.add_to_queue(
                            aim=aim_name,
                            root_name='|||'.join([
                                root_name_raw,
                                os.path.join(
                                    self.settings[folder_name],
                                    file_name,
                                    'ordered_class_averages_good.hdf'
                                    )
                                ])
                            )
                    elif 'Train2d' in compare:
                        pass
                    elif 'Auto3d' in compare:
                        self.add_to_queue(
                            aim=aim_name,
                            root_name='|||'.join([
                                str(self.settings['do_feedback_loop'].value),
                                root_name_raw,
                                os.path.join(
                                    self.settings[folder_name],
                                    file_name,
                                    'ordered_class_averages_good.hdf'
                                    )
                                ])
                            )
                    else:
                        self.add_to_queue(aim=aim_name, root_name=copied_log_files)
                else:
                    pass

        self.queue_com['log'].put(tu.create_log(self.name, 'run_select2d', root_name_input, 'stop process', time.time() - start_prog))

    def run_picking(self, root_name):
        """
        Run picking particles.

        root_name - name of the file to process.

        Returns:
        None
        """
        root_name_input = root_name
        start_prog = time.time()
        self.queue_com['log'].put(tu.create_log(self.name, 'run_picking', root_name_input, 'start process'))

        self.shared_dict['typ']['Picking']['queue_list_lock'].acquire()
        try:
            try:
                with open(self.shared_dict_typ['settings_file'], 'r') as read:
                    new_model, new_config, new_threshold = read.readline().strip().split('|||')
            except FileNotFoundError:
                pass
            except AttributeError:
                pass
            else:
                self.settings[self.settings['Copy']['Picking']]['--weights'] = new_model
                self.settings[self.settings['Copy']['Picking']]['--conf'] = new_config
                self.settings[self.settings['Copy']['Picking']]['--threshold'] = new_threshold
        finally:
            self.shared_dict['typ']['Picking']['queue_list_lock'].release()

        folder_name = 'picking_folder_feedback_{0}'.format(self.settings['do_feedback_loop'].value)
        entry_name = 'picking_folder_feedback_{0}'.format(self.settings['do_feedback_loop'].value)

        if root_name == 'None':
            pass
        else:
            # New name; Splitis file_sum, file_dw_sum, file_frames
            file_sum, file_dw_sum, file_frames = root_name.split(';;;')
            if file_dw_sum == 'None':
                file_name = os.path.basename(os.path.splitext(file_sum)[0])
                file_use = file_sum
            else:
                file_name = os.path.basename(os.path.splitext(file_dw_sum)[0])
                file_use = file_dw_sum

            # Create the command for filtering
            command, file_input, check_files, block_gpu, gpu_list = tup.create_filter_command(
                file_input=file_use,
                settings=self.settings,
                )

            # Log files
            log_prefix = os.path.join(
                    self.settings[folder_name],
                    '{0}_filter'.format(file_name)
                    )

            log_file, err_file = self.run_command(
                root_name_input=root_name_input,
                command=command,
                log_prefix=log_prefix,
                block_gpu=block_gpu,
                gpu_list=gpu_list,
                shell=True
                )

            zero_list = [err_file]
            non_zero_list = [log_file]
            non_zero_list.extend(check_files)

            tus.check_outputs(
                zero_list=zero_list,
                non_zero_list=non_zero_list,
                exists_list=[],
                folder=self.settings[folder_name],
                command=command
                )
            self.shared_dict_typ['queue_list_lock'].acquire()
            try:
                self.add_to_queue_file(
                    root_name=root_name,
                    file_name=self.shared_dict_typ['list_file'],
                    )
                self.shared_dict_typ['queue_list'].append(root_name)
                if time.time() - self.shared_dict_typ['queue_list_time'] < 30:
                    self.queue_com['log'].put(tu.create_log(self.name, 'run_picking', root_name_input, self.shared_dict_typ['queue_list_time'], time.time() - self.shared_dict_typ['queue_list_time'], 'stop early 1', time.time() - start_prog))
                    return None
                else:
                    pass
            finally:
                self.shared_dict_typ['queue_list_lock'].release()

        self.shared_dict_typ['queue_list_lock'].acquire()
        try:
            if time.time() - self.shared_dict_typ['queue_list_time'] < 30:
                self.queue_com['log'].put(tu.create_log(self.name, 'run_picking', root_name_input, self.shared_dict_typ['queue_list_time'], time.time() - self.shared_dict_typ['queue_list_time'], 'stop early 2', time.time() - start_prog))
                return None
            elif not self.shared_dict_typ['queue_list']:
                self.shared_dict_typ['queue_list_time'] = time.time()
                self.queue_com['log'].put(tu.create_log(self.name, 'run_picking', root_name_input, self.shared_dict_typ['queue_list_time'], time.time() - self.shared_dict_typ['queue_list_time'], 'stop early 3', time.time() - start_prog))
                return None
            file_use_list = []
            file_name_list = []
            file_queue_list = self.shared_dict_typ['queue_list'][:]
            for entry in self.shared_dict_typ['queue_list']:
                file_sum, file_dw_sum, file_frames = entry.split(';;;')
                if file_dw_sum == 'None':
                    file_use_name = file_sum
                else:
                    file_use_name = file_dw_sum
                if file_use_name.startswith('./'):
                    file_use_name = file_use_name[2:]
                file_use_list.append(file_use_name)
                file_name_list.append(tu.get_name(file_use_name))
            self.shared_dict_typ['queue_list'][:] = []
            self.shared_dict_typ['queue_list_time'] = time.time()
        finally:
            self.shared_dict_typ['queue_list_lock'].release()

        try:
            # Create the command for picking
            command, check_files, block_gpu, gpu_list = tup.get_picking_command(
                file_input=file_use_list,
                new_name=self.settings[folder_name],
                settings=self.settings,
                queue_com=self.queue_com,
                name=self.name
                )

            # Log files
            log_prefix = os.path.join(
                    self.settings[folder_name],
                    file_name_list[-1]
                    )

            log_file, err_file = self.run_command(
                root_name_input=root_name_input,
                command=command,
                log_prefix=log_prefix,
                block_gpu=block_gpu,
                gpu_list=gpu_list,
                shell=False
                )

            zero_list = []
            non_zero_list = [err_file, log_file]
            non_zero_list.extend(check_files)

            file_logs = []
            for file_use, file_name in zip(file_use_list, file_name_list):
                root_path = os.path.join(os.path.dirname(file_use), file_name)
                log_files, copied_log_files = tup.find_logfiles(
                    root_path=root_path,
                    file_name=file_name,
                    settings=self.settings,
                    queue_com=self.queue_com,
                    name=self.name
                    )

                tus.check_outputs(
                    zero_list=zero_list,
                    non_zero_list=non_zero_list,
                    exists_list=log_files,
                    folder=self.settings[folder_name],
                    command=command
                    )
                log_files.extend(non_zero_list)
                log_files.extend(zero_list)

                tup.create_box_jpg(
                    file_name=file_name,
                    settings=self.settings,
                    queue_com=self.queue_com,
                    name=self.name,
                    )
                file_logs.append(log_files)

            export_log_files = []
            for file_use, file_name, file_log in zip(file_use_list, file_name_list, file_logs):
                import_name = tu.get_name(file_use)
                data, data_orig = tu.get_function_dict()[self.prog_name]['plot_data'](
                    self.prog_name,
                    self.prog_name,
                    self.settings,
                    self.settings[entry_name],
                    import_name
                    )

                warnings, skip_list = tus.check_for_outlier(
                    dict_name='Picking',
                    data=data,
                    file_name=file_use,
                    settings=self.settings
                    )

                if skip_list:
                    self.remove_from_translate(os.path.basename(file_use))
                else:
                    export_log_files.extend(file_log)

            for warning in skip_list:
                self.send_out_of_range_error(warning, root_name, 'skip')

            for warning in warnings:
                self.send_out_of_range_error(warning, root_name, 'warning')

            if skip_list:
                pass
            else:
                # Add to queue
                for aim in self.content_settings['aim']:
                    *compare, aim_name = aim.split(':')
                    var = True
                    for typ in compare:
                        name = typ.split('!')[-1]
                        if typ.startswith('!'):
                            if self.settings['Copy'][name] == 'False':
                                continue
                            else:
                                var = False
                                break
                        else:
                            if not self.settings['Copy'][name] == 'False':
                                continue
                            else:
                                var = False
                                break
                    if var:
                        if 'Extract' in compare:
                            self.add_to_queue(
                                aim=aim_name,
                                root_name=[entry for entry in export_log_files if 'EMAN' in entry and 'EMAN_START_END' not in entry]
                                )
                        else:
                            self.add_to_queue(aim=aim_name, root_name=export_log_files)
                    else:
                        pass
        except Exception:
            self.shared_dict_typ['queue_list'].extend(file_queue_list)
            raise
        else:
            self.remove_from_queue_file(file_queue_list, self.shared_dict_typ['list_file'])
        self.queue_com['log'].put(tu.create_log(self.name, 'run_picking', root_name_input, 'stop process', time.time() - start_prog))

    def run_compress(self, root_name):
        """
        Compress stack.

        root_name - Name of the file to compress

        Returns:
        None
        """
        root_name_input = root_name
        start_prog = time.time()
        self.queue_com['log'].put(tu.create_log(self.name, 'run_compress', root_name_input, 'start process'))
        root_name, _ = root_name.split('|||')
        new_root_name, extension = os.path.splitext(os.path.basename(root_name))

        log_prefix = os.path.join(
                self.settings['compress_folder_feedback_0'],
                new_root_name
                )

        if self.settings['compress_folder_feedback_0'] in root_name:
            new_name = root_name
            log_file, err_file = tus.get_logfiles(log_prefix)
            tus.check_outputs(
                zero_list=[err_file],
                non_zero_list=[log_file, new_name],
                exists_list=[],
                folder=self.settings['compress_folder_feedback_0'],
                command='just check'
                )

        elif self.settings['Input']['Input frames extension'] in ('tiff', 'tif'):
            log_prefix = os.path.join(
                    self.settings['stack_folder'],
                    new_root_name
                    )
            new_name = root_name
            log_file, err_file = tus.get_logfiles(log_prefix)
            tus.check_outputs(
                zero_list=[err_file],
                non_zero_list=[log_file, new_name],
                exists_list=[],
                folder=self.settings['stack_folder'],
                command='just check'
                )

        else:
            compress_name = self.settings['Copy']['Compress']
            compress_settings = self.settings[compress_name]
            # Create the command
            if compress_name == 'Compress cmd':
                # Compress command
                new_name = os.path.join(
                    self.settings['compress_folder_feedback_0'],
                    '{0}.{1}'.format(
                        new_root_name,
                        compress_settings['--command_compress_extension']
                        )
                    )

                compress_options = self.settings[compress_name]['--command_compress_option']
                compress_options = compress_options.replace(
                    '##INPUT##',
                    root_name,
                    ).replace(
                        '##OUTPUT##',
                        new_name,
                        )

                command = '{0} {1}'.format(
                    self.settings[compress_name]['--command_compress_path'], 
                    compress_options,
                    )

                # Uncompress command
                uncompress_new_name = os.path.join(
                    self.settings['compress_folder_feedback_0'],
                    '{0}_tmp.{1}'.format(
                        new_root_name,
                        compress_settings['--command_uncompress_extension']
                        )
                    )

                compress_options = self.settings[compress_name]['--command_uncompress_option']
                compress_options = compress_options.replace(
                    '##INPUT##',
                    new_name,
                    ).replace(
                        '##OUTPUT##',
                        uncompress_new_name,
                        )

                command_uncompress = '{0} {1}'.format(
                    self.settings[compress_name]['--command_uncompress_path'], 
                    compress_options,
                    )
            else:
                message = 'Unknown compress name: {0}!'.format(compress_name)
                self.queue_com['error'].put(message)
                raise TypeError(message)

            # Skip files that are already copied but due to an error are still in the queue
            if not os.path.exists(root_name) and os.path.exists(new_name):
                print(root_name, ' does not exist anymore, but', new_name, 'does already!')
                print('Compress - Skip file!')
                self.queue_com['log'].put(tu.create_log(self.name, 'run_compress', root_name_input, 'stop early 1'))
                return None

            if os.path.exists(new_name):
                os.remove(new_name)

            # Log files
            log_file, err_file = self.run_command(
                root_name_input=root_name_input,
                command=command,
                log_prefix=log_prefix,
                block_gpu=False,
                gpu_list=[],
                shell=True
                )

            tus.check_outputs(
                zero_list=[err_file],
                non_zero_list=[log_file, new_name],
                exists_list=[],
                folder=self.settings['compress_folder_feedback_0'],
                command=command
                )

            # Log files
            log_file_uncompress, err_file_uncompress = self.run_command(
                root_name_input=root_name_input,
                command=command_uncompress,
                log_prefix='{0}_uncompress'.format(log_prefix),
                block_gpu=False,
                gpu_list=[],
                shell=True
                )

            tus.check_outputs(
                zero_list=[err_file_uncompress],
                non_zero_list=[log_file_uncompress, uncompress_new_name],
                exists_list=[],
                folder=self.settings['compress_folder_feedback_0'],
                command=command
                )

            try:
                os.remove(uncompress_new_name)
            except OSError:
                pass

        # Add to queue
        for aim in self.content_settings['aim']:
            *compare, aim_name = aim.split(':')
            var = True
            for typ in compare:
                name = typ.split('!')[-1]
                if typ.startswith('!'):
                    if self.settings['Copy'][name] == 'False':
                        continue
                    else:
                        var = False
                        break
                else:
                    if not self.settings['Copy'][name] == 'False':
                        continue
                    else:
                        var = False
                        break
            if var:
                self.add_to_queue(aim=aim_name, root_name=[new_name, log_file, err_file])
            else:
                pass
        self.queue_com['log'].put(tu.create_log(self.name, 'run_compress', root_name_input, 'stop process', time.time() - start_prog))


    def run_auto3d(self, root_name):
        """
        Run AutoSPHIRE.
        In case of Feedback rounds, just work with what is available.
        Otherwise, first wait until the required minimum number of classes is reached.
        Once this condition is met, create the combined classes file and provide it to the first AutoSPHIRE run.
        Afterwards, when the root_name is None start AutoSPHIRE when the minimum number of particles is met.

        root_name - name of the file to process.

        Returns:
        None
        """
        root_name_input = root_name
        start_prog = time.time()
        self.queue_com['log'].put(tu.create_log(self.name, 'run_auto3d', root_name_input, 'start process'))

        def recursive_file_search(folder_name, copy_files):
            """
            Helper function to perform a recursion and find files to copy

            folder_name - Name of the current folder to check.
            copy_files - Output list containing all the found files

            Returns:
            None - Output saved in copy_files
            """
            for name in glob.iglob('{0}/*'.format(folder_name)):
                if os.path.isdir(name):
                    recursive_file_search('{0}'.format(name), copy_files)
                else:
                    copy_files.append(name)

        self.shared_dict_typ['queue_list_lock'].acquire()
        try:
            try:
                with open(self.shared_dict_typ['number_file'], 'r') as read:
                    try:
                        old_shrink_ratio, old_index, volume = read.read().strip().split('|||')
                        old_index = int(old_index)
                        old_shrink_ratio = float(old_shrink_ratio)
                    except ValueError:
                        old_index = -1
                        old_shrink_ratio = -1
                        volume = self.settings[self.prog_name]['input_volume'] if self.settings[self.prog_name]['input_volume'] else 'XXXNoneXXX'
            except FileNotFoundError:
                old_index = -1
                old_shrink_ratio = -1
                volume = self.settings[self.prog_name]['input_volume'] if self.settings[self.prog_name]['input_volume'] else 'XXXNoneXXX'

            # New stack creation, populating the list file, create classes.
            if root_name != 'None' and len(root_name.split('|||')) == 2:
                n_particles, stack_name = root_name.split('|||')
                folder_name = 'auto3d_folder_feedback_{0}'.format(0)

                # Extract a substack from the good class averages.
                file_name = tu.get_name(root_name)
                log_prefix = os.path.join(self.settings[folder_name], 'FILES', 'WINDOW_{0}'.format(file_name))
                self.try_write(self.shared_dict_typ['number_file'], 'w', '|||'.join([str(entry) for entry in [old_shrink_ratio, old_index, volume]]))

                add_to_string = '|||'.join(map(str, [0, stack_name, n_particles, 'NONE', 0]))
                self.add_to_queue_file(
                    root_name=add_to_string,
                    file_name=self.shared_dict_typ['list_file'],
                    )
                self.shared_dict_typ['queue_list'].append(add_to_string)
                self.queue_com['log'].put(tu.create_log(self.name, 'run_auto3d', root_name_input, 'stop early 1', time.time() - start_prog))
                return None ### Early exit for the preparation here.

            elif root_name != 'None' and len(root_name.split('|||')) == 4:
                # Split root_name to get the needed information for this run.
                feedback_loop, isac_folder, particle_stack, class_average_file = root_name.split('|||')
                if feedback_loop != '0' and self.settings[self.prog_name]['Run during feedback'] == 'False':
                    self.queue_com['log'].put(tu.create_log(self.name, 'run_auto3d', root_name_input, 'stop early 2a', time.time() - start_prog))
                    return None ### Early exit here.

                folder_name = 'auto3d_folder_feedback_{0}'.format(feedback_loop)

                # Extract a substack from the good class averages.
                file_name = tu.get_name(isac_folder)
                log_prefix = os.path.join(self.settings[folder_name], 'FILES', 'ISAC_{0}'.format(file_name))

                command, check_files, block_gpu, gpu_list, shell, stack_name = ttrain2d.create_substack_command(
                    class_average_name=class_average_file,
                    input_stack=particle_stack,
                    isac_dir=isac_folder,
                    output_dir=log_prefix,
                    settings=self.settings,
                    )

                log_file, err_file = self.run_command(
                    root_name_input=root_name_input,
                    command=command,
                    log_prefix='{0}_substack'.format(log_prefix),
                    block_gpu=block_gpu,
                    gpu_list=gpu_list,
                    shell=shell
                    )

                zero_list = [err_file]
                non_zero_list = [log_file]
                non_zero_list.extend(check_files)

                tus.check_outputs(
                    zero_list=zero_list,
                    non_zero_list=non_zero_list,
                    exists_list=[],
                    folder=self.settings[folder_name],
                    command=command
                    )

                copy_files = []
                recursive_file_search(log_prefix, copy_files)
                self.copy_extern('Copy_to_work', copy_files)

                with open(log_file, 'r') as read:
                    content = read.read()
                shrink_ratio = re.search(
                    'ISAC shrink ratio\s*:\s*(0\.\d+)',
                    content,
                    re.MULTILINE
                    ).group(1)
                n_particles = int(re.search(
                    'ISAC substack size\s*:\s*(\d+)',
                    content,
                    re.MULTILINE
                    ).group(1))
                n_classes = int(re.search(
                    'Provided class averages\s*:\s*(\d+)',
                    content,
                    re.MULTILINE
                    ).group(1))

                if old_shrink_ratio != -1:
                    assert old_shrink_ratio == float(shrink_ratio), 'Shrink ratios changed! Something is wrong here'
                self.try_write(self.shared_dict_typ['number_file'], 'w', '|||'.join([str(entry) for entry in [shrink_ratio, old_index, volume]]))
                add_to_string = '|||'.join(map(str, [feedback_loop, stack_name, n_particles, class_average_file, n_classes]))
                self.add_to_queue_file(
                    root_name=add_to_string,
                    file_name=self.shared_dict_typ['list_file'],
                    )
                self.shared_dict_typ['queue_list'].append(add_to_string)
                self.queue_com['log'].put(tu.create_log(self.name, 'run_auto3d', root_name_input, 'stop early 2', time.time() - start_prog))
                return None ### Early exit for the preparation here.

            prog_name_window = self.settings['Copy']['Extract']
            mount_name = self.settings['Copy']['Copy to work']

            with open(self.shared_dict_typ['list_file'], 'r') as read:
                lines = [
                    entry.strip()
                    for entry in read.readlines()
                    if entry.strip()
                    ]
            lines_to_use = []
            final_lines_to_use = []
            total_n = 0
            n_particles_to_check = int(self.settings[self.prog_name]['Minimum particles'])
            n_classes_to_check = int(self.settings[self.prog_name]['Minimum classes'])

            for line in lines:
                feedback_loop, stack_name, n_particles, class_average_file, n_classes = line.split('|||')
                folder_name = 'auto3d_folder_feedback_{0}'.format(feedback_loop)
                output_classes = '{0}/FILES/CLASSES/best_classes.hdf'.format(self.settings[folder_name])
                if feedback_loop != '0':
                    final_lines_to_use = [line]
                    break

                elif not os.path.exists(output_classes) and volume == 'XXXNoneXXX':
                    to_check = n_classes_to_check
                    current_number = int(n_classes)

                elif os.path.exists(output_classes) or volume != 'XXXNoneXXX':
                    to_check = n_particles_to_check
                    current_number = int(n_particles)

                else:
                    assert False, 'Unreachable code'

                lines_to_use.append(line)
                total_n += current_number
                if total_n >= to_check:
                    final_lines_to_use = lines_to_use
                    break

            if not final_lines_to_use:
                self.queue_com['log'].put(tu.create_log(self.name, 'run_auto3d', root_name_input, 'stop early 2', time.time() - start_prog))
                return None

            current_index = old_index + 1
            log_prefix = os.path.join(
                self.settings[folder_name],
                'AUTOSPHIRE_{0:03d}'.format(current_index),
                )
            submission_on_work = '{0}/submission_script.sh'.format(log_prefix)
            output_stack = os.path.join(
                '{0}_FILES'.format(log_prefix),
                'best_stack.hdf',
                )

            create_classes = False
            if feedback_loop != '0':
                index_list = [1, 3]
                output_list = [output_stack, output_classes]
            elif not os.path.exists(output_classes) and volume == 'XXXNoneXXX':
                create_classes = True
                index_list = [3]
                output_list = [output_classes]
            elif os.path.exists(output_classes) or volume != 'XXXNoneXXX':
                index_list = [1]
                output_list = [output_stack]
            else:
                assert False, 'Unreachable code'

            for index, output in zip(index_list, output_list):
                if os.path.exists(output):
                    os.remove(output)
                cmd = [self.settings['Path']['e2proc2d.py']]
                cmd.extend([entry.split('|||')[index] for entry in final_lines_to_use])
                cmd.append(output)
                cmd = ' '.join(cmd)

                tu.mkdir_p(os.path.dirname(output))

                cur_log_prefix = os.path.dirname(output)
                log_file, err_file = self.run_command(
                    root_name_input=root_name_input,
                    command=cmd,
                    log_prefix='{0}_combine'.format(cur_log_prefix),
                    block_gpu=False,
                    gpu_list=[],
                    shell=False
                    )

                self.copy_extern('Copy_to_work', [output])

                zero_list = [err_file]
                non_zero_list = [log_file]

                tus.check_outputs(
                    zero_list=zero_list,
                    non_zero_list=non_zero_list,
                    exists_list=[],
                    folder=self.settings[folder_name],
                    command=cmd
                    )

            if create_classes:
                assert os.path.exists(output_classes) and volume == 'XXXNoneXXX', 'There should be classes but no volume present at this point of the code'
            else:
                assert os.path.exists(output_classes) or volume != 'XXXNoneXXX', 'There should be classes or a volume present at this point of the code'

            # Remove output directory prior to running the code
            try:
                shutil.rmtree(log_prefix)
            except FileNotFoundError:
                pass
            cmd = []
            cmd.append(self.settings['Path'][self.prog_name])
            cmd.append(log_prefix)
            cmd.append('--dry_run')
            cmd.append('--skip_unblur')
            cmd.append('--skip_cter')
            cmd.append('--skip_cryolo')
            cmd.append('--skip_window')
            cmd.append('--skip_isac2')
            cmd.append('--skip_cinderella')
            cmd.append('--box_size={0}'.format(self.settings[prog_name_window]['--box_size']))
            cmd.append('--radius={0}'.format(self.settings[self.prog_name]['--radius']))

            if self.settings[self.prog_name]['--skip_mask_rviper'] == 'True':
                cmd.append('--skip_mask_rviper')

            if self.settings[self.prog_name]['--skip_meridien'] == 'True':
                cmd.append('--skip_meridien')
                cmd.append('--skip_sharpening_meridien')
                volume = 'SKIP_MERIDIEN'

            if os.path.exists(output_classes) and volume == 'XXXNoneXXX':
                cmd.append('--skip_meridien')
                cmd.append('--skip_sharpening_meridien')
                cmd.append('--rviper_input_stack={0}'.format(output_classes))
                cmd.append('--adjust_rviper_resample={0}'.format(1/old_shrink_ratio))
            elif volume != 'XXXNoneXXX':
                cmd.append('--skip_rviper')
                cmd.append('--skip_adjust_rviper')
                cmd.append('--meridien_input_volume={0}'.format(volume))
            else:
                assert False, 'Unreachable code'

            if self.settings[self.prog_name]['input_mask']:
                cmd.append('--meridien_input_mask={0}'.format(self.settings[self.prog_name]['input_mask']))

            cmd.append('--skip_restack')
            cmd.append('--skip_ctf_refine')
            cmd.append('--meridien_input_stack={0}'.format(output_stack))

            if self.settings[self.prog_name]['--mtf'].strip():
                cmd.append('--mtf={0}'.format(self.settings[self.prog_name]['--mtf']))

            if self.settings[self.prog_name]['--phase_plate'] == 'True':
                cmd.append('--phase_plate')

            if self.settings[self.prog_name]['--rviper_use_final'] == 'True':
                cmd.append('--rviper_use_final')

            ignore_list = []

            ignore_list.append('--phase_plate')
            ignore_list.append('--rviper_use_final')
            ignore_list.append('Use SSH')
            ignore_list.append('Need SSH password')
            ignore_list.append('Run during feedback')
            ignore_list.append('--mtf')
            ignore_list.append('input_volume')
            ignore_list.append('Viper filter frequency')
            ignore_list.append('input_mask')
            ignore_list.append('SSH username')
            ignore_list.append('SSH password')
            ignore_list.append('Minimum classes')
            ignore_list.append('Minimum particles')
            ignore_list.append('--skip_meridien')
            ignore_list.append('--skip_mask_rviper')
            ignore_list.append('--filament_mode')
            if self.settings[self.prog_name]['--filament_mode'] == 'False':
                ignore_list.append('--filament_width')
                ignore_list.append('--helical_rise')

            ignore_key_list = []
            ignore_key_list.append('--rviper_addition')
            ignore_key_list.append('--adjust_rviper_addition')
            ignore_key_list.append('--mask_rviper_addition')
            ignore_key_list.append('--meridien_addition')
            ignore_key_list.append('--sharpening_meridien_addition')

            filter_freq = min(
                float(self.settings[self.prog_name]['--apix']) / old_shrink_ratio / float(self.settings[self.prog_name]['Viper filter frequency']),
                0.5
                )

            tmp = self.settings[self.prog_name]['--rviper_addition']
            self.settings[self.prog_name]['--rviper_addition'] = ' '.join(['--fl={0}'.format(filter_freq), self.settings[self.prog_name]['--rviper_addition']])

            for key in self.settings[self.prog_name]:
                if key in ignore_list:
                    continue
                elif key in ignore_key_list:
                    if self.settings[self.prog_name][key].strip():
                        cmd.append("{0}='{1}'".format(key, self.settings[self.prog_name][key].strip()))
                else:
                    cmd.append(key)
                    cmd.append(
                        '{0}'.format(self.settings[self.prog_name][key])
                        )
            self.settings[self.prog_name]['--rviper_addition'] = tmp

            cmd = ' '.join(cmd)
            log_file, err_file = self.run_command(
                root_name_input=root_name_input,
                command=cmd,
                log_prefix='{0}_create_template'.format(log_prefix),
                block_gpu=False,
                gpu_list=[],
                shell=True
                )

            zero_list = [err_file]
            non_zero_list = [log_file]

            tus.check_outputs(
                zero_list=zero_list,
                non_zero_list=non_zero_list,
                exists_list=[],
                folder=self.settings[folder_name],
                command=cmd
                )

            execute_command = []
            cmd = []
            if self.settings[self.prog_name]['Use SSH'] == 'True':

                device = os.path.dirname(self.settings['Mount'][mount_name]['IP'].lstrip('/'))
                cmd.append('ssh')
                cmd.append('-o')
                cmd.append('StrictHostKeyChecking=no')
                cmd.append('{0}@{1}'.format(
                    self.settings[self.prog_name]['SSH username'],
                    device,
                    ))

                with open(submission_on_work, 'r') as read:
                    content = read.read()
                submission_on_work = '{0}/submission_script_work.sh'.format(log_prefix)
                self.try_write(submission_on_work, 'w', content.replace(
                        '{0}/'.format(self.settings['project_base']),
                        ''
                        ))

                new_file = os.path.join(
                    os.path.dirname(submission_on_work).replace(
                        '{0}/'.format(self.settings['project_base']),
                        ''
                        ),
                    os.path.basename(submission_on_work),
                    )

                execute_command.append('cd')
                execute_command.append('/{0}'.format(os.path.join(
                    self.settings['Mount'][mount_name]['current_folder'],
                    self.settings['Output']['Project name'],
                    )))
                execute_command.append(';')
                execute_command.append('rm -rf')
                execute_command.append(os.path.join(os.path.dirname(new_file), '00*'))
                execute_command.append(';')
                execute_command.append(self.settings[self.prog_name]['--mpi_submission_command'])
                execute_command.append(new_file)
                cmd.append("'{0}'".format(' '.join(execute_command)))
            else:
                new_file = submission_on_work
                execute_command.append('rm -rf')
                execute_command.append(os.path.join(os.path.dirname(new_file), '00*'))
                execute_command.append(';')
                execute_command.append(self.settings[self.prog_name]['--mpi_submission_command'])
                execute_command.append('/'.join([entry for entry in new_file.split('/') if entry]))
                cmd.append("{0}".format(' '.join(execute_command)))

            cmd = ' '.join(cmd)

            copy_files = []
            recursive_file_search(log_prefix, copy_files)
            recursive_file_search('{0}_FILES'.format(log_prefix), copy_files)
            self.copy_extern('Copy_to_work', copy_files)
            self.wait(10)

            if self.settings[self.prog_name]['Use SSH'] == 'True':
                log_file, err_file = tus.get_logfiles('{0}_run_autosphire'.format(log_prefix))
                self.try_write(err_file, 'w', '')
                start_time = time.time()
                log = []
                child = pe.spawnu(cmd)
                idx = child.expect(
                    [
                        "{0}@{1}'s password:".format(
                        self.settings[self.prog_name]['SSH username'],
                        device
                        ),
                        pe.EOF
                        ]
                    )
                log.append(child.before)
                log.append(child.after)
                if idx == 1 and self.settings[self.prog_name]['Need SSH password'] == 'True':
                    print('SSH autoSPHIRE command failed or no password is required!')
                    self.try_write(err_file, 'w', 'SSH autoSPHIRE command failed or no password is required!')
                    self.queue_com['log'].put(tu.create_log(self.name, 'run_auto3d', root_name_input, 'stop early 4', time.time() - start_prog))
                    raise Exception('SSH autoSPHIRE command failed or no password is required!')

                elif idx == 1:
                    child.expect(pe.EOF, timeout=10)

                elif idx == 0 and self.settings[self.prog_name]['Need SSH password'] == 'False':
                    print('SSH autoSPHIRE command failed or no password is required!')
                    self.try_write(err_file, 'w', 'SSH autoSPHIRE command failed or no password is required!')
                    self.queue_com['log'].put(tu.create_log(self.name, 'run_auto3d', root_name_input, 'stop early 4', time.time() - start_prog))
                    raise Exception('SSH autoSPHIRE command failed or no password is required!')

                elif idx == 0:
                    child.sendline(self.settings[self.prog_name]['SSH password'])
                    log.append(child.before)
                    log.append(child.after)
                    child.expect(pe.EOF, timeout=10)

                log.append(cmd)

                stop_time = time.time()
                content = [
                    '\n'.join(map(str, log)),
                    '\nTime: {0} sec'.format(stop_time - start_time),
                    ]
                self.try_write(log_file, 'w', ''.join(content))
            else:
                log_file, err_file = self.run_command(
                    root_name_input=root_name_input,
                    command=cmd,
                    log_prefix='{0}_run_autosphire'.format(log_prefix),
                    block_gpu=False,
                    gpu_list=[],
                    shell=True
                    )

                zero_list = [err_file]
                non_zero_list = [log_file]

                tus.check_outputs(
                    zero_list=zero_list,
                    non_zero_list=non_zero_list,
                    exists_list=[],
                    folder=self.settings[folder_name],
                    command=cmd
                    )

            meridien_dir = '{0}/0002_MERIDIEN'.format(log_prefix)
            meridien_dir = meridien_dir.replace(
                self.settings['Output']['Project directory'],
                os.path.relpath(self.settings['copy_to_work_folder_feedback_0'])
                )

            if volume == 'XXXNoneXXX' and int(feedback_loop) == 0:
                while True:
                    if self.stop.value:
                        raise Exception('Program stopped')

                    if self.settings[self.prog_name]['Use SSH'] == 'True':
                        viper_model = '{0}/0001_RVIPER_ADJUSTMENT/vol3d_ref_moon_eliminated.hdf'.format(log_prefix).replace(
                            self.settings['Output']['Project directory'],
                            os.path.relpath(self.settings['copy_to_work_folder_feedback_0'])
                            )
                        if os.path.isfile(viper_model):
                            new_volume = viper_model.replace(
                                    os.path.join(
                                        self.settings['copy_to_work_folder_feedback_0'],
                                        self.settings['Output']['Project name'],
                                        '',
                                        ),
                                    ''
                                    )
                            break
                    else:
                        viper_model = '{0}/0001_RVIPER_ADJUSTMENT/vol3d_ref_moon_eliminated.hdf'.format(log_prefix)
                        if os.path.isfile(viper_model):
                            new_volume = viper_model
                            break

                    self.wait(10)
            else:
                new_volume = volume

            skip_list = False
            if skip_list:
                pass
            else:
                # Add to queue
                for aim in self.content_settings['aim']:
                    *compare, aim_name = aim.split(':')
                    var = True
                    for typ in compare:
                        name = typ.split('!')[-1]
                        if typ.startswith('!'):
                            if self.settings['Copy'][name] == 'False':
                                continue
                            else:
                                var = False
                                break
                        else:
                            if not self.settings['Copy'][name] == 'False':
                                continue
                            else:
                                var = False
                                break
                    if var:
                        pass
                    else:
                        pass

            self.try_write(self.shared_dict_typ['number_file'], 'w', '|||'.join([str(entry) for entry in [old_shrink_ratio, current_index, new_volume]]))

            if volume != 'XXXNoneXXX':
                with open(self.shared_dict_typ['list_file'], 'r') as read:
                    lines = [
                        entry.strip()
                        for entry in read.readlines()
                        if entry.strip() and entry.strip() not in final_lines_to_use
                        ]

                for entry in final_lines_to_use:
                    self.shared_dict_typ['queue_list'].remove(entry)

                self.try_write(self.shared_dict_typ['list_file'], 'w', '\n'.join(lines) + '\n')

        finally:
            self.shared_dict_typ['queue_list_time'] = time.time()
            self.queue_com['log'].put(tu.create_log(self.name, 'run_auto3d', root_name_input, 'stop process', time.time() - start_prog))
            self.shared_dict_typ['queue_list_lock'].release()

    def copy_extern(self, my_typ, copy_file):
        new_names = []
        for copy_file_name in copy_file:
            mount_folder_name = '{0}_folder_feedback_0'.format(my_typ.lower())
            mount_name = self.settings['Copy'][my_typ]
            try:
                sudo = self.settings['Mount'][mount_name]['Need sudo for copy?']
                protocol = self.settings['Mount'][mount_name]['Protocol']
            except KeyError as e:
                assert mount_name in ('Later', 'False'), (mount_name, e)
                continue
            if self.settings['Output']['Project directory'] != '.':
                new_suffix = os.path.join(
                    os.path.dirname(copy_file_name).replace(
                        self.settings['Output']['Project directory'],
                        ''
                        ),
                    os.path.basename(copy_file_name),
                    )
            else:
                new_suffix = copy_file_name
            new_suffix = new_suffix.split('/')
            new_prefix = os.path.relpath(self.settings[mount_folder_name]).split('/')

            if sudo == 'True':
                copy_method = self.copy_as_another_user
            else:
                copy_method = self.copy_as_user

            if protocol == 'hdd':
                new_name = None
                for hdd_folder in glob.glob(
                        '{0}/*'.format(
                            self.settings[mount_folder_name]
                            )
                        ):
                    if os.path.getsize(copy_file_name) > \
                            shutil.disk_usage(hdd_folder).free:
                        new_name = None
                        continue
                    else:
                        new_name = os.path.join(
                            *new_prefix,
                            os.path.basename(hdd_folder),
                            *new_suffix
                            )
                        break
                if new_name is None:
                    raise IOError('No space on HDD left!')
            else:
                new_name = os.path.join(*new_prefix, *new_suffix)

            new_names.append(new_name)
            copy_method(copy_file_name, new_name)

        return new_names


    def run_copy_extern(self, root_name):
        """
        Copy to Work/Backup/HDD

        root_name - Root name of the file to copy

        Returns:
        None
        """
        root_name_input = root_name
        start_prog = time.time()
        self.queue_com['log'].put(tu.create_log(self.name, 'run_copy_extern', root_name_input, 'start process'))
        dont_tar = False
        if root_name == 'None':
            pass
        elif not self.settings['Copy']['Tar to work'] == 'True' and self.typ == 'Copy_to_work':
            dont_tar = True
        elif not self.settings['Copy']['Tar to backup'] == 'True' and self.typ == 'Copy_to_backup':
            dont_tar = True
        elif not self.settings['Copy']['Tar to hdd'] == 'True' and self.typ == 'Copy_to_hdd':
            dont_tar = True
        elif root_name.endswith('jpg'):
            dont_tar = True
        elif self.settings['tar_folder'] in root_name:
            dont_tar = True
        elif root_name.startswith('bdb:') or root_name.endswith('.bdb'):
            dont_tar = True
        elif root_name.endswith('mrcs'):
            dont_tar = True
        elif os.path.getsize(root_name) > 40 * 1024**2:
            dont_tar = True
        elif os.path.realpath(os.path.dirname(root_name)) == \
                os.path.realpath(self.settings['project_folder']):
            dont_tar = True
        else:
            for entry in self.settings['Copy']['Picking_entries']:
                if entry.replace(' ', '_').replace('>=', '') in root_name:
                    if root_name.endswith('txt'):
                        dont_tar = True
                    elif root_name.endswith('box'):
                        dont_tar = True
                    elif root_name.endswith('cbox'):
                        dont_tar = True

        if root_name.startswith('bdb:') or root_name.endswith('.bdb'):
            if root_name.startswith('bdb:'):
                root_name = os.path.join(
                    os.path.dirname(root_name.replace('bdb:', '')),
                    'EMAN2DB',
                    os.path.basename(root_name.replace('bdb:', ''))
                    )
            root_name = [entry for entry in glob.glob(os.path.join(os.path.dirname(root_name), '*'))]

        if root_name == 'None':
            self.shared_dict_typ['queue_list_lock'].acquire()
            try:
                try:
                    copy_file = [
                        entry
                        for entry in self.shared_dict_typ['queue_list']
                        if self.settings['tar_folder'] in entry
                        ][0]
                except IndexError:
                    self.queue_com['log'].put(tu.create_log(self.name, 'run_copy_extern', root_name_input, 'stop early 1', time.time() - start_prog))
                    return None
                if not os.path.exists(copy_file):
                    self.shared_dict_typ['queue_list_time'] = time.time()
                    self.queue_com['log'].put(tu.create_log(self.name, 'run_copy_extern', root_name_input, 'stop early 2', time.time() - start_prog))
                    return None

                self.shared_dict_typ['queue_list'].remove(copy_file)
                self.remove_from_queue_file(
                    copy_file,
                    self.shared_dict_typ['list_file'],
                    lock=False
                    )
            finally:
                self.shared_dict_typ['queue_list_lock'].release()

        elif dont_tar:
            copy_file = root_name

        else:
            self.shared_dict_typ['queue_list_lock'].acquire()
            try:
                try:
                    tar_file = [
                        entry
                        for entry in self.shared_dict_typ['queue_list']
                        if self.settings['tar_folder'] in entry and \
                        self.name in entry
                        ][0]
                except IndexError:
                    tar_file = os.path.join(
                        self.settings['tar_folder'],
                        '{0}_{1:06d}.tar'.format(self.name, self.shared_dict_typ['tar_idx'])
                        )
                    self.shared_dict_typ['queue_list'].append(tar_file)
                    self.add_to_queue_file(
                        root_name=tar_file,
                        file_name=self.shared_dict_typ['list_file'],
                        )
                    self.shared_dict_typ['tar_idx'] += 1
            finally:
                self.shared_dict_typ['queue_list_lock'].release()

            if not isinstance(root_name, list):
                root_name = [root_name]
            root_name = [entry for entry in root_name if os.path.isfile(entry)]

            with tarfile.open(tar_file, 'a') as tar:
                for entry in root_name:
                    tar.add(
                        entry,
                        arcname=os.path.join('..', entry.replace(self.settings['project_folder'], ''))
                        )

            self.shared_dict_typ['queue_list_lock'].acquire()
            try:
                if os.path.getsize(tar_file) > float(self.settings['Copy']['Tar size (Gb)']) * 1024**3:
                    copy_file = tar_file
                    self.shared_dict_typ['tar_idx'] += 1
                    new_tar_file = os.path.join(
                        self.settings['tar_folder'],
                        '{0}_{1:06d}.tar'.format(self.name, self.shared_dict_typ['tar_idx'])
                        )

                    self.shared_dict_typ['queue_list'].remove(copy_file)
                    self.remove_from_queue_file(
                        tar_file,
                        self.shared_dict_typ['list_file'],
                        lock=False
                        )
                    self.shared_dict_typ['queue_list'].append(new_tar_file)
                    self.add_to_queue_file(
                        root_name=new_tar_file,
                        file_name=self.shared_dict_typ['list_file'],
                        )
                else:
                    self.shared_dict_typ['queue_list_time'] = time.time()
                    self.queue_com['log'].put(tu.create_log(self.name, 'run_copy_extern', root_name_input, 'stop early 3', time.time() - start_prog))
                    return None
            finally:
                self.shared_dict_typ['queue_list_lock'].release()

        if not isinstance(copy_file, list):
            copy_file = [copy_file]

        self.copy_extern(self.typ, copy_file)

        self.shared_dict_typ['queue_list_time'] = time.time()
        self.queue_com['log'].put(tu.create_log(self.name, 'run_copy_extern', root_name_input, 'stop process', time.time() - start_prog))

    @staticmethod
    def get_hash(file_in, chunksize=1024**2):
        length = 0
        hashes = []
        with open(file_in, 'rb') as read:
            while True:
                data = read.read(chunksize)
                if not data:
                    break
                else:
                    length += len(data)
                    hashes.append(hash(data))
        return length, hash(tuple(hashes))

    def copy_as_user(self, file_in, file_out):
        """
        Copy to another device.

        file_in - Input file path
        file_out - Output file path

        Returns:
        None
        """
        self.check_ready_for_copy(file_out=file_out)

        tu.mkdir_p(os.path.dirname(file_out))
        counter = 0

        do_checksum = os.path.split(file_in)[0] != self.settings['project_folder']
        if do_checksum:
            len_data_in, checksum_in = self.get_hash(file_in)

        while True:
            tu.copy(file_in, file_out)
            if not do_checksum:
                break

            len_data_out, checksum_out = self.get_hash(file_out)

            if len_data_in == len_data_out:
                if checksum_in == checksum_out:
                    break
                elif counter == 5:
                    #print('PROBLEM', counter, file_in, file_out, checksum_in, checksum_out, len_data_out, len_data_in)
                    raise Exception('PROBLEM')
                else:
                    #print('PROBLEM', counter, file_in, file_out, checksum_in, checksum_out, len_data_out, len_data_in)
                    counter += 1
            elif counter == 5:
                #print('PROBLEM', counter, file_in, file_out, checksum_in, checksum_out, len_data_out, len_data_in)
                raise Exception('PROBLEM')
            else:
                #print('PROBLEM', counter, file_in, file_out, checksum_in, checksum_out, len_data_out, len_data_in)
                counter += 1


    def check_ready_for_copy(self, file_out):
        """
        Check, if the current file is ready to copy.

        file_out - File to copy

        Returns:
        True, if ready
        """
        return True

    def copy_as_another_user(self, file_in, file_out):
        """
        Copy to device as another user via sudo.

        file_in - Input file path
        file_out - Output file path

        Returns:
        None
        """
        self.check_ready_for_copy(file_out=file_out)

        self.mkdir_p_as_another_user(folder=os.path.dirname(file_out))


        counter = 0
        do_checksum = os.path.split(file_in)[0] != self.settings['project_folder']
        if do_checksum:
            with open(file_in, 'rb') as read:
                content = read.read()
            checksum_in = hash(content)
            len_data_in = len(content)

        while True:
            command = 'sudo -k -S -u {0} rsync {1} {2}'.format(
                self.user,
                file_in,
                file_out
                )
            child = pe.spawnu(command)
            child.sendline(self.password)
            child.expect(pe.EOF)

            if 'rsync:' in child.before:
                text = child.before.replace(self.password, 'PASSWORD')
                raise IOError(
                    'Cannot copy file: {0}! {1}'.format(file_out, text)
                    )
            else:
                pass

            if not do_checksum:
                break

            with open(file_out, 'rb') as read:
                content = read.read()
            len_data_out = len(content)
            checksum_out = hash(content)

            if len_data_in == len_data_out:
                if checksum_in == checksum_out:
                    break
                elif counter == 5:
                    print('PROBLEM', counter, file_in, file_out)
                    raise IOError('PROBLEM')
                else:
                    print('PROBLEM', counter, file_in, file_out)
                    counter += 1
            else:
                print('PROBLEM', counter, file_in, file_out)
                counter += 1

    def mkdir_p_as_another_user(self, folder):
        """
        Create folders recursively as another user with the help of sudo.

        folder - Folder structure to create

        Returns:
        None
        """
        command = 'sudo -k -S -u {0} mkdir -p {1}'.format(self.user, folder)
        child = pe.spawnu(command)
        child.sendline(self.password)
        child.expect(pe.EOF)
        if 'mkdir:' in child.before:
            text = child.before.replace(self.password, 'PASSWORD')
            raise IOError(
                'Cannot create directory: {0}! {1}'.format(folder, text)
                )
        else:
            pass

    def run_command(self, command, log_prefix, block_gpu, gpu_list, shell, file_to_delete=None, root_name_input='INVALID'):
        """
        Run the command with respect to the gpu list.

        command - Command to run
        block_gpu - Block the GPU
        gpu_list - List of GPUs to use
        settings - Transphire settings

        Return:
        log_file name, err_file name
        """
        log_file, err_file = tus.get_logfiles(log_prefix)

        mutex_idx = 0
        count_idx = 1

        if gpu_list:
            gpu_list = [
                (entry.split('_')[0], entry)
                if '_' in entry
                else
                (entry, entry)
                for entry in sorted(gpu_list)
                ]

            for main, entry in gpu_list:
                if '_' in entry:
                    self.shared_dict['gpu_lock'][main][mutex_idx].acquire()
                self.shared_dict['gpu_lock'][entry][mutex_idx].acquire()

            for main, entry in gpu_list:
                if '_' in entry:
                    with self.shared_dict['gpu_lock'][main][count_idx].get_lock():
                        self.shared_dict['gpu_lock'][main][count_idx].value += 1
                    self.shared_dict['gpu_lock'][main][mutex_idx].release()
                else:
                    while self.shared_dict['gpu_lock'][main][count_idx].value != 0:
                        self.wait(0.05)

        try:
            if self.abort.value:
                raise UserWarning('STOP: abort')

            # Run the command
            self.delete_file_to_delete(file_to_delete)

            self.queue_com['log'].put(tu.create_log(self.name, 'run_command', root_name_input, 'start program'))
            while True:
                self.try_write(log_file, 'w', '{}\n'.format(command))
                with open(log_file, 'a') as out:
                    with open(err_file, 'w') as err:
                        start_time = time.time()
                        self.delete_file_to_delete(file_to_delete)
                        stop_time = time.time()
                        if shell:
                            command_popen = command
                        else:
                            command_popen = command.split()
                        cmd = sp.Popen(
                            command_popen,
                            shell=shell,
                            stdout=out,
                            stderr=err,
                            preexec_fn=os.setsid
                            )
                        self.delete_file_to_delete(file_to_delete)
                        while cmd.poll() is None:
                            if self.abort.value:
                                os.killpg(
                                    os.getpgid(cmd.pid),
                                    signal.SIGTERM
                                    )
                                break
                            self.wait(1)

                self.delete_file_to_delete(file_to_delete)
                stop_time = time.time()
                self.try_write(log_file, 'a', '\nTime: {0} sec'.format(stop_time - start_time)) 
                if self.abort.value:
                    raise UserWarning('STOP: abort')
                with open(err_file, 'r') as err:
                    if 'Error: All GPUs are in use, quit.' in err.read():
                        continue
                break

            self.queue_com['log'].put(
                tu.create_log(
                    self.name,
                    'run_command',
                    root_name_input,
                    'stop program'
                    )
                )

            self.delete_file_to_delete(file_to_delete)

        finally:
            if gpu_list:
                for main, entry in gpu_list:
                    if '_' in entry:
                        with self.shared_dict['gpu_lock'][main][count_idx].get_lock():
                            self.shared_dict['gpu_lock'][main][count_idx].value -= 1
                    self.shared_dict['gpu_lock'][entry][mutex_idx].release()

        return log_file, err_file

    @staticmethod
    def delete_file_to_delete(file_to_delete):
        if file_to_delete is not None:
            time.sleep(0.1)
            try:
                os.remove(file_to_delete)
            except FileNotFoundError:
                pass
            except PermissionError:
                with open(file_to_delete, 'w'):
                    pass
            time.sleep(0.1)

    def send_out_of_range_error(self, warning, file_name, error_type):
        message_const = 'If this is not the only message, you might consider changing microscope settings!'

        if error_type == 'warning':
            message_notification = '{0}: Subsequent parameters out of range!'.format(self.name)
            message_error = 'The median of the last {0} values for parameter {1} is {2}, which is not in the range: {3} to {4}!'.format(
                self.settings['Notification']['Nr. of values used for median'],
                warning[0],
                warning[1],
                warning[2],
                warning[3]
                )
        elif error_type == 'skip':
            message_notification = '{0}: Parameter out of range!'.format(self.name)
            message_error = 'The parameter {0} is {1} for file {2}, which is not in the range: {3} to {4} and will be skipped!'.format(
                warning[0],
                warning[1],
                file_name,
                warning[2],
                warning[3]
                )
        else:
            assert True
        message_notification = '\n'.join([message_notification, message_const])
        message_error = '\n'.join([message_error, message_const])
        if time.time() - self.time_last_error > 1800:
            self.queue_com['notification'].put(message_notification)
            self.queue_com['error'].put(message_error)
            self.time_last_error = time.time()
        else:
            pass
        self.write_error(msg=message_error, root_name=file_name)

    def create_combines(self, combine_list):
        for file_lock, in_file, out_file in combine_list:
            file_lock.acquire()
            try:
                with open(in_file, 'r') as read:
                    if not os.path.exists(out_file):
                        lines = read.readlines()
                    else:
                        lines = read.readlines()[-1]
                self.try_write(out_file, 'a+', ''.join(lines))
            finally:
                file_lock.release()
            self.file_to_distribute(file_name=in_file)
            self.file_to_distribute(file_name=out_file)

    @staticmethod
    @tu.rerun_function_in_case_of_error
    def try_write(file_name, opener, content):
        with open(file_name, opener) as write:
            write.write(content)
