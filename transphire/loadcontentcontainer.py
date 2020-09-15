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
import json
import copy
from PyQt5.QtWidgets import QWidget, QPushButton, QVBoxLayout, QHBoxLayout, QComboBox, QLabel
from PyQt5.QtCore import pyqtSlot

from . import transphire_utils as tu

class LoadContentContainer(QWidget):
    """
    LoadContentContainer widget
    Inherits from:
    QWidget

    Buttons:
    Save settings - Save currently defined settings to settings files
    Add - Add new Mount entry (Case Mount)
    """

    def __init__(self, typ, template_name, templates, settings_folder, is_shared, default_file, parent=None):
        """
        Setup the layout for the widget

        Arguments:
        typ - Typ/Name of content container
        file_name - File name for the saving settings
        parent - Parent widget (default None)

        Return:
        None
        """
        super(LoadContentContainer, self).__init__(parent)

        # Variables
        self.layout = QHBoxLayout()
        self.content = []
        self.template_name = template_name
        self.settings_folder = settings_folder
        self.typ = typ
        self.name = '{0} settings'.format(self.typ)
        self.tab_widget = None
        self.file = default_file
        self.default_settings = None
        self.prev_item = self.template_name

        # Layout
        layout = QVBoxLayout(self)
        if not is_shared:

            layout_h1 = QHBoxLayout()
            layout_h1.addWidget(QLabel('Copy from:', self))
            combo_box = QComboBox(self)
            combo_box.addItems([entry for entry in templates if entry != 'SHARED'])
            combo_box.setCurrentText(template_name)
            combo_box.currentTextChanged.connect(self.copy_from_template)
            layout_h1.addWidget(combo_box)
            layout_h1.addStretch(1)
            layout.addLayout(layout_h1)

        # Save button
        save_button = QPushButton('Save settings', self)
        save_button.clicked.connect(self.save_settings)

        # Typ based settings
        if self.typ == 'Mount':
            self.tab_widget = TabDocker(self)
            self.tab_widget.setMovable(True)
            self.layout.addWidget(self.tab_widget)
            add_button = QPushButton(self)
            add_button.clicked.connect(self.add_widget)
            layout.addWidget(add_button)
            layout.addWidget(Separator(typ='horizontal', color='black'))
            add_button.setText('Add mount point')
            hdd = True
        else:
            hdd = None

        # Add HDD entry
        self.add_widget(name='HDD', hdd=hdd)
        self.setWindowTitle(self.name)

        # Add layout to global layout
        layout.addLayout(self.layout)
        layout.addStretch(1)
        layout.addWidget(Separator(typ='horizontal', color='black'))
        layout.addWidget(save_button)

        # Set minimum width of widget
        title_length = len(self.windowTitle())
        self.setMinimumWidth(title_length * 21)

    @pyqtSlot(str)
    def copy_from_template(self, template):
        result = tu.question(
            head='Change template.',
            text='Changing the template will overwrite all unsaved changes!\nDo you really want to continue?.',
            )
        if result:
            default_file = os.path.join(self.settings_folder, template, os.path.basename(self.file))
            try:
                with open(default_file, 'r') as file_r:
                    settings = json.load(file_r)
            except FileNotFoundError:
                #tu.message('The template {0} does not have settings for this File, fall back to default settings.'.format(template))
                settings = self.default_settings
            self.set_settings(settings)
            self.prev_item = template
        else:
            self.sender().blockSignals(True)
            self.sender().setCurrentText(self.prev_item)
            self.sender().blockSignals(False)

    @pyqtSlot()
    def add_widget(self, name=None, hdd=None):
        """
        Add new widget to layout.

        Arguments:
        name - Name of new mount point (default None)
        hdd - Is hdd entry (default None)

        Return:
        None
        """
        # Widget for entry
        separator_1 = Separator(typ='vertical', color='white')
        separator_2 = Separator(typ='vertical', color='white')
        widget = LoadContent(
            typ=self.typ,
            hdd=hdd,
            parent=self,
            separator=[separator_1, separator_2],
            settings_folder=self.settings_folder,
            )
        widget.delete.connect(self.remove_widget)
        self.content.append(widget)

        # If tab_widget exists, add to tab_widget, else to layout
        if self.tab_widget is not None:
            if name is None:
                self.tab_widget.add_tab(
                    widget,
                    'Mount {0}'.format(self.tab_widget.count() + 1)
                    )
            else:
                self.tab_widget.add_tab(widget, name)
        else:
            self.layout.addWidget(separator_1, stretch=0)
            self.layout.addWidget(widget, stretch=1)
            self.layout.addWidget(separator_2, stretch=0)
        self.default_settings = self.get_settings()

    @pyqtSlot(object)
    def remove_widget(self, separator):
        """
        Remove widget from layout.

        Arguments:
        separator - List of seperator widgets

        Return:
        None
        """
        # Sending widget
        widget = self.sender()

        # If tab widget exists, remove from tab widget, else from layout
        if self.tab_widget is not None:
            idx = self.tab_widget.indexOf(widget)
            self.tab_widget.removeTab(idx)

            # Rename mount entry widgets
            for idx in range(self.tab_widget.count()):
                if self.tab_widget.tabText(idx).startswith('Mount '):
                    self.tab_widget.setTabText(idx, 'Mount {0}'.format(idx + 1))
                else:
                    pass
        else:
            self.layout.removeWidget(widget)

        # Remove from content
        self.content.remove(widget)
        widget.setParent(None)
        for entry in separator:
            self.layout.removeWidget(entry)
            entry.setParent(None)

    def save_settings(self):
        """
        Save settings specified in widget to json text file.

        Arguments:
        None

        Return:
        None
        """
        settings = copy.deepcopy(self.get_settings())

        if settings is None:
            return None

        for entry in settings:
            for widget in entry:
                for key in widget:
                    widget[key][1].pop('dtype')

        try:
            with open(self.file, 'w') as file_w:
                json.dump(settings, file_w, indent=1)
        except PermissionError:
            tu.message('{0} - Permission denied!\nYou are not allowed to change TranSHPIRE wide settings!\nPlease contact your system administrator'.format(self.file))
        else:
            tu.message('{0} saved!'.format(self.name))

    def get_settings_tab(self):
        """
        Get settings from tab widget.

        Arguments:
        None

        Return:
        List of widget settings
        """
        settings = []
        for idx in range(self.tab_widget.count()):
            widget = self.tab_widget.widget(idx)
            entry_settings = widget.get_settings()
            if entry_settings is None:
                return None
            else:
                settings.append(entry_settings)
        return settings

    def get_settings_widget(self):
        """
        Get settings from normal widget.

        Arguments:
        None

        Return:
        List of widget settings
        """
        settings = []
        for entry in self.content:
            entry_settings = entry.get_settings()
            if entry_settings is None:
                return None
            else:
                settings.append(entry_settings)
        return settings

    def get_settings(self):
        """
        Get settings from tab or normal normal widget.

        Arguments:
        None

        Return:
        List of widget settings
        """
        if self.tab_widget is None:
            settings = self.get_settings_widget()
        else:
            settings = self.get_settings_tab()

        return settings

    def set_settings(self, settings):
        """
        Set settings to widget.

        Arguments:
        settings - List of widget settings

        Return:
        None
        """
        for idx, entry in enumerate(settings):
            if self.typ == 'Mount':
                name = entry[0]['Mount name'][0]
                if idx != 0:
                    self.add_widget(name=name)
                else:
                    self.tab_widget.setTabText(idx, name)
            else:
                pass
            if self.typ == 'Path':
                for vals in entry:
                    for key, value in list(vals.items()):
                        new_key = key.replace(' v', ' >=v')
                        if new_key != key:
                            vals[new_key] = value
                            vals[new_key][1]['name'] = new_key
                            del vals[key]
            self.content[idx].set_settings(entry)

from .tabdocker import TabDocker
from .loadcontent import LoadContent
from .separator import Separator
