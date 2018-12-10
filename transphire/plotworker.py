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
    sig_visible = pyqtSignal(bool, str)
    sig_calculate = pyqtSignal()
    sig_reset_list = pyqtSignal()

    def __init__(self, parent=None):
        """
        Initialise variables.

        Arguments:
        parent - Parent widget (default None)

        Returns:
        None
        """
        super(PlotWorker, self).__init__(parent)
        self.settings = []
        self.sig_calculate.connect(self.calculate_array)
        self.sig_reset_list.connect(self.reset_list)
        self.running = False

    @pyqtSlot()
    def reset_list(self):
        self.settings = []

    @pyqtSlot(str, object, object, str)
    def set_settings(self, name, directory_name, settings, current_name):
        """
        Set settings for the calculation of the arrays.

        name - Name of the software that calls the calculation
        directory_name - Name of the directory that contains the log files
        settings - TranSPHIRE settings

        Returns:
        None
        """
        if name not in ('Later', 'False'):
            if name == current_name:
                self.settings.append([name, directory_name, settings])
            if os.path.isdir(directory_name):
                self.calculate_array_now(
                    name=name,
                    directory_name=directory_name,
                    settings=settings
                    )
                self.sig_visible.emit(True, name)
            else:
                self.sig_visible.emit(False, name)


    @pyqtSlot()
    def reset_running(self):
        self.running = False

    @pyqtSlot()
    def calculate_array(self):
        """
        Calculate array.

        Returns:
        None
        """
        if not self.running:
            for name, directory_name, settings in self.settings:
                self.running = True
                self.calculate_array_now(
                    name=name,
                    directory_name=directory_name,
                    settings=settings
                    )

    def calculate_array_now(self, name, directory_name, settings):
        data, _ = tu.get_function_dict()[name]['plot_data'](
            name=name,
            directory_name=directory_name
            )

        if data is None:
            self.running = False
        elif data.size == 0:
            self.running = False
        else:
            self.sig_data.emit(name, data, directory_name, settings)
