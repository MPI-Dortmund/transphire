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
from PyQt5.QtWidgets import QLabel, QWidget, QHBoxLayout, QVBoxLayout, QPushButton



class Separator(QWidget):
    """Separator widget"""

    def __init__(
            self,
            typ,
            color,
            up=False,
            down=False,
            left=False,
            right=False,
            parent=None
            ):
        """
        Init function for the Seperator

        Arguments:
        typ - Either horizontal or vertical
        color - Color of the widget
        up - Affects the widgets to the top
        down - Affects the widgets to the down
        left - Affects the widgets to the left
        right - Affects the widgets to the right
        parent - Parent widget
        """
        super(Separator, self).__init__(parent)

        up_char = '\u2227'
        down_char = '\u2228'
        left_char = '<'
        right_char = '>'

        self.direction_dict = {
            up_char: up,
            down_char: down,
            left_char: left,
            right_char: right,
            }

        label = QLabel()
        label.setStyleSheet('background: {0}'.format(color))
        if typ == 'horizontal':
            label.setFixedHeight(2)
            layout = QHBoxLayout(self)
            layout_2 = QVBoxLayout()
        elif typ == 'vertical':
            label.setFixedWidth(2)
            layout = QVBoxLayout(self)
            layout_2 = QHBoxLayout()
        else:
            NameError('Typ not known {0}'.format(typ))

        layout_2.setContentsMargins(0, 0, 0, 0)
        #layout_2.addStretch(1)
        layout_2.addWidget(label)
        #layout_2.addStretch(1)

        layout.setContentsMargins(0, 0, 0, 0)
        layout.addLayout(layout_2, stretch=1)

        if up or down or left or right:
            label2 = QLabel()
            label2.setStyleSheet('background: {0}'.format(color))
            if typ == 'horizontal':
                layout_buttons = QHBoxLayout()
                layout_2_2 = QVBoxLayout()
                layout_2_3 = QVBoxLayout()
                label2.setFixedHeight(2)
            elif typ == 'vertical':
                layout_buttons = QVBoxLayout()
                layout_2_2 = QHBoxLayout()
                layout_2_3 = QHBoxLayout()
                label2.setFixedWidth(2)
            else:
                NameError('Typ not known {0}'.format(typ))

            button_list = []
            if up:
                button_list.append(QPushButton(up_char))
            if down:
                button_list.append(QPushButton(down_char))
            if left:
                button_list.append(QPushButton(left_char))
            if right:
                button_list.append(QPushButton(right_char))

            for button in button_list:
                button.toggled.connect(self.hide_show_widget)
                button.setObjectName('sep')
                button.setCheckable(True)
                if typ == 'horizontal':
                    button.setFixedHeight(15)
                elif typ == 'vertical':
                    button.setFixedWidth(15)
                else:
                    NameError('Typ not known {0}'.format(typ))
                layout_buttons.addWidget(button, stretch=0)

            layout_2_3.setContentsMargins(0, 0, 0, 0)
            layout_2_3.addStretch(1)
            layout_2_3.addLayout(layout_buttons)
            layout_2_3.addStretch(1)

            layout_2_2.setContentsMargins(0, 0, 0, 0)
            layout_2_2.addStretch(1)
            layout_2_2.addWidget(label2)
            layout_2_2.addStretch(1)

            layout.addLayout(layout_2_3, stretch=0)
            layout.addLayout(layout_2_2, stretch=1)


    def hide_show_widget(self, status):
        """
        Hide or show the widget with the status.

        Arguments:
        status - Status show or status hide.
        """
        self.direction_dict[self.sender().text()].setVisible(not status)
