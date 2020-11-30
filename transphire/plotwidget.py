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

import json
import os
import warnings
import imageio
import numpy as np
import matplotlib
matplotlib.use('QT5Agg')

from PyQt5.QtWidgets import QWidget, QVBoxLayout, QHBoxLayout, QComboBox, QPushButton, QLineEdit, QLabel, QCheckBox
from PyQt5.QtCore import pyqtSlot, pyqtSignal, Qt
from matplotlib.backends.backend_qt5agg import (
    FigureCanvasQTAgg as FigureCanvas,
    NavigationToolbar2QT as NavigationToolbar
    )

from . import transphire_utils as tu
warnings.filterwarnings('ignore')

LIGHTRED = '#ff726f'
LIGHTBLUE = '#3481B8'


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
            try:
                self.buttons[label].setSizeAdjustPolicy(QComboBox.AdjustToContents)
            except AttributeError:
                pass

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

        layout.addStretch(1)

    @pyqtSlot(int)
    def check_enable(self, idx):
        if idx == 0 and idx == self.buttons['Image'].count() - 1:
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
        try:
            sender_text = self.sender().text() if self.sender() is not None else 'None'
        except AttributeError:
            sender_text = 'None'
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

        cur_state = self.buttons['Image'].blockSignals(True)
        self.buttons['Image'].setCurrentIndex(current_idx)
        self.buttons['Image'].blockSignals(cur_state)

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

        cur_state = self.buttons['Image'].blockSignals(True)
        self.buttons['Image'].clear()
        self.buttons['Image'].addItems(['latest'] * bool(text == '') + items)
        self.buttons['Image'].blockSignals(cur_state)
        if items:
            self.handle_change()

    def get_value(self):
        return self.buttons['Image'].currentText()

    def set_values(self, value_list):
        self._full_combo_list = value_list.tolist()

        current_value = self.buttons['Image'].currentText()
        cur_state = self.buttons['Image'].blockSignals(True)
        self.buttons['Filter'].textEdited.emit(self.buttons['Filter'].text())

        idx = self.buttons['Image'].setCurrentText(current_value)
        self.buttons['Image'].blockSignals(cur_state)
        if idx != -1:
            self.handle_change()
        else:
            self.buttons['Image'].activated.emit(self.buttons['Image'].currentIndex())



class TrimWidget(QWidget):
    sig_update = pyqtSignal()
    sig_hide = pyqtSignal(int)
    sig_set_state = pyqtSignal(bool)

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
                layout.addWidget(qt_label, stretch=0)
                layout.addWidget(self.buttons[label][self.widget_idx], stretch=1)

        self.btn_reset = QPushButton('Reset', self)
        self.btn_reset.setObjectName('frame')
        self.btn_reset.clicked.connect(self.reset_values)
        layout.addWidget(self.btn_reset, stretch=0)

        self.check_hide = QCheckBox('Hide overview', self)
        self.check_hide.setObjectName('frame')
        self.check_hide.stateChanged.connect(self.sig_hide.emit)
        layout.addWidget(self.check_hide, stretch=0)

        self.sig_set_state.connect(self.set_state)

    @pyqtSlot(bool)
    def set_state(self, state):
        self.check_hide.setChecked(state)

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
            return None, None

        if return_dict[self._name_min_x] > return_dict[self._name_max_x] or return_dict[self._name_min_y] > return_dict[self._name_max_y]:
            tu.message('Minimum cannot be greater than maximum! Falling back to previous values!')
            self.set_values(previous_dict)
            return None, None

        try:
            return_dict[self._name_bins] = int(return_dict[self._name_bins])
        except ValueError:
            tu.message('Bins need to be an integer! Falling back to previous values!')
            self.set_values(previous_dict)
            return None, None

        if return_dict[self._name_bins] <= 0:
            tu.message('Bins need to be a positive integer > 0! Falling back to previous values!')
            self.set_values(previous_dict)
            return None, None

        for key, value in return_dict.items():
            self.buttons[key][self.previous_idx] = str(value)

        return return_dict.values(), previous_dict

    def set_values(self, value_dict):
        for key, value in value_dict.items():
            self.buttons[key][0].setText(str(value))


class MplCanvas(FigureCanvas):
    sig_twin = pyqtSignal(object)
    def __init__(self, no_grid, width=5, height=5, dpi=100, parent=None):
        self.my_parent = parent
        self.fig = matplotlib.figure.Figure(figsize=(width, height), dpi=dpi)
        self.axes = self.fig.add_subplot(111)
        self.axes.grid(True)
        self.axes.autoscale(enable=False)
        self.axes.set_axisbelow(True)
        self.fig.set_tight_layout({'pad': 0.2})
        super(MplCanvas, self).__init__(self.fig)

    #@pyqtSlot(object)
    #def hover_twin(self, event):
    #    vis = self.tooltip.get_visible()
    #    if cont:
    #        self.tooltip.set_visible(True)
    #        self.draw_idle()
    #    else:
    #        if vis:
    #            self.tooltip.set_visible(False)
    #            self.draw_idle()

class MplCanvasWidget(QWidget):

    def __init__(self, no_grid, plot_type, is_twin=False, width=5, height=5, dpi=100, parent=None):
        super(MplCanvasWidget, self).__init__(parent)
        self.mpl_canvas = MplCanvas(no_grid=no_grid, width=width, height=height, dpi=dpi, parent=parent)
        layout = QVBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.addWidget(self.mpl_canvas)

        if is_twin:
            self.font_size = 6
            self.labelpad = 0
        else:
            self.font_size = 8
            self.labelpad = 5

        self.no_grid = no_grid
        self.plot_type = plot_type

        self.mpl_canvas.axes.tick_params(axis='both', which='major', labelsize=self.font_size)
        self.mpl_canvas.axes.ticklabel_format(useOffset=False, style='plain')
        if is_twin:
            self.mpl_canvas.mpl_connect('button_press_event', self.mpl_canvas.sig_twin.emit)
            self.setToolTip(
                "Left mouse button: Show larger version of the plot\n"
                "Right mouse button: Hide plot from overview\n"
                "(Can be re-enabled in the larger version)"
                )

    def __del__(self):
        matplotlib.pyplot.close(self.mpl_canvas.fig)
        del self.mpl_canvas

    def update_labels(self, title, label_x, label_y):
        title = tu.split_maximum(title, 20)

        self.mpl_canvas.axes.set_title(title, fontsize=self.font_size, pad=self.labelpad)
        if self.plot_type == 'histogram':
            final_label_y = tu.split_maximum(label_x[1], 20)
            final_label_x = tu.split_maximum(label_y[1], 20)
        elif self.plot_type == 'values':
            final_label_x = tu.split_maximum(label_x[0], 20)
            final_label_y = tu.split_maximum(label_y[1], 20)
        elif self.plot_type == 'image':
            final_label_x = tu.split_maximum(label_x, 20)
            final_label_y = tu.split_maximum(label_y, 20)

        self.mpl_canvas.axes.set_ylabel(
            final_label_y,
            fontsize=self.font_size,
            labelpad=self.labelpad
            )
        self.mpl_canvas.axes.set_xlabel(
            final_label_x,
            fontsize=self.font_size,
            labelpad=self.labelpad
            )


class ViewWidget(QWidget):
    sig_hide = pyqtSignal()

    def __init__(self, parent=None):
        super(ViewWidget, self).__init__(parent)
        layout = QHBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)
        entries = ['Min', 'Max', 'Mean', 'Median', 'Sum', 'In range', 'of']
        self.widgets = {}
        for entry in entries:
            layout.addWidget(QLabel('{}:'.format(entry)), stretch=0)
            label = QLineEdit('--')
            label.setAlignment(Qt.AlignRight)
            label.setReadOnly(True)
            layout.addWidget(label, stretch=1)
            self.widgets[entry] = label
        check_hide = QCheckBox('Hide marker', self)
        check_hide.clicked.connect(self.sig_hide.emit)
        layout.addWidget(check_hide, stretch=0)

        self.widgets['Mean'].setStyleSheet('color: {}'.format(LIGHTBLUE))
        self.widgets['Median'].setStyleSheet('color: {}'.format(LIGHTRED))

    def update_label(self, label_dict):
        for key, value in label_dict.items():
            try:
                self.widgets[key].setText('{0:d}'.format(value))
            except ValueError:
                self.widgets[key].setText('{0:10.2f}'.format(value))


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
        self._is_first = True

        layout_v = QVBoxLayout(self)
        self.layout_canvas = QHBoxLayout()
        self._plot_ref = []
        self._image_ref = []
        self._mean_ref = []
        self._median_ref = []
        self._canvas_list = []
        self._is_started = False
        self.setup_values()

        if self.plot_typ in ('values', 'histogram'):
            self._hide_marker = False

            self.markersize = 4

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

            self.view_widget = ViewWidget(self)
            self.view_widget.sig_hide.connect(self.hide_marker)
            layout_v.addWidget(self.view_widget, stretch=0)

        elif plot_typ == 'image' and label == 'image':
            self.select_widget = SelectWidget(self)
            self.select_widget.sig_update.connect(self.set_current_image_name)
            layout_v.addWidget(self.select_widget, stretch=0)

            self.current_image_name = 'latest'

        layout_v.addLayout(self.layout_canvas, stretch=1)

    def setup_values(self):
        self._xdata = np.array([])
        self._ydata = np.array([])
        self._data = None
        self._basenames = None
        self._directory_name = None
        self._color = '#68a3c3'

        self._cur_min_x = 0
        self._cur_max_x = 0
        self._cur_min_y = 0
        self._cur_max_y = 0

        self._applied_min_x = 0
        self._applied_max_x = 0
        self._applied_min_y = 0
        self._applied_max_y = 0

        self._xdata_raw = np.array([])
        self._ydata_raw = np.array([])
        self._bins = 50
        self._minimum_x = float('-inf')
        self._maximum_x = float('inf')
        self._minimum_y = float('-inf')
        self._maximum_y = float('inf')
        self._previous_dict = {}
        self.mean = None
        self.median = None

    @pyqtSlot()
    def hide_marker(self):
        self._hide_marker = not self._hide_marker
        self.force_update()

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
            self.parent.parent.content[self.parent.parent_layout].sig_start_plot.connect(
                self.update_figure
                )
            self._is_started = True

    def add_canvas(self):
        layout_v = QVBoxLayout()
        is_image = self.plot_typ == 'image'
        canvas_settings = {
            'parent': self,
            'no_grid': is_image,
            'plot_type': self.plot_typ,
            }
        self.canvas = MplCanvasWidget(**canvas_settings)
        self._canvas_list.append(self.canvas)
        self._plot_ref.append(None)
        self._mean_ref.append(None)
        self._median_ref.append(None)

        if self.twin_container is not None and not is_image:
            self.twin_canvas = MplCanvasWidget(**canvas_settings, is_twin=True)
            self._canvas_list.append(self.twin_canvas)
            self.twin_container.add_to_layout(self.plot_typ, self.twin_canvas)
            self._plot_ref.append(None)
            self._mean_ref.append(None)
            self._median_ref.append(None)
        else:
            self.twin_canvas = None

        toolbar = NavigationToolbar(self.canvas.mpl_canvas, self)
        toolbar.actions()[0].triggered.connect(self.force_update)

        layout_v.addWidget(toolbar)
        layout_v.addWidget(self.canvas, stretch=1)

        self.layout_canvas.addLayout(layout_v)

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
        self._mean_ref = []
        self._median_ref = []

    @pyqtSlot(str, str, object, str, object)
    def set_settings(self, name, name_no_feedback, data, directory_name, settings):
        self._directory_name = directory_name
        self._data = data
        self._basenames = np.array([os.path.basename(entry) for entry in data['file_name']])
        if self.plot_typ in ('values', 'histogram'):
            self._xdata_raw, self._ydata_raw, labels_x, label_y, title = tu.get_function_dict()[name_no_feedback]['plot'](
                data=data,
                settings=settings,
                label=self.label,
                )
            if self._is_first:
                self._is_first = False
                for canvas in self._canvas_list:
                    canvas.update_labels(title, labels_x, label_y)
            self.update_figure()

        elif self.plot_typ == 'image':
            self.select_widget.set_values(self._basenames)

    @pyqtSlot()
    def update_trim(self):
        return_value, self._previous_dict = self.trim_widget.get_values()
        if return_value is not None:
            self._minimum_x, self._maximum_x, self._minimum_y, self._maximum_y, self._bins = \
                return_value
            self.force_update(do_message=True)

        self.force_update()

    def update_data(self, do_message=False):
        if self.plot_typ in ('values', 'histogram'):
            mask_y = np.logical_and(
                self._ydata_raw >= self._minimum_y,
                self._ydata_raw <= self._maximum_y
                )
            mask_x = np.logical_and(
                self._xdata_raw >= self._minimum_x,
                self._xdata_raw <= self._maximum_x
                )
            mask = np.logical_and(mask_y, mask_x)

            if self._ydata_raw[mask].size == 0 or self._xdata_raw[mask].size == 0:
                self.trim_widget.set_values(self._previous_dict)
                if do_message:
                    tu.message('Masking values do not contain any data points! Falling back to previous values!')
                return False

            self.mean = np.mean(self._ydata_raw[mask])
            self.median = np.median(self._ydata_raw[mask])
            self.view_widget.update_label({
                'Min': np.min(self._ydata_raw[mask]),
                'Max': np.max(self._ydata_raw[mask]),
                'Sum': np.sum(self._ydata_raw[mask]),
                'Mean': self.mean,
                'Median': self.median,
                'In range': np.count_nonzero(mask),
                'of': mask.shape[0],
                })

            if self.plot_typ == 'values':
                self._xdata = self._xdata_raw[mask]
                self._ydata = self._ydata_raw[mask]
            elif self.plot_typ == 'histogram':
                self._ydata, self._xdata = np.histogram(
                    self._ydata_raw[mask],
                    self._bins
                    )
        return True

    @pyqtSlot()
    def force_update(self, do_message=False):
        for plot_line in self._median_ref:
            if plot_line is not None:
                for entry in plot_line:
                    entry.remove()
        for plot_line in self._mean_ref:
            if plot_line is not None:
                for entry in plot_line:
                    entry.remove()
        for plot_line in self._plot_ref:
            if plot_line is not None:
                for entry in plot_line:
                    entry.remove()
        self._plot_ref = [None] * len(self._plot_ref)
        self._median_ref = [None] * len(self._median_ref)
        self._mean_ref = [None] * len(self._mean_ref)
        self.update_figure(do_message)

    def prepare_axes(self, update):
        if (
                (
                    self._cur_min_x > np.min(self._xdata) or \
                    self._cur_min_y > np.min(self._ydata) or \
                    self._cur_max_x < np.max(self._xdata) or \
                    self._cur_max_y < np.max(self._ydata)
                    ) and \
                    self.canvas.mpl_canvas.axes.get_xlim() == (self._applied_min_x, self._applied_max_x) and \
                    self.canvas.mpl_canvas.axes.get_ylim() == (self._applied_min_y, self._applied_max_y)
                ) or \
                update:

            is_histogram = bool(self.plot_typ == 'histogram')

            try:
                width = self._xdata[1] - self._xdata[0]
            except IndexError:
                width = 0
                assert not is_histogram, (self._xdata, self._ydata)

            diff_x = np.max(self._xdata) - np.min(self._xdata)
            diff_x = np.maximum(diff_x, 1)
            diff_y = np.max(self._ydata) - np.min(self._ydata) * bool(not is_histogram)
            diff_y = np.maximum(diff_y, 1)

            mult = 0.05
            boarder_x = np.maximum(diff_x * mult / 2, width * is_histogram)
            boarder_y = diff_y * mult / 2

            if self.plot_typ == 'values':
                self._cur_min_x = np.min(self._xdata) - boarder_x
                self._cur_min_y = np.min(self._ydata) - boarder_y
                self._cur_max_x = np.max(self._xdata) + boarder_x
                self._cur_max_y = np.max(self._ydata) + boarder_y

                self._applied_min_x = self._cur_min_x - boarder_x / 2
                self._applied_min_y = self._cur_min_y - boarder_y / 2
                self._applied_max_x = self._cur_max_x + boarder_x / 2
                self._applied_max_y = self._cur_max_y + boarder_y / 2

            elif self.plot_typ == 'histogram':
                self._cur_min_x = np.min(self._xdata[:-1]) - boarder_x
                self._cur_min_y = 0
                self._cur_max_x = np.max(self._xdata[:-1]) + boarder_x
                self._cur_max_y = np.max(self._ydata) + boarder_y

                self._applied_min_x = self._cur_min_x
                self._applied_min_y = self._cur_min_y
                self._applied_max_x = self._cur_max_x
                self._applied_max_y = self._cur_max_y + boarder_y / 2

            update = True
        return update

    @pyqtSlot()
    def do_data_reset(self):
        if self.plot_typ in ('values', 'histogram'):
            self._cur_min_x = 0.5
            self._cur_max_x = 0.6
            self._cur_min_y = 0.5
            self._cur_max_y = 0.6

            self._applied_min_x = 0.5
            self._applied_max_x = 0.6
            self._applied_min_y = 0.5
            self._applied_max_y = 0.6

            for canvas in self._canvas_list:
                canvas.mpl_canvas.axes.set_xlim(
                    self._applied_min_x,
                    self._applied_max_x
                    )
                canvas.mpl_canvas.axes.set_ylim(
                    self._applied_min_y,
                    self._applied_max_y
                    )
                canvas.mpl_canvas.draw()

    @pyqtSlot()
    def update_figure(self, do_message=False):

        try:
            is_active = self.parent.parent.content[self.parent.parent_layout] == self.parent.parent.content[self.parent.parent_layout].latest_active[0]

            overview_is_floating = self.twin_container.dock_widget.isFloating() if self.twin_canvas is not None else False

            if not self.dock_widget.isFloating() and not is_active and not overview_is_floating:
                return

            if not self._plot_ref:
                return

            if not self.update_data(do_message):
                return

            if self.plot_typ in ('values', 'histogram'):
                try:
                    update = self.prepare_axes(update=self._plot_ref[0] is None)
                except ValueError as e:
                    print(e)
                    return

                for plot_idx, canvas in enumerate(self._canvas_list):
                    if update and self._mean_ref[plot_idx] is not None:
                        for entry in self._mean_ref[plot_idx]:
                            entry.remove()
                    if update and self._median_ref[plot_idx] is not None:
                        for entry in self._median_ref[plot_idx]:
                            entry.remove()
                    if update and self._plot_ref[plot_idx] is not None:
                        for entry in self._plot_ref[plot_idx]:
                            entry.remove()

                    if self.plot_typ == 'values':
                        self.update_values(canvas.mpl_canvas, plot_idx, update)
                    elif self.plot_typ == 'histogram':
                        self.update_histogram(canvas.mpl_canvas, plot_idx, update)
                    self.update_helpers(canvas.mpl_canvas, plot_idx, update, self.plot_typ)

                    if update:
                        canvas.mpl_canvas.axes.set_xlim(
                            self._applied_min_x,
                            self._applied_max_x
                            )
                        canvas.mpl_canvas.axes.set_ylim(
                            self._applied_min_y,
                            self._applied_max_y
                            )
                        canvas.mpl_canvas.draw()
                    else:
                        canvas.mpl_canvas.update()
                        canvas.mpl_canvas.flush_events()
                    if plot_idx == 0:
                        output_name = os.path.join(
                            self._directory_name,
                            'overview_plots',
                            '{0}_{1}.png'.format(
                                self.label,
                                self.plot_typ,
                                )
                            ).replace(' ', '_')
                        try:
                            tu.mkdir_p(os.path.dirname(output_name))
                            canvas.mpl_canvas.fig.savefig(output_name)
                        except Exception as e:
                            print(e)
                            pass

            elif self.plot_typ in ('image'):
                self.update_image()
        except Exception:
            pass

    def update_image(self):
        current_name = self.current_image_name
        if current_name == 'latest':
            try:
                current_name = self._basenames[-1]
            except IndexError:
                return
            except TypeError:
                return
        elif not current_name:
            return

        try:
            data_list = self._data['image'][self._basenames == current_name][0].split(';;;')
        except IndexError:
            return
        except KeyError:
            self.clear_canvas()
            return

        if len(data_list) != len(self._canvas_list):
            self.clear_canvas()
            for _ in range(len(data_list)):
                self.add_canvas()

        for idx, data_file in enumerate(data_list):
            label_x = ''
            label_y = ''
            if data_file.endswith('.jpg'):
                try:
                    data = imageio.imread(data_file)[::-1, ...]
                except Exception as e:
                    print('Error reading image: {}. - {}'.format(data_file, str(e)))
                    continue
                if self._plot_ref[idx] is None:
                    self._plot_ref[idx] = [self._canvas_list[idx].mpl_canvas.axes.imshow(data, resample=False, aspect='equal')]
                    self._canvas_list[idx].mpl_canvas.axes.set_xlim(
                        0,
                        data.shape[1]-1
                        )
                    self._canvas_list[idx].mpl_canvas.axes.set_ylim(
                        0,
                        data.shape[0]-1
                        )
                else:
                    self._plot_ref[idx][0].set_data(data)
                self._canvas_list[idx].mpl_canvas.axes.grid(False)
                self._canvas_list[idx].mpl_canvas.axes.get_xaxis().set_visible(False)
                self._canvas_list[idx].mpl_canvas.axes.get_yaxis().set_visible(False)

            elif data_file.endswith('.json'):
                try:
                    with open(data_file, 'r') as read:
                        json_data = json.load(read)
                except Exception as e:
                    print('Error reading image: {}. - {}'.format(data_file, str(e)))
                    continue

                for entry in self._image_ref:
                    for plot_obj in entry:
                        try:
                            plot_obj.remove()
                        except Exception as e:
                            print(e, plot_obj)
                self._image_ref = []

                plot_idx = 0
                label_x = json_data['label_x']
                label_y = json_data['label_y']
                try:
                    is_equal = json_data['is_equal']
                except KeyError:
                    is_equal = True
                min_x = []
                max_x = []
                min_y = []
                max_y = []
                for data_dict in json_data['data']:
                    if is_equal:
                        max_abs = np.maximum(
                            np.max(np.abs(data_dict['values_x'])),
                            np.max(np.abs(data_dict['values_y'])),
                            )
                        min_x.append(-max_abs - np.maximum(max_abs * 0.1, 1))
                        max_x.append(max_abs + np.maximum(max_abs * 0.1, 1))
                        min_y.append(-max_abs - np.maximum(max_abs * 0.1, 1))
                        max_y.append(max_abs + np.maximum(max_abs * 0.1, 1))
                    else:
                        min_x.append(np.min(data_dict['values_x']))
                        max_x.append(np.max(data_dict['values_x']))
                        min_y.append(np.min(data_dict['values_y']))
                        max_y.append(np.max(data_dict['values_y']))
                    self.update_image_plot(
                        self._canvas_list[idx].mpl_canvas,
                        data_dict['values_x'],
                        data_dict['values_y'],
                        data_dict['is_high_res'],
                        data_dict['label_plot'],
                        data_dict['marker'],
                        data_dict['color'],
                        plot_idx,
                        )
                    plot_idx += 1
                self._canvas_list[idx].mpl_canvas.axes.set_xlim(
                    np.min(min_x),
                    np.max(max_x)
                    )
                self._canvas_list[idx].mpl_canvas.axes.set_ylim(
                    np.min(min_y),
                    np.max(max_y)
                    )

            self._canvas_list[idx].update_labels(
                tu.split_maximum(tu.get_name(data_file), 20, '_'),
                label_x,
                label_y,
                )
            self._canvas_list[idx].mpl_canvas.draw()

    def update_histogram(self, canvas, plot_idx, update):
        try:
            width = self._xdata[1] - self._xdata[0]
        except IndexError:
            return
        if update:
            self._plot_ref[plot_idx] = canvas.axes.bar(
                    self._xdata[:-1],
                    self._ydata,
                    width,
                    facecolor=self._color,
                    edgecolor='k'
                    )
        else:
            try:
                canvas.axes.draw_artist(canvas.axes.patch)
                canvas.axes.draw_artist(canvas.axes.gridline)
            except AttributeError:
                canvas.draw()

            for value, patch in zip(self._ydata, self._plot_ref[plot_idx]):
                if patch.get_height() != value:
                    patch.set_height(value)
                    patch.set_width(width)
                    try:
                        canvas.axes.draw_artist(patch)
                    except AttributeError:
                        canvas.draw()

    def update_helpers(self, canvas, plot_idx, update, plot_type):
        if not self._hide_marker:
            mean = [self.mean, self.mean]
            median = [self.median, self.median]
            if plot_type == 'values':
                max_x = np.max(np.abs(self._xdata))*1e5
                values_x = [np.min(self._xdata)-max_x, np.max(self._xdata)+max_x]
                values = [
                    [self._mean_ref, values_x, mean, LIGHTBLUE],
                    [self._median_ref, values_x, median, LIGHTRED]
                    ]
            elif plot_type == 'histogram':
                max_y = np.max(np.abs(self._ydata))*1e5
                values_y = [np.min(self._ydata)-max_y, np.max(self._ydata)+max_y]
                values = [
                    [self._mean_ref, mean, values_y, LIGHTBLUE],
                    [self._median_ref, median, values_y, LIGHTRED]
                    ]

            for aim_list, values_x, values_y, color in values:
                if update:
                    aim_list[plot_idx] = canvas.axes.plot(
                        values_x,
                        values_y,
                        color=color,
                        linewidth=0.8,
                        )
                else:
                    aim_list[plot_idx][0].set_data(values_x, values_y)

                try:
                    canvas.axes.draw_artist(aim_list[plot_idx][0])
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
                canvas.axes.draw_artist(canvas.axes.patch)
                canvas.axes.draw_artist(canvas.axes.gridline)
                canvas.axes.draw_artist(self._plot_ref[plot_idx][0])
            except AttributeError:
                canvas.draw()

    @staticmethod
    def high_res(x_data, y_data, splits):
        cm = matplotlib.cm.get_cmap('viridis')
        if splits != 1:
            n_points = (len(x_data) - 1) * (splits - 1)
            colors = [cm(1.*i/(n_points-1)) for i in range(n_points)]
            new_values = []
            for i in range(len(x_data)-1):
                new_x = np.linspace(x_data[i], x_data[i+1], splits)
                new_y = np.linspace(y_data[i], y_data[i+1], splits)
                for i in range(splits-1):
                    new_values.append([new_x[i:i+2], new_y[i:i+2]])
        else:
            n_points = len(x_data)
            colors = [cm(1.*i/(n_points-1)) for i in range(n_points)]
            new_values = np.array([x_data, y_data]).T
        return colors, new_values

    def update_image_plot(self, canvas, data_x, data_y, high_res, label, marker, color, idx):
        if high_res:
            color, vals = self.high_res(data_x, data_y, 30)
            canvas.axes.set_prop_cycle('color', color)
            for x, y in vals:
                self._image_ref.append(canvas.axes.plot(
                    x,
                    y,
                    '-',
                    ))
            color, vals = self.high_res(data_x, data_y, 1)
            canvas.axes.set_prop_cycle('color', color)
            for x, y in vals:
                self._image_ref.append(canvas.axes.plot(
                    x,
                    y,
                    'o',
                    ))
        else:
            if color is None:
                color = self._color
            self._image_ref.append(canvas.axes.plot(
                data_x,
                data_y,
                marker,
                label=label,
                color=color,
                markeredgecolor='black',
                markersize=6,
                ))
            self._image_ref.append([canvas.axes.legend(loc='best')])
