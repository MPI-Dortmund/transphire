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

from PyQt5.QtWidgets import (
    QWidget,
    QVBoxLayout,
    QPushButton,
    QLabel,
    QHBoxLayout,
    QLineEdit
    )
from PyQt5.QtCore import pyqtSlot

from . import transphire_utils as tu

class FrameContainer(QWidget):
    """
    FrameContainer widget.

    Inherits from:
    QWidget

    Buttons:
    Add - Add FrameWidget widget to the layout

    LineEdit:
    First frame - First frame to use for a smaller amount of dose
    Last frame - Last frame to use for a smaller amount of dose
    """

    def __init__(self, parent=None, **kwargs):
        """
        Setup the layout for the widget

        Arguments:
        parent - Parent widget (default None)

        Return:
        None
        """
        super(FrameContainer, self).__init__(parent)

        # Variables
        kwargs = kwargs
        self.content = []
        self.content_frames = []

        # Setup layout
        layout_v = QVBoxLayout(self)
        layout_v.setContentsMargins(0, 0, 0, 0)

        # Static layout
        layout = QHBoxLayout()
        layout.setContentsMargins(0, 0, 0, 0)
        layout_v.addLayout(layout)

        # First frame textedit
        first = QLabel('First frame:', self)
        first.setObjectName('frame')
        layout.addWidget(first)
        self.first = QLineEdit('1', self)
        self.first.setObjectName('frame')
        layout.addWidget(self.first)

        # Last frame textedit
        last = QLabel('Last frame:', self)
        last.setObjectName('frame')
        layout.addWidget(last)
        self.last = QLineEdit('20', self)
        self.last.setObjectName('frame')
        layout.addWidget(self.last)

        # Stretch between edits and add button
        layout.addStretch(1)

        # Add button
        self.button = QPushButton('Add', self)
        self.button.setObjectName('frame')
        self.button.clicked.connect(self.add_widget)
        layout.addWidget(self.button)

        # Seperator between static layout and dynamic layout
        layout_v.addWidget(Separator(typ='horizontal', color='grey'))

        # Dynamic layout
        self.layout = QVBoxLayout()
        self.layout.setContentsMargins(0, 0, 0, 0)
        layout_v.addLayout(self.layout)

        # Stretch in the end
        layout_v.addStretch(1)

        # First default entry
        widget = FrameWidget(
            first=1,
            last=-1,
            dose_weight=True,
            default=True
            )
        self.layout.addWidget(widget)
        self.content.append(widget)
        self.content_frames.append('1,-1')

    @pyqtSlot()
    def add_widget(self):
        """
        Add a FrameWidget widget to the dynamic layout.
        Called when the add button is clicked.

        Arguments:
        None

        Returns:
        None
        """
        first = self.first.text()
        last = self.last.text()
        name = '{0},{1}'.format(first, last)

        try:
            first = int(first)
            last = int(last)
        except ValueError:
            tu.message('Not castable, input needs to be integer value.')
            return None

        if first <= 0:
            tu.message('No values below 1.')
            return None

        elif first > last:
            tu.message('Last must be smaller or equals first.')
            return None

        elif name in set(self.content_frames):
            tu.message('Already got frame combination {0} {1}'.format(first, last))
            return None

        else:
            pass

        widget = FrameWidget(
            first=first,
            last=last,
            dose_weight=False,
            default=False
            )
        widget.delete.connect(self._del_widget)
        self.layout.addWidget(widget)
        self.content.append(widget)
        self.content_frames.append(name)

    def _reset(self):
        """
        Reset the dynamic layout.

        Arguments:
        None

        Returns:
        None
        """
        for entry in self.content:
            self.layout.removeWidget(entry)
            entry.setParent(None)
        self.content = []
        self.content_frames = []

    @pyqtSlot(object)
    def _del_widget(self, widget):
        """
        Delete widget from the dynamic layout.
        Called when the Del button of a FramEntry is clicked.

        Arguments:
        widget - FrameWidget instance

        Returns:
        None
        """
        settings = widget.get_settings()
        self.content_frames.remove(
            '{0},{1}'.format(settings['first'], settings['last'])
            )
        self.content.remove(widget)
        self.layout.removeWidget(widget)
        widget.setParent(None)

    def get_settings(self):
        """
        Get settings of all FrameWidget widgets.

        Arguments:
        None

        Returns:
        settings - List of FrameWidget settings
        """
        settings = []
        for entry in self.content:
            settings.append(entry.get_settings())
        return settings

    def set_settings(self, settings):
        """
        Add FrameWidget widgets to the dynamic layout
        based on setting entries.

        Arguments:
        settings - List of FrameWidget settings.

        Returns:
        None
        """
        self._reset()
        for entry in settings:
            first = entry['first']
            last = entry['last']
            dose_weight = bool(entry['dw'] == 'True')
            default = bool(entry['default'] == 'True')

            widget = FrameWidget(
                first=first,
                last=last,
                dose_weight=dose_weight,
                default=default,
                parent=self
                )
            self.layout.addWidget(widget)
            self.content.append(widget)
            self.content_frames.append('{0},{1}'.format(first, last))
            if not default:
                widget.delete.connect(self._del_widget)
            else:
                pass

    def enable(self, var, use_all):
        """
        Enable or disable the buttons and widgets.

        Arguments:
        var - State of buttons (True or False)
        use_all - Disable all buttons (True) or only some (False)

        Return:
        None
        """
        if use_all:
            pass
        else:
            pass
        self.first.setEnabled(var)
        self.last.setEnabled(var)
        self.button.setEnabled(var)
        for entry in self.content:
            entry.setEnabled(var)

from .framewidget import FrameWidget
from .separator import Separator
