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
from PyQt5.QtWidgets import QWidget, QVBoxLayout, QLabel, QHBoxLayout


class MountContainer(QWidget):
    """
    MountContainer widget.

    Inherits from:
    QWidget

    Buttons:
    None

    Signals:
    None
    """

    def __init__(self, content_mount, mount_worker, parent=None, **kwargs):
        """
        Setup the layout for the widget

        Arguments:
        content_mount - Mount points as transphire settings dict.
        mount_worker - Worker thread instance.
        parent - Parent widget (default None)
        kwargs - Unused arguments for easier automatisation

        Return:
        None
        """
        super(MountContainer, self).__init__(parent)

        # Global layout
        central_layout = QVBoxLayout(self)
        central_layout.setContentsMargins(0, 0, 0, 0)
        central_widget = QWidget(self)
        central_widget.setObjectName('central')
        central_layout.addWidget(central_widget)

        # Global content
        self.content = {}

        # Layout
        layout = QVBoxLayout(central_widget)

        # Temp content
        content_temp = {}
        for entry in content_mount:
            content = {}
            for widget in entry:
                for key in widget:
                    content[key] = widget[key]
            content_temp.setdefault(
                content['Typ'][0].split('_')[-1].capitalize(),
                []
                ).append(content)

        # Content
        for key in sorted(content_temp.keys()):
            layout_h = QHBoxLayout()
            layout_h.addStretch(1)
            label = QLabel(key, self)
            label.setToolTip(key)
            layout_h.addWidget(label)
            layout_h.addStretch(1)
            layout.addLayout(layout_h)

            key_names = []
            for entry in content_temp[key]:
                key_names.append((entry['Mount name'][0], entry))

            for key_name, entry in sorted(key_names):
                if key_name:
                    self.content[key_name] = MountWidget(
                        content=entry,
                        mount_worker=mount_worker,
                        parent=self
                        )
                    layout.addWidget(self.content[key_name])

            layout_h = QHBoxLayout()
            layout_h.addStretch(1)
            layout_h.addWidget(QLabel('', self))
            layout_h.addStretch(1)
            layout.addLayout(layout_h)

        layout.addStretch(1)

    def get_settings(self):
        """
        Return settings of the container.

        Arguments:
        None

        Return:
        Settings as list
        """
        settings = {}
        for key in self.content:
            settings[key] = self.content[key].get_settings()
        return [settings]

    def set_threadlist(self, thread_list):
        """
        Set the thread instances for the different objects.

        Arguments:
        thread_list - List of mount threads

        Return:
        None
        """
        for key in self.content:
            self.content[key].set_thread_object(
                thread_object=thread_list[key]['object']
                )

    def enable(self, var, use_all):
        """
        Enable or disable the content.

        Arguments:
        var - State of buttons (True or False)
        use_all - Disable all buttons (True) or only some (False)

        Return:
        None
        """
        for key in self.content:
            if use_all:
                self.content[key].setEnabled(var)
            else:
                self.content[key].setEnabled(var)

from .mountwidget import MountWidget
