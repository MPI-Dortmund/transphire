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
try:
    QT_VERSION = 4
    from PyQt4.QtGui import (
        QWidget,
        QVBoxLayout,
        QLabel,
        QPushButton,
        QLineEdit,
        QHBoxLayout,
        QComboBox,
        QFileDialog
        )
    from PyQt4.QtCore import pyqtSignal, pyqtSlot
except ImportError:
    QT_VERSION = 5
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
from transphire import transphire_utils as tu


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
        self.content = []
        self.layout.setContentsMargins(0, 0, 0, 0)

        self.idx_name = 0
        self.idx_values = 1
        self.idx_dtype = 2
        self.idx_group = 3
        self.idx_type = 4
        self.idx_priority = 5
        self.idx_tooltip = 6

        # Fill content based on typ
        content_function = tu.get_function_dict()[typ]['content']
        if typ == 'Mount':
            button = QPushButton('Delete', self)
            button.clicked.connect(self._button_clicked)
            self.layout.addWidget(button)
            items = content_function(hdd=hdd)
            if hdd is None:
                pass
            else:
                self.setEnabled(False)
        elif typ == 'Copy':
            items = content_function(settings_folder=settings_folder)
        else:
            items = content_function()

        # Fill widget with content items
        self._fill_default(items)

    def _fill_default(self, items):
        """
        Fill the widget with content.

        Arguments:
        items - Content for the widget as list

        Return:
        None
        """
        # Layout
        layout_h = QHBoxLayout()
        self.layout.addLayout(layout_h)
        layout_v = None
        for idx, entry in enumerate(items):
            if idx % 11 == 0:
                if layout_v is not None:
                    layout_v.addStretch(1)
                else:
                    pass
                layout_v = QVBoxLayout()
                layout_h.addLayout(layout_v)
            layout_v.addWidget(QLabel(entry[self.idx_name], self))

            # Behaviour based on typ
            if entry[self.idx_type] == 'COMBO':
                widget = QComboBox(self)
                widget.addItems(entry[self.idx_values])
                widget.setCurrentIndex(0)
                widget.currentIndexChanged.connect(self._change_color_to_changed)
            elif entry[self.idx_type] == 'DIR':
                widget = QLineEdit(entry[self.idx_values], self)
                widget.textChanged.connect(self._change_color_to_changed)
                widget.returnPressed.connect(self._find_dir)
                widget.setPlaceholderText('Press shift+return')
            elif entry[self.idx_type] == 'FILE':
                widget = QLineEdit(entry[self.idx_values], self)
                widget.textChanged.connect(self._change_color_to_changed)
                widget.returnPressed.connect(self._find_file)
                widget.setPlaceholderText('Press shift+return')
            elif entry[self.idx_type] == 'PLAIN':
                widget = QLineEdit(entry[self.idx_values], self)
                widget.textChanged.connect(self._change_color_to_changed)
            else:
                raise IOError('{0}: {1} not known!'.format(entry[self.idx_name], entry[self.idx_type]))

            exclude_typ_list = [
                'Mount',
                'Font',
                'Others',
                'Pipeline',
                'Notification_widget',
                ]
            if self.typ not in exclude_typ_list and not entry[self.idx_name].startswith('WIDGETS'):
                widget_2 = QComboBox(self)
                widget_2.addItems(['Main', 'Advanced', 'Rare'])
                combo_idx = widget_2.findText(entry[self.idx_priority])
                assert combo_idx >= 0, entry
                widget_2.setCurrentIndex(combo_idx)
                widget_2.currentIndexChanged.connect(self._change_color_to_changed)
            else:
                widget_2 = None

            widget.setObjectName('default_settings')
            layout_h_2 = QHBoxLayout()
            layout_h_2.addWidget(widget, stretch=1)
            for test_widget in [widget_2]:
                if test_widget is None:
                    continue
                else:
                    test_widget.setObjectName('default_settings')
                    layout_h_2.addWidget(test_widget, stretch=0)

            layout_v.addLayout(layout_h_2)
            self.content.append({
                'widget': widget,
                'widget_2': widget_2,
                'settings': {
                    'typ': entry[self.idx_type],
                    'name': entry[self.idx_name],
                    'values': entry[self.idx_values],
                    'dtype': entry[self.idx_dtype],
                    'group': entry[self.idx_group],
                    'tooltip': entry[self.idx_tooltip],
                    }
                })
        layout_v.addStretch(1)

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

            for number in ['2']:
                temp_widget = entry['widget_{0}'.format(number)]
                if isinstance(temp_widget, QComboBox):
                    settings['widget_{0}'.format(number)] = temp_widget.currentText()
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
                    print('WARNING: {0} is empty!'.format(key))
                else:
                    pass

            if key == 'Typ' and not widget.isEnabled():
                value = 'Copy_hdd'
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
                    if entry['Typ'][0] == 'Copy_hdd':
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
                            widget.addItem('Copy_hdd')
                            hdd_idx = widget.findText('Copy_hdd')
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
            caption='Find file: {0}'.format(self.typ),
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
        Find directory to insert it into the widget.

        Arguments:
        None

        Return:
        None
        """
        in_dir = QFileDialog.getExistingDirectory(
            caption='Find directory: {0}'.format(self.typ),
            directory=os.getcwd(),
            options=QFileDialog.DontUseNativeDialog
            )
        if in_dir != '':
            self.sender().setText(in_dir)
