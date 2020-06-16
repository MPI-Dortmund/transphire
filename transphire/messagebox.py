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
from PyQt5.QtWidgets import QDialog, QVBoxLayout, QLabel, QPushButton, QDialogButtonBox, QWidget


class MessageBox(QDialog):
    """
    Show a message box

    Inherits:
    QDialog

    Signals:
    None
    """

    def __init__(self, is_question, parent=None):
        """
        Initialise layout of the widget.

        Arguments:
        folder - Folder name to mount.
        default - Default user name
        login - True, if it is possible to test the users credentials on this machine
        extension - True, if a mount extension is required
        parent - Parent widget

        Returns:
        None
        """
        super(MessageBox, self).__init__(parent)
        central_raw_layout = QVBoxLayout(self)
        central_raw_layout.setContentsMargins(0, 0, 0, 0)
        central_widget_raw = QWidget(self)
        central_widget_raw.setObjectName('central_raw')
        central_raw_layout.addWidget(central_widget_raw)

        central_layout = QVBoxLayout(central_widget_raw)
        central_widget = QWidget(self)
        central_widget.setObjectName('central')
        central_layout.addWidget(central_widget)

        layout = QVBoxLayout(central_widget)
        self.label = QLabel(self)

        button_box = QDialogButtonBox(self)
        if is_question:
            accept_button = QPushButton('Yes')
            accept_button.setObjectName('start')
            reject_button = QPushButton('No')
            reject_button.setObjectName('stop')

            button_box.addButton(accept_button, QDialogButtonBox.AcceptRole)
            button_box.addButton(reject_button, QDialogButtonBox.RejectRole)

            button_box.accepted.connect(self.accept)
            button_box.rejected.connect(self.reject)

        else:
            accept_button = QPushButton('Ok')
            accept_button.setObjectName('start')

            button_box.addButton(accept_button, QDialogButtonBox.AcceptRole)

            button_box.accepted.connect(self.accept)

        layout.addWidget(self.label)
        layout.addWidget(button_box)

    def setText(self, heading, text):
        """
        Set the text to the label.

        Arguments:
        heading - Heading of the window
        text - Text of the label

        Returns:
        None
        """
        if heading is not None:
            self.setWindowTitle(heading)
        self.label.setText(text)

    def setDefault(self, text):
        pass
