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
import sys
import os
import copy
from PyQt5.QtWidgets import (
    QWidget,
    QVBoxLayout,
    QLabel,
    QPushButton,
    QLineEdit,
    QHBoxLayout,
    QComboBox,
    QFileDialog
    )
from PyQt5.QtCore import pyqtSignal, pyqtSlot

from . import transphire_utils as tu
from . import transphire_content as tc
from . import tabdocker


class LoadContent(QWidget):
    """
    LoadContent widget.
    Widget used for the LoadContentContainer.

    Inherits from:
    QWidget

    Signals:
    delete - Emited, when the delete button is pressed (object)
    """
    delete = pyqtSignal(object)

    def __init__(self, typ, separator, settings_folder, hdd=None, parent=None):
        """
        Setup the layout for the widget

        Arguments:
        typ - Typ/Name of content
        separator - Separator widget list to delete if necessary
        hdd - Content is hdd (default None)
        parent - Parent widget (default None)

        Return:
        None
        """
        super(LoadContent, self).__init__(parent)
        # Variables
        self.separator = separator
        self.typ = typ
        self.layout = QVBoxLayout(self)
        self.layout_old = None
        self.content = []
        self.label_dict = {}
        self.layout.setContentsMargins(0, 0, 0, 0)

        self.idx_name = 0
        self.idx_values = 1
        self.idx_dtype = 2
        self.idx_group = 3
        self.idx_type = 4
        self.idx_priority = 5
        self.idx_tooltip = 6
        self.idx_toggle = 7

        self.idx_name_name = 0
        self.idx_name_global = 1

        self.idx_type_type = 0
        self.idx_type_toggle = 1

        # Fill content based on typ
        content_function = tu.get_function_dict()[typ]['content']
        is_license = tu.get_function_dict()[typ]['license']
        items_old = None
        if typ == 'Mount':
            button = QPushButton('Delete', self)
            button.clicked.connect(self._button_clicked)
            self.layout.addWidget(button)
            items = content_function(hdd=hdd)
            if hdd is None:
                pass
            else:
                self.setEnabled(False)
        elif typ in ('Copy', 'Others'):
            items = content_function(settings_folder=settings_folder)
        elif typ in ('Path'):
            items, items_old = content_function()
            tab_widget = tabdocker.TabDocker(self)
            self.layout.addWidget(tab_widget)
            widget = QWidget(self)
            self.layout = QVBoxLayout(widget)
            self.layout.setContentsMargins(0, 0, 0, 0)
            tab_widget.add_tab(widget, 'Current')
            widget = QWidget(self)
            self.layout_old = QVBoxLayout(widget)
            self.layout_old.setContentsMargins(0, 0, 0, 0)
            tab_widget.add_tab(widget, 'Old')
        else:
            items = content_function()

        items.extend([
        ['WIDGETS MAIN', '10', int, '', 'PLAIN', '', ''],
        ['WIDGETS ADVANCED', '10', int, '', 'PLAIN', '', ''],
        ['WIDGETS RARE', '10', int, '', 'PLAIN', '', ''],
        ])
        if is_license:
            items.append(
                ['IMPORTANT', 'THIS SOFTWARE IS NOT PUBLISHED UNDER AN OPEN-SOURCE LICENSE.\nPLEASE CHECK IF YOU NEED/OWN A LICENSE BEFORE USING THIS APPLICATION.', str, '', 'PLAIN', '', ''],
                )


        # Fill widget with content items
        self._fill_default(items, items_old)

    def _fill_default(self, items, items_old):
        """
        Fill the widget with content.

        Arguments:
        items - Content for the widget as list

        Return:
        None
        """
        # Layout
        for current_layout, items in zip([self.layout, self.layout_old], [items, items_old]):
            if current_layout is None:
                continue
            global_items = set([entry[0].split(':')[0] for entry in tc.default_global()])
            layout_h = QHBoxLayout()
            current_layout.addLayout(layout_h)
            layout_v = None
            for idx, entry in enumerate(items):
                if idx % 11 == 0:
                    if layout_v is not None:
                        layout_v.addStretch(1)
                    else:
                        pass
                    if layout_v is not None:
                        layout_h.addWidget(Separator(typ='vertical', color='white'), stretch=0)
                    layout_v = QVBoxLayout()
                    layout_h.addLayout(layout_v, stretch=1)
                label_name = entry[self.idx_name].split(':')[self.idx_name_name]
                layout_v.addWidget(QLabel(label_name, self), stretch=0)

                # Behaviour based on typ

                if entry[self.idx_type] in ('COMBO', 'COMBOX'):
                    widget = QComboBox(self)
                    widget.addItems(entry[self.idx_values])
                    widget.setCurrentIndex(0)
                    widget.currentIndexChanged.connect(self._change_color_to_changed)
                elif entry[self.idx_type] in ('DIR', 'DIR/SEARCH'):
                    widget = QLineEdit(entry[self.idx_values], self)
                    widget.textChanged.connect(self._change_color_to_changed)
                    widget.returnPressed.connect(self._find_dir)
                    widget.setPlaceholderText('Press shift+return')
                elif entry[self.idx_type] in ('FILE', 'FILE/SEARCH'):
                    widget = QLineEdit(entry[self.idx_values], self)
                    widget.textChanged.connect(self._change_color_to_changed)
                    widget.returnPressed.connect(self._find_file)
                    widget.setPlaceholderText('Press shift+return')
                elif entry[self.idx_type] == 'PLAIN':
                    widget = QLineEdit(entry[self.idx_values], self)
                    widget.textChanged.connect(self._change_color_to_changed)
                elif entry[self.idx_type] == 'PASSWORD':
                    widget = QLineEdit(entry[self.idx_values], self)
                    widget.textChanged.connect(self._change_color_to_changed)
                    widget.setEnabled(False)
                else:
                    raise IOError('{0}: {1} not known!'.format(entry[self.idx_name], entry[self.idx_type]))
                assert label_name not in self.label_dict, (label_name, self.label_dict)
                self.label_dict[label_name] = widget
                widget.setObjectName('setting')

                exclude_typ_list = [
                    'Mount',
                    'Font',
                    'Others',
                    'Notification_widget',
                    ]
                if self.typ not in exclude_typ_list and not entry[self.idx_name].startswith('WIDGETS') and not entry[self.idx_name] == 'IMPORTANT':
                    widget_2 = QComboBox(self)
                    widget_2.addItems(['Main', 'Advanced', 'Rare'])
                    combo_idx = widget_2.findText(entry[self.idx_priority])
                    assert combo_idx >= 0, entry
                    widget_2.setCurrentIndex(combo_idx)
                    widget_2.currentIndexChanged.connect(self._change_color_to_changed)
                else:
                    widget_2 = None

                try:
                    global_name = entry[self.idx_name].split(':')[self.idx_name_global:]
                    if not global_name:
                        raise IndexError
                except IndexError:
                    global_name = None
                    widget_3 = None
                else:
                    for entry_global in global_name:
                        if entry_global not in global_items:
                            assert False, (entry_global, 'not in ', global_items)
                    widget_3 = QPushButton(self)
                    widget_3.setCheckable(True)
                    widget_3.setText('GLOBAL')
                    widget_3.toggled.connect(self._toggle_change)

                widget.setObjectName('default_settings')
                layout_h_2 = QHBoxLayout()
                layout_h_2.setContentsMargins(0, 0, 0, 0)
                layout_h_2.addWidget(widget, stretch=1)
                for test_widget in [widget_2, widget_3]:
                    if test_widget is None:
                        continue
                    else:
                        test_widget.setObjectName('default_settings')
                        layout_h_2.addWidget(test_widget, stretch=0)

                layout_v.addLayout(layout_h_2, stretch=1)
                self.content.append({
                    'widget': widget,
                    'widget_2': widget_2,
                    'widget_3': widget_3,
                    'settings': {
                        'typ': entry[self.idx_type],
                        'name': entry[self.idx_name].split(':')[self.idx_name_name],
                        'name_global': global_name,
                        'values': entry[self.idx_values],
                        'dtype': entry[self.idx_dtype],
                        'group': entry[self.idx_group],
                        'tooltip': entry[self.idx_tooltip],
                        }
                    })

                if widget_3 is not None:
                    widget_3.setChecked(True)
            layout_v.addStretch(1)

    @pyqtSlot(bool)
    def _toggle_change(self, state):
        """
        Change the color of the entry to color changed.

        Arguments:
        None

        Return:
        None
        """
        for entry in self.content:
            if entry['widget_3'] == self.sender():
                entry['widget'].setEnabled(not state)

    @pyqtSlot()
    def _change_color_to_changed(self):
        """
        Change the color of the entry to color changed.

        Arguments:
        None

        Return:
        None
        """
        self.sender().setStyleSheet(tu.get_style(typ='changed'))

    @pyqtSlot()
    def _button_clicked(self):
        """
        Emit the signal, if the delete button is clicked.
        Send the seperator widget for deletion.

        Arguments:
        None

        Return:
        None
        """
        self.delete.emit(self.separator)

    def get_settings(self):
        """
        Get the settings from the child widgets.

        Arguments:
        None

        Return:
        List of settings
        """
        settings_list = []
        error_occured = False
        for entry in self.content:
            widget = entry['widget']
            settings = copy.deepcopy(entry['settings'])
            dtype = settings['dtype']
            key = settings['name']
            default_value = settings['values']
            if isinstance(widget, QComboBox):
                value = widget.currentText()
            elif isinstance(widget, QLineEdit):
                value = widget.text()
            else:
                message = '{0}: Type {1} not known!'.format(key, type(widget))
                print(message)
                tu.message(message)
                sys.exit()

            for number in ['2', '3']:
                temp_widget = entry['widget_{0}'.format(number)]
                if isinstance(temp_widget, QComboBox):
                    settings['widget_{0}'.format(number)] = temp_widget.currentText()
                elif isinstance(temp_widget, QPushButton):
                    settings['widget_{0}'.format(number)] = temp_widget.isChecked()
                else:
                    assert temp_widget is None
                    settings['widget_{0}'.format(number)] = temp_widget

            if value:
                if tu.check_instance(value=value, typ=dtype):
                    widget.setStyleSheet(tu.get_style(typ='unchanged'))
                else:
                    widget.setStyleSheet(tu.get_style(typ='error'))
                    message = '{0}: {1} needs to be {2}'.format(
                        key,
                        value,
                        dtype
                        )
                    print(message)
                    tu.message(message)
                    error_occured = True
            else:
                if default_value:
                    widget.setStyleSheet(tu.get_style(typ='unchanged'))
                    #print('WARNING: {0} is empty!'.format(key))
                else:
                    pass

            if key == 'Typ' and not widget.isEnabled():
                value = 'Copy_to_hdd'
            elif key == 'Protocol' and not widget.isEnabled():
                value = 'hdd'
            else:
                pass
            settings_list.append({key: [value, settings]})

        if error_occured:
            return None
        else:
            return settings_list

    def set_settings(self, settings):
        """
        Set settings to the entry widgets.

        Arguments:
        settings - List of settings

        Return:
        None
        """
        disable_name = False
        disable_typ = False
        for entry in settings:
            if self.typ == 'Mount':
                if 'Mount name' in entry:
                    if entry['Mount name'][0] == 'HDD':
                        disable_name = True
                    else:
                        pass
                elif 'Typ' in entry:
                    if entry['Typ'][0] == 'Copy_to_hdd':
                        disable_typ = True
                    else:
                        pass
                else:
                    pass
            else:
                pass

            if disable_name and disable_typ:
                is_hdd = True
                self.setEnabled(False)
            else:
                is_hdd = False
                self.setEnabled(True)

            for key in entry:
                idx = None
                for idx, setting in enumerate(self.content):
                    name = setting['settings']['name']
                    if key != name:
                        continue
                    else:
                        break

                if idx is None:
                    continue
                else:
                    pass

                if name == key:
                    pass
                else:
                    continue

                try:
                    widget = self.content[idx]['widget']
                except KeyError:
                    continue
                else:
                    pass

                if isinstance(widget, QComboBox):
                    hdd_idx = widget.findText(entry[key][0])
                    if idx < 0:
                        if is_hdd:
                            widget.addItem('Copy_to_hdd')
                            hdd_idx = widget.findText('Copy_to_hdd')
                        else:
                            hdd_idx = 0
                    else:
                        pass
                    widget.setCurrentIndex(hdd_idx)
                elif isinstance(widget, QLineEdit):
                    widget.setText(entry[key][0])
                else:
                    print(key, type(widget, 'Not known!'))
                    sys.exit()
                widget.setStyleSheet(tu.get_style(typ='unchanged'))

                try:
                    widget_2 = self.content[idx]['widget_2']
                except KeyError:
                    continue
                else:
                    pass

                if isinstance(widget_2, QComboBox):
                    try:
                        widget_2_idx = widget_2.findText(entry[key][1]['widget_2'])
                    except KeyError:
                        print(
                            'Older version of a save file detected!',
                            'Please save default settings again!'
                            )
                        continue
                    else:
                        widget_2_idx = max(0, widget_2_idx)
                        widget_2.setCurrentIndex(widget_2_idx)
                        widget_2.setStyleSheet(tu.get_style(typ='unchanged'))
                elif widget_2 is None:
                    pass
                else:
                    pass

                try:
                    widget_3 = self.content[idx]['widget_3']
                except KeyError:
                    continue
                else:
                    pass

                if isinstance(widget_3, QPushButton):
                    try:
                        widget_3.setChecked(entry[key][1]['widget_3'])
                    except KeyError:
                        widget_3.setChecked(True)
                    except TypeError:
                        widget_3.setChecked(True)
                elif widget_3 is None:
                    pass
                else:
                    pass

    def _find_label(self, widget):
        for key, value in self.label_dict.items():
            if value == widget:
                return key

    @pyqtSlot()
    def _find_file(self):
        """
        Find file name to insert it into the widget.

        Arguments:
        None

        Return:
        None
        """
        in_file = QFileDialog.getOpenFileName(
            caption='Find file: {0} - {1}'.format(self.typ, self._find_label(self.sender())),
            directory=os.getcwd(),
            options=QFileDialog.DontUseNativeDialog
            )

        in_file = in_file[0]

        if in_file != '':
            self.sender().setText(in_file)

    @pyqtSlot()
    def _find_dir(self):
        """
        Find directory to insert it into the widget.

        Arguments:
        None

        Return:
        None
        """
        in_dir = QFileDialog.getExistingDirectory(
            caption='Find directory: {0} - {1}'.format(self.typ, self._find_label(self.sender())),
            directory=os.getcwd(),
            options=QFileDialog.DontUseNativeDialog
            )
        if in_dir != '':
            self.sender().setText(in_dir)

from .separator import Separator
