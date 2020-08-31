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
import os
from PyQt5.QtWidgets import QDialog, QVBoxLayout, QLabel, QPushButton, QDialogButtonBox, QWidget, QLineEdit, QFileDialog, QCheckBox
from PyQt5.QtCore import pyqtSlot


class InputBox(QDialog):
    """
    Show a message box with an input field.

    Inherits:
    QDialog

    Signals:
    None
    """

    def __init__(self, is_password, restart_names=None, is_stop=False, settings=None, parent=None):
        """
        Initialise layout of the widget.

        Arguments:
        is_password - Input is a password and needs to be hidden.
        parent - Parent widget

        Returns:
        None
        """
        super(InputBox, self).__init__(parent)
        self.settings = settings

        if restart_names is None:
            restart_names = np.array([])
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
        self.label = QLabel(self)
        self.edit = QLineEdit('', self)
        self.edit.setObjectName('setting_xlarge')

        if is_password:
            self.edit.setEchoMode(QLineEdit.Password)
        else:
            pass

        button_box = QDialogButtonBox(self)
        accept_button = QPushButton('Ok')
        accept_button.setObjectName('start')
        reject_button = QPushButton('Cancel')
        reject_button.setObjectName('stop')

        button_box.addButton(accept_button, QDialogButtonBox.AcceptRole)
        button_box.addButton(reject_button, QDialogButtonBox.RejectRole)

        button_box.accepted.connect(self.accept)
        button_box.rejected.connect(self.reject)

        layout.addWidget(self.label)
        layout.addWidget(self.edit)
        layout.addStretch(1)

        if is_stop:
            self.abort = QCheckBox('Abort running processes?', self)
            self.abort.setChecked(True)
            layout.addWidget(self.abort)

        self.restart_content = {}
        if restart_names.size:
            layout.addWidget(QLabel('-----', self))
            self.restart_content['feedback'] = QCheckBox('Restart feedback - Check this if you modified "Number of feedbacks"', self)
            self.restart_content['feedback'].stateChanged.connect(self.handle_check)
            layout.addWidget(self.restart_content['feedback'])
            for entry in restart_names:
                if entry == 'Compress':
                    name = 'Restart {}'.format(entry)
                else:
                    name = 'Restart {} - Restarts subsequent jobs.'.format(entry)
                self.restart_content[entry] = QCheckBox(name, self)
                self.restart_content[entry].stateChanged.connect(self.handle_check)
                layout.addWidget(self.restart_content[entry])

        layout.addWidget(button_box)

    @pyqtSlot(int)
    def handle_check(self, state):
        ctf_name = self.settings['Copy']['CTF']
        is_movie = False
        try:
            is_movie = self.settings[ctf_name]['Use movies'] == 'True'
        except KeyError:
            pass
        sender = self.sender()
        key = sender.text().split()[1]
        if key not in ('Compress', 'feedback'):
            is_checked = None
            for input_key in self.restart_content:
                if key == input_key and is_checked is None:
                    cur_state = self.restart_content[input_key].blockSignals(True)
                    self.restart_content[input_key].setChecked(state)
                    self.restart_content[input_key].blockSignals(cur_state)
                    is_checked = 1 if state else 0
                elif key in ('Motion') and input_key in ('CTF') and is_movie:
                    continue
                elif key in ('CTF', 'Picking') and input_key in ('CTF', 'Picking'):
                    if not state and not is_checked:
                        is_checked = 1 if self.restart_content[input_key].isChecked() else 0
                elif key in ('Train2d', 'Auto3d') and input_key in ('Train2d', 'Auto3d'):
                    pass
                elif is_checked is not None:
                    cur_state = self.restart_content[input_key].blockSignals(True)
                    self.restart_content[input_key].setCheckState(is_checked)
                    self.restart_content[input_key].setEnabled(not is_checked)
                    self.restart_content[input_key].blockSignals(cur_state)
            if key == 'Motion' and not state:
                check_states = ['feedback']
                if is_movie:
                    check_states.append('CTF')
                for name in check_states:
                    if self.restart_content[name].isChecked():
                        self.restart_content[name].setCheckState(0)
                        self.restart_content[name].setCheckState(2)

        elif key == 'feedback':
            if self.restart_content['Picking'].isEnabled() or self.restart_content['Picking'].checkState() == 2:
                self.restart_content['Picking'].setCheckState(state)
                self.restart_content['Picking'].setEnabled(not state)

    def get_restart_dict(self):
        for key in self.restart_content:
            self.restart_content[key] = self.restart_content[key].checkState()
        return self.restart_content

    def setText(self, heading, text):
        """
        Set the text to the label.

        Arguments:
        heading - Heading of the window
        text - Text of the label

        Returns:
        None
        """
        if heading is not None:
            self.setWindowTitle(heading)
        self.label.setText(text)

    def getText(self):
        """
        Get the text from the label.

        Arguments:
        None

        Returns:
        Text content
        """
        return self.edit.text()

    def setDefault(self, text):
        """
        Set the default values for the QLineEdit.

        text - Text to put

        Returns:
        None
        """
        self.edit.setText(text)

    def set_type(self, this_type):
        if this_type in ('FILE', 'FILE/CHOICE'):
            self.edit.returnPressed.connect(self._find_file)
            self.edit.setToolTip(self.edit.toolTip() + '\n Shortcut: Shift + Return -> Open file dialog')
        elif this_type in ('DIR'):
            self.edit.returnPressed.connect(self._find_dir)
            self.edit.setToolTip(self.edit.toolTip() + '\n Shortcut: Shift + Return -> Open directory dialog')
        else:
            pass

    @pyqtSlot()
    def _find_file(self):
        """
        Find file with an open file dialog.

        Arguments:
        None

        Returns:
        None
        """
        in_file = QFileDialog.getOpenFileName(
            caption='Find file: {0}'.format(self.label.text()),
            directory=os.getcwd(),
            options=QFileDialog.DontUseNativeDialog
            )

        in_file = in_file[0]

        if in_file != '':
            self.sender().setText(in_file)


    @pyqtSlot()
    def _find_dir(self):
        """
        Find directory with an open directory dialog

        Arguments:
        None

        Returns:
        None
        """
        in_dir = QFileDialog.getExistingDirectory(
            caption='Find directory: {0}'.format(self.label.text()),
            directory=os.getcwd(),
            options=QFileDialog.DontUseNativeDialog
            )
        if in_dir != '':
            self.sender().setText(in_dir)

