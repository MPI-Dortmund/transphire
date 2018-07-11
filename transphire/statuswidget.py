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
    from PyQt4.QtGui import QWidget, QLabel, QHBoxLayout
    from PyQt4.QtCore import pyqtSignal, pyqtSlot
except ImportError:
    from PyQt5.QtWidgets import QWidget, QLabel, QHBoxLayout
    from PyQt5.QtCore import pyqtSignal, pyqtSlot


class StatusWidget(QWidget):
    """
    Widget to show the current status of the processes.

    Inherits:
    QWidget

    Signals:
    sig_change_info_name - Connected, to change the info name information (text|str, color|str)
    sig_change_info_quota - Connected, to change the quota name information (text|str, color|str)
    """
    sig_change_info_name = pyqtSignal(str, str)
    sig_change_info_quota = pyqtSignal(str, str)

    def __init__(self, name, default_name, default_quota, parent=None):
        super(StatusWidget, self).__init__(parent)

        # Global content
        self.info_name = QLabel(default_name, self)
        self.info_name.setObjectName('status_info')
        self.info_name.setStyleSheet('color: white')

        self.info_quota = QLabel(default_quota, self)
        self.info_quota.setObjectName('status_quota')
        self.info_quota.setStyleSheet('color: white')

        # Content
        name = QLabel('{0}: '.format(name), self)
        name.setObjectName('status_name')
        name.setStyleSheet('color: #68a3c3')

        # Layout
        layout = QHBoxLayout(self)
        layout.addWidget(name)
        layout.addWidget(self.info_name)
        layout.addWidget(self.info_quota, stretch=1)
        layout.setContentsMargins(0, 0, 0, 0)

        # events
        self.sig_change_info_name.connect(self.change_info_name)
        self.sig_change_info_quota.connect(self.change_info_quota)

    @pyqtSlot(str, str)
    def change_info_name(self, text, color):
        """
        Change the info text and the info text color.

        Arguments:
        text - Text to put
        color - Color to use

        Returns:
        None
        """
        self.info_name.setText(text)
        self.info_name.setStyleSheet('color: {0}'.format(color))

    @pyqtSlot(str, str)
    def change_info_quota(self, text, color):
        """
        Change the info text and the info text color.

        Arguments:
        text - Text to put
        color - Color to use

        Returns:
        None
        """
        self.info_quota.setText(text)
        self.info_quota.setStyleSheet('color: {0}'.format(color))
