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
import glob
import json
import copy
from PyQt5.QtWidgets import QDialog, QVBoxLayout, QPushButton, QWidget, QComboBox, QLineEdit, QLabel, QHBoxLayout
from PyQt5.QtCore import pyqtSlot

from . import transphire_utils as tu

class DefaultSettings(QDialog):
    """
    DefaultSettings dialog.
    Dialog used to enter default values.

    Inherits from:
    QDialog
    """
    def __init__(self, apply, settings_directory, template_name, parent=None):
        """
        Setup the layout for the widget.

        Arguments:
        apply - If True, the changes will be applied after saving.
        parent - Parent widget (default None)

        Return:
        None
        """

        super(DefaultSettings, self).__init__(parent)

        self.settings_directory = settings_directory
        self.current_template = template_name
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

        layout_h = QHBoxLayout()
        load_button = QPushButton('Load template', self)
        load_button.clicked.connect(self.load_template)
        self.template_name = QLabel('No template selected', self)
        layout_h.addWidget(load_button)
        layout_h.addWidget(self.template_name)
        layout.addLayout(layout_h)
        layout.addWidget(Separator(typ='horizontal', color='#68a3c3'))

        self.tab_widget = TabDocker(self)
        layout.addWidget(self.tab_widget)
        self.tab_widget.setObjectName('tab')
        self.tab_content = {}

        self.default_tabs = {}

        self.fill_default_dict()

        self.default_tabs['OLD'] = {
            'sub_content': copy.deepcopy(self.default_tabs),
            'content': [],
            }

        self.create_initial_tabs(self.default_tabs, self.tab_widget)

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

    def fill_default_dict(self):
        """
        Fill the default dict with the information from the function dict.

        Arguments:
        None - The self.default_dict is used

        Returns:
        None - The self.default_dict is changed in-place
        """
        function_dict = tu.get_function_dict()
        for name_version, content in function_dict.items():
            name = name_version.split(' >=')[0]
            typ = content['typ']
            category = content['category']
            if typ is None:
                self.default_tabs \
                    .setdefault(category, {}) \
                    .setdefault('content', []) \
                    .append(name)
                self.default_tabs[category]['sub_content'] = {}
            else:
                self.default_tabs \
                    .setdefault(category, {}) \
                    .setdefault('sub_content', {}) \
                    .setdefault(typ, {}) \
                    .setdefault('sub_content', {}) \
                    .setdefault(name, {}) \
                    .setdefault('content', []).append(name)
                self.default_tabs[category]['content'] = []
                self.default_tabs[category]['sub_content'][typ]['content'] = []
                self.default_tabs[category]['sub_content'][typ]['sub_content'][name]['sub_content'] = {}


    def create_initial_tabs(self, tab_dict, parent_widget, is_old=False):
        for tab_name in tab_dict:
            if is_old:
                cur_tab_name = 'OLD {0}'.format(tab_name)
                tab_dict[tab_name]['content'] = ['OLD {0}'.format(entry) for entry in tab_dict[tab_name]['content']]
            else:
                cur_tab_name = tab_name

            if tab_name == 'OLD':
                is_old = True

            self.tab_content[cur_tab_name] = TabDocker(self)
            self.tab_content[cur_tab_name].setObjectName('tab')
            parent_widget.add_tab(self.tab_content[cur_tab_name], tab_name)

            self.create_initial_tabs(tab_dict[tab_name]['sub_content'], self.tab_content[cur_tab_name], is_old)

    def is_in_content(self, tab_dict, name):
        for tab_name in tab_dict:
            for entry in tab_dict[tab_name]['content']: 
                if name.split(' >=')[0] == entry:
                    return tab_name if not name.startswith('OLD') else 'OLD {0}'.format(tab_name)

            found = self.is_in_content(tab_dict[tab_name]['sub_content'], name)
            if found:
                return found
        return False

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
        for tab_widget in self.tab_content.values():
            for idx in range(tab_widget.count()):
                try:
                    widgets = tab_widget.widget(idx).content
                except AttributeError:
                    pass
                else:
                    for widget_subtab in widgets:
                        for info in widget_subtab.content:
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
                )
        else:
            result = True

        # Result is True if answer is Yes
        if not result:
            return False
        elif done is None:
            for info in wrongly_mod_list:
                if isinstance(info['widget'], QLineEdit):
                    info['widget'].setText(info['settings']['values'])
                elif isinstance(info['widget'], QComboBox):
                    idx = info['widget'].findText(info['settings']['values'][0])
                    info['widget'].setCurrentIndex(idx)
                else:
                    raise Exception('Instance not known! Please contact the TranSPHIRE authors!')
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
        inside_name = self.is_in_content(self.default_tabs, name)
        if not inside_name:
            raise OSError('Name {0} not known! Please fix before continuation'.format(name))
        else:
            pass

        self.tab_content[inside_name].add_tab(widget, name.split('OLD ')[-1])

    def recursive_clear(self, tab_widget):
        count = tab_widget.count()
        for idx in reversed(range(count)):
            widget = tab_widget.widget(idx)
            if isinstance(widget, TabDocker):
                self.recursive_clear(widget)
            else:
                tab_widget.removeTab(idx)
                widget.setParent(None)
                del widget

    def clear_tabs(self):
        self.recursive_clear(self.tab_widget)

    def get_apply(self):
        """
        Getter for the self.apply variable.

        Arguments:
        None

        Return:
        Content of self.apply
        """
        return self.apply

    @pyqtSlot()
    def load_template(self):
        template_dialog = TemplateDialog(self.settings_directory)
        result = template_dialog.exec_()
        if result:
            if self.check_modified_widgets(done=None):
                self.current_template = template_dialog.template
                self.clear_tabs()
                self.add_tabs()

    def add_tabs(self):
        template_folder = sorted([
            os.path.basename(entry)
            for entry in glob.glob(os.path.join(self.settings_directory, '*'))
            if os.path.isdir(entry)
            ])

        self.template_name.setText('Current template: {0}'.format(self.current_template))

        content_temp = {}
        for template_name in template_folder:
            template_directory = os.path.join(self.settings_directory, template_name)

            setting_names = tu.get_function_dict().keys()
            content_temp[template_name] = {}
            for name in reversed(list(setting_names)):
                directory = template_directory
                is_shared = False
                for entry in self.default_tabs['TranSPHIRE settings']['content']:
                    if entry in name:
                        directory = os.path.join(self.settings_directory, 'SHARED')
                        is_shared = True
                        break
                default_file = '{0}/content_{1}.txt'.format(directory, name.replace(' ', '_'))
                if not os.path.isfile(default_file):
                    default_file = '{0}/content_{1}.txt'.format(directory, name.replace(' ', '_').replace('>=', ''))
                assert name not in content_temp[template_name]
                content_temp[template_name][name] = LoadContentContainer(
                    typ=name,
                    template_name=template_name,
                    templates=template_folder,
                    settings_folder=self.settings_directory,
                    is_shared=is_shared,
                    default_file=default_file,
                    )

                try:
                    with open(default_file, 'r') as file_r:
                        settings = json.load(file_r)
                except FileNotFoundError:
                    pass
                else:
                    content_temp[template_name][name].set_settings(settings)

                if template_name == self.current_template:
                    if tu.get_function_dict()[name]['old']:
                        current_name = 'OLD {0}'.format(name)
                    else:
                        current_name = name
                    self.add_tab(widget=content_temp[template_name][name], name=current_name)
                else:
                    content_temp[template_name][name].setVisible(False)
        return content_temp

    @staticmethod
    def get_content_default(
            edit_settings,
            apply,
            settings_folder,
            template_name,
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
        default_widget = DefaultSettings(apply=apply, settings_directory=settings_folder, template_name=template_name)

        templates = sorted([
            os.path.basename(entry)
            for entry in glob.glob(os.path.join(settings_folder, '*'))
            if os.path.isdir(entry)
            ])
        content_temp = default_widget.add_tabs()

        # Initialise a new LoadContentContainer and add it as a new tab
        # Load default settings from settings file into LoadContentContainer

        # If edit settings, open default settings dialog
        if edit_settings:
            result = default_widget.exec_()
            content_temp = default_widget.add_tabs()
            if result:
                apply = default_widget.get_apply()
            else:
                apply = None
        else:
            apply = None

        # Refresh content of LoadContentContainer by the provided default settings
        templates = sorted([
            os.path.basename(entry)
            for entry in glob.glob(os.path.join(settings_folder, '*'))
            if os.path.isdir(entry)
            ])

        content = {}
        for template in templates:
            content[template] = {}
            for name in setting_names:
                directory = os.path.join(settings_folder, template)
                for entry in default_widget.default_tabs['TranSPHIRE settings']['content']:
                    if entry in name:
                        directory = settings_folder
                        break
                default_file = '{0}/content_{1}.txt'.format(directory, name.replace(' ', '_'))
                if not os.path.isfile(default_file):
                    default_file = '{0}/content_{1}.txt'.format(directory, name.replace(' ', '_').replace('>=', ''))
                content[template][name] = content_temp[template][name].get_settings()
                if name == 'Mount':
                    continue
                elif not os.path.exists(default_file):
                    pass
                else:
                    with open(default_file, 'r') as file_r:
                        data = json.load(file_r)
                        for entry in data:
                            for dictionary in entry:
                                for name_content in content[template][name]:
                                    for default_value in name_content:
                                        if default_value.keys() == dictionary.keys():
                                            for key in default_value:
                                                default = dictionary[key][0]
                                                widget_2 = dictionary[key][1]['widget_2']
                                                default_value[key][0] = default
                                                default_value[key][1]['widget_2'] = widget_2
                                            break
                                        else:
                                            pass
        return content, apply

from .loadcontentcontainer import LoadContentContainer
from .separator import Separator
from .tabdocker import TabDocker
from .templatedialog import TemplateDialog
