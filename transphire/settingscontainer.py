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
import glob
import os
from PyQt5.QtWidgets import QWidget, QHBoxLayout, QVBoxLayout, QScrollArea, QLabel
from PyQt5.QtCore import pyqtSlot, pyqtSignal

from . import transphire_utils as tu

class SettingsContainer(QWidget):
    """
    Widget for setting widgets.

    Inherits:
    QWidget
    """
    sig_change_use_movie = pyqtSignal(int)
    sig_adjust_tab = pyqtSignal(object, str)

    def __init__(self, content, name, global_dict, settings_folder, mount_worker, parent=None, **kwargs):
        """
        Initialise layout of the widget.

        Arguments:
        content - Content for the widget
        max_widgets - Maximum widgets per column
        parent - Parent widget (default None)

        Returns:
        None
        """
        super(SettingsContainer, self).__init__(parent)

        self.parent = parent
        self.name = name
        self.global_dict = None
        self.input_file_names = []
        try:
            content_others = kwargs['content_others']
        except KeyError:
            content_others = None
        try:
            content_mount = kwargs['content_mount']
            self.content_mount = {}
            for entry in content_mount:
                for widget in entry:
                    for key in widget:
                        if key == 'Mount name':
                            current_name = widget[key][0]
                        if key == 'Typ':
                            if widget[key][0] == 'Import':
                                self.content_mount[current_name] = os.path.join(settings_folder, current_name).replace(' ', '_')
 
        except KeyError:
            self.content_mount = None

        # TabDocker widget for Main and Advanced
        my_tab_docker = TabDocker(self)
        my_tab_docker.setTabPosition('South')
        my_tab_docker.tab_widget.setObjectName('bot')
        layout_main = QVBoxLayout(self)
        layout_main.setContentsMargins(0, 0, 0, 0)

        self.layout_dict = {
            'Main_count': 0,
            'Advanced_count': 0,
            'Rare_count': 0,
            }
        important_note = ''
        for entry in content:
            for widget in entry:
                for key in widget:
                    if key == 'WIDGETS MAIN':
                        self.layout_dict['Main_max'] = int(widget[key][0])
                    elif key == 'WIDGETS ADVANCED':
                        self.layout_dict['Advanced_max'] = int(widget[key][0])
                    elif key == 'WIDGETS RARE':
                        self.layout_dict['Rare_max'] = int(widget[key][0])
                    elif key == 'IMPORTANT':
                        important_note = widget[key][0]
                    else:
                        self.layout_dict['{}_count'.format(widget[key][1]['widget_2'])] += 1
                        continue

        if important_note:
            important_widget = QLabel(important_note)
            important_widget.setObjectName('important')
            layout_main.addWidget(important_widget)
        layout_main.addWidget(my_tab_docker)

        for dict_name in ['Main', 'Advanced', 'Rare']:
            widget = QWidget(self)
            widget.setObjectName('settings')

            self.layout_dict[dict_name] = QHBoxLayout(widget)
            self.layout_dict[dict_name].setContentsMargins(3, 3, 3, 3)
            self.layout_dict[dict_name].addStretch(1)

            self.layout_dict['{0}_v'.format(dict_name)] = None
            self.layout_dict['{0}_idx'.format(dict_name)] = 0

            scroll_area = QScrollArea(my_tab_docker)
            scroll_area.setWidgetResizable(True)
            scroll_area.setWidget(widget)
            my_tab_docker.add_tab(scroll_area, '{}: {}'.format(dict_name, self.layout_dict['{}_count'.format(dict_name)]))

        # Global content
        self.content = {}
        self.group = {}

        # Add to layout
        for entry in content:
            for widget in entry:
                for key in widget:
                    if key == 'WIDGETS MAIN' or key == 'WIDGETS ADVANCED' or key == 'WIDGETS RARE' or key == 'IMPORTANT':
                        continue
                    layout_name = widget[key][1]['widget_2']
                    widget_name = widget[key][1]['name']
                    group = widget[key][1]['group']

                    if self.layout_dict['{0}_idx'.format(layout_name)] % self.layout_dict['{0}_max'.format(layout_name)] == 0:
                        if self.layout_dict['{0}_v'.format(layout_name)] is not None:
                            self.layout_dict[layout_name].addWidget(Separator(typ='vertical', color='lightgrey'))
                            self.layout_dict['{0}_v'.format(layout_name)].addStretch(1)
                        else:
                            pass
                        self.layout_dict['{0}_v'.format(layout_name)] = QVBoxLayout()
                        self.layout_dict['{0}_v'.format(layout_name)].setContentsMargins(0, 0, 0, 0)
                        self.layout_dict[layout_name].addLayout(self.layout_dict['{0}_v'.format(layout_name)])

                    settings_widget = SettingsWidget(
                        content=widget[key],
                        name=name,
                        content_others=content_others,
                        mount_directory=mount_worker.mount_directory,
                        global_dict=global_dict,
                        input_file_names=self.input_file_names,
                        parent=self
                        )

                    if self.name == 'Copy':
                        try:
                            settings_widget.edit.currentTextChanged.connect(self.prepare_send_adjust)
                        except AttributeError:
                            pass

                    if widget[key][1]['name'] == 'Use movies':
                        try:
                            settings_widget.edit.currentIndexChanged.connect(self.sig_change_use_movie.emit)
                        except AttributeError:
                            pass

                    if group and name not in ('Pipeline'):
                        group, state = group.split(':')
                        self.group.setdefault(group, [])
                        self.group[group].append([settings_widget, state, widget_name])
                    self.content[widget_name] = settings_widget
                    self.layout_dict['{0}_v'.format(layout_name)].addWidget(settings_widget)
                    self.layout_dict['{0}_idx'.format(layout_name)] += 1

        for key in self.group:
            self.content[key].sig_index_changed.connect(self.change_state)
            self.change_state(name=key)

        for dict_name in ['Main', 'Advanced', 'Rare']:
            try:
                self.layout_dict['{0}_v'.format(dict_name)].addStretch(1)
                self.layout_dict[dict_name].addStretch(1)
            except AttributeError:
                pass

    def emit_signals(self):
        for key in self.content:
            try:
                self.content[key].edit.currentTextChanged.emit(
                    self.content[key].edit.currentText()
                    )
            except AttributeError:
                pass

    @pyqtSlot(str)
    def prepare_send_adjust(self, text):
        self.sig_adjust_tab.emit(self.sender(), text)

    @pyqtSlot(str)
    def change_state(self, name):
        """
        Change the state of widgets based on the choice of the corresponding combo box

        name - Name of the group to change status (Emitted by the combo box)

        Returns:
        None
        """
        try:
            for entry in self.group[name]:
                widget = entry[0]
                state = entry[1]
                sub_name = entry[2]
                if not self.content[name].isEnabled():
                    widget.setEnabled(False)
                elif self.content[name].edit.currentText() == state:
                    widget.setEnabled(True)
                else:
                    widget.setEnabled(False)
                self.change_state(name=sub_name)
        except KeyError:
            return None

    def get_input_names(self):
        return self.input_file_names

    def get_settings(self, quiet=False):
        """
        Get the settings as dict

        Arguments:
        quiet - If True, no prints are executed

        Returns:
        Settings as dictionary
        """
        settings = {}
        error = False
        for key in self.content:
            dictionary = self.content[key].get_settings(quiet=quiet)
            if dictionary is None:
                error = True
            else:
                settings.update(dictionary)
            if self.name == 'Copy':
                new_key = '{0}_entries'.format(key.replace(' ', '_'))
                try:
                    entries = self.content[key].get_combo_entries()
                except AttributeError:
                    pass
                else:
                    test_list = ['False', 'True']
                    if set(test_list) == set(entries):
                        continue
                    elif 'Symlink' in entries:
                        continue
                    settings[new_key] = self.content[key].get_combo_entries()
            else:
                pass
        if error:
            return None
        else:
            return [settings]

    def set_design(self, settings):
        """
        Set settings to the widgets

        Arguments:
        settings - Settings to set.

        Returns:
        None
        """

        # Clear old layout design
        for dict_name in ['Main', 'Advanced', 'Rare']:
            self.layout_dict['{0}_max'.format(dict_name)] = int(settings['WIDGETS {0}'.format(dict_name.upper())])
            self.layout_dict['{0}_v'.format(dict_name)] = None
            self.layout_dict['{0}_idx'.format(dict_name)] = 0
            for idx in reversed(range(self.layout_dict[dict_name].count())):
                item = self.layout_dict[dict_name].itemAt(idx)
                self.layout_dict[dict_name].removeItem(item)
                if isinstance(item, QVBoxLayout):
                    for idx in reversed(range(item.count())):
                        item2 = item.itemAt(idx)
                        item.removeItem(item2)
                    item.setParent(None)
                else:
                    try:
                        item.widget().setParent(None)
                    except AttributeError:
                        pass
            self.layout_dict[dict_name].addStretch(1)

        for key in settings:
            if key == 'WIDGETS MAIN' or key == 'WIDGETS ADVANCED' or key == 'WIDGETS RARE':
                continue
            layout_name = settings[key]
            try:
                widget = self.content[key]
            except KeyError:
                if self.name == 'Path':
                    continue
                elif key == 'IMPORTANT':
                    continue
                else:
                    raise

            if self.layout_dict['{0}_idx'.format(layout_name)] % self.layout_dict['{0}_max'.format(layout_name)] == 0:
                if self.layout_dict['{0}_v'.format(layout_name)] is not None:
                    self.layout_dict[layout_name].addWidget(Separator(typ='vertical', color='lightgrey'))
                    self.layout_dict['{0}_v'.format(layout_name)].addStretch(1)
                else:
                    pass
                self.layout_dict['{0}_v'.format(layout_name)] = QVBoxLayout()
                self.layout_dict['{0}_v'.format(layout_name)].setContentsMargins(0, 0, 0, 0)
                self.layout_dict[layout_name].addLayout(self.layout_dict['{0}_v'.format(layout_name)])

            self.layout_dict['{0}_v'.format(layout_name)].addWidget(widget)
            self.layout_dict['{0}_idx'.format(layout_name)] += 1

        for dict_name in ['Main', 'Advanced', 'Rare']:
            try:
                self.layout_dict['{0}_v'.format(dict_name)].addStretch(1)
                self.layout_dict[dict_name].addStretch(1)
            except AttributeError:
                pass

    def set_settings(self, settings):
        """
        Set settings to the widgets

        Arguments:
        settings - Settings to set.

        Returns:
        None
        """
        for key in settings:
            if key.endswith('_global'):
                continue
            try:
                content = self.content[key]
            except KeyError:
                try: # This block has been introduced for backwards compatibility changes.
                    content = self.content[key.replace(' v', ' >=v')]
                except KeyError:
                    if self.name == 'Copy' and key.endswith('_entries'):
                        continue
                    else:
                        #print('Content for {0} is disabled.'.format(key))
                        continue

            try:
                key_global = '{0}_global'.format(key)
                global_settings = settings[key_global] if key_global in settings else None
                content.set_settings(settings[key], global_settings)
            except KeyError:
                if self.name == 'Copy' and key.endswith('_entries'):
                    continue
                else:
                    print(
                        'Setting changed: {0}!'.format(key),
                        'Please do provide new values'
                        )

    def enable(self, var, use_all):
        """
        Disable or enable all widgets

        Arguments:
        var - If True, enable the widgets, else disable them
        use_all - If True, all widgets are enabled/disabled

        Returns:
        None
        """
        for key in self.content:
            if use_all:
                self.content[key].setEnabled(var)
            else:
                self.content[key].setEnabled(var)

        if var:
            try:
                self.set_settings(self.get_settings(quiet=True)[0])
            except TypeError:
                pass
        else:
            pass

    def set_global(self, global_dict):
        self.global_dict = global_dict
        for key in self.content:
            try:
                self.content[key].edit.textChanged.connect(self.update_global)
            except AttributeError:
                self.content[key].edit.currentTextChanged.connect(self.update_global)
        self.emit_global()

    @pyqtSlot(int)
    def emit_global(self, _=None):
        for key in self.content:
            try:
                self.content[key].edit.textChanged.emit(self.content[key].edit.text())
            except AttributeError:
                self.content[key].edit.currentTextChanged.emit(self.content[key].edit.currentText())

    @pyqtSlot(str, str)
    def set_new_model(self, weights, threshold):
        self.content['--weights'].edit.setText(weights)
        self.content['--confidence_threshold'].edit.setText(threshold)

    @pyqtSlot(str)
    def update_global(self, text):
        if self.sender().parent().name not in self.global_dict:
            return

        for entry in self.global_dict[self.sender().parent().name]:

            is_movie_mode = None
            try:
                is_movie_mode = entry.parent.content['Use movies'].get_settings()['Use movies'] == 'True'
            except KeyError:
                pass

            if is_movie_mode is None:
                pass
            elif is_movie_mode and self.sender().parent().name == 'Pixel size bin':
                continue
            elif not is_movie_mode and self.sender().parent().name == 'Pixel size':
                continue

            entry.global_value = text
            try:
                if entry.widget_auto.isChecked():
                    try:
                        entry.edit.setText(text)
                    except AttributeError:
                        entry.edit.setCurrentText(text)

                    entry.widget_auto.toggled.emit(True)
            except AttributeError:
                pass


    def search_for_projects(self, project_dir):
        text = self.content['Software'].get_settings()['Software']
        project_dir = os.path.realpath(project_dir)

        if text.startswith('EPU'):
            if not [entry for entry in os.listdir(project_dir) if entry.startswith('Images-Disc')]:
                tu.message('Could not find "Images-Disc" folder in the specified directory! Please check if you specified the correct project directory created by EPU or your EPU version is correct.')
                return


            mount_path = None
            for key in self.content_mount:
                if os.stat(self.content_mount[key]).st_size == 0:
                    continue
                with open(self.content_mount[key], 'r') as read:
                    current_mount_path = os.path.realpath(read.readline().split('\t')[2])
                if project_dir.startswith(current_mount_path):
                    mount_path = current_mount_path
                    break

            if mount_path is None:
                tu.message('Could not identify related mounted mount point. Please provide the "Input project path for frames", "Input project path for jpg" and "Input frames extension" manually.')
                return

            matches = []
            self.recursive_search(mount_path, os.path.basename(project_dir), matches)

            if len(matches) in (1, 2):
                pass
            elif not matches:
                tu.message('Could not find project {0} in specified mount directory {1}. Please provide the "Input project path for frames", "Input project path for jpg" and "Input frames extension" manually.'.format(project_dir, mount_path))
                return
            else:
                tu.message('Found more than 2 folders with the name {0} in specified mount directory {1}. Please provide the "Input project path for frames", "Input project path for jpg" and "Input frames extension" manually.'.format(project_dir, mount_path))
                return

            is_meta = []
            is_frames = []
            extension = []
            possible_extensions = self.content['Input frames extension'].get_combo_entries()
            for entry in matches:
                files = glob.glob(os.path.join(entry, 'Images-Disc*', '*', 'Data', '*'))

                for file_name in files:
                    if file_name.endswith('.jpg'):
                        is_meta.append(entry)

                    if 'ractions.' in file_name:
                        is_frames.append(entry)
                        extension.extend(list(filter(
                            lambda x: file_name.endswith(x),
                            possible_extensions
                            )))

            if len(set(is_meta)) != 1 or len(set(is_frames)) != 1:
                tu.message('Could not identify meta and frames folder, yet. Did the data collection already start? If not, try again afterwards :)')
                return

            self.content['Input project path for frames'].set_settings(is_frames[0], '[None, None]')
            self.content['Input project path for jpg'].set_settings(is_meta[0], '[None, None]')

            if len(set(extension)) != 1:
                tu.message('Input project path for frames:\n{0}\n\nInput project path for jpg:\n{1}\n\Input frames extension:\nFOUND SEVERAL - Please provide manually!'.format(is_frames[0], is_meta[0]))
            else:
                self.content['Input frames extension'].set_settings(extension[0], '[None, None]')
                tu.message('Input project path for frames:\n{0}\n\nInput project path for jpg:\n{1}\n\nInput frames extension:\n{2}'.format(is_frames[0], is_meta[0], extension[0]))

        elif text.startswith('Just Stack'):
            self.content['Input project path for frames'].set_settings(project_dir, '[None, None]')
            self.content['Input project path for jpg'].set_settings(project_dir, '[None, None]')
            self.content['Number of frames'].set_settings('-1', '[None, None]')

            possible_extensions = self.content['Input frames extension'].get_combo_entries()
            extension = []
            for file_name in glob.iglob(os.path.join(project_dir, '*')):
                extension.extend(list(filter(
                    lambda x: file_name.endswith(x),
                    possible_extensions
                    )))

            if len(set(extension)) != 1:
                tu.message('Input project path for frames:\n{0}\n\nInput project path for jpg:\n{1}\n\nNumber of frames:\n-1\n\nInput frames extension:\nFOUND SEVERAL - Please provide manually!'.format(project_dir, project_dir))
            else:
                self.content['Input frames extension'].set_settings(extension[0], '[None, None]')
                tu.message('Input project path for frames:\n{0}\n\nInput project path for jpg:\n{1}\n\nNumber of frames:\n-1\n\nInput frames extension:\n{2}'.format(project_dir, project_dir, extension[0]))

        else:
            tu.message('Automatic folder detection is currently only supported for the EPU software. Please provide the "Input project path for frames", "Input project path for jpg" and "Input frames extension" manually.')

    @staticmethod
    def recursive_search(folder, match, matches):
        folders = sorted([entry for entry in glob.glob(os.path.join(folder, '*')) if os.path.isdir(entry)])
        for folder_name in folders:
            if os.path.basename(folder_name) == match:
                matches.append(folder_name)
                continue
            elif list(filter(
                    lambda x: os.path.basename(folder_name).startswith(x),
                    ('Images-Disc', 'Metadata', 'Sample', 'Atlas')
                    )):
                continue
            else:
                SettingsContainer.recursive_search(folder_name, match, matches)

from .settingswidget import SettingsWidget
from .separator import Separator
from .tabdocker import TabDocker
