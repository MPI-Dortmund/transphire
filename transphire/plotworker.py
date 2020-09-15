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
import traceback as tb
import os
import multiprocessing as mp
from PyQt5.QtCore import pyqtSignal, QObject, pyqtSlot

from . import transphire_utils as tu


class PlotWorker(QObject):
    """
    Plot different information about motion correction and ctf estimation.

    Inherits:
    QObject

    Signals:
    sig_data - Emitted, if data for plotting is found (name|str, data|object, directory|str, settings|object)
    sig_notification - Emitted, if phase plate limit is reached. (text|str)
    """
    sig_data = pyqtSignal(str, str, object, str, object)
    sig_reset = pyqtSignal()
    sig_visible = pyqtSignal(bool, str)
    sig_calculate = pyqtSignal()
    sig_reset_list = pyqtSignal()
    sig_new_round = pyqtSignal()
    sig_set_visual = pyqtSignal()

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

    @pyqtSlot()
    def reset_list(self):
        self.sig_reset.emit()
        self.settings = []

    @pyqtSlot(object)
    def set_settings(self, settings):
        """
        Set settings for the calculation of the arrays.

        name - Name of the software that calls the calculation
        directory_name - Name of the directory that contains the log files
        settings - TranSPHIRE settings

        Returns:
        None
        """
        small_settings = {'Output': {}, 'Path': {}}
        for name, name_no_feedback, directory_name, settings, current_name in settings:
            if name_no_feedback not in ('Later', 'False'):
                small_settings['Output']['Project directory']= settings['Output']['Project directory']
                small_settings['Path']['chimerax']= settings['Path']['chimerax']
                small_settings['copy_to_work_folder_feedback_0']= settings['copy_to_work_folder_feedback_0']
                small_settings['Output']['Rename prefix'] = settings['Output']['Rename prefix']
                small_settings['Output']['Rename suffix'] = settings['Output']['Rename suffix']
                small_settings['Output']['Rename micrographs'] = settings['Output']['Rename micrographs']
                self.settings.append([name, name_no_feedback, directory_name, small_settings, current_name])

        self.calculate_array()
        self.sig_set_visual.emit()

    def send_data(self, data):
        for entry in data:
            if entry is not None:
                self.sig_data.emit(*entry)

    @pyqtSlot()
    def calculate_array(self):
        """
        Calculate array.

        Returns:
        None
        """
        valid_entries = []
        for entry in self.settings[:]:
            name, name_no_feedback, directory_name, settings, current_name = entry
            if os.path.isdir(directory_name):
                valid_entries.append([name, name_no_feedback, directory_name, settings])
                self.sig_visible.emit(True, name)
            else:
                self.sig_visible.emit(False, name)
            if name_no_feedback != current_name:
                self.settings.remove(entry)

        if valid_entries:
            try:
                with mp.Pool(min(len(valid_entries), len(valid_entries))) as p:
                    data = p.starmap(self.calculate_array_now, valid_entries)
            except Exception as e:
                print(e)
                print(tb.format_exc())
            else:
                self.send_data(data)
        self.sig_new_round.emit()

    @staticmethod
    def calculate_array_now(name, name_no_feedback, directory_name, settings):
        try:
            data, _ = tu.get_function_dict()[name_no_feedback]['plot_data'](
                name=name,
                name_no_feedback=name_no_feedback,
                settings=settings,
                directory_name=directory_name
                )
        except KeyError:
            pass
        else:
            if data is None or data.size == 0:
                return None
            else:
                return [name, name_no_feedback, data, directory_name, settings]
