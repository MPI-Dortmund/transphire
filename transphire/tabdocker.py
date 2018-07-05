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
    from PyQt5.Qt import QPalette, QColor, QBrush


class TabDocker(QWidget):
    """
    Tab widget for the settingswidgets.

    Inherits:
    QWidget
    """

    def __init__(self, transparent=False, parent=None, **kwargs):
        """
        Initialise layout for TabDocker

        Arguments:
        parent - Parent widget (default None)

        Return:
        None
        """
        super(TabDocker, self).__init__(parent)
        layout_tmp = QVBoxLayout(self)
        self.widget = QWidget(self)
        layout_tmp.addWidget(self.widget)
        layout_tmp.setContentsMargins(0, 0, 0, 0)

        layout = QVBoxLayout(self.widget)
        self.tab_widget = QTabWidget(self)
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
        if isinstance(widget, TabDocker):
            widget.widget.setObjectName('tab')
        else:
            pass
        self.tab_widget.addTab(widget, name)
