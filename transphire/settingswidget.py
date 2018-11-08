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
import sys
try:
    QT_VERSION = 4
    from PyQt4.QtGui import QWidget, QLabel, QFileDialog, QVBoxLayout, QComboBox, QLineEdit
    from PyQt4.QtCore import pyqtSlot, pyqtSignal
except ImportError:
    QT_VERSION = 5
    from PyQt5.QtWidgets import QWidget, QLabel, QFileDialog, QVBoxLayout, QComboBox, QLineEdit
    from PyQt5.QtCore import pyqtSlot, pyqtSignal
from transphire import transphire_utils as tu


class SettingsWidget(QWidget):
    """
    Widget for setting entrys

    Inherits:
    QWidget

    Signals:
    sig_index_changed - Emitted, if the index of a combo box changes (Combo box name|str)
    """
    sig_index_changed = pyqtSignal(str)

    def __init__(self, name, content, content_others, parent=None):
        """
        Initialise the layout.

        Arguments:
        content - Content for the widget.
        parent - Parent widget (default None)

        Returns:
        None
        """
        super(SettingsWidget, self).__init__(parent)

        # Layout
        layout = QVBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)

        # Global content
        self.default = content[0]
        self.typ = content[1]['typ']
        self.values = content[1]['values']
        self.name = content[1]['name']
        tooltip = content[1]['tooltip']
        self.dtype = content[1]['dtype']

        if self.name == 'Project name':
            pattern = None
            pattern_example = None
            for entry in content_others:
                for widget in entry:
                    for key in widget:
                        if key == 'Project name pattern':
                            pattern = widget[key][0]
                        elif key == 'Project name pattern example':
                            pattern_example = widget[key][0]
            add_to_tooltip = [tooltip]
            if pattern:
                add_to_tooltip.extend([
                    'Needs to follow:',
                    pattern,
                    ])
            if pattern_example:
                add_to_tooltip.extend([
                    'For example',
                    pattern_example
                    ])
            tooltip = '\n'.join(add_to_tooltip)

        if self.typ == 'PLAIN':
            self.edit = QLineEdit(self.name, self)
            self.edit.setText(self.default)

        elif self.typ == 'FILE':
            self.edit = QLineEdit(self.name, self)
            self.edit.setText(self.default)
            self.edit.setPlaceholderText('Press shift+return')
            self.edit.returnPressed.connect(self._find_file)

        elif self.typ == 'FILE/CHOICE':
            self.edit = QLineEdit(self.name, self)
            self.edit.setText(self.default)
            self.edit.setPlaceholderText('Press shift+return')
            self.edit.returnPressed.connect(self._find_file)

        elif self.typ == 'DIR':
            self.edit = QLineEdit(self.name, self)
            self.edit.setText(self.default)
            self.edit.setPlaceholderText('Press shift+return')
            self.edit.returnPressed.connect(self._find_dir)

        elif self.typ == 'COMBO':
            self.edit = QComboBox(self)
            self.edit.currentIndexChanged.connect(lambda: self.sig_index_changed.emit(self.name))
            self.edit.addItems(self.values)
            self.edit.setCurrentIndex(self.edit.findText(self.default))
            self.change_color_if_true()

        else:
            print('SettingsWidget:', self.typ, 'Not known! Stopping here!')
            sys.exit()

        self.label = QLabel(self.name, self)
        large_list = ['Path']
        if name in large_list:
            self.label.setObjectName('setting_large')
            self.edit.setObjectName('setting_large')
        else:
            self.label.setObjectName('setting')
            self.edit.setObjectName('setting')
        self.label.setToolTip(self.name)
        if tooltip:
            final_tooltip = []
            for line in tooltip.splitlines():
                final_tooltip.append('\n'.join([line[i:i+80] for i in range(0, len(line), 80)]))
            self.edit.setToolTip('\n'.join(final_tooltip))
        else:
            self.edit.setToolTip(self.name)
        try:
            self.edit.textEdited.connect(
                lambda: self.edit.setStyleSheet(tu.get_style(typ='unchanged'))
                )
        except AttributeError:
            pass
        try:
            self.edit.currentIndexChanged.connect(
                self.change_color_if_true
                )
        except AttributeError:
            pass
        layout.addWidget(self.label)
        layout.addWidget(self.edit)

    def change_color_if_true(self):
        """
        Change the color, if the types are all true.

        Arguments:
        None

        Returns:
        None
        """
        if self.edit.currentText() == 'False':
            self.edit.setStyleSheet(tu.get_style(typ='False'))
        else:
            self.edit.setStyleSheet(tu.get_style(typ='True'))

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
            caption='Find file: {0}'.format(self.name),
            directory=os.getcwd(),
            options=QFileDialog.DontUseNativeDialog
            )

        if QT_VERSION == 4:
            in_file = in_file
        elif QT_VERSION == 5:
            in_file = in_file[0]
        else:
            raise ImportError('QT version unknown! Please contact the transphire authors!')

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
            caption='Find directory: {0}'.format(self.name),
            directory=os.getcwd(),
            options=QFileDialog.DontUseNativeDialog
            )
        if in_dir != '':
            self.sender().setText(in_dir)

    def get_settings(self, quiet=False):
        """
        Get the settings as dict.

        Arguments:
        quiet - True, if prints should not be shown.

        Returns:
        None, if an error occured.
        Settings as dictionary.
        """
        settings = {}
        if isinstance(self.edit, QComboBox):
            value = self.edit.currentText()

        elif isinstance(self.edit, QLineEdit):
            value = self.edit.text()

        else:
            message = 'Unreachable code! Please contact the TranSPHIRE authors!'
            print(message)
            tu.message(message)
            return None

        if value:

            if tu.check_instance(value=value, typ=self.dtype):
                pass

            else:
                self.edit.setStyleSheet(tu.get_style(typ='error'))
                message = '{0}: {1} needs to be {2}'.format(
                    self.label.text(),
                    value,
                    self.dtype
                    )

                if not quiet:
                    print(message)
                    tu.message(message)

                else:
                    pass
                return None

        else:
            pass

        settings[self.name] = value

        return settings

    def get_combo_entries(self):
        """
        Get the entries of the combo boxes.

        Arguments:
        None

        Returns:
        List containing entries.
        """
        entries_list = []
        for idx in range(self.edit.count()):
            entries_list.append(self.edit.itemText(idx))
        return entries_list

    def set_settings(self, text):
        """
        Set settings

        text - Text to set to the widget.

        Returns:
        None
        """
        if self.typ == 'COMBO':
            index = self.edit.findText(text)
            if index == -1:
                index = 0
            else:
                pass
            self.edit.setCurrentIndex(index-1)
            self.edit.setCurrentIndex(index)
        else:
            self.edit.setText(text)
