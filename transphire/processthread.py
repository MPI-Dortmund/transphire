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
import time
import os
import re
import shutil as sh
import traceback as tb
import glob
import copy
import tarfile
import subprocess as sp
import numpy as np
import pexpect as pe
try:
    from PyQt4.QtCore import QThread
except ImportError:
    from PyQt5.QtCore import QThread
from transphire import transphire_utils as tu
from transphire import transphire_software as tus
from transphire import transphire_motion as tum
from transphire import transphire_ctf as tuc
from transphire import transphire_picking as tup


class ProcessThread(QThread):
    """
    Worker thread

    Inherits from:
    QThread

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
        super(ProcessThread, self).__init__(parent)
        # Variables
        self.stop = stop
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

        self.queue = shared_dict['queue'][self.content_settings['name']]
        self.shared_dict_typ = shared_dict['typ'][self.content_settings['name']]
        self.queue_lock = self.shared_dict_typ['queue_lock']

        try:
            self.later = bool(self.settings['Copy'][self.typ] == 'Later')
        except KeyError:
            self.later = False

        try:
            self.user = self.settings['{0}_user'.format(self.typ)]
        except KeyError:
            self.user = None

        self.queue_com['status'].put(['Starting', [], name, '#fff266'])

    def run(self):
        """
        Run the thread.

        Arguments:
        None

        Return:
        None
        """
        # Current time
        self.time_last = time.time()
        self.time_last_error = time.time()
        self.notification_send = False

        # Event loop
        while not self.stop:
            if self.done:
                while not self.stop:
                    self.queue_com['status'].put([
                        'Finished',
                        [],
                        self.name,
                        '#d9d9d9'
                        ])
                    QThread.sleep(10)
                continue
            else:
                pass

            if not self.run_this_thread:
                while not self.stop:
                    self.queue_com['status'].put([
                        'Skipped',
                        [self.queue.qsize()],
                        self.name,
                        '#d9d9d9'
                        ])
                    QThread.sleep(10)
                continue
            else:
                pass

            if self.later:
                while not self.stop:
                    self.queue_com['status'].put([
                        'Later',
                        [self.queue.qsize()],
                        self.name,
                        '#d9d9d9'
                        ])
                    QThread.sleep(10)
                continue
            else:
                pass

            if self.check_quota():
                pass
            else:
                self.queue_com['status'].put([
                    'Quota Error',
                    [self.queue.qsize()],
                    self.name,
                    '#ff5c33'
                    ])
                QThread.sleep(10)
                continue

            if self.check_connection():
                pass
            else:
                self.queue_com['status'].put([
                    'Connection Error',
                    [self.queue.qsize()],
                    self.name,
                    '#ff5c33'
                    ])
                QThread.sleep(10)
                continue

            if self.check_full():
                pass
            else:
                self.queue_com['status'].put([
                    'No space Error',
                    [self.queue.qsize()],
                    self.name,
                    '#ff5c33'
                    ])
                QThread.sleep(10)
                continue

            if self.shared_dict_typ['delay_error']:
                QThread.sleep(10)
                self.shared_dict_typ['delay_error'] = False

            if self.shared_dict_typ['unknown_error']:
                time_diff = time.time() - self.time_last
                if self.typ == 'Find':
                    self.queue_com['status'].put([
                        'Unknown Error',
                        ['{0:.1f} min'.format(time_diff / 60)],
                        self.name,
                        '#ff5c33'
                        ])
                else:
                    self.queue_com['status'].put([
                        'Unknown Error',
                        [
                            self.queue.qsize(),
                            self.shared_dict_typ['file_number'],
                            '{0:.1f} min'.format(time_diff / 60)
                            ],
                        self.name,
                        '#ff5c33'
                        ])
                i = 0
                while i < 6:
                    QThread.sleep(10)
                    if self.stop:
                        break
                    else:
                        i += 1
                self.shared_dict_typ['unknown_error'] = False
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
            if self.later:
                pass
            elif not self.run_this_thread:
                pass
            else:
                self.is_running = True
                if self.typ not in ('Find', 'Meta'):
                    self.start_queue(clear_list=True)
                self.is_running = False

        # Print, if stopped
        self.queue_com['status'].put(['STOPPED', [], self.name, '#ff5c33'])
        print(self.name, ': Stopped')

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
        if self.typ in ['Copy_work', 'Copy_backup', 'Copy_hdd']:
            return True
        else:
            pass

        for stop, folder in zip(
                [project_stop, scratch_stop],
                ['project_folder', 'scratch_folder']
                ):
            try:
                total_quota = sh.disk_usage(self.settings[folder]).total / 1e12
                used_quota = sh.disk_usage(self.settings[folder]).used / 1e12
            except FileNotFoundError:
                self.stop = True
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
                self.stop = True
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
            ['lost_input_frames', 'Search path frames'],
            ['lost_input_meta', 'Search path meta'],
            ['lost_work', 'Copy_work_folder'],
            ['lost_backup', 'Copy_backup_folder'],
            ['lost_hdd', 'Copy_hdd_folder']
            ]
        for process, folder in processes:
            if self.shared_dict_typ[process]:
                time_diff = time.time() - self.time_last
                if folder == 'Search path frames' or \
                        folder == 'Search path meta':
                    output_folder = self.settings['General'][folder]
                else:
                    output_folder = self.settings[folder]

                self.queue_com['status'].put([
                    'Lost connection',
                    ['{0:.1f} min'.format(time_diff / 60)],
                    self.name,
                    '#ff5c33'
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
        folder = self.settings['General']['Search path meta']
        if folder:
            self.queue_com['status'].put([
                'Copy Metadata',
                [],
                self.name,
                'lightgreen'
                ])
            try:
                self.run_software_meta(directory=folder)
            except FileNotFoundError:
                self.stop = True
                message_notification = '\n'.join([
                    'Folder no longer available!',
                    '{0} is stopping now!'.format(self.name)
                    ])
                message_error = '\n'.join([
                    '{0} no longer available!'.format(
                        folder.replace('_', ' ')
                        ),
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
            'Running',
            ['{0:.1f} min'.format(time_diff / 60)],
            self.name,
            'lightgreen'
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
                self.queue_com['notification'].put(message_notification)
                if time.time() - self.time_last_error > 1800:
                    self.queue_com['error'].put(message_error)
                    self.time_last_error = time.time()
                else:
                    pass
                self.shared_dict_typ['unknown_error'] = True
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
        QThread.sleep(20)

    def start_queue(self, clear_list):
        """
        Start pipeline processes.

        Arguments:
        None

        Return:
        None
        """
        self.queue_lock.lock()
        error = False
        dummy = False
        try:
            if clear_list:
                dummy = True
                self.shared_dict_typ['queue_list_time'] -= 60
            else:
                if self.queue.empty():
                    self.queue_com['status'].put([
                        'Waiting',
                        [
                            self.queue.qsize(),
                            self.shared_dict_typ['file_number']
                            ],
                        self.name,
                        '#ffc14d'
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
            self.queue_lock.unlock()

        if error:
            QThread.sleep(5)
            return None
        else:
            pass

        # Get new file
        self.queue_lock.lock()
        try:
            self.queue_com['status'].put([
                'Running',
                [
                    self.queue.qsize(),
                    self.shared_dict_typ['file_number']
                    ],
                self.name,
                'lightgreen'
                ])
            if dummy:
                root_name = 'None'
            else:
                root_name = self.remove_from_queue()
        except Exception:
            return None
        finally:
            self.queue_lock.unlock()

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
            'Compress': {
                'method': self.run_compress,
                'lost_connect': 'full_transphire'
                },
            'Copy_work': {
                'method': self.run_copy_extern,
                'lost_connect': 'full_work'
                },
            'Copy_backup': {
                'method': self.run_copy_extern,
                'lost_connect': 'full_backup'
                },
            'Copy_hdd': {
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
                self.queue_com['notification'].put(message_notification)
                if time.time() - self.time_last_error > 1800:
                    self.queue_com['error'].put(message_error)
                    self.time_last_error = time.time()
                else:
                    pass
                self.shared_dict_typ['unknown_error'] = True
            else:
                pass
        except IOError:
            if not dummy:
                self.add_to_queue(aim=self.typ, root_name=root_name)
            self.write_error(msg=tb.format_exc(), root_name=root_name)
            self.lost_connection(
                typ=method_dict[self.typ]['lost_connect']
                )
            self.shared_dict_typ['delay_error'] = True
        except UserWarning:
            if not dummy:
                self.add_to_queue(aim=self.typ, root_name=root_name)
            self.write_error(msg=tb.format_exc(), root_name=root_name)
            self.stop = True
            self.shared_dict_typ['delay_error'] = True
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
                self.queue_com['notification'].put(message_notification)
                if time.time() - self.time_last_error > 1800:
                    self.queue_com['error'].put(message_error)
                    self.time_last_error = time.time()
                else:
                    pass
                self.shared_dict_typ['unknown_error'] = True
            else:
                pass
        else:
            if not dummy:
                self.remove_from_queue_file(root_name, self.shared_dict_typ['save_file'])

                self.queue_lock.lock()
                try:
                    self.add_to_queue_file(
                        root_name=root_name,
                        file_name=self.shared_dict['typ'][self.typ]['done_file'],
                        )
                    self.check_queue_files(root_name=root_name)
                finally:
                    self.queue_lock.unlock()

                if self.typ == 'Import':
                    pass
                else:
                    self.queue_lock.lock()
                    try:
                        self.shared_dict_typ['file_number'] += 1
                    finally:
                        self.queue_lock.unlock()

    def check_queue_files(self, root_name):
        if self.settings['Copy']['Delete stack after compression?'] == 'True':
            basename = os.path.basename(os.path.splitext(root_name)[0])
            delete_stack = True

            for key in self.shared_dict['typ']:
                if key.startswith('Copy_'):
                    continue
                with open(self.shared_dict['typ'][key]['save_file']) as read:
                    if basename in read.read():
                        delete_stack = False

            if delete_stack:
                stack_mrc = os.path.join(self.settings['stack_folder'], '{0}.mrc'.format(basename))
                for key in self.shared_dict['typ']:
                    if not key.startswith('Copy_'):
                        continue
                    with open(self.shared_dict['typ'][key]['save_file']) as read:
                        if stack_mrc in read.read():
                            delete_stack = False
                if delete_stack:
                    try:
                        os.remove(stack_mrc)
                    except:
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
        self.shared_dict_typ['error_lock'].lock()
        try:
            local = time.localtime()
            print('\n{0}/{1}/{2}-{3}:{4}:{5}\t'.format(*local[0:6]))
            print(root_name)
            print('New error message in error file: {0}'.format(
                self.shared_dict_typ['error_file']
                ))
            with open(self.shared_dict_typ['error_file'], 'a') as append:
                append.write('{0}/{1}/{2}-{3}:{4}:{5}\t'.format(*local[0:6]))
                append.write('{0}\n'.format(self.typ))
                append.write('{0}\n'.format(root_name))
                if self.password:
                    append.write('{0}\n\n\n'.format(
                        str(msg).replace(self.password, 'SUDOPASSWORD')
                        ))
                else:
                    append.write('{0}\n\n\n'.format(str(msg)))
        finally:
            self.shared_dict_typ['error_lock'].unlock()

    def remove_from_queue(self):
        """
        Remove item from queue.

        Arguments:
        None

        Return:
        Name removed from the queue.
        """
        value = self.queue.get(block=False)
        QThread.msleep(100)
        return value

    @staticmethod
    def add_to_queue_file(root_name, file_name):
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
                is_present = bool(root_name in read.read())
        except FileNotFoundError:
            pass

        if not is_present:
            with open(file_name, 'a') as append:
                append.write('{0}\n'.format(root_name))
        else:
            pass

    def add_to_queue(self, aim, root_name):
        """
        Add item to queue.

        Arguments:
        aim - Aim queue
        root_name - Name to add

        Return:
        None
        """
        self.shared_dict['typ'][aim]['queue_lock'].lock()
        try:
            self.shared_dict['queue'][aim].put(root_name, block=False)
            self.add_to_queue_file(
                root_name=root_name,
                file_name=self.shared_dict['typ'][aim]['save_file']
                )
            QThread.msleep(100)
        finally:
            self.shared_dict['typ'][aim]['queue_lock'].unlock()

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
        self.queue_com['notification'].put(message_notification)
        if time.time() - self.time_last_error > 1800:
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
            self.queue_lock.lock()
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

            with open(file_name, 'w') as write:
                write.write('{0}\n'.format('\n'.join(useable_lines)))
        finally:
            if lock:
                self.queue_lock.unlock()

    def run_software_meta(self, directory):
        """
        Copy meta files produces by the collection software.

        Arguments:
        directory - Start directory for recursive search.

        Return:
        None
        """
        file_list = []
        file_list = self.recursive_search(
            directory=directory,
            file_list=file_list,
            find_meta=True
            )

        for entry in file_list:
            if self.stop:
                break
            else:
                pass
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


    def run_find(self):
        """
        Find files

        Arguments:
        None

        Return:
        None
        """
        self.queue_lock.lock()
        file_list = []
        try:
            file_list = self.recursive_search(
                directory=self.settings['General']['Search path meta'],
                file_list=file_list,
                find_meta=False
                )
        finally:
            self.queue_lock.unlock()

        data = np.empty(
            len(file_list),
            dtype=[('root', '|U1200'), ('date', '<i8'), ('time', '<i8')]
            )

        for idx, root_name in enumerate(file_list):
            hole, grid_number, spot1, spot2, date, time = \
                tus.extract_time_and_grid_information(
                    root_name=root_name,
                    settings=self.settings,
                    queue_com=self.queue_com,
                    name=self.name
                    )
            del spot1, spot2, hole, grid_number
            data[idx]['root'] = root_name
            data[idx]['date'] = int(date)
            data[idx]['time'] = int(time)

        data = np.sort(data, order=['date', 'time'])
        for root_name in data['root']:
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
                    self.add_to_queue(
                        aim=aim_name,
                        root_name=root_name
                        )
                else:
                    pass

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
            if self.stop:
                break
            elif os.path.isdir(entry_dir):
                file_list = self.recursive_search(
                    directory=entry_dir,
                    file_list=file_list,
                    find_meta=find_meta
                    )
            elif find_meta:
                if os.path.isfile(entry_dir) and 'Data' not in entry_dir:
                    file_list.append(entry_dir)
                else:
                    continue
            elif os.path.isfile(entry_dir) and \
                    'Data' in entry_dir and \
                    entry_dir.endswith('.jpg'):
                root_name = entry_dir[:-len('.jpg')]
                self.shared_dict_typ['bad_lock'].lock()
                try:
                    if root_name in self.shared_dict['bad'][self.typ]:
                        continue
                    else:
                        pass
                finally:
                    self.shared_dict_typ['bad_lock'].unlock()

                frames_root = root_name.replace(
                    self.settings['General']['Search path meta'],
                    self.settings['General']['Search path frames'],
                    )
                compare_name = frames_root[:-len('_19911213_2019')]

                frames = tus.find_frames(
                    frames_root=frames_root,
                    compare_name=compare_name,
                    settings=self.settings,
                    queue_com=self.queue_com,
                    name=self.name,
                    write_error=self.write_error
                    )
                if frames is None:
                    self.shared_dict_typ['bad_lock'].lock()
                    try:
                        if root_name not in self.shared_dict['bad'][self.typ]:
                            self.shared_dict['bad'][self.typ].append(root_name)
                        else:
                            pass
                    finally:
                        self.shared_dict_typ['bad_lock'].unlock()
                    continue
                elif not frames:
                    continue
                else:
                    pass

                self.shared_dict['typ'][self.content_settings['group']]['share_lock'].lock()
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
                    self.shared_dict['typ'][self.content_settings['group']]['share_lock'].unlock()
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
        frames_root = root_name.replace(
            self.settings['General']['Search path meta'],
            self.settings['General']['Search path frames'],
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
                return None
            else:
                pass
        else:
            message = '{0}: No frames found! If this appears very often, please restart TranSPHIRE.'.format(self.name)
            self.queue_com['notification'].put(message)
            self.write_error(msg=message, root_name=root_name)
            raise Exception(message)

        if overall_file_size > \
                sh.disk_usage(self.settings['project_folder']).free:
            self.stop = True
            message = '{0}: Not enough space in project folder'.format(
                self.name
                )
            self.queue_com['notification'].put(message)
            raise IOError(message)
        else:
            pass

        self.shared_dict_typ['count_lock'].lock()
        try:
            self.shared_dict_typ['file_number'] += 1
            with open(self.shared_dict_typ['number_file'], 'w') as write:
                write.write(str(self.shared_dict_typ['file_number']))
            if self.settings['General']['Rename micrographs'] == 'True':
                new_name_stack = '{0}/{1}{2:0{3}d}{4}'.format(
                    self.settings['stack_folder'],
                    self.settings['General']['Rename prefix'],
                    self.shared_dict_typ['file_number'],
                    len(self.settings['General']['Estimated mic number']),
                    self.settings['General']['Rename suffix']
                    )
                new_name_meta = '{0}/{1}{2:0{3}d}{4}'.format(
                    self.settings['meta_folder'],
                    self.settings['General']['Rename prefix'],
                    self.shared_dict_typ['file_number'],
                    len(self.settings['General']['Estimated mic number']),
                    self.settings['General']['Rename suffix']
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
            self.shared_dict_typ['count_lock'].unlock()

        if os.path.exists('{0}.jpg'.format(new_name_meta)):
            self.stop = True
            if os.path.exists(self.shared_dict_typ['done_file']):
                self.queue_lock.lock()
                try:
                    with open(self.shared_dict_typ['done_file'], 'r') as read:
                        self.shared_dict_typ['file_number'] = len(read.readlines())
                finally:
                    self.queue_lock.unlock()
            else:
                self.shared_dict_typ['file_number'] = int(
                    self.settings['General']['Start number']
                    )
            message = '{0}: Filenumber {1} already exists!\n'.format(
                self.name,
                self.shared_dict_typ['file_number']
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

        command = '{0} {1} {2}'.format(
            command_raw,
            ' '.join(frames),
            new_stack
            )

        log_file, err_file = self.run_command(
            command=command,
            log_prefix=new_name_stack,
            block_gpu=False,
            gpu_list=[],
            shell=False
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
            elif extension == 'mrc':
                name = '{0}_krios_sum'.format(new_name_meta)
            elif extension == 'dm4' and 'gain' in file_entry:
                name = '{0}_gain'.format(new_name_meta)
            elif extension == 'xml' and file_entry in meta_files:
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

            tu.copy('{0}'.format(file_entry), new_file)
            log_files.append(new_file)

        tus.check_outputs(
            zero_list=[],
            non_zero_list=log_files,
            exists_list=[],
            folder=self.settings['meta_folder'],
            command='copy'
            )

        log_files.extend([log_file, err_file])

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
                if '!Compress' in compare or \
                        'Compress' in compare or \
                        'Motion' in compare or \
                        'CTF_frames' in compare:
                    self.add_to_queue(aim=aim_name, root_name=new_stack)
                else:
                    for log_file in log_files:
                        self.add_to_queue(aim=aim_name, root_name=log_file)
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

        QThread.sleep(1)
        self.shared_dict['typ'][self.content_settings['group']]['share_lock'].lock()
        try:
            self.shared_dict['share'][self.content_settings['group']].remove(root_name)
        finally:
            self.shared_dict['typ'][self.content_settings['group']]['share_lock'].unlock()


    def already_in_translation_file(self, root_name):
        """
        Check, if the root_name already exists in the translation file.

        root_name - root_name

        Returns:
        True, if root_name in translation file.
        """
        check_list = []
        try:
            for name in ('Translation_file.txt', 'Translation_file_bad.txt'):
                self.shared_dict['translate_lock'].lock()
                try:
                    content_translation_file = np.genfromtxt(
                        os.path.join(
                            self.settings['project_folder'],
                            name
                            ),
                        usecols=0,
                        dtype=str
                        )
                finally:
                    self.shared_dict['translate_lock'].unlock()
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
        file_name = os.path.join(
            self.settings['project_folder'],
            'Translation_file.txt'
            )
        file_name_bad = os.path.join(
            self.settings['project_folder'],
            'Translation_file_bad.txt'
            )
        self.shared_dict['translate_lock'].lock()
        try:
            with open(file_name, 'r') as read:
                good_lines = []
                bad_lines = []
                for line in read.readlines():
                    if root_name in line:
                        bad_lines.append(line)
                    else:
                        good_lines.append(line)

            with open(file_name, 'w') as write:
                write.write(''.join(good_lines))

            with open(file_name_bad, 'a') as write:
                write.write(''.join(bad_lines))

        finally:
            self.shared_dict['translate_lock'].unlock()

        self.file_to_distribute(file_name=file_name)
        self.file_to_distribute(file_name=file_name_bad)

    def file_to_distribute(self, file_name):
        for copy_name in ('work', 'HDD', 'backup'):
            copy_type = 'Copy_{0}'.format(copy_name.lower())
            if not self.settings['Copy']['Copy to {0}'.format(copy_name)] == 'False':
                self.add_to_queue(aim=copy_type, root_name=file_name)
            else:
                pass

    def append_to_translate(self, root_name, new_name, xml_file):
        """
        Write to the translation file.

        root_name - Root name of the file
        new_name - New name of the file
        xml_file - XML file that contains meta data information

        Returns:
        None
        """
        file_name = os.path.join(
            self.settings['project_folder'],
            'Translation_file.txt'
            )
        file_name_bad = os.path.join(
            self.settings['project_folder'],
            'Translation_file_bad.txt'
            )

        if os.path.exists(file_name):
            first_entry = []
        else:
            first_entry = [
                '_pipeRootName',
                '_pipeNewName',
                '_pipeHoleNumber',
                '_pipeSpotNumber',
                '_pipeDate',
                '_pipeTime',
                '_pipeGridNumber',
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
                with open(
                        '{0}/.spot_dict'.format(
                            self.settings['project_folder']
                            ),
                        'a'
                        ) as append:
                    append.write('{0}\t{1}\n'.format(
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
            else:
                try:
                    with open(xml_file, 'r') as read:
                        lines = read.read()
                except IOError:
                    pass
                else:
                    xml_values = {
                        '_pipeCoordX': [r'.*<X>(.*?)</X>.*'],
                        '_pipeCoordY': [r'.*<Y>(.*?)</Y>.*'],
                        '_pipeCoordZ': [r'.*<Z>(.*?)</Z>.*'],
                        '_pipeDefocusMicroscope': [r'.*<Defocus>(.*?)</Defocus>.*'],
                        '_pipeAppliedDefocusMicroscope': [r'.*<a:Key>AppliedDefocus</a:Key><a:Value .*?>(.*?)</a:Value>.*'],
                        '_pipeDose': [r'.*<a:Key>Dose</a:Key><a:Value .*?>(.*?)</a:Value>.*'],
                        '_pipePixelSize': [r'.*<pixelSize><x><numericValue>(.*?)</numericValue>.*'],
                        '_pipeNrFractions': [r'.*<b:NumberOffractions>(.*?)</b:NumberOffractions>.*', r'<b:StartFrameNumber>'],
                        '_pipeExposureTime': [r'.*<camera>.*?<ExposureTime>(.*?)</ExposureTime>.*'],
                        '_pipeHeight': [r'.*<ReadoutArea.*?<a:height>(.*?)</a:height>.*'],
                        '_pipeWidth': [r'.*<ReadoutArea.*?<a:width>(.*?)</a:width>.*'],
                        }
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
                            first_entry.append(xml_key)
                        else:
                            pass

                        if error:
                            print('Attribute {0} not present in the XML file, please contact the TranSPHIRE authors'.format(xml_key))
                        else:
                            pass

        except ValueError:
            if first_entry:
                first_entry = [
                    '_pipeRootName',
                    '_pipeRootDir',
                    '_pipeNewName'
                    ]
            else:
                pass
            entries = [
                os.path.basename(root_name),
                os.path.dirname(root_name),
                new_name
                ]

        template = '{0}\n'
        with open(file_name, 'a') as write:
            if first_entry:
                write.write(template.format('\n'.join(first_entry)))
            else:
                pass
            write.write(
                template.format(
                    '\t'.join(
                        ['{0}'.format(entry) for entry in entries]
                        )
                    )
                )
        self.shared_dict['translate_lock'].lock()
        try:
            with open(file_name_bad, 'a') as write:
                if first_entry:
                    write.write(template.format('\n'.join(first_entry)))
                else:
                    pass
        finally:
            self.shared_dict['translate_lock'].unlock()

        self.file_to_distribute(file_name=file_name)
        self.file_to_distribute(file_name=file_name_bad)

    def run_motion(self, root_name):
        """
        Do the motion correction.

        root_name - Root name of the micrograph.

        Returns:
        None
        """
        file_input = root_name
        root_name, _ = os.path.splitext(file_input)
        file_dw_post_move = None
        file_stack = None
        queue_dict = {}
        do_subsum = bool(len(self.settings['motion_frames']) > 1)
        for motion_idx, key in enumerate(self.settings['motion_frames']):
            # The current settings that we work with
            motion_frames = copy.deepcopy(self.settings['motion_frames'][key])
            queue_dict[motion_idx] = {'log': [], 'sum': [], 'sum_dw': []}

            # Abort if frames out of range
            if motion_frames['first'] > \
                    int(self.settings['General']['Number of frames']) or \
                    motion_frames['last'] > \
                    int(self.settings['General']['Number of frames']):
                print('First:{0} Last:{1} not valid! Skip!\n'.format(
                    motion_frames['first'],
                    motion_frames['last']
                    ))
                continue
            else:
                pass

            # Create an unblur shift file
            file_shift = os.path.join(
                self.settings['motion_folder'],
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
                with open(file_shift, 'w') as write:
                    write.write('{0}\n{0}\n'.format('\t'.join(zeros_list)))
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
                self.settings['motion_folder'],
                output_folder_name
                )
            output_transfer_log = os.path.join(
                self.settings['motion_folder'],
                output_logfile
                )
            # Scratch
            output_transfer_scratch_root = os.path.join(
                self.settings['scratch_motion_folder'],
                output_folder_name
                )
            output_transfer_log_scratch = os.path.join(
                self.settings['scratch_motion_folder'],
                output_logfile
                )

            output_dw = os.path.join(output_transfer_root, 'DW')
            output_transfer = os.path.join(output_transfer_root, 'Non_DW')
            output_transfer_scratch = os.path.join(
                output_transfer_scratch_root,
                'Non_DW'
                )

            # Create folders if they do not exist
            self.queue_lock.lock()
            try:
                tu.mkdir_p(output_transfer_root)
                tu.mkdir_p(output_transfer)
                tu.mkdir_p(output_transfer_log)
                tu.mkdir_p(output_transfer_scratch)
                tu.mkdir_p(output_transfer_log_scratch)
            finally:
                self.queue_lock.unlock()

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
                self.queue_lock.lock()
                try:
                    tu.mkdir_p(output_dw)
                finally:
                    self.queue_lock.unlock()

                # Files
                file_stack = os.path.join(
                    output_transfer_scratch,
                    '{0}_Stk.mrc'.format(file_name)
                    )
                file_dw_post_move = os.path.join(
                    output_dw,
                    '{0}.mrc'.format(file_name)
                    )
                file_dw_pre_move = tum.get_dw_file_name(
                    output_transfer_scratch=output_transfer_scratch,
                    file_name=file_name,
                    settings=self.settings,
                    queue_com=self.queue_com,
                    name=self.name
                    )
                command, block_gpu, gpu_list = tum.get_motion_command(
                    file_input=file_input,
                    file_output_scratch=file_output_scratch,
                    file_log_scratch=file_log_scratch,
                    queue_com=self.queue_com,
                    name=self.name,
                    settings=self.settings,
                    do_subsum=do_subsum
                    )

                file_stdout_scratch, file_stderr_scratch = self.run_command(
                    command=command,
                    log_prefix=file_log_scratch,
                    block_gpu=block_gpu,
                    gpu_list=gpu_list,
                    shell=False
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
                tu.copy(file_dw_pre_move, file_dw_post_move)
                tus.check_outputs(
                    zero_list=[],
                    non_zero_list=[file_dw_post_move],
                    exists_list=[],
                    folder=self.settings['motion_folder'],
                    command='copy'
                    )

            if os.path.realpath(self.settings['scratch_motion_folder']) != \
                    os.path.realpath(self.settings['motion_folder']):
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
                    folder=self.settings['motion_folder'],
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
            else:
                pass

        try:
            file_for_jpg = queue_dict[motion_idx]['sum_dw'][0]
        except IndexError:
            file_for_jpg = queue_dict[motion_idx]['sum'][0]

        tum.create_jpg_file(
            file_for_jpg,
            self.settings
            )

        data, data_original = tu.get_function_dict()[self.settings['Copy']['Motion']]['plot_data'](
            self.settings['Copy']['Motion'],
            self.settings['Motion_folder'][self.settings['Copy']['Motion']]
            )

        warnings, skip_list = tus.check_for_outlier(
            dict_name='motion',
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

        mask = np.in1d(
            np.array(
                np.char.rsplit(
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
                    '.',
                    1
                    ).tolist()
                )[:,0],
            np.char.rsplit(np.char.rsplit(
                queue_dict[0]['sum'][0],
                '/',
                1
                ).tolist()[-1], '.', 1).tolist()[0]
            )
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
                )
            output_name_mic = output_combine[0]
            output_name_star = output_combine[1]
            output_name_star_relion3 = output_combine[2]
            new_gain = output_combine[3]
            new_defect = output_combine[4]
            motion_files = sorted(glob.glob(
                '{0}/*_transphire_motion.txt'.format(
                    os.path.dirname(file_stdout_combine)
                    )
                ))

            output_lines = []
            self.shared_dict['motion_txt_lock'].lock()
            try:
                for file_name in motion_files:
                    with open(file_name, 'r') as read:
                        output_lines.append(read.readlines()[-1])
                with open(output_name_mic, 'w') as write:
                    write.write(''.join(output_lines))
            finally:
                self.shared_dict['motion_txt_lock'].unlock()

            star_files = sorted(glob.glob(
                '{0}/*_transphire_motion.star'.format(
                    os.path.dirname(file_stdout_combine)
                    )
                ))
            header = []
            self.shared_dict['motion_star_lock'].lock()
            try:
                with open(star_files[0], 'r') as read:
                    header.extend(read.readlines()[:-1])
                output_lines = []
                for file_name in star_files:
                    with open(file_name, 'r') as read:
                        output_lines.append(read.readlines()[-1])
                with open(output_name_star, 'w') as write:
                    write.write(''.join(header))
                    write.write(''.join(output_lines))
            finally:
                self.shared_dict['motion_star_lock'].unlock()

            star_files_relion3 = sorted(glob.glob(
                '{0}/*_transphire_motion_relion3.star'.format(
                    os.path.dirname(file_stdout_combine)
                    )
                ))

            header = []
            self.shared_dict['motion_star_relion3_lock'].lock()
            try:
                with open(star_files_relion3[0], 'r') as read:
                    header.extend(read.readlines()[:-1])
                output_lines = []
                for file_name in star_files_relion3:
                    with open(file_name, 'r') as read:
                        output_lines.append(read.readlines()[-1])
                with open(output_name_star_relion3, 'w') as write:
                    write.write(''.join(header))
                    write.write(''.join(output_lines))
            finally:
                self.shared_dict['motion_star_relion3_lock'].unlock()

            star_files_relion3_meta = sorted(glob.glob(
                '{0}/*_transphire_motion_relion3_meta.star'.format(
                    os.path.dirname(file_stdout_combine)
                    )
                ))

            copy_names = []
            copy_names.extend(star_files_relion3_meta)
            copy_names.extend(star_files_relion3)
            copy_names.extend(star_files)
            copy_names.extend(motion_files)

            for file_name in copy_names:
                if not os.path.basename(root_name) in file_name:
                    continue
                else:
                    self.file_to_distribute(file_name=file_name)

            self.file_to_distribute(file_name=output_name_mic)
            self.file_to_distribute(file_name=output_name_star)
            self.file_to_distribute(file_name=output_name_star_relion3)
            if new_gain:
                self.file_to_distribute(file_name=new_gain)
            else:
                pass
            if new_defect:
                self.file_to_distribute(file_name=new_defect)
            else:
                pass
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
                        elif 'CTF_frames' in compare or 'CTF_sum' in compare or 'Picking' in compare:
                            if motion_idx == 0:
                                sum_file = sum_files[0]
                                if sum_dw_files:
                                    dw_file = sum_dw_files[0]
                                else:
                                    dw_file = 'None'
                                self.add_to_queue(
                                    aim=aim_name,
                                    root_name=';;;'.join([sum_file, dw_file, file_input])
                                    )
                            else:
                                pass
                        else:
                            for file_name in sum_files:
                                self.add_to_queue(aim=aim_name, root_name=file_name)
                            for file_name in log_files:
                                self.add_to_queue(aim=aim_name, root_name=file_name)
                            for file_name in sum_dw_files:
                                self.add_to_queue(aim=aim_name, root_name=file_name)
                    else:
                        pass

        if do_subsum:
            os.remove(file_stack)
        else:
            pass

    def run_ctf(self, root_name):
        """
        Run CTF estimation.

        root_name - name of the file to process.

        Returns:
        None
        """
        root_name_raw = root_name
        # Split is file_sum, file_dw_sum, file_frames
        try:
            file_sum, file_dw, file_input = root_name.split(';;;')
        except ValueError:
            file_input = root_name
            file_sum = root_name
            file_dw = 'None'
        try:
            if self.settings[self.settings['Copy']['CTF']]['Use movies'] == 'True':
                root_name, _ = os.path.splitext(file_input)
            else:
                root_name, _ = os.path.splitext(file_sum)
        except KeyError:
            root_name, _ = os.path.splitext(file_sum)

        # New name
        file_name = os.path.basename(root_name)
        new_name = os.path.join(
            self.settings['ctf_folder'],
            '{0}.mrc'.format(file_name)
            )

        # Create the command
        command, check_files, block_gpu, gpu_list, shell = tuc.get_ctf_command(
            file_sum=file_sum,
            file_input=file_input,
            new_name=new_name,
            settings=self.settings,
            queue_com=self.queue_com,
            name=self.name
            )

        # Log files
        log_prefix = os.path.join(
                self.settings['ctf_folder'],
                file_name
                )

        log_file, err_file = self.run_command(
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
            folder=self.settings['ctf_folder'],
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
            folder=self.settings['ctf_folder'],
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

        data, data_orig = tu.get_function_dict()[self.settings['Copy']['CTF']]['plot_data'](
            self.settings['Copy']['CTF'],
            self.settings['ctf_folder']
            )

        try:
            warnings, skip_list = tus.check_for_outlier(
                dict_name='ctf',
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
        if data.shape[0] != 0:
            output_name_partres, output_name_star = tuc.combine_ctf_outputs(
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
            partres_files = sorted(glob.glob(
                '{0}/*_transphire_ctf_partres.txt'.format(
                    self.settings['ctf_folder']
                    )
                ))

            output_lines = []
            self.shared_dict['ctf_partres_lock'].lock()
            try:
                for file_name in partres_files:
                    with open(file_name, 'r') as read:
                        output_lines.append(read.readlines()[-1])
                with open(output_name_partres, 'w') as write:
                    write.write(''.join(output_lines))
            finally:
                self.shared_dict['ctf_partres_lock'].unlock()

            star_files = sorted(glob.glob(
                '{0}/*_transphire_ctf.star'.format(
                    self.settings['ctf_folder']
                    )
                ))

            header = []
            self.shared_dict['ctf_star_lock'].lock()
            try:
                with open(star_files[0], 'r') as read:
                    header.extend(read.readlines()[:-1])
                output_lines = []
                for file_name in star_files:
                    with open(file_name, 'r') as read:
                        output_lines.append(read.readlines()[-1])
                with open(output_name_star, 'w') as write:
                    write.write(''.join(header))
                    write.write(''.join(output_lines))
            finally:
                self.shared_dict['ctf_star_lock'].unlock()

            copy_names = []
            copy_names.extend(star_files)
            copy_names.extend(partres_files)

            for file_name in copy_names:
                if not os.path.basename(root_name) in file_name:
                    continue
                else:
                    self.file_to_distribute(file_name=file_name)

            self.file_to_distribute(file_name=output_name_partres)
            self.file_to_distribute(file_name=output_name_star)
        else:
            pass

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
                    else:
                        for log_file in copied_log_files:
                            self.add_to_queue(aim=aim_name, root_name=log_file)
                else:
                    pass

    def run_picking(self, root_name):
        """
        Run picking particles.

        root_name - name of the file to process.

        Returns:
        None
        """

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
                    self.settings['picking_folder'],
                    '{0}_filter'.format(file_name)
                    )

            log_file, err_file = self.run_command(
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
                folder=self.settings['picking_folder'],
                command=command
                )
            self.queue_lock.lock()
            try:
                self.add_to_queue_file(
                    root_name=root_name,
                    file_name=self.shared_dict_typ['list_file'],
                    )
                self.shared_dict_typ['queue_list'].append(root_name)
                if time.time() - self.shared_dict_typ['queue_list_time'] < 30:
                    return None
                else:
                    pass
            finally:
                self.queue_lock.unlock()

        self.queue_lock.lock()
        try:
            if time.time() - self.shared_dict_typ['queue_list_time'] < 30:
                return None
            elif not self.shared_dict_typ['queue_list']:
                self.shared_dict_typ['queue_list_time'] = time.time()
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
                file_use_list.append(file_use_name)
                file_name_list.append(tu.get_name(file_use_name))
            self.shared_dict_typ['queue_list'] = []
            self.shared_dict_typ['queue_list_time'] = time.time()
            QThread.msleep(100)
        finally:
            self.queue_lock.unlock()

        # Create the command for picking
        command, check_files, block_gpu, gpu_list = tup.get_picking_command(
            file_input=file_use_list,
            new_name=self.settings['picking_folder'],
            settings=self.settings,
            queue_com=self.queue_com,
            name=self.name
            )

        # Log files
        log_prefix = os.path.join(
                self.settings['picking_folder'],
                file_name_list[-1]
                )

        log_file, err_file = self.run_command(
            command=command,
            log_prefix=log_prefix,
            block_gpu=block_gpu,
            gpu_list=gpu_list,
            shell=False
            )

        zero_list = []
        non_zero_list = [err_file, log_file]
        non_zero_list.extend(check_files)

        data, data_orig = tu.get_function_dict()[self.settings['Copy']['Picking']]['plot_data'](
            self.settings['Copy']['Picking'],
            self.settings['Picking_folder'][self.settings['Copy']['Picking']]
            )

        export_log_files = []
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
                folder=self.settings['picking_folder'],
                command=command
                )
            log_files.extend(non_zero_list)
            log_files.extend(zero_list)

            tup.create_box_jpg(
                file_name=file_name,
                settings=self.settings,
                queue_com=self.queue_com,
                name=self.name
                )

        data, data_orig = tu.get_function_dict()[self.settings['Copy']['Picking']]['plot_data'](
            self.settings['Copy']['Picking'],
            self.settings['Picking_folder'][self.settings['Copy']['Picking']]
            )

        for file_use, file_name in zip(file_use_list, file_name_list):
            warnings, skip_list = tus.check_for_outlier(
                dict_name='picking',
                data=data,
                file_name=file_use,
                settings=self.settings
                )

            if skip_list:
                self.remove_from_translate(os.path.basename(file_use))
            else:
                export_log_files.extend(log_files)

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
                    for log_file in export_log_files:
                        self.add_to_queue(aim=aim_name, root_name=log_file)
                else:
                    pass

        self.remove_from_queue_file(file_queue_list, self.shared_dict_typ['list_file'])

    def run_compress(self, root_name):
        """
        Compress stack.

        root_name - Name of the file to compress

        Returns:
        None
        """
        new_root_name, extension = os.path.splitext(os.path.basename(root_name))

        log_prefix = os.path.join(
                self.settings['compress_folder'],
                new_root_name
                )

        if self.settings['compress_folder'] in root_name:
            new_name = root_name
            log_file, err_file = tus.get_logfiles(log_prefix)
            tus.check_outputs(
                zero_list=[err_file],
                non_zero_list=[log_file, new_name],
                exists_list=[],
                folder=self.settings['compress_folder'],
                command='just check'
                )

        else:
            # New name
            new_name = os.path.join(
                    self.settings['compress_folder'],
                    '{0}.tiff'.format(new_root_name)
                    )

            # Skip files that are already copied but due to an error are still in the queue
            if not os.path.exists(root_name) and os.path.exists(new_name):
                print(root_name, ' does not exist anymore, but', new_name, 'does already!')
                print('Compress - Skip file!')
                return None

            # Create the command
            if extension == '.mrc':
                command = '{0} -s -c lzw {1} {2}'.format(
                    self.settings['Path']['IMOD mrc2tif'],
                    root_name,
                    new_name
                    )
            elif extension == '.tiff' or \
                    extension == '.tif':
                command = 'rsync {0} {1}'.format(root_name, new_name)
            else:
                message = '\n'.join([
                    '{0}: Not known!'.format(extension),
                    'Please contact the TranSPHIRE authors.'
                    ])
                self.queue_com['error'].put(message)
                raise IOError(message)

            # Log files
            log_file, err_file = self.run_command(
                command=command,
                log_prefix=log_prefix,
                block_gpu=False,
                gpu_list=[],
                shell=False
                )

            tus.check_outputs(
                zero_list=[err_file],
                non_zero_list=[log_file, new_name],
                exists_list=[],
                folder=self.settings['compress_folder'],
                command=command
                )


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
                self.add_to_queue(aim=aim_name, root_name=new_name)
                self.add_to_queue(aim=aim_name, root_name=log_file)
                self.add_to_queue(aim=aim_name, root_name=err_file)
            else:
                pass

        if self.settings['compress_folder'] in root_name:
            pass
        else:
            pass


    def run_copy_extern(self, root_name):
        """
        Copy to Work/Backup/HDD

        root_name - Root name of the file to copy

        Returns:
        None
        """
        dont_tar = False
        if root_name == 'None':
            pass
        elif not self.settings['Copy']['Tar to work'] == 'True' and self.typ == 'Copy_work':
            dont_tar = True
        elif not self.settings['Copy']['Tar to backup'] == 'True' and self.typ == 'Copy_backup':
            dont_tar = True
        elif not self.settings['Copy']['Tar to HDD'] == 'True' and self.typ == 'Copy_HDD':
            dont_tar = True
        elif root_name.endswith('jpg'):
            dont_tar = True
        elif self.settings['tar_folder'] in root_name:
            dont_tar = True
        elif os.path.getsize(root_name) > 40 * 1024**2:
            dont_tar = True
        elif os.path.realpath(os.path.dirname(root_name)) == \
                os.path.realpath(self.settings['project_folder']):
            dont_tar = True
        else:
            for entry in self.settings['Copy']['Picking_entries']:
                if entry.replace(' ', '_') in root_name:
                    if root_name.endswith('txt'):
                        dont_tar = True
                    elif root_name.endswith('box'):
                        dont_tar = True

        if root_name == 'None':
            self.queue_lock.lock()
            try:
                copy_file = [
                    entry
                    for entry in self.shared_dict_typ['queue_list']
                    if self.settings['tar_folder'] in entry
                    ][0]
                if not os.path.exists(copy_file):
                    self.shared_dict_typ['queue_list_time'] = time.time()
                    return None
                self.shared_dict_typ['tar_idx'] += 1
                new_tar_file = os.path.join(
                    self.settings['tar_folder'],
                    '{0}_{1:06d}.tar'.format(self.name, self.shared_dict_typ['tar_idx'])
                    )

                self.shared_dict_typ['queue_list'].remove(copy_file)
                self.remove_from_queue_file(
                    copy_file,
                    self.shared_dict_typ['list_file'],
                    lock=False
                    )
                self.shared_dict_typ['queue_list'].append(new_tar_file)
                self.add_to_queue_file(
                    root_name=new_tar_file,
                    file_name=self.shared_dict_typ['list_file'],
                    )
            finally:
                self.queue_lock.unlock()

        elif dont_tar:
            copy_file = root_name

        else:
            self.queue_lock.lock()
            try:
                try:
                    tar_file = [
                        entry
                        for entry in self.shared_dict_typ['queue_list']
                        if self.settings['tar_folder'] in entry
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

                with tarfile.open(tar_file, 'a') as tar:
                    tar.add(
                        root_name,
                        arcname=os.path.join('..', root_name.replace(self.settings['project_folder'], ''))
                        )

                if os.path.getsize(tar_file) > 200 * 1024**2:
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
                    return None
            finally:
                self.queue_lock.unlock()


        mount_folder_name = '{0}_folder'.format(self.typ)
        mount_name = self.settings['Copy'][self.typ]
        sudo = self.settings['Mount'][mount_name]['Need sudo for copy?']
        protocol = self.settings['Mount'][mount_name]['Protocol']
        new_suffix = copy_file.replace(
            self.settings['General']['Project directory'],
            ''
            )
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
                if os.path.getsize(copy_file) > \
                        sh.disk_usage(hdd_folder).free:
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

        copy_method(copy_file, new_name)
        self.shared_dict_typ['queue_list_time'] = time.time()

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
        tu.copy(file_in, file_out)


    def check_ready_for_copy(self, file_out):
        """
        Check, if the current file is ready to copy.

        file_out - File to copy

        Returns:
        True, if ready
        """
        return True
        #if 'Translation_file.txt' in file_out:
        #    while True:
        #        is_locked = bool(not self.shared_dict['translate_lock'].tryLock())
        #        if not is_locked:
        #            self.shared_dict['translate_lock'].unlock()
        #            break
        #        else:
        #            QThread.msleep(100)
        #elif 'Translation_file_bad.txt' in file_out:
        #    while True:
        #        is_locked = bool(not self.shared_dict['translate_lock'].tryLock())
        #        if not is_locked:
        #            self.shared_dict['translate_lock'].unlock()
        #            break
        #        else:
        #            QThread.msleep(100)
        #elif '_transphire_ctf_partres.txt' in file_out:
        #    while True:
        #        is_locked = bool(not self.shared_dict['ctf_partres_lock'].tryLock())
        #        if not is_locked:
        #            self.shared_dict['ctf_partres_lock'].unlock()
        #            break
        #        else:
        #            QThread.msleep(100)
        #elif '_transphire_ctf.star' in file_out:
        #    while True:
        #        is_locked = bool(not self.shared_dict['ctf_star_lock'].tryLock())
        #        if not is_locked:
        #            self.shared_dict['ctf_star_lock'].unlock()
        #            break
        #        else:
        #            QThread.msleep(100)
        #elif '_transphire_motion.txt' in file_out:
        #    while True:
        #        is_locked = bool(not self.shared_dict['motion_txt_lock'].tryLock())
        #        if not is_locked:
        #            self.shared_dict['motion_txt_lock'].unlock()
        #            break
        #        else:
        #            QThread.msleep(100)
        #elif '_transphire_motion.star' in file_out:
        #    while True:
        #        is_locked = bool(not self.shared_dict['motion_star_lock'].tryLock())
        #        if not is_locked:
        #            self.shared_dict['motion_star_lock'].unlock()
        #            break
        #        else:
        #            QThread.msleep(100)
        #elif '_transphire_motion_relion3.star' in file_out:
        #    while True:
        #        is_locked = bool(not self.shared_dict['motion_star_relion3_lock'].tryLock())
        #        if not is_locked:
        #            self.shared_dict['motion_star_relion3_lock'].unlock()
        #            break
        #        else:
        #            QThread.msleep(100)
        #else:
        #    pass
        #return True

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

    def run_command(self, command, log_prefix, block_gpu, gpu_list, shell):
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
            for entry in sorted(gpu_list):
                self.shared_dict['gpu_lock'][entry][mutex_idx].lock()

            if block_gpu:
                for entry in sorted(gpu_list):
                    lock_var = self.shared_dict['gpu_lock'][entry][mutex_idx].tryLock()
                    assert bool(not lock_var)
                    while self.shared_dict['gpu_lock'][entry][count_idx] != 0:
                        QThread.msleep(500)

            else:
                for entry in sorted(gpu_list):
                    self.shared_dict['gpu_lock'][entry][count_idx] += 1
                    self.shared_dict['gpu_lock'][entry][mutex_idx].unlock()
        else:
            pass

        # Run the command
        with open(log_file, 'w') as out:
            out.write(command)
            with open(err_file, 'w') as err:
                start_time = time.time()
                if shell:
                    sp.Popen(command, shell=True, stdout=out, stderr=err).wait()
                else:
                    sp.Popen(command.split(), stdout=out, stderr=err).wait()
                stop_time = time.time()
                out.write('\nTime: {0} sec'.format(stop_time - start_time)) 

        QThread.msleep(500)
        if gpu_list:
            if block_gpu:
                for entry in gpu_list:
                    lock_var = self.shared_dict['gpu_lock'][entry][mutex_idx].tryLock()
                    assert bool(not lock_var)
                    self.shared_dict['gpu_lock'][entry][mutex_idx].unlock()

            else:
                for entry in gpu_list:
                    self.shared_dict['gpu_lock'][entry][count_idx] -= 1
        else:
            pass

        return log_file, err_file

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
            self.queue_com['error'].put(message_error)
            self.time_last_error = time.time()
        else:
            pass
        self.queue_com['notification'].put(message_notification)
        self.write_error(msg=message_error, root_name=file_name)
