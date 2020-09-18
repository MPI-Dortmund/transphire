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
import shutil
import sys
import os
import pexpect as pe
from PyQt5.QtCore import pyqtSignal, QObject, pyqtSlot, QThread


class MountWorker(QObject):
    """
    Mounting and unmounting shared devices.

    Inherits from:
    QObject

    Buttons:
    None

    Signals:
    sig_mount_hdd - Signal connected to mount HDD (device|str)
    sig_mount - Signal connected to mount a mount point (device|str, user|str, password|str, folder|str, server|str, typ|str, domain|str, version|str, sec|str, gid|str)
    sig_umount - Signal connected to unmount a mount point (device_folder|str, device|str, thread|object)

    sig_success - Signal emitted, if a task was a success (text|str, device|str, color|str)
    sig_error - Signal emitted, if a task was a failure (text|str, device|str)
    sig_info - Signal emitted, to show text in a text box (text|str)
    sig_notification - Signal emitted, to send a notification message (text|str)

    sig_add_save - Signal connected to add a save file to the dictionary (device|str, ss_address|str, quota_command|str, is_right_quota|str, quota|str)
    sig_load_save - Signal connected to load data from save file (No object)
    sig_refresh - Signal connected to recalculate quota (No object)
    sig_quota - Signal emitted, to refresh the quota status in the GUI (text|str, device|str, color|str)
    sig_set_settings - Signal connected set quota related settings (settings|object)

    sig_calculate_ssh_quota - Signal emitted to calculate the quota via ssh (user|str, folder|str, device|str, mount_folder|str, ssh_dict|object, quota_command_dict|object, password_dict|object)
    sig_calculate_df_quota - Signal emitted to calculate the quota via system information (device|str, mount_folder|str)
    sig_calculate_get_quota - Signal emitted to calculate the quota brute force (device|str, total_quota|str, mount_folder|str)
    """
    sig_mount_hdd = pyqtSignal(str)
    sig_mount = pyqtSignal(str, str, str, str, str, str, str, str, str, str, str, str)

    sig_umount = pyqtSignal(str, str, str, object)

    sig_success = pyqtSignal(str, str, str)
    sig_error = pyqtSignal(str, str)
    sig_info = pyqtSignal(str)
    sig_notification = pyqtSignal(str)

    sig_add_save = pyqtSignal(str, str, str, str, str)
    sig_load_save = pyqtSignal()
    sig_refresh = pyqtSignal()
    sig_quota = pyqtSignal(str, str, str)
    sig_set_settings = pyqtSignal(object)

    sig_calculate_ssh_quota = pyqtSignal(str, str, str, str, object, object, object)
    sig_calculate_df_quota = pyqtSignal(str, str)
    sig_calculate_get_quota = pyqtSignal(str, str, str)

    sig_set_folder = pyqtSignal(str, str)

    def __init__(self, password, settings_folder, mount_directory, parent=None):
        """
        Initialize object variables.

        Arguments:
        password - Sudo password
        settings_folder - Folder to save settings to
        mount_directory - Folder for mount points
        parent - Parent widget (default None)

        Return:
        None
        """
        super(MountWorker, self).__init__(parent)

        # Variables
        self.mount_directory = mount_directory
        self.password = password
        self.settings_folder = settings_folder
        self.save_files = {}
        self.password_dict = {}
        self.ssh_dict = {}
        self.quota_command_dict = {}
        self.is_right_quota_dict = {}
        self.quota_dict = {}
        self.refresh_count = {}
        self.refresh_billy = 0
        self.refresh_clr = 0
        self.project_directory = None
        self.project_quota_limit = None
        self.project_quota_warning = True
        self.scratch_directory = None
        self.scratch_quota_limit = None
        self.scratch_quota_warning = True
        self.abort_finished = False

        # Events
        self.sig_mount.connect(self.mount)
        self.sig_mount_hdd.connect(self.mount_hdd)
        self.sig_umount.connect(self.umount)
        self.sig_add_save.connect(self.add_save)
        self.sig_load_save.connect(self.load_save)
        self.sig_refresh.connect(self.refresh_quota)
        self.sig_set_settings.connect(self.set_settings)

        self.refresh_quota()

    @pyqtSlot(object)
    def set_settings(self, settings):
        """
        Set settings used by the worker.

        Arguments:
        settings - TranSPHIRE settings

        Return:
        None
        """
        if settings['Output']['Project directory']:
            self.project_directory = settings['Output']['Project directory']
        else:
            self.project_directory = '.'

        if settings['Notification']['Project quota warning (%)']:
            self.project_quota_limit = min(float(settings['Notification']['Project quota warning (%)']), 100)
        else:
            self.project_quota_limit = 95

        if settings['Output']['Scratch directory']:
            self.scratch_directory = settings['Output']['Scratch directory']
        else:
            self.scratch_directory = '.'

        if settings['Notification']['Scratch quota warning (%)']:
            self.scratch_quota_limit = min(float(settings['Notification']['Scratch quota warning (%)']), 100)
        else:
            self.scratch_quota_limit = 95

        self.refresh_quota()

    @pyqtSlot(str, str, str, str, str)
    def add_save(self, device, ssh_address, quota_command, is_right_quota, quota):
        """
        Add a save file to the dictonaries.

        Arguments:
        device - Mounted device name
        ssh_address - ssh adress
        quota_command - Command to calculate quota via ssh
        is_right_quota - True, if df is showing the right quota
        quota - Provided maximum quota

        Return:
        None
        """
        file_name = os.path.join(self.settings_folder, device)
        self.save_files[device] = file_name
        self.ssh_dict[device] = ssh_address
        self.quota_command_dict[device] = quota_command
        self.is_right_quota_dict[device] = is_right_quota
        self.quota_dict[device] = quota
        self.refresh_count[device] = 0
        if not os.path.exists(file_name):
            file_name = open(file_name, 'w')
            file_name.close()
        else:
            pass

    @pyqtSlot()
    def load_save(self):
        """
        Load connection status from the files

        Arguments:
        None

        Return:
        None
        """
        for key in self.save_files:
            with open(self.save_files[key], 'r') as read:
                line = read.readline().rstrip()
            if '\t' not in line:
                continue
            else:
                entry = line.split('\t')
                self.sig_success.emit(entry[0], key, 'lightgreen')
        self.refresh_quota()

    @pyqtSlot()
    def refresh_quota(self):
        """
        Refresh quota information.

        Arguments:
        None

        Return:
        None
        """
        self.check_connection()
        for key in self.save_files:
            with open(self.save_files[key], 'r') as read:
                lines = [line.rstrip('\n') for line in read.readlines()]

            # Continue if the file is empty
            if not lines:
                self.refresh_count[key] = 0
                self.sig_quota.emit('-- / --', key, 'white')
                continue
            else:
                pass

            for line in lines:
                user, folder, mount_folder, device, ssh_address, right_quota, quota, folder_from_root = line.split('\t')
                assert key == device

                # Only refresh quota after some time
                if self.refresh_count[key] == 0:
                    self.sig_quota.emit('Calculating...', key, 'lightgreen')
                    self.refresh_count[key] += 1
                    if ssh_address:
                        self.sig_calculate_ssh_quota.emit(
                            user,
                            folder,
                            device,
                            mount_folder,
                            self.ssh_dict,
                            self.quota_command_dict,
                            self.password_dict
                            )
                    elif right_quota == 'True':
                        self.sig_calculate_df_quota.emit(
                            key, mount_folder
                            )
                    else:
                        self.sig_calculate_get_quota.emit(
                            key,
                            quota,
                            mount_folder
                            )
                elif self.refresh_count[key] > 500:
                    self.refresh_count[key] = 0
                else:
                    self.refresh_count[key] += 1
                self.sig_set_folder.emit(device, os.path.join(folder_from_root, folder))

        if self.scratch_directory is not None:
            self.scratch_quota_warning = self.fill_quota_project_and_scratch(
                name='scratch',
                directory=self.scratch_directory,
                warning=self.scratch_quota_warning,
                quota_limit=self.scratch_quota_limit
                )
        else:
            pass
        if self.project_directory is not None:
            self.project_quota_warning = self.fill_quota_project_and_scratch(
                name='project',
                directory=self.project_directory,
                warning=self.project_quota_warning,
                quota_limit=self.project_quota_limit
                )
        else:
            pass

        self.check_connection()

    def fill_quota_project_and_scratch(self, name, directory, warning, quota_limit):
        """
        Refresh quota information for the project and scratch directory.

        Arguments:
        name - Name (project or scratch)
        directory - Directory to check
        warning - current warning status
        quota_limit - Limit of the quota to show a warning

        Return:
        Current warning status
        """
        try:
            total_quota = shutil.disk_usage(directory).total / 1e12
            used_quota = shutil.disk_usage(directory).used / 1e12
            free_quota = shutil.disk_usage(directory).free / 1e12

            # Decide if there is a quota warning
            limit = total_quota * (100 - quota_limit) / 100
            if warning:
                if free_quota < limit:
                    warning = False
                    message = 'Less than {0:.2f}Tb ({1:.2f}Tb) free on {2}!'.format(
                        limit,
                        free_quota,
                        name
                        )
                    self.sig_notification.emit(message)
                    self.sig_error.emit(message, 'None')
                else:
                    pass
            elif used_quota < limit * 0.9:
                warning = True
            else:
                pass
        except FileNotFoundError:
            self.sig_quota.emit('Not avilable', name, '#ff5c33')
            self.sig_success.emit('Not connected', name, '#ff5c33')

        else:
            self.sig_quota.emit('{0:.1f}TB / {1:.1f}TB'.format(used_quota, total_quota), name, 'lightgreen')
            self.sig_success.emit('Connected', name, 'lightgreen')
        return warning

    @pyqtSlot()
    def check_connection(self):
        """
        Check if a mount connection crashed

        Arguments:
        None

        Return:
        None
        """
        for key in self.save_files:
            with open(self.save_files[key], 'r') as read:
                line = read.readline().rstrip()

            if not line:
                continue
            else:
                entry = line.split('\t')
                mount_folder = '{0}'.format(entry[2])
                if not os.path.ismount(os.path.relpath(mount_folder)):
                    try:
                        os.rmdir(mount_folder)
                    except OSError as err:
                        try:
                            os.listdir(mount_folder)
                        except PermissionError:
                            pass
                        except OSError as err_os:
                            if 'Required key not available:' in str(err_os):
                                self.sig_notification.emit('Lost connection: {0}'.format(key))
                                with open(self.save_files[key], 'w') as write:
                                    write.write('')
                                self.sig_error.emit('Lost connection: {0}'.format(key), key)
                                self.refresh_quota()
                            else:
                                print('{0} - Host seems to be down! It may recover soon! You might need to manually unmount with sudo umount -l {0}.'.format(mount_folder))
                        else:
                            print('OSError caught in mount_folder: {0}'.format(mount_folder))
                            if self.password:
                                print(str(err).replace(self.password, 'SUDOPASSWORD'))
                            else:
                                print(str(err))
                    else:
                        self.sig_notification.emit('Lost connection: {0}'.format(key))
                        with open(self.save_files[key], 'w') as write:
                            write.write('')
                        self.sig_error.emit('Lost connection: {0}'.format(key), key)
                        self.refresh_quota()
                else:
                    pass

    @pyqtSlot(str)
    def mount_hdd(self, device):
        """
        Mount external HDD

        Arguments:
        device - Device name

        Return:
        None
        """
        test_name = 'hdd_test'
        mount_folder = os.path.join(self.mount_directory, device)
        folder_test = os.path.join(mount_folder, test_name)

        check_existence(self.mount_directory, mount_folder)
        try:
            os.rmdir(folder_test)
        except FileNotFoundError:
            pass
        except Exception as e:
            print(e)
            print('Removal of {0} failed because the directory is not empty or still a mount point! Please unmount and remove manually: sudo umount {0}'.format(folder_test))
            return None

        if os.listdir(mount_folder):
            self.sig_info.emit('First unmount {0}'.format(device))
            return None
        else:
            pass

        devices = ['/dev/sd{0}'.format(chr(i)) for i in range(ord('a'), ord('z') + 1)]
        useable_partitions = []

        existing_devices = [entry for entry in devices if os.path.exists(entry)]

        with open('/proc/mounts', 'r') as read:
            lines = read.read()
        existing_devices = [
            entry for entry in existing_devices
            if entry not in lines
            ]

        if not existing_devices:
            self.sig_info.emit('All mountable devices are already mounted!')
            os.rmdir(mount_folder)
            return None
        else:
            pass

        existing_partitions = [
            '{0}{1}'.format(entry, number)
            for entry in existing_devices
            for number in range(10)
            if os.path.exists('{0}{1}'.format(entry, number))
            ]

        for entry in existing_partitions:
            try:
                os.mkdir(folder_test)
            except FileExistsError:
                try:
                    os.rmdir(folder_test)
                    os.mkdir(folder_test)
                except OSError:
                    self.sig_info.emit('Check folder {0} and remove it manually.'.format(folder_test))
                    return None

            cmd = "sudo -S -k mount.exfat -o uid={0} {1} {2}".format(
                os.environ['USER'],
                entry,
                folder_test
                )
            idx, value = self._start_process(cmd)

            if 'ERROR' in value or idx != 0:
                cmd = "sudo -S -k mount.ntfs {0} {1}".format(
                    entry,
                    folder_test
                    )
                idx, value = self._start_process(cmd)
                if 'ERROR' in value or idx != 0:
                    cmd = "sudo -S -k mount -o uid={0} {1} {2}".format(
                        os.environ['USER'],
                        entry,
                        folder_test
                        )
                    idx, value = self._start_process(cmd)
                else:
                    pass
            else:
                pass

            if idx == 0 and 'ERROR' not in value:
                if shutil.disk_usage(folder_test).total > 1e12:
                    useable_partitions.append(entry)
                else:
                    self.sig_info.emit(
                        '{0}: Partition smaller then 1TB'.format(entry)
                        )
                self.umount(device, test_name, '', None)
            else:
                self.sig_info.emit('{0}: Mounting error - {1}'.format(entry, value))
                if os.path.exists(folder_test):
                    os.rmdir(folder_test)
                else:
                    pass

        if useable_partitions:
            for idx, entry in enumerate(useable_partitions):
                device_name = 'HDD_{0}'.format(idx)
                folder_name = os.path.join(mount_folder, device_name)
                os.mkdir(folder_name)

                cmd = "sudo -S -k mount.exfat -o uid={0} {1} {2}".format(
                    os.environ['USER'],
                    entry,
                    folder_name
                    )
                idx, value = self._start_process(cmd)

                if 'ERROR' in value:
                    cmd = "sudo -S -k mount.ntfs {0} {1}".format(
                        entry,
                        folder_name
                        )
                    idx, value = self._start_process(cmd)
                    if 'ERROR' in value:
                        cmd = "sudo -S -k mount -o uid={0} {1} {2}".format(
                            os.environ['USER'],
                            entry,
                            folder_name
                            )
                        idx, value = self._start_process(cmd)
                    else:
                        pass
                else:
                    pass

                if idx == 0:
                    self._write_save_file(
                        user='Connected',
                        folder='',
                        mount_folder=folder_name,
                        device=device_name,
                        text='Connected',
                        folder_from_root='',
                        )
                else:
                    self.sig_error.emit('Mount error {0}: {1}'.format(
                        device_name,
                        value
                        ))
        else:
            os.rmdir(mount_folder)

        self.refresh_quota()

    @pyqtSlot(str, str, str, str, str, str, str, str, str, str, str, str)
    def mount(self, device, user, password, folder, server, typ, domain, version, sec, gid, folder_from_root, fixed_folder):
        """
        Mount device except HDD

        Arguments:
        device - Device name
        user - Username
        password - User password
        folder - Mount folder
        server - Server name
        typ - Mount type
        domain - Domain name
        version - Mount type version
        sec - security protocol
        gid - groupid to mount
        folder_from_root - Absolute path pointing towards the mount point

        Return:
        None
        """

        self.refresh_clr = 0
        self.refresh_billy = 0

        if fixed_folder:
            mount_folder = fixed_folder
            self.refresh_count[device] = 0
            self._write_save_file(
                user=user,
                folder=folder,
                mount_folder=mount_folder,
                device=device,
                text=user,
                folder_from_root=folder_from_root,
                )
        else:
            mount_folder = os.path.join(self.mount_directory, device)
            self.password_dict[device] = password

            options = ['-o nolock']
            if typ == 'cifs' or typ == 'smbfs':
                options.append("username={0},password='{1}',uid={2},vers={3},domain={4},gid={5},sec={6}".format(
                    user,
                    password,
                    os.environ['USER'],
                    version,
                    domain,
                    gid,
                    sec
                    ))
                if sec == 'krb5' or sec == 'krb5i':
                    options.append("cruid={0}".format(user))
            elif typ == 'nfs':
                pass
            else:
                print('Mountworker:', typ, ' not known! Exiting here!')
                sys.exit(1)

            cmd = "sudo -S -k mount.{0} {1} {2}/{3}/ {4}".format(
                typ,
                ','.join(options),
                server,
                folder,
                mount_folder
                )

            idx, value = self._start_process(cmd)
            if 'ERROR' in value:
                cmd = "sudo -S -k mount {0} {1}/{2}/ {3}".format(
                    ','.join(options),
                    server,
                    folder,
                    mount_folder
                    )
                idx, value = self._start_process(cmd)
            else:
                pass
            cmd = cmd.replace(password, 'PASSWORD')

            if 'mount error' in value or 'bad UNC' in value:
                print(cmd, ' - Failed:', value)
                try:
                    os.rmdir(mount_folder)
                except OSError:
                    self.sig_info.emit(
                        'Could not mount {0}: {1}'.format(mount_folder, value)
                        )
                self.sig_info.emit(
                    'Could not mount {0}: {1}'.format(mount_folder, value)
                    )
            elif idx == 0:
                print(cmd, ' - Worked:', value)
                self.refresh_count[device] = 0
                self._write_save_file(
                    user=user,
                    folder=folder,
                    mount_folder=mount_folder,
                    device=device,
                    text=user,
                    folder_from_root=folder_from_root,
                    )
            else:
                print(cmd, ' - Failed:', value)
                os.rmdir(mount_folder)
                self.sig_error.emit('Mount failed', device)

        self.refresh_quota()

    def _write_save_file(self, user, folder, mount_folder, device, text, folder_from_root):
        """
        Write a save file

        Arguments:
        user - Username
        folder - Mount folder
        mount_folder - Mount folder
        device - Device name
        text - Text

        Return:
        None
        """
        with open(self.save_files[device], 'w') as write:
            write.write('{0}\t{1}\t{2}\t{3}\t{4}\t{5}\t{6}\t{7}'.format(
                user,
                folder,
                mount_folder,
                device,
                self.ssh_dict[device],
                self.is_right_quota_dict[device],
                self.quota_dict[device],
                folder_from_root,
                ))
        self.sig_success.emit(text, device, 'lightgreen')

    @pyqtSlot(str, str, str, object)
    def umount(self, device_folder, device, fixed_folder, thread_object):
        """
        Unmount device

        Arguments:
        device_folder - Mount point folder
        device - Device name
        thread_object - Thread object that is connected to the mount point

        Return:
        None
        """

        if fixed_folder:
            self.sig_success.emit('Not connected', device, 'white')
            device = device.split('/')[-1]
            with open(self.save_files[device], 'w') as write:
                write.write('')
            self.refresh_quota()
            return None

        if 'HDD' == os.path.basename(device_folder):
            mount_folder = os.path.join(self.mount_directory, device_folder, device)
        else:
            mount_folder = os.path.join(self.mount_directory, device_folder)

        if not check_existence(self.mount_directory, mount_folder):
            try:
                os.rmdir(mount_folder)
            except OSError:
                self.sig_info.emit(
                    '\n'.join([
                        '{0} is not accessable!'.format(mount_folder),
                        'The computer might need to be restarted!',
                        'Please contact your system administrator!'
                        ])
                    )
            else:
                self.sig_info.emit('First mount {0}'.format(mount_folder))
            return None

        self.abort_finished = False
        if thread_object is None:
            pass
        elif thread_object.running:
            thread_object.kill_thread = True
            while not self.abort_finished:
                QThread.sleep(1)
            thread_object.kill_thread = False
        else:
            pass
        self.abort_finished = False

        cmd = 'sudo -S -k umount {0}'.format(mount_folder)
        idx, value = self._start_process(cmd)

        if 'mount error' in value:
            self.sig_info.emit('Could not umount {0}: {1}'.format(mount_folder, value))
        elif idx == 1:
            self.sig_info.emit('Could not umount {0}: {1}'.format(mount_folder, value))
        elif 'hdd_test' in mount_folder:
            os.rmdir(mount_folder)
        else:
            try:
                os.rmdir(mount_folder)
            except OSError:
                if self.password:
                    self.sig_info.emit(
                        'Could not umount {0}: {1}'.format(mount_folder, value.replace(self.password, 'SUDOPASSWORD'))
                        )
                else:
                    self.sig_info.emit(
                        'Could not umount {0}: {1}'.format(mount_folder, value)
                        )
                return
            device = device.split('/')[-1]
            self.sig_success.emit('Not connected', device, 'white')
            with open(self.save_files[device], 'w') as write:
                write.write('')

            if device_folder == 'HDD':
                hdd_folder = '{0}/{1}'.format(self.mount_directory, device_folder)
                if not os.listdir(hdd_folder):
                    os.rmdir(hdd_folder)

        self.refresh_quota()

    def _start_process(self, command):
        """
        Start the process with pexpect.

        Arguments:
        command - Command to run

        Return:
        index of expect, text of expect
        """
        child = pe.spawnu(command)
        child.sendline(self.password)
        try:
            idx = child.expect([pe.EOF, 'sudo: 1 incorrect password attempt'])
        except pe.exceptions.TIMEOUT:
            idx = 1
            value = 'ERROR: Do you have sudo rights for mounting?' 
        else:
            if self.password:
                if self.password:
                    value = child.before.replace(self.password, 'SUDOPASSWORD')
                else:
                    value = child.before
            else:
                value = child.before
            child.interact()

        if list(filter(lambda x: x in value, ['Error', 'Failed'])):
            idx = 1
        return idx, value

def check_existence(mount_directory, mount_folder):
    """
    Check existence of the mount folder and create it if it does not

    Arguments:
    mount_folder - tolder to check

    Return:
    True, if the mount folder exists
    """

    if not os.path.exists(mount_directory):
        try:
            os.mkdir(mount_directory)
        except OSError:
            return False
    else:
        pass

    if not os.path.exists(mount_folder):
        try:
            os.mkdir(mount_folder)
        except OSError:
            try:
                os.listdir(mount_folder)
            except OSError as err:
                if 'Required key not available:' in str(err):
                    return True
                else:
                    return False
            else:
                return False
        else:
            return False
    else:
        return True
