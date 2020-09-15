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
import pexpect as pe
from PyQt5.QtWidgets import QDialog, QHBoxLayout, QVBoxLayout, QLabel, QPushButton, QLineEdit, QWidget
from PyQt5.QtCore import pyqtSlot

from . import transphire_utils as tu


class PasswordDialog(QDialog):
    """
    User password dialog

    Inherits:
    QDialog

    Signals:
    None
    """

    def __init__(self, folder, default, login, extension, fixed_folder, parent=None):
        """
        Initialise layout of the widget.

        Arguments:
        folder - Folder name to mount.
        default - Default user name
        login - True, if it is possible to test the users credentials on this machine
        extension - True, if a mount extension is required
        parent - Parent widget

        Returns:
        None
        """
        super(PasswordDialog, self).__init__(parent)

        # Global content
        self.user_le = QLineEdit(self)
        self.user_le.setText(default)
        self.password_le = QLineEdit(self)
        self.password_le.setEchoMode(QLineEdit.Password)
        self.folder_le = QLineEdit(self)
        self.folder_le.setText(folder)
        self.folder_le.setReadOnly(True)
        self.add_to_folder = QLineEdit(self)

        self.login = login
        self.extension = extension
        self.add_to_folder.setEnabled(self.extension)

        self.password = None
        self.username = None
        self.folder = None

        # Buttons
        button_accept = QPushButton('OK', self)
        button_accept.setObjectName('start')
        button_reject = QPushButton('Cancel', self)
        button_reject.setObjectName('stop')
        layout_button = QHBoxLayout()
        layout_button.setContentsMargins(0, 0, 0, 0)
        layout_button.addWidget(button_accept)
        layout_button.addWidget(button_reject)

        # Layout
        central_raw_layout = QVBoxLayout(self)
        central_raw_layout.setContentsMargins(0, 0, 0, 0)
        central_widget_raw = QWidget(self)
        central_widget_raw.setObjectName('central_raw')
        central_raw_layout.addWidget(central_widget_raw)

        central_layout = QVBoxLayout(central_widget_raw)
        central_widget = QWidget(self)
        central_widget.setObjectName('central')
        central_layout.addWidget(central_widget)

        layout = QVBoxLayout(central_widget)
        if not fixed_folder:
            layout.addWidget(QLabel('Username', self))
            layout.addWidget(self.user_le)
            layout.addWidget(QLabel('Password', self))
            layout.addWidget(self.password_le)
        else:
            self.user_le.hide()
            self.user_le.setText('FIXED')
            self.password_le.hide()
        layout.addWidget(QLabel('Mount device', self))
        layout.addWidget(self.folder_le)
        if self.extension:
            self.add_to_folder.setPlaceholderText('Subfolder of mount device')
            layout.addWidget(QLabel('Mount device extension', self))
            layout.addWidget(self.add_to_folder)
        else:
            self.add_to_folder.hide()
        layout.addLayout(layout_button)

        # Events
        button_accept.clicked.connect(self._my_accept)
        button_reject.clicked.connect(self.reject)

    @pyqtSlot()
    def _my_accept(self):
        """
        Modified accept function.
        """
        self.username = self.user_le.text()
        self.password = self.password_le.text()
        self.folder = os.path.join(
            *self.folder_le.text().split('/'),
            *self.add_to_folder.text().split('/')
            ).rstrip('/')

        if not self.add_to_folder.text().rstrip('/ \t\n').lstrip('/ \t\n'):
            if self.extension:
                tu.message('Folder extension not specified, but required!')
                return None
            else:
                pass
        else:
            pass

        if self.login:
            cmd = 'su - {0} -c \'ls\''.format(self.username)

            process = pe.spawn(cmd)
            idx = process.expect(['Password:', 'No passwd entry for user.*'])
            if idx == 0:
                process.sendline(self.password)
                idx = process.expect([pe.EOF, 'su: Authentication failure'])
                process.interact()
                if idx == 0:
                    self.accept()
                else:
                    print('Wrong password for user: {0}'.format(self.username))
                    self.reject()
            else:
                print('User not known on this machine: {0}'.format(self.username))
                self.reject()

        else:
            self.accept()
