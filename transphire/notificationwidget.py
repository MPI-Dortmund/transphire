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
from PyQt5.QtWidgets import QWidget, QCheckBox, QHBoxLayout, QComboBox, QLineEdit
from PyQt5.QtCore import pyqtSlot


class NotificationWidget(QWidget):
    """Widget for notification phone numbers"""

    def __init__(self, name, default, default_programs_dict, parent=None):
        """
        Initialise layout.

        Arguments:
        name - Name of the widget
        default - Default value for the widget
        parent - Parent widget

        Returns:
        None
        """
        super(NotificationWidget, self).__init__(parent)

        # Global content
        self.name = name
        self.default = default
        self.default_programs_dict = default_programs_dict
        if self.default == 'choose':
            self.edit = QComboBox(self)
            self.edit.currentTextChanged.connect(self.change_tooltip)
        else:
            self.edit = QLineEdit(self.default, self)
            self.edit.setReadOnly(True)
        self.check_box = QCheckBox(self.name, self)
        self.check_box.setToolTip('{0} : {1}'.format(self.check_box.isChecked(), self.name))

        # Event
        self.check_box.stateChanged.connect(self._change_state)

        # Layout
        layout = QHBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.addWidget(self.check_box)
        layout.addWidget(self.edit)
        self.edit.setEnabled(False)

        # Default
        if self.default == 'choose':
            pass
        else:
            self.edit.setText(default)
            self.edit.setToolTip(default)

        # Object name
        self.edit.setObjectName('noti_edit')
        self.check_box.setObjectName('noti_check')
        self.exceptions = []

    @pyqtSlot(str)
    def change_tooltip(self, text):
        self.sender().setToolTip(text)

    @pyqtSlot()
    def _change_state(self):
        """
        Change enable state of the edit

        Arguments:
        None

        Returns:
        None
        """
        self.edit.setEnabled(self.check_box.isChecked())
        self.check_box.setToolTip('{0} : {1}'.format(self.check_box.isChecked(), self.name))

    def add_exceptions(self, name):
        """
        Add a person to the exception list and dont send notification anymore.

        Arguments:
        name - Name of the person

        Returns:
        None
        """
        self.exceptions.append(name)

    def update_combo(self, typ, users):
        """
        Update the combo boxes.

        Arguments:
        users - User dictionary

        Returns:
        None
        """
        if self.default == 'choose':
            prefix = self.default_programs_dict[typ]
            items = ['{0} {1}'.format(prefix, key) for key in users if '{0} {1}'.format(prefix, key) not in self.exceptions]
            self.edit.addItems(sorted(items))

    def clear_combo(self):
        """
        Remove all users from the combo box.

        Arguments:
        None

        Returns:
        None
        """
        if self.default == 'choose':
            self.edit.clear()

    def get_settings(self):
        """
        Get text of the currently selected combo item.

        Arguments:
        None

        Returns:
        Settings dictionary
        """
        settings = {}
        if self.default == 'choose':
            settings[self.name] = '{0}\t{1}'.format(
                self.edit.currentText(),
                self.check_box.isChecked()
                )
        else:
            settings[self.name] = '{0}\t{1}'.format(
                self.edit.text(),
                self.check_box.isChecked()
                )
        return settings

    def set_settings(self, name, state):
        """
        Set currently selected combo item in text.

        Arguments:
        name - Name of the person that should be currently selected.
        state - State of the person (True/False;Enables/Disables)

        Returns:
        None
        """
        self.check_box.setChecked(bool(state == 'True'))
        if self.default == 'choose':
            index = self.edit.findText(name)
            self.edit.setCurrentIndex(index)
        else:
            self.edit.setText(name)
