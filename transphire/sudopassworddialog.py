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
import os
import pexpect as pe
try:
    from PyQt4.QtGui import QInputDialog, QLineEdit
except ImportError:
    from PyQt5.QtWidgets import QInputDialog, QLineEdit
from transphire import transphire_utils as tu


class SudoPasswordDialog(QInputDialog):
    """
    Sudo password dialog.

    Inherits:
    QInputDialog
    """

    def __init__(self, parent=None):
        """
        Initialisation of the SudoPasswordDialog.

        Arguments:
        parent - Parent widget (default None)

        Returns:
        None
        """
        super(SudoPasswordDialog, self).__init__(parent)

        # Global content
        self.password = 'None'

        # Label text
        self.setLabelText('sudo password for {0}:'.format(os.environ['USER']))
        self.setTextEchoMode(QLineEdit.Password)

    def accept(self):
        """
        Modified accept event to check if the sudopassword is valid.

        Arguments:
        None

        Returns:
        None
        """
        self.password = self.textValue()

        child = pe.spawnu('sudo -S -k ls')
        child.sendline(self.password)
        try:
            idx = child.expect([pe.EOF, 'sudo: 1 incorrect password attempt', 'Sorry, try again'], timeout=10)
        except pe.exceptions.TIMEOUT:
            print('Wrong sudo password!')
            tu.message('Wrong sudo password!')
            return None
        else:
            if idx == 0:
                super().accept()
            else:
                print('Wrong sudo password!')
                tu.message('Wrong sudo password!')
                return None
