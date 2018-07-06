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
import numpy as np
try:
    from PyQt4.QtCore import pyqtSignal, QObject, pyqtSlot
except ImportError:
    from PyQt5.QtCore import pyqtSignal, QObject, pyqtSlot
from transphire import transphire_utils as tu


class PlotWorker(QObject):
    """
    Plot different information about motion correction and ctf estimation.

    Inherits:
    QObject

    Signals:
    sig_data - Emitted, if data for plotting is found (name|str, data|object, directory|str, settings|object)
    sig_notification - Emitted, if phase plate limit is reached. (text|str)
    """
    sig_data = pyqtSignal(str, object, str, object)

    def __init__(self, parent=None):
        """
        Initialise variables.

        Arguments:
        parent - Parent widget (default None)

        Returns:
        None
        """
        super(PlotWorker, self).__init__(parent)

    @pyqtSlot(str, object, object)
    def calculate_array_ctf(self, ctf_name, directory_name, settings):
        """
        Calculate ctf array.

        ctf_name - Name of the software that calls the calculation
        directory_name - Name of the directory that contains the log files
        settings - TranSPHIRE settings

        Returns:
        None
        """
        data, _ = tu.import_ctf(
            ctf_name=ctf_name,
            directory_name=directory_name
            )
        if data is None:
            pass
        elif data.size == 0:
            pass
        else:
            self.sig_data.emit(ctf_name, data, directory_name, settings)

    @pyqtSlot(str, object, object)
    def calculate_array_motion(self, motion_name, directory_name, settings):
        """
        Calculate motion array.

        motion_name - Name of the software that calls the calculation
        directory_name - Name of the directory that contains the log files
        settings - TranSPHIRE settings

        Returns:
        None
        """
        data = tu.import_motion(
            motion_name=motion_name,
            directory_name=directory_name
            )
        if data is None:
            pass
        elif data.size == 0:
            pass
        else:
            self.sig_data.emit(motion_name, data, directory_name, settings)

    @pyqtSlot(str, object, object)
    def calculate_array_picking(self, picking_name, directory_name, settings):
        """
        Calculate picking array.

        picking_name - Name of the software that calls the calculation
        names - Name of the directory that contains the log files and the file to look for
        settings - TranSPHIRE settings

        Returns:
        None
        """
        data = tu.import_picking(
            picking_name=picking_name,
            directory_name=directory_name
            )
        if data is None:
            pass
        elif data.size == 0:
            pass
        else:
            self.sig_data.emit(picking_name, data, directory_name, settings)
