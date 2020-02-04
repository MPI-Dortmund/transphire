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
QT_VERSION = 5
from PyQt5.QtWidgets import QWidget, QLabel, QFileDialog, QVBoxLayout, QComboBox, QLineEdit, QHBoxLayout, QPushButton, QAction
from PyQt5.QtCore import pyqtSlot, pyqtSignal, Qt
from PyQt5.QtGui import QKeySequence
from transphire import transphire_utils as tu
from transphire import inputbox


class SettingsWidget(QWidget):
    """
    Widget for setting entrys

    Inherits:
    QWidget

    Signals:
    sig_index_changed - Emitted, if the index of a combo box changes (Combo box name|str)
    """
    sig_index_changed = pyqtSignal(str)

    def __init__(self, name, content, content_others, global_dict=None, parent=None):
        """
        Initialise the layout.

        Arguments:
        content - Content for the widget.
        parent - Parent widget (default None)

        Returns:
        None
        """
        super(SettingsWidget, self).__init__(parent)

        self.action = QAction(self)
        self.action.setShortcut(QKeySequence(Qt.CTRL + Qt.SHIFT + Qt.Key_Return))
        self.action.setShortcutContext(Qt.WidgetWithChildrenShortcut)
        self.action.triggered.connect(self.enlarge)
        self.addAction(self.action)

        # Layout
        layout = QVBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)

        # Global content
        self.default = content[0]
        self.key_name = name
        self.typ = content[1]['typ']
        self.values = content[1]['values']
        self.name = content[1]['name']
        self.tooltip = content[1]['tooltip']
        self.dtype = content[1]['dtype']
        self.name_global = content[1]['name_global']
        self.global_value = 'ON-THE-FLY'

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
            add_to_tooltip = [self.tooltip]
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
            self.tooltip = '\n'.join(add_to_tooltip)

        if self.tooltip:
            final_tooltip = []
            for line in self.tooltip.splitlines():
                final_tooltip.append('\n'.join([line[i:i+80] for i in range(0, len(line), 80)]))
            self.tooltip = '\n'.join(final_tooltip)
        else:
            self.tooltip = self.name

        self.tooltip = '{0}\nDefault: \'{1}\''.format(self.tooltip, self.default)

        if self.typ == 'PLAIN' or self.typ == 'PASSWORD':
            self.edit = QLineEdit(self.name, self)
            self.edit.setToolTip(self.tooltip)
            self.edit.textChanged.connect(self.change_tooltip)
            self.edit.setText(self.default)

            if self.typ == 'PASSWORD':
                self.edit.setEchoMode(self.edit.Password)

            self.tooltip = '{0}\n\nShortcuts:\nCtrl + Shift + Return -> Open enlarged view'.format(self.tooltip)

        elif self.typ == 'FILE':
            self.edit = QLineEdit(self.name, self)
            self.edit.textChanged.connect(self.change_tooltip)
            self.edit.setText(self.default)
            self.edit.setPlaceholderText('Press shift+return')
            self.edit.returnPressed.connect(self._find_file)
            self.tooltip = '{0}\n\nShortcuts:\Ctrl + Shift + Return -> Open file dialog\nCtrl + Return -> Open enlarged view'.format(self.tooltip)

        elif self.typ == 'FILE/CHOICE':
            self.edit = QLineEdit(self.name, self)
            self.edit.textChanged.connect(self.change_tooltip)
            self.edit.setText(self.default)
            self.edit.setPlaceholderText('Press shift+return')
            self.edit.returnPressed.connect(self._find_file)
            self.tooltip = '{0}\n\nShortcuts:\Ctrl + Shift + Return -> Open file dialog\nCtrl + Return -> Open enlarged view'.format(self.tooltip)

        elif self.typ == 'DIR':
            self.edit = QLineEdit(self.name, self)
            self.edit.textChanged.connect(self.change_tooltip)
            self.edit.setText(self.default)
            self.edit.setPlaceholderText('Press shift+return')
            self.edit.returnPressed.connect(self._find_dir)
            self.tooltip = '{0}\n\nShortcuts:\Ctrl + Shift + Return -> Open directory dialog\nCtrl + Return -> Open enlarged view'.format(self.tooltip)

        elif self.typ == 'COMBO':
            self.edit = QComboBox(self)
            self.edit.currentTextChanged.connect(self.change_tooltip)
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

        layout_h = QHBoxLayout()
        layout_h.setContentsMargins(0, 0, 0, 0)
        layout_h.setSpacing(0)
        layout_h.addWidget(self.edit, stretch=1)

        try:
            self.pre_global = self.edit.text()
        except AttributeError:
            self.pre_global = self.edit.currentText()
        if content[1]['name_global'] is not None:
            self.edit.setObjectName('settinger')
            self.tooltip = '{0}\n\nGlobal value: {{global_value}}'.format(self.tooltip)

            self.widget_auto = QPushButton('G', self)
            self.widget_auto.setObjectName('global')
            self.widget_auto.setToolTip('Use the global value specified in the "Global" settings tab')
            self.widget_auto.setCheckable(True)
            self.widget_auto.toggled.connect(self._toggle_change)
            self.widget_auto.setChecked(True)
            layout_h.addWidget(self.widget_auto)

            if global_dict is not None and self.key_name != 'Global':
                global_dict.setdefault(self.name_global, []).append(self)

        else:
            self.widget_auto = None

        layout_h.addStretch(1)
        layout.addLayout(layout_h)

        self.tooltip = '{0}\n\nCurrent Text: \'{{current_text}}\''.format(self.tooltip)
        try:
            self.edit.textChanged.emit(self.edit.text())
        except AttributeError:
            self.edit.currentTextChanged.emit(self.edit.currentText())


    @pyqtSlot(bool)
    def _toggle_change(self, state):
        self.edit.setEnabled(not state)
        self.action.setEnabled(not state)
        if not state:
            try:
                self.edit.setText(self.pre_global)
                self.edit.setStyleSheet(tu.get_style('unchanged'))
            except AttributeError:
                self.edit.setCurrentText(self.pre_global)
                self.edit.blockSignals(False)
                self.edit.removeItem(0)
                self.change_color_if_true()
        else:
            try:
                self.pre_global = self.edit.text()
                self.edit.setText(self.global_value)
                self.edit.setStyleSheet(tu.get_style('global'))
            except AttributeError:
                self.pre_global = self.edit.currentText()
                self.edit.blockSignals(True)
                self.edit.setStyleSheet(tu.get_style('global'))
                self.edit.insertItem(0, self.global_value)
                self.edit.setCurrentText(self.global_value)

    def change_tooltip(self, text):
        edit = self.sender()
        if self.typ != 'PASSWORD':
            tooltip = self.tooltip.format(current_text=text, global_value=self.global_value)
            edit.setToolTip(tooltip)

    @pyqtSlot()
    def enlarge(self):
        if self.typ == 'COMBO':
            return
        else:
            input_box = inputbox.InputBox(is_password=False, parent=self)
            input_box.setText('Enlarged view', self.name)
            input_box.setDefault(self.edit.text())
            input_box.set_type(self.typ)
            result = input_box.exec_()

            if result:
                self.edit.setText(input_box.getText())

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

            elif value == 'ON-THE-FLY' and self.widget_auto is not None:
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
        if self.widget_auto is not None:
            is_auto = self.widget_auto.isChecked()
        else:
            is_auto = None
        settings['{0}_global'.format(self.name)] = [self.name_global, is_auto]

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

    def set_settings(self, text, is_checked):
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

        is_checked_type = is_checked.split(', ')[1][:-1]
        if is_checked_type == 'None':
            is_checked = None
        elif is_checked_type == 'True':
            is_checked = True
        elif is_checked_type == 'False':
            is_checked = False
        else:
            assert False, is_checked_type

        if is_checked is not None:
            self.widget_auto.setChecked(is_checked)
