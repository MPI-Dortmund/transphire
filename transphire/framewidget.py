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
from PyQt5.QtWidgets import QWidget, QHBoxLayout, QLabel, QPushButton
from PyQt5.QtCore import pyqtSignal, pyqtSlot


class FrameWidget(QWidget):
    """
    FrameWidget widget.

    Inherits from:
    QWidget

    Buttons:
    Delete - Delete this instance of the variable.

    Signals:
    delete - Delete this instance of the variable (class instance).
    """
    delete = pyqtSignal(object)

    def __init__(self, first, last, dose_weight, default, parent=None):
        """
        Setup the layout for the widget

        Arguments:
        first - First frame
        last - Last frame
        dose_weight - Do dose weighting or not
        default - Is this instance default or not
        parent - Parent widget (default None)

        Return:
        None
        """
        super(FrameWidget, self).__init__(parent)

        # Global content
        self.first = int(first)
        self.last = int(last)
        self.dose_weight = dose_weight
        self.default = default

        # Label content
        label_first = QLabel('First: {0}'.format(self.first), self)
        label_last = QLabel('Last: {0}'.format(self.last), self)
        label_dose_weight = QLabel(
            'Dose weighting: {0}'.format(self.dose_weight),
            self
            )

        # Delete button
        if self.default:
            button = QPushButton('Default', self)
            button.setEnabled(False)
        else:
            button = QPushButton('Del', self)
            button.clicked.connect(self._button_clicked)

        # Add to layout
        layout = QHBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.addWidget(label_first)
        layout.addWidget(label_last)
        layout.addWidget(label_dose_weight)
        layout.addWidget(button)

        # Object names
        label_first.setObjectName('entry')
        label_last.setObjectName('entry')
        label_dose_weight.setObjectName('entry')
        button.setObjectName('button_entry')

    @pyqtSlot()
    def _button_clicked(self):
        """
        Emit the signal with the information

        Arguments:
        None

        Return:
        None
        """
        self.delete.emit(self)

    def get_settings(self):
        """
        Get the settings

        Arguments:
        None

        Return:
        settings as dictionary
        """
        settings = {}
        settings['first'] = self.first
        settings['last'] = self.last
        settings['dw'] = self.dose_weight
        settings['default'] = self.default
        return settings
