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
sys.setrecursionlimit(4*sys.getrecursionlimit())

import os
import warnings
import imageio
import numpy as np
import matplotlib
matplotlib.use('QT5Agg')
from PyQt5.QtWidgets import QApplication

from PyQt5.QtWidgets import QWidget, QVBoxLayout, QHBoxLayout, QComboBox, QPushButton, QLineEdit, QLabel, QCheckBox
from PyQt5.QtCore import pyqtSlot, QTimer, pyqtSignal
from matplotlib.backends.backend_qt5agg import (
    FigureCanvasQTAgg as FigureCanvas,
    NavigationToolbar2QT as NavigationToolbar
    )
from transphire import transphire_utils as tu
warnings.filterwarnings('ignore')


class SelectWidget(QWidget):
    sig_update = pyqtSignal(str)

    def __init__(self, parent=None):
        super(SelectWidget, self).__init__(parent=parent)
        self._full_combo_list = []
        self.prev_text = 'Prev'
        self.next_text = 'Next'
        self.first_text = 'First'
        self.last_text = 'Last'

        layout = QHBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)

        fields = [
            ['Image', QComboBox],
            ['Filter', QLineEdit],
            ]
        self.buttons = {}
        for label, widget in fields:
            self.buttons[label] = widget(self)
            qt_label = QLabel(label + ':', self)
            layout.addWidget(qt_label)
            layout.addWidget(self.buttons[label])

        fields = [
            [self.prev_text, QPushButton],
            [self.next_text, QPushButton],
            [self.first_text, QPushButton],
            [self.last_text, QPushButton],
            ['Reset', QPushButton],
            ]
        for label, widget in fields:
            self.buttons[label] = widget(label, self)
            self.buttons[label].setObjectName('frame')
            layout.addWidget(self.buttons[label])

        self.buttons['Image'].addItem('latest')
        self.buttons[self.prev_text].clicked.connect(self.handle_change)
        self.buttons[self.next_text].clicked.connect(self.handle_change)
        self.buttons[self.first_text].clicked.connect(self.handle_change)
        self.buttons[self.last_text].clicked.connect(self.handle_change)
        self.buttons['Reset'].clicked.connect(self.reset_values)

        self.buttons['Image'].currentTextChanged.connect(lambda x: self.sig_update.emit(x))
        self.buttons['Image'].activated.connect(self.check_enable)
        self.buttons['Filter'].textEdited.connect(self.filter_combo)
        self.set_values(list(map(str, range(1000))))

        layout.addStretch(1)

    @pyqtSlot(int)
    def check_enable(self, idx):
        if idx == 0 and idx == self.buttons['Image'].count() + 1:
            self.buttons[self.prev_text].setEnabled(False)
            self.buttons[self.next_text].setEnabled(False)
        elif idx == 0:
            self.buttons[self.prev_text].setEnabled(False)
            self.buttons[self.next_text].setEnabled(True)
        elif idx == self.buttons['Image'].count() - 1:
            self.buttons[self.prev_text].setEnabled(True)
            self.buttons[self.next_text].setEnabled(False)
        elif idx == -1:
            self.buttons[self.prev_text].setEnabled(False)
            self.buttons[self.next_text].setEnabled(False)
        else:
            self.buttons[self.prev_text].setEnabled(True)
            self.buttons[self.next_text].setEnabled(True)

    @pyqtSlot()
    def handle_change(self):
        current_idx = self.buttons['Image'].currentIndex()
        sender_text = self.sender().text() if self.sender() is not None else 'None'
        if sender_text == self.first_text:
            current_idx = 0
        elif sender_text == self.last_text:
            current_idx = self.buttons['Image'].count() - 1
        elif sender_text == self.prev_text:
            current_idx -= 1
        elif sender_text == self.next_text:
            current_idx += 1
        else:
            current_idx = current_idx
        self.buttons['Image'].blockSignals(True)
        self.buttons['Image'].setCurrentIndex(current_idx)
        self.buttons['Image'].blockSignals(False)
        self.buttons['Image'].activated.emit(current_idx)
        self.buttons['Image'].currentTextChanged.emit(self.buttons['Image'].currentText())

    @pyqtSlot()
    def reset_values(self):
        self.buttons['Filter'].setText('')
        self.buttons['Filter'].textEdited.emit('')
        self.handle_change()

    @pyqtSlot(str)
    def filter_combo(self, text):
        items = [entry for entry in self._full_combo_list if text in entry]

        self.buttons['Image'].blockSignals(True)
        self.buttons['Image'].clear()
        self.buttons['Image'].addItems(['latest'] * bool(text == '') + items)
        self.buttons['Image'].blockSignals(False)
        if items:
            self.handle_change()

    def get_value(self):
        return self.buttons['Image'].currentText()

    def set_values(self, value_list):
        self._full_combo_list = value_list
        if self.buttons['Filter'].text() == '':
            self.buttons['Image'].blockSignals(True)
            current_value = self.buttons['Image'].currentText()
            self.buttons['Image'].clear()
            self.buttons['Image'].addItems(['latest'] + self._full_combo_list)
            idx = self.buttons['Image'].setCurrentText(current_value)
            self.buttons['Image'].blockSignals(False)
            if idx == -1:
                self.handle_change()


class TrimWidget(QWidget):
    sig_update = pyqtSignal()
    sig_hide = pyqtSignal(int)

    def __init__(self, plot_typ, min_default_x, max_default_x, min_default_y, max_default_y, bin_default, parent=None):
        super(TrimWidget, self).__init__(parent=parent)

        layout = QHBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)
        self._name_min_y = 'Min Y'
        self._name_max_y = 'Max Y'
        self._name_min_x = 'Min X'
        self._name_max_x = 'Max X'
        self._name_bins = 'Bins'

        self.widget_idx = 0
        self.previous_idx = 1
        self.default_idx = 2

        fields = [
            [self._name_min_x, str(min_default_x)],
            [self._name_max_x, str(max_default_x)],
            [self._name_min_y, str(min_default_y)],
            [self._name_max_y, str(max_default_y)],
            [self._name_bins, str(bin_default)],
            ]
        self.buttons = {}
        for label, default in fields:
            self.buttons[label] = [QLineEdit(default, self), default, default]
            self.buttons[label][self.widget_idx].editingFinished.connect(self.sig_update.emit)
            qt_label = QLabel(label + ':', self)

            if not plot_typ == 'histogram' and label == self._name_bins:
                self.buttons[label][self.widget_idx].setVisible(False)
                qt_label.setVisible(False)
            else:
                layout.addWidget(qt_label)
                layout.addWidget(self.buttons[label][self.widget_idx])

        self.btn_reset = QPushButton('Reset', self)
        self.btn_reset.setObjectName('frame')
        self.btn_reset.clicked.connect(self.reset_values)
        layout.addWidget(self.btn_reset)

        check_hide = QCheckBox('Hide overview', self)
        check_hide.setObjectName('frame')
        check_hide.stateChanged.connect(self.sig_hide.emit)
        layout.addWidget(check_hide)
        layout.addStretch(1)

    @pyqtSlot()
    def reset_values(self):
        for entry in self.buttons.values():
            entry[self.widget_idx].setText(entry[self.default_idx])
        self.sig_update.emit()

    def get_values(self):
        previous_dict = {}
        for key, value in self.buttons.items():
            previous_dict[key] = value[self.previous_idx]

        return_dict = {}
        try:
            for key, value in self.buttons.items():
                return_dict[key] = float(value[self.widget_idx].text())
        except ValueError:
            tu.message('Non-float value detected! Falling back to previous values!')
            self.set_values(previous_dict)
            return

        if return_dict[self._name_min_x] > return_dict[self._name_max_x] or return_dict[self._name_min_y] > return_dict[self._name_max_y]:
            tu.message('Minimum cannot be greater than maximum! Falling back to previous values!')
            self.set_values(previous_dict)
            return

        try:
            return_dict[self._name_bins] = int(return_dict[self._name_bins])
        except ValueError:
            tu.message('Bins need to be an integer! Falling back to previous values!')
            self.set_values(previous_dict)
            return

        if return_dict[self._name_bins] <= 0:
            tu.message('Bins need to be a positive integer > 0! Falling back to previous values!')
            self.set_values(previous_dict)
            return

        for key, value in return_dict.items():
            self.buttons[key][self.previous_idx] = str(value)

        return return_dict.values()

    def set_values(self, value_dict):
        for key, value in value_dict.items():
            self.buttons[key][0].setText(str(value))


class MplCanvas(FigureCanvas):
    def __init__(self, no_grid, width=5, height=5, dpi=100, parent=None):
        
        self.fig = matplotlib.figure.Figure(figsize=(width, height), dpi=dpi)
        self.axes = self.fig.add_subplot(111)
        self.axes.grid(not no_grid)
        self.axes.get_xaxis().set_visible(not no_grid)
        self.axes.get_yaxis().set_visible(not no_grid)
        self.axes.autoscale(enable=False)
        self.tight_layout()
        super(MplCanvas, self).__init__(self.fig)

    def tight_layout(self):
        try:
            self.fig.tight_layout()
        except np.linalg.linalg.LinAlgError as e:
            print(e)


class MplCanvasWidget(QWidget):
    def __init__(self, no_grid, width=5, height=5, dpi=100, parent=None):
        super(MplCanvasWidget, self).__init__(parent)
        self.mpl_canvas = MplCanvas(no_grid=no_grid, width=width, height=height, dpi=dpi, parent=parent)
        layout = QVBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.addWidget(self.mpl_canvas)

    def __del__(self):
        matplotlib.pyplot.close(self.mpl_canvas.fig)
        del self.mpl_canvas


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

    def __init__(self, label, plot_typ, dock_widget, twin_container, *args, parent=None, **kwargs):
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
        self.twin_container = twin_container
        self.twin_canvas = None

        layout_v = QVBoxLayout(self)
        self.layout_canvas = QHBoxLayout()
        self._plot_ref = []
        self._canvas_list = []
        self._is_started = False

        if self.plot_typ in ('values', 'histogram'):
            self._bins = 50
            self._minimum_x = float('-inf')
            self._maximum_x = float('inf')
            self._minimum_y = float('-inf')
            self._maximum_y = float('inf')

            self._color = '#68a3c3'
            self.markersize = 4

            self._cur_min_x = 0
            self._cur_max_x = 0
            self._cur_min_y = 0
            self._cur_max_y = 0

            self._applied_min_x = 0
            self._applied_max_x = 0
            self._applied_min_y = 0
            self._applied_max_y = 0

            n_data = 50
            self._xdata_tmp = np.arange(n_data)
            self._ydata_tmp = np.array([random.randint(0, 10) for i in range(n_data)])
            self._xdata = np.array([])
            self._ydata = np.array([])
            self.mask = None

            self.trim_widget = TrimWidget(
                self.plot_typ,
                self._minimum_x,
                self._maximum_x,
                self._minimum_y,
                self._maximum_y,
                self._bins,
                self
                )
            self.trim_widget.sig_update.connect(self.update_trim)
            self.trim_widget.sig_hide.connect(self.hide_twin)
            layout_v.addWidget(self.trim_widget, stretch=0)

        elif plot_typ == 'image' and label == 'image':
            n_data = 50
            self._xdata_tmp = np.arange(n_data)
            self._ydata_tmp = np.array([random.randint(0, 10) for i in range(n_data)])

            self.select_widget = SelectWidget(self)
            self.select_widget.sig_update.connect(self.set_current_image_name)
            layout_v.addWidget(self.select_widget, stretch=0)

            self._image_dict = {}
            self.current_image_name = 'latest'

        layout_v.addLayout(self.layout_canvas, stretch=1)

    @pyqtSlot(int)
    def hide_twin(self, state):
        if self.twin_canvas is not None:
            self.twin_container.handle_show(self.plot_typ, self.twin_canvas, not state)

    @pyqtSlot(str)
    def set_current_image_name(self, text):
        self.current_image_name = text
        self.update_figure()

    def start_plotting(self):
        if not self._is_started:
            self.add_canvas()
            self.parent.parent.content[self.parent.parent_layout].sig_start_plot.connect(self.update_figure)
            self._is_started = True

    def add_canvas(self):
        layout_v = QVBoxLayout()
        is_image = self.plot_typ == 'image'
        self.canvas = MplCanvasWidget(parent=self, no_grid=is_image)
        self._plot_ref.append(None)
        if self.twin_container is not None and not is_image:
            self.twin_canvas = MplCanvasWidget(parent=self, no_grid=is_image)
            self.twin_container.add_to_layout(self.plot_typ, self.twin_canvas)
            self._plot_ref.append(None)
        else:
            self.twin_canvas = None
        toolbar = NavigationToolbar(self.canvas.mpl_canvas, self)
        toolbar.actions()[0].triggered.connect(self.force_update)

        layout_v.addWidget(toolbar)
        layout_v.addWidget(self.canvas, stretch=1)

        self.layout_canvas.addLayout(layout_v)
        self._canvas_list.append(self.canvas)

    def clear_canvas(self):
        for idx in reversed(range(self.layout_canvas.count())):
            current_layout = self.layout_canvas.itemAt(idx)
            for idx2 in reversed(range(current_layout.count())):
                widget = current_layout.itemAt(idx2).widget()
                try:
                    self._canvas_list.remove(widget)
                except ValueError:
                    pass
                current_layout.removeWidget(widget)
                widget.setParent(None)
                widget = None
                del widget
            self.layout_canvas.removeItem(current_layout)
            current_layout.setParent(None)
            current_layout = None
            del current_layout
        self._plot_ref = []

    @pyqtSlot(str, str, object, str, object)
    def set_settings(self, name, name_no_feedback, data, directory_name, settings):
        self._name = name
        self._name_no_feedback = name_no_feedback
        self._data = data
        self._directory_name = directory_name
        self._settings = settings

    @pyqtSlot()
    def update_trim(self):
        return_value = self.trim_widget.get_values()
        if return_value is not None:
            self._minimum_x, self._maximum_x, self._minimum_y, self._maximum_y, self._bins = \
                return_value
            self.force_update()

    def update_data(self, data_x, data_y):
        if self.plot_typ in ('values', 'histogram'):
            self._ydata_tmp = np.array(data_y.tolist() + [random.randint(0, 1000)])
            self._xdata_tmp = np.array(data_x.tolist() + [data_x[-1]+1])

            mask_y = np.logical_and(self._ydata_tmp >= self._minimum_y, self._ydata_tmp <= self._maximum_y)
            mask_x = np.logical_and(self._xdata_tmp >= self._minimum_x, self._xdata_tmp <= self._maximum_x)
            self.mask = np.logical_and(mask_y, mask_x)

            if self.plot_typ == 'values':
                self._xdata = self._xdata_tmp[self.mask]
                self._ydata = self._ydata_tmp[self.mask]
            elif self.plot_typ == 'histogram':
                self._ydata, self._xdata = np.histogram(self._ydata_tmp[self.mask], self._bins)
        elif self.plot_typ == 'image':
            self._ydata_tmp = np.array(data_y.tolist()[1:] + [random.randint(0, 1000)])
            self._xdata_tmp = data_x

            data1 = np.multiply.outer(self._xdata_tmp, self._ydata_tmp)
            data2 = np.subtract.outer(self._xdata_tmp, self._ydata_tmp)

            self._image_dict[str(np.sum(self._ydata_tmp))] = [
                data1,
                data2
                ]
            self.select_widget.set_values(list(self._image_dict.keys()))

        else:
            assert False, self.plot_typ


    @pyqtSlot()
    def force_update(self):
        for plot_line in self._plot_ref:
            if plot_line is not None:
                for entry in plot_line:
                    entry.remove()
        self._plot_ref = [None] * len(self._plot_ref)
        self.update_figure()

    def prepare_axes(self, update):
        if (
                (
                    self._cur_min_x > min(self._xdata) or \
                    self._cur_min_y > min(self._ydata) or \
                    self._cur_max_x < max(self._xdata) or \
                    self._cur_max_y < max(self._ydata)
                    ) and \
                    self.canvas.mpl_canvas.axes.get_xlim() == (self._applied_min_x, self._applied_max_x) and \
                    self.canvas.mpl_canvas.axes.get_ylim() == (self._applied_min_y, self._applied_max_y)
                ) or \
                update:

            is_histogram = bool(self.plot_typ == 'histogram')

            width = self._xdata[1] - self._xdata[0]
            diff_x = np.max(self._xdata) - np.min(self._xdata)
            diff_y = np.max(self._ydata) - np.min(self._ydata) * is_histogram

            mult = 0.025
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

        is_active = self.parent.parent.content[self.parent.parent_layout] == self.parent.parent.content[self.parent.parent_layout].latest_active[0]

        overview_is_floating = self.twin_container.dock_widget.isFloating() if self.twin_canvas is not None else False

        #print('self.label', self.label)
        #print('self.plot_typ', self.plot_typ)
        #print('self.dock_widget.isFloating()', self.dock_widget.isFloating())
        #print('self.dock_widget.isVisible()', self.dock_widget.isVisible())
        #print('is_active', is_active)
        #print('overview_is_floating', overview_is_floating)
        #print('self.isVisible()', self.isVisible())
        #print('self.twin_container.dock_widget.isVisible()', self.twin_container.dock_widget.isVisible() if self.twin_container is not None else None)
        #print('self.twin_container.dock_widget.widget().isVisible()', self.twin_container.dock_widget.widget().isVisible() if self.twin_container is not None else None)
        #print('self.twin_container.isVisible()', self.twin_container.isVisible() if self.twin_container is not None else None)
        #print('')

        if not self.dock_widget.isFloating() and not is_active and not overview_is_floating:
            return

        if not self._plot_ref:
            return

        print('self.label', self.label)

        self.update_data(self._xdata_tmp, self._ydata_tmp)
        if self.plot_typ in ('values', 'histogram'):
            try:
                update = self.prepare_axes(update=self._plot_ref[0] is None)
            except ValueError:
                return

            for plot_idx, canvas in enumerate((self.canvas, self.twin_canvas)):
                if canvas is None:
                    continue

                if update and self._plot_ref[plot_idx] is not None:
                    for entry in self._plot_ref[plot_idx]:
                        entry.remove()

                if plot_idx != 0:
                    size = 5
                else:
                    size = 10
                matplotlib.rcParams.update({'font.size': size})
                matplotlib.rcParams.update({'xtick.labelsize': size})
                matplotlib.rcParams.update({'ytick.labelsize': size})
                matplotlib.rcParams.update({'axes.labelsize': size})

                if self.plot_typ == 'values':
                    self.update_values(canvas.mpl_canvas, plot_idx, update)
                elif self.plot_typ == 'histogram':
                    self.update_histogram(canvas.mpl_canvas, plot_idx, update)

                canvas.mpl_canvas.axes.set_title(self.label)
                if update:
                    canvas.mpl_canvas.axes.set_xlim(self._applied_min_x, self._applied_max_x)
                    canvas.mpl_canvas.axes.set_ylim(self._applied_min_y, self._applied_max_y)
                    canvas.mpl_canvas.tight_layout()
                    canvas.mpl_canvas.draw()
                else:
                    canvas.mpl_canvas.update()
                    canvas.mpl_canvas.flush_events()

        elif self.plot_typ in ('image'):
            self.update_image()

    def update_image(self):
        current_name = self.current_image_name
        if current_name == 'latest':
            try:
                current_name = list(self._image_dict.keys())[-1]
            except IndexError:
                pass

        try:
            data_list = self._image_dict[current_name]
        except KeyError:
            self.clear_canvas()
            return

        if len(data_list) != len(self._canvas_list):
            self.clear_canvas()
            for _ in range(len(data_list)):
                self.add_canvas()

        for idx, data in enumerate(data_list):
            if self._plot_ref[idx] is None:
                self._plot_ref[idx] = self._canvas_list[idx].mpl_canvas.axes.imshow(data)
            else:
                self._plot_ref[idx].set_data(data)
            self._canvas_list[idx].mpl_canvas.axes.set_xlim(0, data.shape[0]-1)
            self._canvas_list[idx].mpl_canvas.axes.set_ylim(0, data.shape[1]-1)
            self._canvas_list[idx].mpl_canvas.axes.set_title(current_name)
            self._canvas_list[idx].mpl_canvas.tight_layout()
            self._canvas_list[idx].mpl_canvas.draw()

    def update_histogram(self, canvas, plot_idx, update):
        width = self._xdata[1] - self._xdata[0]
        if update:
            self._plot_ref[plot_idx] = canvas.axes.bar(
                    self._xdata[:-1],
                    self._ydata,
                    width,
                    facecolor=self._color,
                    edgecolor='k'
                    )
        else:
            for value, patch in zip(self._ydata, self._plot_ref[plot_idx]):
                if patch.get_height() != value:
                    patch.set_height(value)
                    patch.set_width(width)
                    try:
                        canvas.axes.draw_artist(patch)
                    except AttributeError:
                        canvas.draw()

    def update_values(self, canvas, plot_idx, update):
        if update:
            self._plot_ref[plot_idx] = canvas.axes.plot(
                self._xdata,
                self._ydata,
                '.',
                color=self._color,
                markersize=self.markersize / (plot_idx+1)
                )
        else:
            self._plot_ref[plot_idx][0].set_data(self._xdata, self._ydata)
            try:
                canvas.axes.draw_artist(self._plot_ref[plot_idx][0])
            except AttributeError:
                canvas.draw()
