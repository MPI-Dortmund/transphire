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
from PyQt5.QtCore import pyqtSlot, QTimer, pyqtSignal
from matplotlib.backends.backend_qt5agg import (
    FigureCanvasQTAgg as FigureCanvas,
    NavigationToolbar2QT as NavigationToolbar
    )
from transphire import transphire_utils as tu
warnings.filterwarnings('ignore')


class TrimWidget(QWidget):
    sig_update = pyqtSignal()

    def __init__(self, plot_typ, parent=None):
        super(TrimWidget, self).__init__(parent=parent)

        layout = QHBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)

        fields = [
            ['Min', '-inf'],
            ['Max', 'inf'],
            ['Bins', '50'],
            ]
        self.buttons = {}
        for label, default in fields:
            self.buttons[label] = [QLineEdit(default, self), default]
            self.buttons[label][0].editingFinished.connect(self.sig_update.emit)
            qt_label = QLabel(label + ':', self)

            if not plot_typ == 'histogram' and label == 'Bins':
                self.buttons[label][0].setVisible(False)
                qt_label.setVisible(False)
            else:
                layout.addWidget(qt_label)
                layout.addWidget(self.buttons[label][0])

        self.btn_reset = QPushButton('Reset', self)
        self.btn_reset.clicked.connect(self.reset_values)
        layout.addWidget(self.btn_reset)
        layout.addStretch(1)

    @pyqtSlot()
    def reset_values(self):
        for widget, default in self.buttons.values():
            widget.setText(default)
        self.sig_update.emit()

    def get_values(self):
        return_values = []
        for widget, default in self.buttons.values():
            return_values.append(float(widget.text()))
        return return_values

    def set_values(self, value_dict):
        for key, value in value_dict.items():
            self.buttons[key][0].setText(str(value))


class MplCanvas(FigureCanvas):
    def __init__(self, width=5, height=5, dpi=100, parent=None):
        fig = matplotlib.figure.Figure(figsize=(width, height), dpi=dpi)
        self.axes = fig.add_subplot(111)
        self.axes.grid(True)
        self.axes.autoscale(enable=False)
        fig.tight_layout()
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

        self.trim_widget = TrimWidget(self.plot_typ, self)
        self.trim_widget.sig_update.connect(self.update_trim)
        if self.plot_typ in ('values', 'histogram'):
            layout_v.addWidget(self.trim_widget, stretch=0)
        else:
            self.trim_widget.setVisible(False)

        self.layout_canvas = QVBoxLayout()
        layout_v.addLayout(self.layout_canvas, stretch=1)

        self._plot_ref = None
        self._color = '#68a3c3'

        self._cur_min_x = 0
        self._cur_max_x = 0
        self._cur_min_y = 0
        self._cur_max_y = 0
        self._applied_min_x = 0
        self._applied_max_x = 0
        self._applied_min_y = 0
        self._applied_max_y = 0

        self._bins = 50
        self._minimum_y = float('-inf')
        self._maximum_y = float('inf')

        n_data = 50
        self._xdata_tmp = np.arange(n_data)
        self._ydata_tmp = np.array([random.randint(0, 10) for i in range(n_data)])
        self._xdata = np.array([])
        self._ydata = np.array([])

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

    @pyqtSlot()
    def update_trim(self):
        previous_dict = {'Min': self._minimum_y, 'Max': self._maximum_y, 'Bins': self._bins}
        try:
            minimum, maximum, bins = self.trim_widget.get_values()
        except ValueError:
            tu.message('Non-float value detected! Falling back to previous values!')
            self.trim_widget.set_values(previous_dict)
            return

        if minimum > maximum:
            tu.message('Minimum cannot be greater than maximum! Falling back to previous values!')
            self.trim_widget.set_values(previous_dict)
            return

        try:
            bins = int(bins)
        except ValueError:
            tu.message('Bins need to be an integer! Falling back to previous values!')
            self.trim_widget.set_values(previous_dict)
            return

        self._minimum_y = minimum
        self._maximum_y = maximum
        self._bins = bins
        self.force_update()

    def update_data(self, data_x, data_y):
        self._ydata_tmp = np.array(data_y.tolist() + [random.randint(0, 1000)])
        self._xdata_tmp = np.array(data_x.tolist() + [data_x[-1]+1])

        mask = (self._ydata_tmp >= self._minimum_y) & (self._ydata_tmp <= self._maximum_y)

        if self.plot_typ == 'values':
            self._xdata = self._xdata_tmp[mask]
            self._ydata = self._ydata_tmp[mask]
        elif self.plot_typ == 'histogram':
            self._ydata, self._xdata = np.histogram(self._ydata_tmp[mask], self._bins)

    @pyqtSlot()
    def force_update(self):
        if self._plot_ref is not None:
            for entry in self._plot_ref:
                entry.remove()
        self._plot_ref = None
        self.update_figure()

    def prepare_axes(self, update):
        if (
                (
                    self._cur_min_x > min(self._xdata) or \
                    self._cur_min_y > min(self._ydata) or \
                    self._cur_max_x < max(self._xdata) or \
                    self._cur_max_y < max(self._ydata)
                    ) and \
                    self.canvas.axes.get_xlim() == (self._applied_min_x, self._applied_max_x) and \
                    self.canvas.axes.get_ylim() == (self._applied_min_y, self._applied_max_y)
                ) or \
                update:

            is_histogram = bool(self.plot_typ == 'histogram')

            width = self._xdata[1] - self._xdata[0]
            diff_x = np.max(self._xdata) - np.min(self._xdata)
            diff_y = np.max(self._ydata) - np.min(self._ydata) * is_histogram

            mult = 0.05
            boarder_x = max(diff_x * mult / 2, width * is_histogram)
            boarder_y = diff_y * mult / 2

            if self.plot_typ == 'values':
                self._cur_min_x = min(self._xdata) - boarder_x
                self._cur_min_y = min(self._ydata) - boarder_y
                self._cur_max_x = max(self._xdata) + boarder_x
                self._cur_max_y = max(self._ydata) + boarder_y

                self._applied_min_x = self._cur_min_x - boarder_y / 2
                self._applied_min_y = self._cur_min_y - boarder_y / 2
                self._applied_max_x = self._cur_max_x + boarder_y / 2
                self._applied_max_y = self._cur_max_y + boarder_y / 2

            elif self.plot_typ == 'histogram':
                self._cur_min_x = min(self._xdata[:-1]) - boarder_x
                self._cur_min_y = 0
                self._cur_max_x = max(self._xdata[:-1]) + boarder_x
                self._cur_max_y = max(self._ydata) + boarder_y

                self._applied_min_x = self._cur_min_x
                self._applied_min_y = self._cur_min_y
                self._applied_max_x = self._cur_max_x
                self._applied_max_y = self._cur_max_y + boarder_y / 2

            update = True
        return update

    @pyqtSlot()
    def update_figure(self):
        self.update_data(self._xdata_tmp, self._ydata_tmp)

        is_active = self.parent.parent.content[self.parent.parent_layout] == self.parent.parent.content[self.parent.parent_layout].latest_active[0]
        if not self.dock_widget.isFloating() and not is_active:
            return

        try:
            update = self.prepare_axes(update=self._plot_ref is None)
        except ValueError:
            return

        if self.plot_typ == 'values':
            self.update_values(update)
        elif self.plot_typ == 'histogram':
            self.update_histogram(update)

        if update:
            self.canvas.axes.set_xlim(self._applied_min_x, self._applied_max_x)
            self.canvas.axes.set_ylim(self._applied_min_y, self._applied_max_y)
            self.canvas.draw()
        else:
            self.canvas.update()
            self.canvas.flush_events()

    def update_histogram(self, update):
        width = self._xdata[1] - self._xdata[0]
        if update:
            if self._plot_ref is not None:
                for entry in self._plot_ref:
                    entry.remove()
            self._plot_ref = self.canvas.axes.bar(
                    self._xdata[:-1],
                    self._ydata,
                    width,
                    facecolor=self._color,
                    edgecolor='k'
                    )
        else:
            for value, patch in zip(self._ydata, self._plot_ref):
                if patch.get_height() != value:
                    patch.set_height(value)
                    patch.set_width(width)
                    self.canvas.axes.draw_artist(patch)

    def update_values(self, update):
        if update:
            if self._plot_ref is not None:
                self._plot_ref[0].remove()
            self._plot_ref = self.canvas.axes.plot(
                self._xdata,
                self._ydata,
                '.',
                color=self._color
                )
        else:
            self._plot_ref[0].set_data(self._xdata, self._ydata)
            self.canvas.axes.draw_artist(self._plot_ref[0])
