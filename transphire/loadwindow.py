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
try:
    from PyQt4.QtGui import QDialog, QVBoxLayout, QPushButton, QWidget, QComboBox, QLineEdit
except ImportError:
    from PyQt5.QtWidgets import QDialog, QVBoxLayout, QPushButton, QWidget, QComboBox, QLineEdit

from transphire.loadcontentcontainer import LoadContentContainer
from transphire.separator import Separator
from transphire.tabdocker import TabDocker
from transphire import transphire_utils as tu


class DefaultSettings(QDialog):
    """
    DefaultSettings dialog.
    Dialog used to enter default values.

    Inherits from:
    QWidget
    """
    def __init__(self, apply, parent=None):
        """
        Setup the layout for the widget.

        Arguments:
        apply - If True, the changes will be applied after saving.
        parent - Parent widget (default None)

        Return:
        None
        """

        super(DefaultSettings, self).__init__(parent)

        # Add new tab widget for the settings to layout
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

        self.tab_widget = TabDocker(self)
        layout.addWidget(self.tab_widget)
        self.tab_widget.setObjectName('tab')

        self.default_tabs = {
            'External software': [
                [
                    'CTFFIND4',
                    'Gctf',
                    'CTER',
                    'MotionCor2',
                    'crYOLO'
                    ],
                TabDocker(self)
                ],
            'TranSPHIRE settings': [
                [
                    'Mount',
                    'Pipeline',
                    'General',
                    'Notification',
                    'Others',
                    'Font',
                    'Copy',
                    'Path'
                    ],
                TabDocker(self)
                ]
            }
        for tab_name in self.default_tabs:
            self.default_tabs[tab_name][1].setObjectName('tab')
            self.tab_widget.add_tab(self.default_tabs[tab_name][1], tab_name)

        # Variables
        self.apply = False
        self.overwrite = True

        # Add buttons
        done_button = QPushButton('Quit dialog and start TranSPHIRE.', self)
        layout.addWidget(Separator(typ='horizontal', color='#68a3c3'))
        layout.addWidget(done_button)
        done_button.clicked.connect(lambda: self.check_modified_widgets(done=True))
        if apply:
            done_button.setText('Quit dialog without applying changes.')
            layout.addWidget(Separator(typ='horizontal', color='#68a3c3'))
            apply_button = QPushButton('Quit dialog and apply changes.', self)
            apply_button.clicked.connect(lambda: self.check_modified_widgets(done=False))
            layout.addWidget(apply_button)


    def check_modified_widgets(self, done):
        """
        Check, if a widget is modified before saving.

        Arguments:
        done - If True, close after input, else apply settings.

        Return:
        True if no modification, else False
        """
        text_modified = False
        wrongly_mod_list = []
        for idx in range(self.tab_widget.count()):
            widget = self.tab_widget.widget(idx)
            for idx_subtab in range(widget.count()):
                widget_subtab = widget.widget(idx_subtab)
                for entry in widget_subtab.content:
                    for info in entry.content:
                        if tu.get_style(typ='changed') == info['widget'].styleSheet() or \
                                tu.get_style(typ='error') == info['widget'].styleSheet():
                            text_modified = True
                            wrongly_mod_list.append(info)
                        else:
                            continue

        if text_modified:
            result = tu.question(
                head='Unsaved changes',
                text='You do have unsaved changes!\nDo you really want to continue?.\nThose changes will not be saved or applied.',
                parent=self
                )
        else:
            result = True

        # Result is True if answer is Yes
        if not result:
            return False
        elif done:
            for info in wrongly_mod_list:
                if isinstance(info['widget'], QLineEdit):
                    info['widget'].setText(info['settings']['values'])
                elif isinstance(info['widget'], QComboBox):
                    idx = info['widget'].findText(info['settings']['values'][0])
                    info['widget'].setCurrentIndex(idx)
                else:
                    raise Exception('Instance not known! Please contact the TranSPHIRE authors!')
            self.accept()
        else:
            for info in wrongly_mod_list:
                if isinstance(info['widget'], QLineEdit):
                    info['widget'].setText(info['settings']['values'])
                elif isinstance(info['widget'], QComboBox):
                    idx = info['widget'].findText(info['settings']['values'][0])
                    info['widget'].setCurrentIndex(idx)
                else:
                    raise Exception('Instance not known! Please contact the TranSPHIRE authors!')
            self.accept_apply()

        return True

    def closeEvent(self, event):
        """
        Handle the close event.

        Arguments:
        event - Close event

        Return:
        None
        """
        if self.check_modified_widgets(done=True):
            pass
        else:
            event.ignore()

    def accept_apply(self):
        """
        Set the apply settings variable to True before saving.

        Argumens:
        None

        Return:
        None
        """
        self.apply = True
        self.accept()

    def add_tab(self, widget, name):
        """
        Add a new widget to the tab widget

        Arguments:
        widget - Widget to add as new tab
        Name - Name of the new tab

        Return:
        None
        """
        is_inside = False
        for key in self.default_tabs:
            compare = self.default_tabs[key][0]
            tab_widget = self.default_tabs[key][1]
            for tab_name in compare:
                if name.startswith(tab_name):
                    is_inside = True
                    tab_widget.add_tab(widget, name)
                else:
                    pass
        if not is_inside:
            raise OSError('Name {0} not known! Please fix before continuation'.format(name))
        else:
            pass

    def get_apply(self):
        """
        Getter for the self.apply variable.

        Arguments:
        None

        Return:
        Content of self.apply
        """
        return self.apply

    @staticmethod
    def get_content_default(
            edit_settings,
            apply,
            settings_folder
            ):
        """
        Staticmethod to open the default content dialog.

        Arguments:
        edit_settings - If True, open default settings dialog, else just return content
        apply - Apply settings after closing the default settings dialog
        settings_folder - Folder to store the default settings

        Return:
        Content for the widgets, Content of the apply variable
        """
        # Initialise default settings
        setting_names = sorted(tu.get_function_dict().keys())
        default_widget = DefaultSettings(apply=apply)

        # Initialise a new LoadContentContainer and add it as a new tab
        # Load default settings from settings file into LoadContentContainer
        content_temp = {}
        for name in setting_names:
            default_file = '{0}/content_{1}.txt'.format(settings_folder, name.replace(' ', '_'))
            content_temp[name] = LoadContentContainer(
                typ=name,
                file_name=default_file,
                settings_folder=settings_folder,
                )
            default_widget.add_tab(widget=content_temp[name], name=name)
            try:
                with open(default_file, 'r') as file_r:
                    settings = json.load(file_r)
            except FileNotFoundError:
                pass
            else:
                content_temp[name].set_settings(settings)

        # If edit settings, open default settings dialog
        if edit_settings:
            result = default_widget.exec_()
            if result:
                apply = default_widget.get_apply()
            else:
                apply = None
        else:
            apply = None

        # Refresh content of LoadContentContainer by the provided default settings
        content = {}
        for name in setting_names:
            default_file = '{0}/content_{1}.txt'.format(settings_folder, name.replace(' ', '_'))
            content[name] = content_temp[name].get_settings()
            if name == 'Mount':
                continue
            elif not os.path.exists(default_file):
                print('INFORMATION: {0} default settings not modified!'.format(name))
            else:
                with open(default_file, 'r') as file_r:
                    data = json.load(file_r)
                    for entry in data:
                        for dictionary in entry:
                            for name_content in content[name]:
                                for default_value in name_content:
                                    if default_value.keys() == dictionary.keys():
                                        for key in default_value:
                                            default = dictionary[key][0]
                                            default_value[key][0] = default
                                        break
                                    else:
                                        pass
        return content, apply
