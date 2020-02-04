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
import os
import pexpect as pe
from PyQt5.QtCore import QObject, pyqtSlot, pyqtSignal


class MountCalculator(QObject):
    """
    MountCalculator object.

    Inherits from:
    QObject

    Buttons:
    None

    Signals:
    sig_finished - Signal emitted, if process finished (str, str, str)
    """
    sig_finished = pyqtSignal(str, str, str)

    def __init__(self, name, parent=None):
        """
        Initialize object variables.

        Arguments:
        name - Name of the mount point
        parent - Parent widget (default None)

        Return:
        None
        """
        super(MountCalculator, self).__init__(parent)
        self.name = name
        self.ssh_dict = None
        self.quota_command_dict = None
        self.password_dict = None
        self.kill_thread = False
        self.running = False

    @pyqtSlot(str, str)
    def calculate_df_quota(self, key, mount_folder):
        """
        Calculate the quota with the help of the df command.

        Arguments:
        key - Mount point key
        mount_folder - Mount folder

        Return:
        None
        """
        if key.startswith('HDD') and len(key) == 5:
            old_key = key
            key = key[:-2]
        else:
            old_key = key
            key = key

        if key != self.name.replace(' ', '_'):
            return None
        else:
            pass

        if old_key.startswith('HDD') and len(old_key) == 5:
            key = old_key
        else:
            pass

        self.running = True
        try:
            total_quota = shutil.disk_usage(mount_folder).total / 1e12
            used_quota = shutil.disk_usage(mount_folder).used / 1e12
        except FileNotFoundError:
            self.sig_finished.emit(
                'Needs remount',
                key,
                'red'
                )
        else:
            if total_quota == used_quota and total_quota == 0:
                self.sig_finished.emit(
                    'Needs remount',
                    key,
                    'red'
                    )
            else:
                self.sig_finished.emit(
                    '{0:.1f}TB / {1:.1f}TB'.format(used_quota, total_quota),
                    key,
                    'lightgreen'
                    )
        self.running = False

    @pyqtSlot(str, str, str, str, object, object, object)
    def calculate_ssh_quota(
            self, user, folder, device, mount_folder, ssh_dict,
            quota_command_dict, password_dict
            ):
        """
        Calculate the quota via ssh.

        Arguments:
        mount_folder - Mount folder
        user - Username
        folder - Folder to mount
        device - Device name
        ssh_dict - ssh_dict containing ssh information
        quota_command_dict - Dictionary containing the quota commands
        password_dict - Dictionary containing passwords

        Return:
        None
        """
        if device != self.name.replace(' ', '_'):
            return None
        else:
            pass

        self.running = True
        self.ssh_dict = ssh_dict
        self.quota_command_dict = quota_command_dict
        self.password_dict = password_dict

        try:
            used_quota, total_quota = self.get_ssh_quota(
                user=user,
                folder=folder,
                device=device
                )
        except KeyError:
            total_quota = shutil.disk_usage(mount_folder).total / 1e12
            used_quota = shutil.disk_usage(mount_folder).used / 1e12
        except pe.exceptions.TIMEOUT:
            total_quota = shutil.disk_usage(mount_folder).total / 1e12
            used_quota = shutil.disk_usage(mount_folder).used / 1e12

        self.sig_finished.emit(
            '{0:.1f}TB / {1:.1f}TB'.format(used_quota, total_quota),
            device,
            'lightgreen'
            )
        self.running = False

    @pyqtSlot(str, str, str)
    def calculate_get_quota(self, key, quota, mount_folder):
        """
        Calculate the quota by calculating the size of every file.

        Arguments:
        key - Mount point key
        mount_folder - Mount folder
        quota - User provided maximum quota

        Return:
        None
        """
        if key != self.name.replace(' ', '_'):
            return None
        else:
            pass

        self.running = True
        total_quota = float(quota)
        try:
            used_quota = self.get_folder_size(mount_folder, 0) / 1024 ** 4
        except PermissionError:
            self.sig_finished.emit(
                'DENIED',
                key,
                'red'
                )
        except FileNotFoundError:
            print(mount_folder, 'Directory changed during quota estimation! Wait for next run!')
            self.sig_finished.emit(
                'CHANGED',
                key,
                'red'
                )
        except OSError:
            print(mount_folder, 'Please remount!')
            self.sig_finished.emit(
                'Needs remount',
                key,
                'red'
                )
        else:
            self.sig_finished.emit(
                '{0:.1f}TB / {1:.1f}TB'.format(used_quota, total_quota),
                key,
                'lightgreen'
                )
        self.running = False

    def get_ssh_quota(self, user, folder, device):
        """
        Get the quota via ssh command.

        Arguments:
        user - User name
        folder - Mounted folder
        device - Device name

        Return:
        None
        """
        command = 'ssh {0}@{1} {2}'.format(
            user,
            self.ssh_dict[device],
            self.quota_command_dict[device]
            )
        child = pe.spawnu(command)

        try:
            idx = child.expect(
                [
                    "{0}@{1}'s password:".format(user, self.ssh_dict[device]),
                    'RSA.*'
                    ],
                timeout=4
                )
        except pe.exceptions.TIMEOUT:
            print('SSH quota command failed! Mount point might be unavailable.')
            raise
        except pe.exceptions.EOF:
            print('SSH quota command failed! Mount point might be unavailable.')
            raise

        if idx == 0:
            child.sendline(self.password_dict[device])
        elif idx == 1:
            child.sendline('yes')
            child.expect([
                "{0}@{1}'s password:".format(user, self.ssh_dict[device]),
                'RSA.*'
                ])
            child.sendline(self.password_dict[device])
        else:
            print('SSH quota command failed!')
            raise pe.exceptions.TIMEOUT

        child.expect(pe.EOF)
        if self.quota_command_dict[device].startswith('quota'):
            used_quota, total_quota = self.get_quota_quota_command(
                text=child.before.split('\n'),
                folder=folder
                )
        else:
            print('To get the quota via SSH failed, do not know how to handle {0}'.format(
                self.quota_command_dict[device]
                ))
            print('Command:\n{0}'.format(child.before))
            print('Please write a wrapper for this case or write the content to the author of TranSPHIRE')
            raise pe.exceptions.TIMEOUT
        return used_quota, total_quota

    @staticmethod
    def get_quota_quota_command(text, folder):
        """
        Extract the quota from the quota command.

        Arguments:
        text - Text returned by quota command.
        folder - Mounted folder

        Return:
        None
        """
        write_value = False
        value_line = None
        for line in text:
            if write_value:
                value_line = line
                write_value = False
            else:
                pass
            if '{0}/'.format(folder.split('/')[0]) in line:
                write_value = True
            else:
                pass

        if value_line is None:
            raise KeyError

        size_list = []
        for value in value_line.split()[:2]:
            unit = value[-1]
            try:
                int(unit)
            except ValueError:
                size = value[:-1]
                if unit.startswith('M'):
                    adjust = 1024**2
                elif unit.startswith('G'):
                    adjust = 1024
                elif unit.startswith('T'):
                    adjust = 1
                elif unit.startswith('P'):
                    adjust = 1/1024
                else:
                    print(
                        unit,
                        'unit of quota command not known!'
                        )
                    print(
                        'Please contact the author of TranSPHIRE to fix this issue'
                        )
                    raise KeyError
            else:
                adjust = 1024**3
                size = value
            size_list.append(float(size) / adjust)
        return size_list[0], size_list[1]

    def get_folder_size(self, folder, size):
        """
        Get the size of the folder recursively

        Arguments:
        folder - Folder to check contents
        size - Current caclulated size

        Return:
        Calculated size
        """
        for entry in os.scandir(folder):
            if self.kill_thread:
                return size
            elif entry.is_dir():
                size = self.get_folder_size(entry.path, size)
            else:
                size += entry.stat().st_size

        return size
