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
import time
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
    sig_notification = pyqtSignal(str)
    sig_message = pyqtSignal(str)

    def __init__(self, parent=None):
        """
        Initialise variables.

        Arguments:
        parent - Parent widget (default None)

        Returns:
        None
        """
        super(PlotWorker, self).__init__(parent)
        self.notified = False
        self.time_last_error = 0

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
            return None
        elif data.size == 0:
            return None
        else:
            pass

        last_phase_shift = data['phase_shift'][-1]
        phase_shift_warning = float(settings['General']['Phase shift warning (deg)'])
        if last_phase_shift > phase_shift_warning:
            if self.notified:
                if last_phase_shift < 90:
                    self.notified = False
                else:
                    pass
            else:
                msg = '\n'.join([
                    '{0}:'.format(ctf_name),
                    'Phase shift is higher than {0}!'.format(phase_shift_warning),
                    'You might want to change the phase plate position.'
                    ])
                self.sig_notification.emit(msg)
                self.notified = True
                if time.time() - self.time_last_error > 1800:
                    self.sig_message.emit(msg)
                    self.time_last_error = time.time()
                else:
                    pass
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
            return None
        elif data.size == 0:
            return None
        else:
            self.sig_data.emit(motion_name, data, directory_name, settings)
