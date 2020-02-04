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
    QDialog,
    QHBoxLayout,
    QVBoxLayout,
    QLabel,
    QPushButton,
    QLineEdit,
    QWidget
    )


class EmailDialog(QDialog):
    """
    EmailDialog widget.

    Inherits from:
    QDialog

    Buttons:
    OK
    Cancel

    LineEdit:
    Name - Name, that associates with the E-Mail
    E-Mail - E-Mail adress of the user
    """

    def __init__(self, parent=None):
        """
        Setup the layout for the widget

        Arguments:
        parent - Parent widget (default None)

        Return:
        None
        """
        super(EmailDialog, self).__init__(parent)

        # Setup layout
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

        # Name textedit
        layout.addWidget(QLabel('Name:', self))
        self.user_le = QLineEdit(self)
        layout.addWidget(self.user_le)

        # E-Mail textedit
        layout.addWidget(QLabel('E-Mail:', self))
        self.email_le = QLineEdit(self)
        layout.addWidget(self.email_le)

        # Button layout
        layout_button = QHBoxLayout()
        layout_button.setContentsMargins(0, 0, 0, 0)

        # Accept button
        button_accept = QPushButton('OK', self)
        button_accept.clicked.connect(self.accept)
        layout_button.addWidget(button_accept)

        # Reject button
        button_reject = QPushButton('Cancel', self)
        button_reject.clicked.connect(self.reject)
        layout_button.addWidget(button_reject)

        # Add button layout to setup layout
        layout.addLayout(layout_button)

    def get_name(self):
        """
        Return the text of the Name.

        Arguments:
        None

        Return:
        Name
        """
        return self.user_le.text()

    def get_email(self):
        """
        Return the text of the E-Mail.

        Arguments:
        None

        Return:
        E-Mail
        """
        return self.email_le.text()
