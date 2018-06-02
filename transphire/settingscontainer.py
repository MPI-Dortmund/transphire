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
try:
    from PyQt4.QtGui import QWidget, QHBoxLayout, QVBoxLayout
    from PyQt4.QtCore import pyqtSlot
except ImportError:
    from PyQt5.QtWidgets import QWidget, QHBoxLayout, QVBoxLayout
    from PyQt5.QtCore import pyqtSlot
from transphire.settingswidget import SettingsWidget
from transphire.separator import Separator


class SettingsContainer(QWidget):
    """
    Widget for setting widgets.

    Inherits:
    QWidget
    """

    def __init__(self, content, max_widgets, parent=None, **kwargs):
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

        # Layout
        layout_v_global = QVBoxLayout(self)
        layout_v_global.setContentsMargins(0, 0, 0, 0)
        self.layout = QHBoxLayout()
        self.layout.setContentsMargins(0, 0, 0, 0)
        self.layout_v = None
        self.idx = 0
        self.max_widgets = max_widgets

        # Global content
        self.content = {}
        self.group = {}

        # Add to v global layout
        layout_v_global.addLayout(self.layout, stretch=0)
        layout_v_global.addStretch(1)

        # Add to layout
        for entry in content:
            for widget in entry:
                for key in widget:
                    if self.idx % self.max_widgets == 0:
                        if self.layout_v is not None:
                            self.layout.addWidget(Separator(typ='vertical', color='lightgrey'))
                            self.layout_v.addStretch(1)
                        self.layout_v = QVBoxLayout()
                        self.layout_v.setContentsMargins(0, 0, 0, 0)
                        self.layout.addLayout(self.layout_v)
                    name = widget[key][1]['name']
                    group = widget[key][1]['group']
                    widget = SettingsWidget(content=widget[key], parent=self)
                    if group:
                        group, state = group.split(':')
                        self.group.setdefault(group, [])
                        self.group[group].append([widget, state, name])
                    self.content[name] = widget
                    self.layout_v.addWidget(widget)
                    self.idx += 1

        for key in self.group:
            self.content[key].sig_index_changed.connect(self.change_state)
            self.change_state(name=key)

        self.layout_v.addStretch(1)
        self.layout.addStretch(1)

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
            if key == 'Motion' or key == 'CTF':
                new_key = '{0}_entries'.format(key)
                settings[new_key] = self.content[key].get_combo_entries()
            else:
                pass
        if error:
            return None
        else:
            return [settings]

    def set_settings(self, settings):
        """
        Set settings to the widgets

        Arguments:
        settings - Settings to set.

        Returns:
        None
        """
        for key in settings:
            try:
                content = self.content[key]
            except KeyError:
                if key == 'CTF_entries':
                    continue
                elif key == 'Motion_entries':
                    continue
                else:
                    print('Content for {0} is disabled.'.format(key))
                    continue

            try:
                content.set_settings(settings[key])
            except KeyError:
                if key == 'CTF_entries':
                    pass
                elif key == 'Motion_entries':
                    pass
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
