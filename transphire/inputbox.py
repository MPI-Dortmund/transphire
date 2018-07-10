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
    from PyQt4.QtGui import QDialog, QVBoxLayout, QLabel, QPushButton, QDialogButtonBox, QWidget, QLineEdit
except ImportError:
    from PyQt5.QtWidgets import QDialog, QVBoxLayout, QLabel, QPushButton, QDialogButtonBox, QWidget, QLineEdit


class InputBox(QDialog):
    """
    Show a message box with an input field.

    Inherits:
    QDialog

    Signals:
    None
    """

    def __init__(self, is_password, parent=None):
        """
        Initialise layout of the widget.

        Arguments:
        is_password - Input is a password and needs to be hidden.
        parent - Parent widget

        Returns:
        None
        """
        super(InputBox, self).__init__(parent)
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
        self.edit = QLineEdit('', self)
        if is_password:
            self.edit.setEchoMode(QLineEdit.Password)
        else:
            pass

        button_box = QDialogButtonBox(self)
        accept_button = QPushButton('Ok')
        accept_button.setObjectName('start')
        reject_button = QPushButton('Cancel')
        reject_button.setObjectName('stop')

        button_box.addButton(accept_button, QDialogButtonBox.AcceptRole)
        button_box.addButton(reject_button, QDialogButtonBox.RejectRole)

        button_box.accepted.connect(self.accept)
        button_box.rejected.connect(self.reject)

        layout.addWidget(self.label)
        layout.addWidget(self.edit)
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

    def getText(self):
        """
        Get the text from the label.

        Arguments:
        None

        Returns:
        Text content
        """
        return self.edit.text()
