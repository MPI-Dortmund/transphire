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
from PyQt5.QtWidgets import QWidget, QHBoxLayout, QVBoxLayout, QScrollArea
from PyQt5.QtCore import pyqtSlot
from transphire.settingswidget import SettingsWidget
from transphire.separator import Separator
from transphire.tabdocker import TabDocker


class SettingsContainer(QWidget):
    """
    Widget for setting widgets.

    Inherits:
    QWidget
    """

    def __init__(self, content, name, global_dict, parent=None, **kwargs):
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

        self.name = name
        self.global_dict = None
        try:
            content_others = kwargs['content_others']
        except KeyError:
            content_others = None

        # TabDocker widget for Main and Advanced
        my_tab_docker = TabDocker(self)
        my_tab_docker.setTabPosition('South')
        my_tab_docker.tab_widget.setObjectName('bot')
        layout_main = QVBoxLayout(self)
        layout_main.setContentsMargins(0, 0, 0, 0)
        layout_main.addWidget(my_tab_docker)

        self.layout_dict = {}
        for entry in content:
            for widget in entry:
                for key in widget:
                    if key == 'WIDGETS MAIN':
                        self.layout_dict['Main_max'] = int(widget['WIDGETS MAIN'][0])
                    elif key == 'WIDGETS ADVANCED':
                        self.layout_dict['Advanced_max'] = int(widget['WIDGETS ADVANCED'][0])
                    elif key == 'WIDGETS RARE':
                        self.layout_dict['Rare_max'] = int(widget['WIDGETS RARE'][0])
                    else:
                        continue

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
            my_tab_docker.add_tab(scroll_area, dict_name)

        # Global content
        self.content = {}
        self.group = {}

        # Add to layout
        for entry in content:
            for widget in entry:
                for key in widget:
                    if key == 'WIDGETS MAIN' or key == 'WIDGETS ADVANCED' or key == 'WIDGETS RARE':
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

                    widget = SettingsWidget(content=widget[key], name=name, content_others=content_others, global_dict=global_dict, parent=self)
                    if group and name not in ('Pipeline'):
                        group, state = group.split(':')
                        self.group.setdefault(group, [])
                        self.group[group].append([widget, state, widget_name])
                    self.content[widget_name] = widget
                    self.layout_dict['{0}_v'.format(layout_name)].addWidget(widget)
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
                content.set_settings(settings[key], settings['{0}_global'.format(key)])
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
                self.content[key].edit.textChanged.emit(self.content[key].edit.text())
            except AttributeError:
                self.content[key].edit.currentTextChanged.connect(self.update_global)
                self.content[key].edit.currentTextChanged.emit(self.content[key].edit.currentText())

    @pyqtSlot(str)
    def update_global(self, text):
        if self.sender().parent().name not in self.global_dict:
            return

        for entry in self.global_dict[self.sender().parent().name]:

            if self.sender().parent().name == 'Bin superres' and text == 'False':
                text = '1'

            entry.global_value = text
            if not entry.edit.isEnabled():
                try:
                    entry.edit.setText(text)
                except AttributeError:
                    entry.edit.setCurrentText(text)

