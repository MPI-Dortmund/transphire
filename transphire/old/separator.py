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
    from PyQt4.QtGui import QLabel
except ImportError:
    from PyQt5.QtWidgets import QLabel


class Separator(QLabel):
    """Separator widget"""

    def __init__(self, typ, color, parent=None):
        super(Separator, self).__init__(parent)

        self.setStyleSheet('background: {0}'.format(color))
        if typ == 'horizontal':
            self.setFixedHeight(2)
        elif typ == 'vertical':
            self.setFixedWidth(2)
