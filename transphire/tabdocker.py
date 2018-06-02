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
    from PyQt4.QtGui import QWidget, QVBoxLayout, QTabWidget
except ImportError:
    from PyQt5.QtWidgets import QWidget, QVBoxLayout, QTabWidget


class TabDocker(QWidget):
    """
    Tab widget for the settingswidgets.

    Inherits:
    QWidget
    """

    def __init__(self, parent=None, **kwargs):
        """
        Initialise layout for TabDocker

        Arguments:
        parent - Parent widget (default None)

        Return:
        None
        """
        super(TabDocker, self).__init__(parent)

        layout = QVBoxLayout(self)
        self.tab_widget = QTabWidget(self)
        self.tab_widget.setObjectName('tab')
        layout.addWidget(self.tab_widget)

    def add_tab(self, widget, name):
        """
        Add a new tab to the TabDocker

        Arguments:
        widget - Widget to add
        name - Name of the widget

        Return:
        None
        """
        self.tab_widget.addTab(widget, name)
