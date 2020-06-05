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
import sys
sys.setrecursionlimit(2*sys.getrecursionlimit())

import os
import warnings
import imageio
import numpy as np
import matplotlib
matplotlib.use('QT5Agg')
from PyQt5.QtWidgets import QApplication

from PyQt5.QtWidgets import QWidget, QVBoxLayout, QHBoxLayout, QComboBox, QPushButton, QLineEdit, QLabel
from PyQt5.QtCore import pyqtSlot, QTimer
from matplotlib.backends.backend_qt5agg import (
    FigureCanvasQTAgg as FigureCanvas,
    NavigationToolbar2QT as NavigationToolbar
    )
from transphire import transphire_utils as tu
warnings.filterwarnings('ignore')


class MplCanvas(FigureCanvas):
    def __init__(self, width=5, height=5, dpi=100, parent=None):
        fig = matplotlib.figure.Figure(figsize=(width, height), dpi=dpi)
        self.axes = fig.add_subplot(111)
        self.axes.grid(True)
        self.axes.autoscale(enable=False)
        super(MplCanvas, self).__init__(fig)


import random
class PlotWidget(QWidget):
    """
    PlotWidget widget.
    Widget used to show data plots.

    Inherits from:
    QWidget

    Signals:
    None
    """

    def __init__(self, label, plot_typ, dock_widget, *args, parent=None, **kwargs):
        """
        Setup the layout for the widget.

        Arguments:
        label - Label of the plot.
        plot_typ - Type of plot (e.g. histogram, values)
        parent - Parent widget (Default None)
        *args - Unused additional arguments
        **kwargs - Unused named additional arguments

        Return:
        None
        """
        super(PlotWidget, self).__init__(parent=parent)

        self.parent = parent
        self.label = label
        self.plot_typ = plot_typ
        self.dock_widget = dock_widget

        layout_v = QVBoxLayout(self)
        self.layout_canvas = QVBoxLayout()
        layout_v.addLayout(self.layout_canvas, stretch=1)

        self._plot_ref = None

        self._color = '#68a3c3'
        self._boarder_x = 0
        self._boarder_y = 0
        self._cur_min_x = 0
        self._cur_max_x = 0
        self._cur_min_y = 0
        self._cur_max_y = 0

        n_data = 50
        self._xdata = list(range(n_data))
        self._ydata = [random.randint(0, 10) for i in range(n_data)]

    def start_plotting(self):
        self.add_canvas()

        self.parent.parent.content[self.parent.parent_layout].sig_start_plot.connect(self.update_figure)

        timer = QTimer(self)
        timer.setInterval(1000)
        timer.timeout.connect(self.update_figure)
        timer.start()

    def add_canvas(self):
        layout_v = QVBoxLayout()
        self.canvas = MplCanvas(parent=self)
        toolbar = NavigationToolbar(self.canvas, self)
        toolbar.actions()[0].triggered.connect(self.force_update)

        self.update_figure()

        layout_v.addWidget(toolbar)
        layout_v.addWidget(self.canvas, stretch=1)

        self.layout_canvas.addLayout(layout_v)

    @pyqtSlot(str, str, object, str, object)
    def set_settings(self, name, name_no_feedback, data, directory_name, settings):
        self._name = name
        self._name_no_feedback = name_no_feedback
        self._data = data
        self._directory_name = directory_name
        self._settings = settings

    def update_data(self, data_x, data_y):
        self._ydata = data_y + [random.randint(0, 1000)]
        self._xdata = data_x + [data_x[-1]+1]

    @pyqtSlot()
    def force_update(self):
        self._plot_ref = None
        self.update_figure()

    @pyqtSlot()
    def update_figure(self):
        self.update_data(self._xdata, self._ydata)

        is_active = self.parent.parent.content[self.parent.parent_layout] == self.parent.parent.content[self.parent.parent_layout].latest_active[0]
        if not self.dock_widget.isFloating() and not is_active:
            return

        update = self._plot_ref is None
        if (
                (
                    self._cur_min_x > min(self._xdata) or \
                    self._cur_min_y > min(self._ydata) or \
                    self._cur_max_x < max(self._xdata) or \
                    self._cur_max_y < max(self._ydata)
                    ) and \
                    self.canvas.axes.get_xlim() == (self._cur_min_x, self._cur_max_x) and \
                    self.canvas.axes.get_ylim() == (self._cur_min_y, self._cur_max_y)
                ) or \
                update:

            diff_x = np.max(self._xdata) - np.min(self._xdata)
            diff_y = np.max(self._ydata) - np.min(self._ydata)

            mult = 0.05
            self._boarder_x = diff_x * mult / 2
            self._boarder_y = diff_y * mult / 2

            self._cur_min_x = min(self._xdata) - self._boarder_x
            self._cur_min_y = min(self._ydata) - self._boarder_y
            self._cur_max_x = max(self._xdata) + self._boarder_x
            self._cur_max_y = max(self._ydata) + self._boarder_y
            update = True

        if self.plot_typ == 'values':
            self.update_values(update)

    def update_values(self, update):
        if update:
            if self._plot_ref is not None:
                self._plot_ref.remove()
            #self.canvas.axes.cla()
            self._plot_ref, = self.canvas.axes.plot(
                self._xdata,
                self._ydata,
                '.',
                color=self._color
                )

            self.canvas.axes.set_xlim(self._cur_min_x, self._cur_max_x)
            self.canvas.axes.set_ylim(self._cur_min_y, self._cur_max_y)
            self.canvas.draw()
        else:
            self._plot_ref.set_data(self._xdata, self._ydata)
            self.canvas.axes.draw_artist(self._plot_ref)
            self.canvas.update()
            self.canvas.flush_events()
