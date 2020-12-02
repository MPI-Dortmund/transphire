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
import re
import os
import sys
from PyQt5.QtWidgets import QWidget, QLabel, QFileDialog, QVBoxLayout, QComboBox, QLineEdit, QHBoxLayout, QPushButton, QAction, QStyle
from PyQt5.QtCore import pyqtSlot, pyqtSignal, Qt
from PyQt5.QtGui import QKeySequence
import subprocess

from . import transphire_utils as tu
from . import inputbox


class SettingsWidget(QWidget):
    """
    Widget for setting entrys

    Inherits:
    QWidget

    Signals:
    sig_index_changed - Emitted, if the index of a combo box changes (Combo box name|str)
    """
    sig_index_changed = pyqtSignal(str)

    def __init__(self, name, content, content_others, mount_directory, global_dict=None, input_file_names=None, parent=None):
        """
        Initialise the layout.

        Arguments:
        content - Content for the widget.
        parent - Parent widget (default None)

        Returns:
        None
        """
        super(SettingsWidget, self).__init__(parent=parent)

        self.action = QAction(self)
        self.action.setShortcut(QKeySequence(Qt.CTRL + Qt.SHIFT + Qt.Key_Return))
        self.action.setShortcutContext(Qt.WidgetWithChildrenShortcut)
        self.action.triggered.connect(self.enlarge)
        self.addAction(self.action)

        # Layout
        layout = QVBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)

        # Global content
        self.parent = parent
        self.default = content[0]
        self.key_name = name
        self.typ = content[1]['typ']
        self.values = content[1]['values']
        self.name = content[1]['name']
        self.tooltip = content[1]['tooltip']
        self.dtype = content[1]['dtype']
        self.name_global = content[1]['name_global']
        self.global_value = 'ON-THE-FLY'
        self.widget_auto = None
        self.mount_directory = mount_directory
        try:
            dependency_name, dependency_value = content[1]['group'].split(':')
        except ValueError:
            dependency_name = None
            dependency_value = None

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
                self.default = pattern
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
        if dependency_name is not None:
            self.tooltip += '\n\nDependency: \'{0}\' is \'{1}\''.format(dependency_name, dependency_value)

        additional_widget = []
        self.add_widgets = []
        if self.typ not in ('COMBO', 'COMBOX'):
            additional_widget.append((self.enlarge, QStyle.SP_TitleBarNormalButton, 'Open the text field in "Enlarged mode".'))

        if self.typ == 'PLAIN' or self.typ == 'PASSWORD':
            self.edit = QLineEdit(self.name, self)
            self.edit.setToolTip(self.tooltip)
            self.edit.textChanged.connect(self.change_tooltip)
            self.edit.setText(self.default)

            if self.typ == 'PASSWORD':
                self.edit.setEchoMode(self.edit.Password)

            self.tooltip = '{0}\n\nShortcuts:\nCtrl + Shift + Return -> Open enlarged view'.format(self.tooltip)

        elif self.typ in ('FILE', 'FILE/SEARCH'):
            input_file_names.append(self.name)
            self.edit = QLineEdit(self.name, self)
            self.edit.textChanged.connect(self.change_tooltip)
            self.edit.setText(self.default)
            self.edit.setPlaceholderText('Press shift+return')
            self.edit.returnPressed.connect(self._find_file)
            self.tooltip = '{0}\n\nShortcuts:\nCtrl + Shift + Return -> Open file dialog\nCtrl + Return -> Open enlarged view'.format(self.tooltip)

            additional_widget.append((self._find_file, QStyle.SP_DialogOpenButton, 'Open the "Find file" dialog.'))

        elif self.typ in ('DIR', 'DIR/SEARCH'):
            self.edit = QLineEdit(self.name, self)
            self.edit.textChanged.connect(self.change_tooltip)
            self.edit.setText(self.default)
            self.edit.setPlaceholderText('Press shift+return')
            self.edit.returnPressed.connect(self._find_dir)
            self.tooltip = '{0}\n\nShortcuts:\nCtrl + Shift + Return -> Open directory dialog\nCtrl + Return -> Open enlarged view'.format(self.tooltip)

            additional_widget.append((self._find_dir, QStyle.SP_DialogOpenButton, 'Open the "Find directory" dialog.'))

        elif self.typ in ('COMBO', 'COMBOX'):
            self.edit = QComboBox(self)
            self.edit.setSizeAdjustPolicy(QComboBox.AdjustToContents)
            self.edit.currentTextChanged.connect(self.change_tooltip)
            self.edit.currentIndexChanged.connect(lambda: self.sig_index_changed.emit(self.name))
            self.edit.addItems(self.values)
            self.edit.setCurrentIndex(self.edit.findText(self.default))
            self.change_color_if_true()
            if self.typ == 'COMBOX':
                self.edit.setEditable(True)
                self.edit.setInsertPolicy(QComboBox.NoInsert)
                self.edit.editTextChanged.connect(self.change_tooltip)
                self.edit.editTextChanged.connect(lambda: self.sig_index_changed.emit(self.name))

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

        for func, icon, tooltip in additional_widget:
            pb = QPushButton(self)
            pb.setObjectName('global')
            pb.setStyleSheet('QPushButton {color: rgba(0, 0, 0 ,0); background-color: rgba(0, 0, 0, 0)}')
            icon = pb.style().standardIcon(icon)
            pb.setIcon(icon)
            pb.setToolTip(tooltip)
            pb.clicked.connect(func)
            self.add_widgets.append(pb)

        if self.name_global is not None:
            self.edit.setObjectName('settinger')
            self.tooltip = '{0}\n\nGlobal value: {{global_value}}'.format(self.tooltip)

            self.widget_auto = QPushButton('G', self)
            self.widget_auto.setObjectName('global')
            self.widget_auto.setToolTip('Use the global value specified in the "Global" settings tab')
            state = True
            self.widget_auto.setCheckable(state)
            self.widget_auto.toggled.connect(self._toggle_change)
            self.widget_auto.setChecked(state)
            layout_h.addWidget(self.widget_auto, stretch=0)

            for global_name in self.name_global:
                if global_dict is not None:
                    global_dict.setdefault(global_name, []).append(self)

        for pb in self.add_widgets:
            layout_h.addWidget(pb, stretch=0)

        layout_h.addStretch(1)
        layout.addLayout(layout_h)

        self.tooltip = '{0}\n\nCurrent Text: \'{{current_text}}\''.format(self.tooltip)
        try:
            self.edit.textChanged.emit(self.edit.text())
        except AttributeError:
            self.edit.currentTextChanged.emit(self.edit.currentText())


    @pyqtSlot(bool)
    def _toggle_change(self, state):
        pre_pre_global = self.pre_global
        if state and self.edit.isEnabled() == True:
            try:
                self.pre_global = self.edit.text()
            except AttributeError:
                self.pre_global = self.edit.currentText()
        if self.key_name == 'Global' and state:
            try:
                current_global = self.get_current_global()
                if not current_global:
                    self.sender().setChecked(not state)
                    self.pre_global = pre_pre_global
                    return
            except Exception:
                self.pre_global = pre_pre_global
                self.sender().setChecked(not state)
                return
        elif state:
            current_global = self.global_value

        self.edit.setEnabled(not state)
        for entry in self.add_widgets:
            entry.setEnabled(not state)
        self.action.setEnabled(not state)

        if not state:
            try:
                self.edit.setText(self.pre_global)
                self.edit.setStyleSheet(tu.get_style('unchanged'))
            except AttributeError:
                self.edit.setCurrentText(self.pre_global)
                self.change_color_if_true()

        else:
            try:
                self.edit.setText(current_global)
            except AttributeError:
                self.edit.setCurrentText(current_global)
            self.edit.setStyleSheet(tu.get_style('global'))

    def get_current_global(self):
        current_global = self.pre_global
        if self.name == 'GPU':
            try:
                nvidia_output = subprocess.check_output(['nvidia-smi', '-L'])
                gpu_devices = re.findall(
                    '^GPU \d+: (.+) \(UUID: GPU-.*\)$',
                    nvidia_output.decode('utf-8'),
                    re.MULTILINE
                    )
            except subprocess.CalledProcessError:
                gpu_devices = []
            except Exception as e:
                print(e)
                gpu_devices = []
            if len(set(gpu_devices)) != 1:
                tu.message('The computer does have different types of GPUs available or no GPUs available or the GPU\'s crashed! In order to not make any mistakes, please specify the GPU IDs manually')
                return False
            else:
                current_global = ' '.join([str(entry) for entry in range(len(gpu_devices))])

        elif self.name in ('Memory usage', 'Memory usage large'):
            try:
                current_global = str(float(self.pre_global) / max(int(self.global_value), 1))
            except Exception:
                pass

        elif self.name == 'Pixel size bin':
            try:
                pixel_size_raw = float(self.parent.content['Pixel size'].get_settings()['Pixel size'])
                current_bin = int(self.parent.content['Bin X times'].get_settings()['Bin X times'])
                current_global = str(pixel_size_raw * current_bin)
            except Exception:
                pass

        elif self.name == 'Box size':
            try:
                current_radius = float(self.parent.content['Protein radius'].get_settings()['Protein radius'])
                good_box_size = [16, 24, 32, 36, 40, 44, 48, 52, 56, 60, 64, 72, 84, 96, 100, 104, 112, 120, 128, 132, 140, 168, 180, 192, 196, 208, 216, 220, 224, 240, 256, 260, 288, 300, 320, 352, 360, 384, 416, 440, 448, 480, 512, 540, 560, 576, 588, 600, 630, 640, 648, 672, 686, 700, 720, 750, 756, 768, 784, 800, 810, 840, 864, 882, 896, 900, 960, 972, 980, 1000, 1008, 1024]
                box_size = int(current_radius * 3)
                good_box_size.append(box_size)
                good_box_size = sorted(good_box_size)

                try:
                    current_global = str(good_box_size[good_box_size.index(box_size)+1])
                except IndexError:
                    current_global = str(box_size)
            except Exception:
                pass

        return current_global


    @pyqtSlot(str)
    def change_tooltip(self, text):
        edit = self.sender()
        if self.typ != 'PASSWORD':
            tooltip = self.tooltip.format(current_text=text, global_value=self.global_value)
            edit.setToolTip(tooltip)

    @pyqtSlot()
    def enlarge(self):
        if self.typ in ('COMBO', 'COMBOX'):
            return
        else:
            input_box = inputbox.InputBox(is_password=bool(self.typ == 'PASSWORD'), parent=self)
            input_box.setText('Enlarged view', self.name)
            input_box.setDefault(self.edit.text())
            input_box.set_type(self.typ)
            result = input_box.exec_()

            if result:
                self.edit.setText(input_box.getText())

    @pyqtSlot()
    def change_color_if_true(self):
        """
        Change the color, if the types are all true.

        Arguments:
        None

        Returns:
        None
        """
        if self.widget_auto is not None:
            if self.widget_auto.isChecked():
                self.edit.setStyleSheet(tu.get_style(typ='global'))
                return

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
        if '/SEARCH' in self.typ:
            current_dir = self.mount_directory
        else:
            current_dir = os.getcwd()

        in_file = QFileDialog.getOpenFileName(
            caption='Find file: {0}'.format(self.name),
            directory=current_dir,
            options=QFileDialog.DontUseNativeDialog
            )

        in_file = in_file[0]

        if in_file != '':
            self.edit.setText(in_file)

    @pyqtSlot()
    def _find_dir(self):
        """
        Find directory with an open directory dialog

        Arguments:
        None

        Returns:
        None
        """
        if '/SEARCH' in self.typ:
            current_dir = self.mount_directory
        else:
            current_dir = os.getcwd()

        in_dir = QFileDialog.getExistingDirectory(
            caption='Find directory: {0}'.format(self.name),
            directory=current_dir,
            options=QFileDialog.DontUseNativeDialog
            )
        if in_dir != '':
            if self.name == 'Project name':
                in_dir = os.path.basename(in_dir)
            self.edit.setText(in_dir)

            if '/SEARCH' in self.typ:
                self.parent.search_for_projects(in_dir)

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
            tu.message(message)
            return None
        value = value.strip()

        if ' ' in value and (self.typ in ('FILE', 'DIR', 'FILE/SEARCH') or self.name in ('Rename prefix', 'Rename suffix', 'Project name')):
            self.edit.setStyleSheet(tu.get_style(typ='error'))
            message = '{0}: {1} needs to be {2}. To avoid problems later, file paths are not allowed to contain whitespaces. If this is the case, please rename the respective folders and files'.format(
                self.label.text(),
                value,
                self.dtype
                )

            if not quiet:
                tu.message(message)

            return None

        elif value:

            if tu.check_instance(value=value, typ=self.dtype):
                pass

            elif value == 'ON-THE-FLY' and self.widget_auto is not None:
                pass

            else:
                self.edit.setStyleSheet(tu.get_style(typ='error'))
                message = '{0}: {1} needs to be {2}.'.format(
                    self.label.text(),
                    value,
                    self.dtype
                    )

                if not quiet:
                    tu.message(message)

                return None

        else:
            pass

        settings[self.name] = value
        if self.widget_auto is not None:
            is_auto = self.widget_auto.isChecked()
        else:
            is_auto = None
        global_name = None if self.name_global is None else self.name_global[0]
        settings['{0}_global'.format(self.name)] = [global_name, is_auto]

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
        if is_checked is not None:
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
                try:
                    self.widget_auto.setChecked(is_checked)
                except AttributeError:
                    pass

        widget_auto_checked = self.widget_auto.isChecked() if self.widget_auto is not None else False

        if is_checked or widget_auto_checked:
            self.pre_global = text
        else:
            if self.typ in ('COMBO', 'COMBOX'):
                index = self.edit.findText(text)
                if index == -1:
                    index = 0
                else:
                    pass
                self.edit.setCurrentIndex(index-1)
                self.edit.setCurrentIndex(index)
            else:
                self.edit.setText(text)
