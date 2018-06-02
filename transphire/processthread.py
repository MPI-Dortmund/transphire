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
import time as ti
import os
import re
import shutil as sh
import traceback as tb
import glob
import copy
import subprocess as sp
import tarfile
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
        self.notification_time = float(self.settings['General']['Time until notification'])

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

        self.queue_com['status'].put(['Starting', name, 'yellow'])

    def run(self):
        """
        Run the thread.

        Arguments:
        None

        Return:
        None
        """
        # Current time
        self.time_last = ti.time()
        self.time_last_error = ti.time()
        self.notification_send = False

        # Event loop
        while not self.stop:
            if self.done:
                while not self.stop:
                    self.queue_com['status'].put([
                        'Finished',
                        self.name,
                        'black'
                        ])
                    QThread.sleep(10)
                continue
            else:
                pass

            if not self.run_this_thread:
                while not self.stop:
                    self.queue_com['status'].put([
                        'Skipped {0}'.format(self.queue.qsize()),
                        self.name,
                        'black'
                        ])
                    QThread.sleep(10)
                continue
            else:
                pass

            if self.later:
                while not self.stop:
                    self.queue_com['status'].put([
                        'Later {0}'.format(self.queue.qsize()),
                        self.name,
                        'black'
                        ])
                    QThread.sleep(10)
                continue
            else:
                pass

            if self.check_quota():
                pass
            else:
                self.queue_com['status'].put([
                    'Quota Error {0}'.format(self.queue.qsize()),
                    self.name,
                    'red'
                    ])
                QThread.sleep(10)
                continue

            if self.check_connection():
                pass
            else:
                self.queue_com['status'].put([
                    'Connection Error {0}'.format(self.queue.qsize()),
                    self.name,
                    'red'
                    ])
                QThread.sleep(10)
                continue

            if self.check_full():
                pass
            else:
                self.queue_com['status'].put([
                    'No space Error {0}'.format(self.queue.qsize()),
                    self.name,
                    'red'
                    ])
                QThread.sleep(10)
                continue

            if self.shared_dict_typ['unknown_error']:
                time_diff = ti.time() - self.time_last
                if self.typ == 'Find':
                    self.queue_com['status'].put([
                        'Unknown Error {0:.1f}min'.format(time_diff / 60),
                        self.name,
                        'red'
                        ])
                else:
                    self.queue_com['status'].put([
                        'Unknown Error {0} {1} {2:.1f}min'.format(
                            self.queue.qsize(),
                            self.shared_dict_typ['file_number'],
                            time_diff / 60
                            ),
                        self.name,
                        'red'
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
            if self.typ == 'Find':
                self.start_queue_find()
            elif self.typ == 'Meta':
                self.start_queue_meta()
            else:
                self.start_queue()

        # Print, if stopped
        self.queue_com['status'].put(['STOPPED', self.name, 'red'])
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
        scratch_stop = float(self.settings['General']['Scratch quota stop (%)']) / 100
        project_stop = float(self.settings['General']['Project quota stop (%)']) / 100
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
                message = ''.join([
                    '{0} no longer available!\n'.format(
                        folder.replace('_', ' ')
                        ),
                    '{0} is stopping now!'.format(self.name)
                    ])
                self.queue_com['notification'].put(
                    message
                    )
                self.queue_com['error'].put(
                    message
                    )
                return False
            if used_quota > (total_quota * stop):
                self.stop = True
                message = ''.join([
                    'Less than {0:.1f} Tb free on {1}!'.format(
                        total_quota * (1 - stop),
                        folder.replace('_', ' ')
                        ),
                    '{0} is stopping now!'.format(self.name)
                    ])
                self.queue_com['notification'].put(message)
                self.queue_com['error'].put(message)
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
                time_diff = ti.time() - self.time_last
                if folder == 'Search path frames' or \
                        folder == 'Search path meta':
                    output_folder = self.settings['General'][folder]
                else:
                    output_folder = self.settings[folder]

                self.queue_com['status'].put([
                    '{0}: Lost connection {1:.1f}min'.format(
                        self.typ,
                        time_diff / 60
                        ),
                    self.name,
                    'red'
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
                        if ti.time() - self.time_last_error > 1800:
                            self.queue_com['error'].put(
                                '{0} is connected again!'.format(self.typ)
                                )
                            self.time_last_error = ti.time()
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
        if folder_names[-1] == 'False':
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
        if not self.settings['Copy_software_meta']:
            self.done = True
            return None
        else:
            pass
        folder = self.settings['General']['Search path meta']
        if folder:
            self.queue_com['status'].put([
                'Copy Metadata',
                self.name,
                'green'
                ])
            try:
                self.run_software_meta(directory=folder)
            except FileNotFoundError:
                self.stop = True
                message = ''.join([
                    '{0} no longer available!\n'.format(
                        folder.replace('_', ' ')
                        ),
                    '{0} is stopping now!'.format(self.name)
                    ])
                self.queue_com['notification'].put(
                    message
                    )
                self.queue_com['error'].put(
                    message
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
        time_diff = ti.time() - self.time_last

        self.queue_com['status'].put([
            'Running {0:.1f}min'.format(time_diff / 60),
            self.name,
            'green'
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
                message = ''.join([
                    'Unknown error occured in {0}!'.format(self.name),
                    'The process will continue, but check the error file!',
                    '\n{0}'.format(self.shared_dict_typ['error_file'])
                    ])
                self.queue_com['notification'].put(message)
                if ti.time() - self.time_last_error > 1800:
                    self.queue_com['error'].put(message)
                    self.time_last_error = ti.time()
                else:
                    pass
                self.shared_dict_typ['unknown_error'] = True
            else:
                pass
        else:
            time_diff = ti.time() - self.time_last
            if time_diff / 60 > self.notification_time and \
                    not self.notification_send:
                self.notification_send = True
                message = 'No new files from data collection in the last {0} Minutes!'.format(
                    self.notification_time
                    )
                self.queue_com['notification'].put(message)
                self.queue_com['error'].put(message)
            QThread.sleep(20)

    def start_queue(self):
        """
        Start pipeline processes.

        Arguments:
        None

        Return:
        None
        """
        self.queue_lock.lock()
        try:
            if self.queue.empty():
                self.queue_com['status'].put([
                    'Waiting {0} {1}'.format(
                        self.queue.qsize(),
                        self.shared_dict_typ['file_number']
                        ),
                    self.name,
                    'orange'
                    ])
                QThread.sleep(5)
                return None
            else:
                pass
        except Exception:
            return None
        finally:
            self.queue_lock.unlock()

        # Get new file
        self.queue_lock.lock()
        try:
            self.queue_com['status'].put([
                'Running {0} {1}'.format(
                    self.queue.qsize(),
                    self.shared_dict_typ['file_number']
                    ),
                self.name,
                'green'
                ])
            root_name = self.remove_from_queue()
            QThread.sleep(1)
        except Exception:
            return None
        finally:
            self.queue_lock.unlock()

        # Set for every process a method and the right lost_connection name
        method_dict = {
            'Copy': {
                'method': self.run_copy,
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
        except BlockingIOError:
            self.add_to_queue(aim=self.typ, root_name=root_name)
            print('!!! BlockingIOError !!! \n')
            msg = tb.format_exc()
            self.write_error(msg=msg, root_name=root_name)
            if 'termios.error' not in msg:
                message = ''.join([
                    'BlockingIOError occured in {0}!'.format(self.name),
                    'The process will continue, but check the error file!',
                    '\n{0}'.format(self.shared_dict_typ['error_file'])
                    ])
                self.queue_com['notification'].put(message)
                if ti.time() - self.time_last_error > 1800:
                    self.queue_com['error'].put(message)
                    self.time_last_error = ti.time()
                else:
                    pass
                self.shared_dict_typ['unknown_error'] = True
            else:
                pass
        except IOError:
            self.add_to_queue(aim=self.typ, root_name=root_name)
            self.write_error(msg=tb.format_exc(), root_name=root_name)
            self.lost_connection(
                typ=method_dict[self.typ]['lost_connect']
                )
        except Exception:
            self.add_to_queue(aim=self.typ, root_name=root_name)
            print('!!! UNKNOWN !!! \n')
            msg = tb.format_exc()
            self.write_error(msg=msg, root_name=root_name)
            if 'termios.error' not in msg:
                message = ''.join([
                    'Unknown error occured in {0}!'.format(self.name),
                    'The process will continue, but check the error file!',
                    '\n{0}'.format(self.shared_dict_typ['error_file'])
                    ])
                self.queue_com['notification'].put(message)
                if ti.time() - self.time_last_error > 1800:
                    self.queue_com['error'].put(message)
                    self.time_last_error = ti.time()
                else:
                    pass
                self.shared_dict_typ['unknown_error'] = True
            else:
                pass
        else:
            self.remove_from_queue_file(root_name)
            self.queue_lock.lock()
            try:
                self.add_to_queue_file(
                    root_name=root_name,
                    file_name=self.shared_dict['typ'][self.typ]['done_file'],
                    )
            except Exception:
                raise
            finally:
                self.queue_lock.unlock()
            if self.typ == 'Copy':
                pass
            else:
                self.queue_lock.lock()
                self.shared_dict_typ['file_number'] += 1
                self.queue_lock.unlock()

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
            local = ti.localtime()
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
        except Exception:
            raise
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
        return self.queue.get(block=False)

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
        except Exception:
            raise
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
                'MotionCor2 crashed or em-transfer is full ',
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
        message = '{0} ({1}, {2})'.format(
            message,
            self.name,
            self.shared_dict_typ['error_file']
            )
        self.queue_com['notification'].put(message)
        if ti.time() - self.time_last_error > 1800:
            self.queue_com['error'].put(message)
            self.time_last_error = ti.time()
        else:
            pass

    def remove_from_queue_file(self, root_name):
        """
        Remove the files from the queue file.

        Arguments:
        root_name - Name of the file to delete

        Return:
        None
        """
        self.queue_lock.lock()
        try:
            useable_lines = []
            try:
                with open(self.shared_dict_typ['save_file'], 'r') as read:
                    lines = [line.rstrip() for line in read.readlines()]
            except FileNotFoundError:
                useable_lines = []
            else:
                for line in lines:
                    if root_name != line:
                        useable_lines.append(line)
                    else:
                        pass

            with open(self.shared_dict_typ['save_file'], 'w') as write:
                write.write('{0}\n'.format('\n'.join(useable_lines)))
        except Exception:
            raise
        finally:
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
        tar_file = '{0}.tar'.format(self.settings['software_meta_folder'])
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
        except Exception:
            raise
        finally:
            self.queue_lock.unlock()

        data = np.empty(
            len(file_list),
            dtype=[('root', '|S200'), ('date', '<i8'), ('time', '<i8')]
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
                        root_name=root_name.decode('utf-8')
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
                except Exception:
                    raise
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
                    except Exception:
                        raise
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
                        self.time_last = ti.time()
                        self.notification_send = False
                        file_list.append(root_name)
                        self.shared_dict['share'][self.content_settings['group']].append(
                            root_name
                            )
                except Exception:
                    raise
                finally:
                    self.shared_dict['typ'][self.content_settings['group']]['share_lock'].unlock()
            else:
                continue

        return file_list

    def run_copy(self, root_name):
        """
        Copy found files to em-transfer.

        root_name - Root name of file to copy.

        Returns:
        None
        """
        frames_root = root_name.replace(
            self.settings['General']['Search path meta'],
            self.settings['General']['Search path frames'],
            )
        frames, compare_name_meta = tus.find_related_frames_to_jpg(
            frames_root=frames_root,
            root_name=root_name,
            settings=self.settings,
            queue_com=self.queue_com,
            name=self.name
            )

        overall_file_size = 0
        for frame in frames:
            overall_file_size += os.path.getsize(frame)

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
        except Exception:
            raise
        finally:
            self.shared_dict_typ['count_lock'].unlock()

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
            self.stop = True
            message = '{0}: No frames found!'.format(self.name)
            self.queue_com['error'].put(message, self.name)
            self.queue_com['notification'].put(message)
            self.write_error(msg=message, root_name=root_name)
            raise IOError(message)

        if os.path.exists('{0}.jpg'.format(new_name_meta)):
            self.stop = True
            if os.path.exists(self.shared_dict_typ['done_file']):
                self.queue_lock.lock()
                try:
                    with open(self.shared_dict_typ['done_file'], 'r') as read:
                        self.shared_dict_typ['file_number'] = len(read.readlines())
                except Exception:
                    raise
                finally:
                    self.queue_lock.unlock()
            else:
                self.shared_dict_typ['file_number'] = int(
                    self.settings['General']['Start number']
                    )
            message = '{0}: File {1} already exists!\n'.format(
                self.name,
                new_name_meta
                ) + \
              'Check Startnumber!'
            self.queue_com['notification'].put(message)
            raise FileNotFoundError(message)
        else:
            pass

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

        new_stack = '{0}.{1}'.format(
            new_name_stack,
            self.settings['General']['Output extension']
            )

        command = tus.get_copy_command_for_frames(
            settings=self.settings,
            queue_com=self.queue_com,
            name=self.name
            )

        newstack_command = '{0} {1} {2}'.format(
            command,
            ' '.join(frames),
            new_stack
            )

        # Create the stack
        file_stdout = '{0}.log'.format(new_name_stack)
        file_stderr = '{0}.err'.format(new_name_stack)
        with open(file_stdout, 'w') as out:
            out.write(newstack_command)
            with open(file_stderr, 'w') as err:
                start_time = ti.time()
                sp.Popen(newstack_command.split(), stdout=out, stderr=err).wait()
                stop_time = ti.time()
                out.write('\nTime: {0} sec'.format(stop_time - start_time))

        tus.check_outputs(
            zero_list=[file_stderr],
            non_zero_list=[file_stdout, new_stack],
            folder=self.settings['stack_folder'],
            command=newstack_command
            )

        all_files = tus.find_all_files(
            root_name=root_name,
            compare_name_meta=compare_name_meta,
            settings=self.settings,
            queue_com=self.queue_com,
            name=self.name
            )

        xml_file = None
        log_files = []
        for file_entry in all_files:
            extension = file_entry.split('.')[-1]
            if file_entry in frames:
                continue
            elif extension == 'mrc':
                name = '{0}_krios_sum'.format(new_name_meta)
            elif extension == 'dm4' and 'gain' in file_entry:
                name = '{0}_gain'.format(new_name_meta)
            else:
                name = new_name_meta

            new_file = '{0}.{1}'.format(name, extension)

            if extension == 'xml':
                xml_file = new_file
            else:
                pass

            tu.copy('{0}'.format(file_entry), new_file)
            log_files.append(new_file)

        tus.check_outputs(
            zero_list=[],
            non_zero_list=log_files,
            folder=self.settings['meta_folder'],
            command='copy'
            )

        log_files.extend([file_stdout, file_stderr])
        for file_entry in all_files:
            try:
                os.remove(file_entry)
            except IOError:
                self.write_error(msg=tb.format_exc(), root_name=file_entry)
                raise

        self.append_to_translate(
            root_name=root_name,
            new_name=new_name_meta,
            xml_file=xml_file
            )

        self.shared_dict['typ'][self.content_settings['group']]['share_lock'].lock()
        try:
            self.shared_dict['share'][self.content_settings['group']].remove(root_name)
        except Exception:
            raise
        finally:
            self.shared_dict['typ'][self.content_settings['group']]['share_lock'].unlock()

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
                if '!Compress data' in compare or \
                        'Compress data' in compare or \
                        'Motion' in compare or \
                        'CTF_frames' in compare:
                    self.add_to_queue(aim=aim_name, root_name=new_stack)
                else:
                    for log_file in log_files:
                        self.add_to_queue(aim=aim_name, root_name=log_file)
            else:
                pass

    def already_in_translation_file(self, root_name):
        """
        Check, if the root_name already exists in the translation file.

        root_name - root_name

        Returns:
        True, if root_name in translation file.
        """
        self.shared_dict['translate_lock'].lock()
        try:
            content_translation_file = np.genfromtxt(
                os.path.join(
                    self.settings['project_folder'],
                    'Translation_file.txt'
                    ),
                usecols=0,
                dtype=str
                )
        except OSError:
            return False
        except Exception:
            raise
        else:
            return bool(root_name in content_translation_file)
        finally:
            self.shared_dict['translate_lock'].unlock()

    def append_to_translate(self, root_name, new_name, xml_file):
        """
        Write to the translation file.

        root_name - Root name of the file
        new_name - New name of the file

        Returns:
        None
        """
        file_name = os.path.join(
            self.settings['project_folder'],
            'Translation_file.txt'
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

        self.shared_dict['translate_lock'].lock()
        try:
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
                        try:
                            value_x = re.match('.*<X>(.*)</X>.*', lines).group(1)
                            value_y = re.match('.*<Y>(.*)</Y>.*', lines).group(1)
                            value_z = re.match('.*<Z>(.*)</Z>.*', lines).group(1)
                            defocus = re.match('.*<Defocus>(.*)</Defocus>.*', lines).group(1)
                        except AttributeError:
                            pass
                        else:
                            entries.append(value_x)
                            entries.append(value_y)
                            entries.append(value_z)
                            entries.append(defocus)
                            if first_entry:
                                first_entry.append('_pipeCoordX')
                                first_entry.append('_pipeCoordY')
                                first_entry.append('_pipeCoordZ')
                                first_entry.append('_pipeDefocusMicroscope')
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
        except Exception:
            raise
        finally:
            self.shared_dict['translate_lock'].unlock()

        if not self.settings['Copy']['Copy to work'] == 'False':
            self.add_to_queue(aim='Copy_work', root_name=file_name)
        else:
            pass
        if not self.settings['Copy']['Copy to HDD'] == 'False':
            self.add_to_queue(aim='Copy_hdd', root_name=file_name)
        else:
            pass
        if not self.settings['Copy']['Copy to backup'] == 'False':
            self.add_to_queue(aim='Copy_backup', root_name=file_name)
        else:
            pass

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
            except Exception:
                raise
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
            file_stdout_scratch = '{0}-output.log'.format(
                file_log_scratch
                )
            file_stderr_scratch = '{0}-error.log'.format(
                file_log_scratch
                )

            non_zero_list_scratch = [
                file_output_scratch,
                file_stdout_scratch
                ]
            zero_list_scratch = [file_stderr_scratch]

            # Project output
            file_output = os.path.join(
                output_transfer,
                '{0}.mrc'.format(file_name)
                )
            file_log = os.path.join(
                output_transfer_log,
                '{0}.mrc'.format(file_name)
                )
            file_stdout = '{0}-output.log'.format(
                file_log
                )
            file_stderr = '{0}-error.log'.format(
                file_log
                )
            file_frc = '{0}-frc.log'.format(
                file_log
                )

            non_zero_list = [
                file_output,
                file_stdout
                ]
            zero_list = [file_stderr]

            # Create the commands
            if motion_idx == 0:
                # DW folder
                self.queue_lock.lock()
                try:
                    tu.mkdir_p(output_dw)
                except Exception:
                    raise
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
                command = tum.get_motion_command(
                    file_input=file_input,
                    file_output_scratch=file_output_scratch,
                    file_log_scratch=file_log_scratch,
                    queue_com=self.queue_com,
                    name=self.name,
                    settings=self.settings,
                    )

                with open(file_stdout_scratch, 'w') as out:
                    out.write(command)
                    with open(file_stderr_scratch, 'w') as err:
                        start_time = ti.time()
                        sp.Popen(command.split(), stdout=out, stderr=err).wait()
                        stop_time = ti.time()
                        out.write('\nTime: {0} sec'.format(stop_time - start_time))

                # Move DW file
                if do_dw:
                    non_zero_list_scratch.append(file_dw_pre_move)
                    non_zero_list.append(file_dw_post_move)
                else:
                    pass

            else:
                command = tum.create_sum_movie_command(
                    motion_frames=motion_frames,
                    file_input=file_stack,
                    file_output=file_output_scratch,
                    file_shift=file_shift,
                    file_frc=file_frc,
                    settings=self.settings,
                    queue_com=self.queue_com,
                    name=self.name
                    )
                with open(file_stdout_scratch, 'w') as out:
                    out.write(command)
                    with open(file_stderr_scratch, 'w') as err:
                        start_time = ti.time()
                        sp.Popen(command, shell=True, stdout=out, stderr=err).wait()
                        stop_time = ti.time()
                        out.write('\nTime: {0} sec'.format(stop_time - start_time))

                non_zero_list.append(file_frc)
                self.queue_lock.lock()
                try:
                    for entry_temp in glob.glob('.SumMovie*'):
                        os.remove(entry_temp)
                except Exception:
                    raise
                finally:
                    self.queue_lock.unlock()

            # Sanity check
            log_files_scratch = glob.glob('{0}0*'.format(file_log_scratch))
            non_zero_list_scratch.extend(log_files_scratch)
            tus.check_outputs(
                zero_list=zero_list_scratch,
                non_zero_list=non_zero_list_scratch,
                folder=output_transfer_log_scratch,
                command=command
                )

            if do_dw:
                tu.copy(file_dw_pre_move, file_dw_post_move)
            else:
                pass

            if os.path.realpath(self.settings['scratch_motion_folder']) != \
                    os.path.realpath(self.settings['motion_folder']):
                self.queue_lock.lock()
                try:
                    tu.copy(file_output_scratch, file_output)
                    tu.copy(file_stdout_scratch, file_stdout)
                    tu.copy(file_stderr_scratch, file_stderr)
                    for file_name_log in log_files_scratch:
                        name = os.path.basename(file_name_log)
                        new_name = os.path.join(output_transfer_log, name)
                        tu.copy(file_name_log, new_name)
                except Exception:
                    raise
                finally:
                    self.queue_lock.unlock()
            else:
                pass

            log_files = glob.glob('{0}0*'.format(file_log))
            non_zero_list.extend(log_files)
            tus.check_outputs(
                zero_list=zero_list,
                non_zero_list=non_zero_list,
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

            queue_dict[motion_idx]['sum'].append(file_output)
            for file_name_log in glob.glob('{0}*'.format(file_log)):
                queue_dict[motion_idx]['log'].append(file_name_log)
            if do_dw:
                queue_dict[motion_idx]['sum_dw'].append(file_dw_post_move)
            else:
                pass

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
                    if '!Compress data' in compare:
                        if motion_idx == 0:
                            self.add_to_queue(aim=aim_name, root_name=file_input)
                        else:
                            pass
                    elif 'Compress data' in compare:
                        if motion_idx == 0:
                            self.add_to_queue(aim=aim_name, root_name=file_input)
                        else:
                            pass
                    elif 'CTF_frames' in compare:
                        if motion_idx == 0:
                            for file_name in sum_files:
                                self.add_to_queue(
                                    aim=aim_name,
                                    root_name='{0};;;{1}'.format(file_name, file_input)
                                    )
                        else:
                            pass
                    elif 'CTF_sum' in compare:
                        if motion_idx == 0:
                            for file_name in sum_files:
                                self.add_to_queue(aim=aim_name, root_name=file_name)
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

        # Plot Motion information
        self.queue_lock.lock()
        self.queue_com['plot_motion'].put(True)
        try:
            os.remove(file_stack)
        except Exception:
            raise
        finally:
            self.queue_lock.unlock()

    def run_ctf(self, root_name):
        """
        Run CTF estimation.

        root_name - name of the file to process.

        Returns:
        None
        """
        if ';;;' in root_name:
            sum_file, file_input = root_name.split(';;;')
        else:
            sum_file = root_name
            file_input = root_name
        root_name, _ = os.path.splitext(file_input)

        # New name
        file_name = os.path.basename(root_name)
        new_name = os.path.join(
            self.settings['ctf_folder'],
            '{0}.mrc'.format(file_name)
            )

        # Create the command
        command, check_files = tuc.get_ctf_command(
            file_input=file_input,
            new_name=new_name,
            settings=self.settings,
            queue_com=self.queue_com,
            name=self.name
            )

        # Log files
        out_file = os.path.join(
            self.settings['ctf_folder'],
            '{0}.log'.format(file_name)
            )
        err_file = os.path.join(
            self.settings['ctf_folder'],
            '{0}.err'.format(file_name)
            )

        # Run the command
        with open(out_file, 'w') as out:
            out.write(command)
            with open(err_file, 'w') as err:
                start_time = ti.time()
                sp.Popen(command, shell=True, stdout=out, stderr=err).wait()
                stop_time = ti.time()
                out.write('\nTime: {0} sec'.format(stop_time - start_time))

        zero_list = [err_file]
        non_zero_list = [out_file]
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

        # Combine output files
        output_name_partres, output_name_star = tuc.combine_ctf_outputs(
            root_path=root_path,
            file_name=file_name,
            settings=self.settings,
            queue_com=self.queue_com,
            shared_dict=self.shared_dict,
            name=self.name,
            sum_file=sum_file
            )

        if not self.settings['Copy']['Copy to work'] == 'False':
            self.add_to_queue(aim='Copy_work', root_name=output_name_partres)
            self.add_to_queue(aim='Copy_work', root_name=output_name_star)
        else:
            pass
        if not self.settings['Copy']['Copy to HDD'] == 'False':
            self.add_to_queue(aim='Copy_hdd', root_name=output_name_partres)
            self.add_to_queue(aim='Copy_hdd', root_name=output_name_star)
        else:
            pass
        if not self.settings['Copy']['Copy to backup'] == 'False':
            self.add_to_queue(aim='Copy_backup', root_name=output_name_partres)
            self.add_to_queue(aim='Copy_backup', root_name=output_name_star)
        else:
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
                if '!Compress data' in compare or 'Compress data' in compare:
                    self.add_to_queue(aim=aim_name, root_name=file_input)
                else:
                    for log_file in copied_log_files:
                        self.add_to_queue(aim=aim_name, root_name=log_file)
            else:
                pass

        # Plot CTF information
        self.queue_com['plot_ctf'].put(True)

    def run_compress(self, root_name):
        """
        Compress stack.

        root_name - Name of the file to compress

        Returns:
        None
        """
        if self.settings['compress_folder'] in root_name:
            name, _ = os.path.splitext(root_name)
            new_name = root_name
            log_file = '{0}.log'.format(name)
            err_file = '{0}.err'.format(name)
            tus.check_outputs(
                zero_list=[err_file],
                non_zero_list=[log_file, new_name],
                folder=self.settings['compress_folder'],
                command='just check'
                )

        else:
            # New name
            new_root_name, extension = os.path.splitext(os.path.basename(root_name))

            new_name = os.path.join(
                    self.settings['compress_folder'],
                    '{0}.tiff'.format(new_root_name)
                    )

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
                    '{0}: Not known!'.format(self.settings['General']['Output extension']),
                    'Please contact the TranSPHIRE authors.'
                    ])
                self.queue_com['error'].put(message)
                raise IOError(message)

            # Log files
            err_file = os.path.join(
                    self.settings['compress_folder'],
                    '{0}.err'.format(new_root_name)
                    )
            log_file = os.path.join(
                    self.settings['compress_folder'],
                    '{0}.log'.format(new_root_name)
                    )

            # Run the command
            with open(log_file, 'w') as out:
                out.write(command)
                with open(err_file, 'w') as err:
                    start_time = ti.time()
                    sp.Popen(command.split(), stdout=out, stderr=err).wait()
                    stop_time = ti.time()
                    out.write('\nTime: {0} sec'.format(stop_time - start_time))

            tus.check_outputs(
                zero_list=[err_file],
                non_zero_list=[log_file, new_name],
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
        elif self.settings['Copy']['Delete stack after compression?'] == 'True':
            os.remove(root_name)
        else:
            pass


    def run_copy_extern(self, root_name):
        """
        Copy to Work/Backup/HDD

        root_name - Root name of the file to copy

        Returns:
        None
        """

        mount_folder_name = '{0}_folder'.format(self.typ)
        mount_name = self.settings['Copy'][self.typ]
        sudo = self.settings['Mount'][mount_name]['Need sudo for copy?']
        protocol = self.settings['Mount'][mount_name]['Protocol']
        new_suffix = root_name.replace(
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
            for hdd_folder in glob.glob(
                    '{0}/*'.format(
                        self.settings[mount_folder_name]
                        )
                    ):
                if os.path.getsize(root_name) > \
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

        copy_method(root_name, new_name)

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
        if 'Translation_file.txt' in file_out:
            while True:
                is_locked = bool(not self.shared_dict['translate_lock'].tryLock())
                if not is_locked:
                    self.shared_dict['translate_lock'].unlock()
                    break
                else:
                    QThread.msleep(100)
        elif '_transphire_partres.txt' in file_out:
            while True:
                is_locked = bool(not self.shared_dict['ctf_partres_lock'].tryLock())
                if not is_locked:
                    self.shared_dict['ctf_partres_lock'].unlock()
                    break
                else:
                    QThread.msleep(100)
        elif '_transphire.star' in file_out:
            while True:
                is_locked = bool(not self.shared_dict['ctf_star_lock'].tryLock())
                if not is_locked:
                    self.shared_dict['ctf_star_lock'].unlock()
                    break
                else:
                    QThread.msleep(100)
        else:
            pass
        return True

    def copy_as_another_user(self, file_in, file_out):
        """
        Copy to device as another user via sudo.

        file_in - Input file path
        file_out - Output file path

        Returns:
        None
        """
        self.shared_dict['global_lock'].lock()
        self.check_ready_for_copy(file_out=file_out)

        try:
            self.mkdir_p_as_another_user(folder=os.path.dirname(file_out))
            command = 'sudo -k -S -u {0} rsync {1} {2}'.format(
                self.user,
                file_in,
                file_out
                )
            child = pe.spawnu(command)
            child.sendline(self.password)
            child.expect(pe.EOF)
        except Exception:
            raise
        finally:
            self.shared_dict['global_lock'].unlock()

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

