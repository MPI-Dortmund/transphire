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
import warnings
import imageio
import numpy as np
import matplotlib
matplotlib.use('QT5Agg')
import matplotlib.pyplot as plt
try:
    from PyQt4.QtGui import QWidget, QVBoxLayout, QHBoxLayout, QComboBox, QPushButton, QLineEdit, QLabel
    from PyQt4.QtCore import pyqtSlot
    from matplotlib.backends.backend_qt4agg import (
        FigureCanvasQTAgg as FigureCanvas,
        NavigationToolbar2QT as NavigationToolbar
        )
except ImportError:
    from PyQt5.QtWidgets import QWidget, QVBoxLayout, QHBoxLayout, QComboBox, QPushButton, QLineEdit, QLabel
    from PyQt5.QtCore import pyqtSlot
    from matplotlib.backends.backend_qt5agg import (
        FigureCanvasQTAgg as FigureCanvas,
        NavigationToolbar2QT as NavigationToolbar
        )
from transphire import transphire_utils as tu
warnings.filterwarnings('ignore')


class PlotWidget(QWidget):
    """
    PlotWidget widget.
    Widget used to show data plots.

    Inherits from:
    QWidget

    Signals:
    None
    """

    def __init__(self, label, plot_typ, *args, parent=None, **kwargs):
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
        super(PlotWidget, self).__init__(parent)

        self.color = '#68a3c3'
        self.plot_label = label
        self.plot_typ = plot_typ
        self.x_min = None
        self.x_max = None
        self.y_min = None
        self.y_max = None
        self.title = None
        self.label = None
        self.line = None
        self.rects = None
        self.lower_lim = None
        self.upper_lim = None
        self.img = []
        self.figure = []
        self.axis = []

        layout_v = QVBoxLayout(self)
        self.layout_canvas = QHBoxLayout()

        # Add for image plot typ
        if plot_typ == 'image' and label == 'image':
            self.data = np.array([])
            self.idx = 0
            self.default_value = 'latest'

            layout_h = QHBoxLayout()
            self.combo_box = QComboBox(self)
            self.combo_box.addItems([self.default_value])
            self.combo_box.currentIndexChanged.connect(lambda: self.change_idx('combo'))

            layout_h.addWidget(self.combo_box)
            self.prev_button = QPushButton('Prev', self)
            self.prev_button.setObjectName('frame')
            self.prev_button.clicked.connect(lambda: self.change_idx('prev'))
            self.prev_button.setEnabled(False)

            layout_h.addWidget(self.prev_button)
            self.next_button = QPushButton('Next', self)
            self.next_button.setObjectName('frame')
            self.next_button.clicked.connect(lambda: self.change_idx('next'))
            self.next_button.setEnabled(False)

            layout_h.addWidget(self.next_button)
            self.reset_button = QPushButton(self.default_value, self)
            self.reset_button.setObjectName('frame')
            self.reset_button.clicked.connect(lambda: self.change_idx('reset'))

            layout_h.addWidget(self.reset_button)
            layout_h.addStretch(1)
            layout_v.addLayout(layout_h)
        elif plot_typ == 'values' or plot_typ == 'histogram':
            if plot_typ == 'values':
                axis_name = 'y'
            elif plot_typ == 'histogram':
                axis_name = 'x'
            else:
                assert False, axis_name
            layout_h = QHBoxLayout()
            self.lower_edit = QLineEdit('-inf', self)
            self.upper_edit = QLineEdit('inf', self)
            self.bin_edit = QLineEdit('50', self)

            layout_h.addWidget(QLabel('Lower {0}'.format(axis_name), self))
            layout_h.addWidget(self.lower_edit)
            layout_h.addWidget(QLabel('Upper {0}'.format(axis_name), self))
            layout_h.addWidget(self.upper_edit)
            if plot_typ == 'histogram':
                layout_h.addWidget(QLabel('Bins', self))
                layout_h.addWidget(self.bin_edit)
            else:
                self.bin_edit.setVisible(False)
            layout_h.addStretch(1)
            layout_v.addLayout(layout_h)

        layout_v.addLayout(self.layout_canvas)
        self.add_canvas()

    def add_canvas(self):
        """
        Add a canvas to the interface

        Arguments:
        None

        Returns:
        None
        """
        canvas_layout = QVBoxLayout()
        figure, axis = plt.subplots()
        self.figure.append(figure)
        self.axis.append(axis)

        for entry in self.compute_initial_figure():
            x = entry[0]
            y = entry[1]
            axis.plot(x, y, color=self.color)

        canvas = FigureCanvas(figure)
        canvas.setParent(self)
        toolbar = NavigationToolbar(canvas, self)
        try:
            figure.canvas.draw()
        except RecursionError:
            print('Recursion error')
            pass

        canvas_layout.addWidget(toolbar)
        canvas_layout.addWidget(canvas)
        self.layout_canvas.addLayout(canvas_layout)

        if self.plot_typ == 'image':
            axis.get_xaxis().set_visible(False)
            axis.get_yaxis().set_visible(False)
            self.img.append(None)

    @staticmethod
    def compute_corrupted_figure():
        """
        Compute the corrupted figure shown on startup.

        Arguments:
        None

        Return:
        None
        """
        coord_list = []
        coord_list.append([[0.5, 0, 0, 0.5], [1, 1, 0, 0]])
        coord_list.append([[1, 1.5, 1.5, 1, 1], [0, 0, 1, 1, 0]])
        coord_list.append([[2, 2, 2.5, 2.5, 2, 2.5], [0, 1, 1, 0.5, 0.5, 0]])
        coord_list.append([[3, 3, 3.5, 3.5, 3, 3.5], [0, 1, 1, 0.5, 0.5, 0]])
        coord_list.append([[4, 4, 4.5, 4.5], [1, 0, 0, 1]])
        coord_list.append([[5, 5, 5.5, 5.5, 5], [0, 1, 1, 0.5, 0.5]])
        coord_list.append([[6, 6.5, 6.25, 6.25], [1, 1, 1, 0]])
        return coord_list

    @staticmethod
    def compute_initial_figure():
        """
        Compute the initial figure shown on startup.

        Arguments:
        None

        Return:
        None
        """
        coord_list = []
        coord_list.append([[0, 0, 0, 0.5, 0.5, 0.5], [0, 1, 0.5, 0.5, 0, 1]])
        coord_list.append([[1.5, 1, 1, 1.5, 1, 1, 1.5], [0, 0, 0.5, 0.5, 0.5, 1, 1]])
        coord_list.append([[2, 2, 2.5], [1, 0, 0]])
        coord_list.append([[3, 3, 3.5], [1, 0, 0]])
        coord_list.append([[4, 4.15, 4.35, 4.5, 4.5, 4.35, 4.15, 4, 4], [0.3, 0, 0, 0.3, 0.6, 1, 1, 0.6, 0.3]])
        return coord_list

    def prepare_axis(
            self,
            new_x_min,
            new_x_max,
            new_y_min,
            new_y_max,
            new_label,
            new_title,
            x_values,
            y_values,
            change,
        ):
        axis = self.axis[0]

        if self.x_min is None and self.x_max is None:
            self.x_min = new_x_min - 0.5
            self.x_max = new_x_max + 0.5
            change = True

        if self.y_min is None and self.y_max is None:
            self.y_min = new_y_min - 0.5
            self.y_max = new_y_max + 0.5
            change = True

        if self.plot_typ == 'values':
            if self.line is None or change:
                # dummy plot to get the line
                try:
                    axis.clear()
                except RecursionError:
                    pass
                self.line, = axis.plot([0], [1], '.', color=self.color)
                axis.grid()
                axis.set_xlabel('Micrograph ID')
                x_step = (np.max(x_values) - np.min(x_values)) * 0.1
                axis.set_xlim([np.min(x_values)-x_step, np.max(x_values)+x_step])

                y_step = (np.max(y_values) - np.min(y_values)) * 0.05
                axis.set_ylim([np.min(y_values)-y_step, np.max(y_values)+y_step])
                change = True
            if self.label is None:
                self.label = new_label
                axis.set_ylabel(self.label)
                change = True
            if self.title is None:
                axis.set_title(new_title)
                change = True

        elif self.plot_typ == 'histogram':
            if self.x_min > new_x_min or self.x_max < new_x_max or self.line is None or change:
                try:
                    axis.clear()
                except RecursionError:
                    pass
                self.rects = axis.bar(
                        x_values[:-1],
                        y_values,
                        x_values[1] - x_values[0],
                        facecolor=self.color,
                        edgecolor='k'
                        )
                axis.grid()
                axis.set_ylabel('Nr. of micrographs')
                x_step = (np.max(x_values) - np.min(x_values)) * 0.1
                axis.set_xlim([np.min(x_values)-x_step, np.max(x_values)+x_step])

                y_step = (np.max(y_values) - np.min(y_values)) * 0.05
                axis.set_ylim([np.min(y_values), np.max(y_values)+y_step])
                change = True
            if self.label is None:
                self.label = new_label
                axis.set_xlabel(self.label)
                change = True
            if self.title is None:
                axis.set_title(new_title)
                change = True

        if new_x_max - new_x_min < 0.001:
            self.x_min = new_x_min - 0.5
            self.x_max = new_x_max + 0.5
            axis.set_xlim([self.x_min, self.x_max])
            change = True

        elif self.x_min > new_x_min or self.x_max < new_x_max:
            if self.x_min > new_x_min:
                self.x_min = new_x_min - abs(new_x_min*0.1)
            elif abs(self.x_min) < 0.001 and self.plot_typ == 'values':
                self.x_min = -0.5

            if self.x_max < new_x_max:
                self.x_max = new_x_max + abs(new_x_max*0.1)
            elif abs(self.x_max) < 0.001 and self.plot_typ == 'values':
                self.x_max = 0.5
            axis.set_xlim([self.x_min, self.x_max])
            change = True


        if new_y_max - new_y_min < 0.001:
            self.y_min = new_y_min - 0.5
            self.y_max = new_y_max + 0.5
            axis.set_ylim([self.y_min, self.y_max])
            change = True

        elif self.y_min > new_y_min or self.y_max < new_y_max:
            if self.y_min > new_y_min:
                self.y_min = new_y_min - abs(new_y_min*0.1)
            elif abs(self.y_min) < 0.001 and self.plot_typ == 'values':
                self.y_min = -0.5

            if self.y_max < new_y_max:
                self.y_max = new_y_max + abs(new_y_max*0.1)
            elif abs(self.y_max) < 0.001 and self.plot_typ == 'values':
                self.y_max = 0.5
            axis.set_ylim([self.y_min, self.y_max])
            change = True

        return change

    def get_lower_higher_bin(self):
        try:
            lower_lim = float(self.lower_edit.text())
        except ValueError:
            print('Lower limit value: {0} - Not a valid float! Falling back to -infinity.'.format(self.lower_edit.text()))
            lower_lim = -np.nan_to_num(np.inf)

        try:
            upper_lim = float(self.upper_edit.text())
        except ValueError:
            print('Upper limit value: {0} - Not a valid float! Falling back to infinity.'.format(self.upper_edit.text()))
            upper_lim = np.nan_to_num(np.inf)

        try:
            bins = int(self.bin_edit.text())
        except ValueError:
            print('Bin value: {0} - Not a valid integer! Using 50.'.format(self.bin_edit.text()))
            bins = 50
        return lower_lim, upper_lim, bins


    @pyqtSlot(str, object, str, object)
    def update_figure(self, name, data, directory_name, settings):
        """
        Update the figure with data plot.

        Arguments:
        name - Name of the plot type
        data - Data to plot
        directory_name - Name of the output directory
        settings - Settings provided by the user

        Return:
        None
        """
        if self.plot_typ == 'values' or self.plot_typ == 'histogram':
            x_values_raw, y_values_raw, label, title = tu.get_function_dict()[name]['plot'](
                data=data,
                settings=settings,
                label=self.plot_label,
                )
            change = False
            idx_nan = np.isnan(y_values_raw)
            x_values_raw = x_values_raw[~idx_nan]
            y_values_raw = y_values_raw[~idx_nan]
            lower_lim, upper_lim, bins = self.get_lower_higher_bin()
            mask = (lower_lim < y_values_raw) & (y_values_raw < upper_lim)
            title = '{0}: {1} out of range {2} to {3}'.format(title, y_values_raw[~mask].shape[0], lower_lim, upper_lim)
            if self.plot_typ == 'values':
                y_values = y_values_raw[mask]
                x_values = x_values_raw[mask]
            elif self.plot_typ == 'histogram':
                y_values, x_values = np.histogram(y_values_raw[mask], bins)

            if lower_lim != self.lower_lim:
                self.lower_lim = lower_lim
                change = True
            if upper_lim != self.upper_lim:
                self.upper_lim = upper_lim
                change = True
            change = self.prepare_axis(
                np.min(x_values),
                np.max(x_values),
                np.min(y_values),
                np.max(y_values),
                label,
                title,
                x_values,
                y_values,
                change,
                )

            if self.plot_typ == 'values':
                self.line.set_data(x_values, y_values)
                self.axis[0].draw_artist(self.axis[0].patch)
                self.axis[0].draw_artist(self.line)
            elif self.plot_typ == 'histogram':
                for idx, entry in enumerate(zip(self.rects, y_values)):
                    entry[0].set_height(entry[1])
                    entry[0].set_width(np.abs(x_values[idx]-x_values[idx+1]))

            try:
                if change:
                    self.figure[0].canvas.draw()
                self.figure[0].canvas.update()
                self.figure[0].canvas.flush_events()
            except RecursionError:
                print('Recursion error')
                pass

            output_name = os.path.join(
                directory_name,
                '{0}_{1}.png'.format(
                    self.plot_label,
                    self.plot_typ
                    )
                )
            try:
                self.figure[0].savefig(output_name.replace(' ', '_'))
            except RuntimeError:
                pass
            except FileNotFoundError:
                pass

        elif self.plot_typ == 'image':
            self.data = data[::-1]
            current_text = self.combo_box.currentText()

            self.combo_box.blockSignals(True)
            self.combo_box.clear()
            files = [self.default_value]
            files.extend([
                os.path.basename(os.path.splitext(entry)[0])
                for entry in self.data['file_name'].tolist()
                ])
            self.combo_box.addItems(files)

            self.idx = max(0, self.combo_box.findText(current_text))
            self.combo_box.setCurrentIndex(self.idx)
            self.combo_box.blockSignals(False)

            if self.idx <= 0 and self.idx >= self.data.shape[0]:
                self.prev_button.setEnabled(False)
                self.next_button.setEnabled(False)
            elif self.idx <= 0:
                self.next_button.setEnabled(False)
                self.prev_button.setEnabled(True)
            elif self.idx >= self.data.shape[0]:
                self.next_button.setEnabled(True)
                self.prev_button.setEnabled(False)
            else:
                self.next_button.setEnabled(True)
                self.prev_button.setEnabled(True)

            if str(current_text) == self.default_value:
                self.show_image()
            else:
                pass
        else:
            raise ValueError('PlotWidget - {0} not known!'.format(self.plot_typ))

    @pyqtSlot()
    def show_image(self):
        if self.data.shape[0] == 0:
            return None
        else:
            pass

        if str(self.combo_box.currentText()) == self.default_value:
            idx = 0
        else:
            idx = self.idx-1

        jpg_files = self.data['image'][idx].split(';;;')
        if len(jpg_files) != len(self.img):
            for _ in range(len(jpg_files) - len(self.img)):
                self.add_canvas()

        for idx, jpg_name in enumerate(jpg_files):
            title = os.path.basename(os.path.splitext(jpg_name)[0])
            try:
                jpg_data = imageio.imread(jpg_name)
            except Exception as e:
                print('Error loading image: {0} -- Message: {1}'.format(jpg_name, str(e)))
                try:
                    self.axis[idx].clear()
                except RecursionError:
                    pass
                for entry in self.compute_corrupted_figure():
                    x = entry[0]
                    y = entry[1]
                    self.axis[idx].plot(x, y, color=self.color)
                self.img[idx] = None
            else:
                if self.img[idx] is None:
                    self.img[idx] = self.axis[idx].imshow(jpg_data)
                else:
                    self.img[idx].set_data(jpg_data)
            self.axis[idx].set_title(title)
            try:
                self.figure[idx].canvas.draw()
                self.figure[idx].canvas.update()
                self.figure[idx].canvas.flush_events()
            except RecursionError:
                print('Recursion error')
                pass
            except ValueError:
                print('Value error: Please contact the TranSPHIRE authors')
                pass

    def check_enabled(self, typ, change=True):
        if typ == 'next':
            if self.idx <= 0 and self.idx >= self.data.shape[0]:
                self.prev_button.setEnabled(False)
                self.next_button.setEnabled(False)
            elif self.idx <= 0:
                self.next_button.setEnabled(False)
            else:
                self.prev_button.setEnabled(True)
                if change:
                    self.idx -= 1

        elif typ == 'prev':
            if self.idx <= 0 and self.idx >= self.data.shape[0]:
                self.prev_button.setEnabled(False)
                self.next_button.setEnabled(False)
            elif self.idx >= self.data.shape[0]:
                self.prev_button.setEnabled(False)
            else:
                self.next_button.setEnabled(True)
                if change:
                    self.idx += 1

        elif typ == 'combo':
            self.idx = self.combo_box.currentIndex()
            if self.idx <= 0 and self.idx >= self.data.shape[0]:
                self.idx = 0
                self.prev_button.setEnabled(False)
                self.next_button.setEnabled(False)
            elif self.idx <= 0:
                self.idx = 0
                self.next_button.setEnabled(False)
                self.prev_button.setEnabled(True)
            elif self.idx >= self.data.shape[0]:
                self.next_button.setEnabled(True)
                self.prev_button.setEnabled(False)
            else:
                self.next_button.setEnabled(True)
                self.next_button.setEnabled(True)

        elif typ == 'reset':
            self.idx = 0
            if self.idx <= 0 and self.idx >= self.data.shape[0]:
                self.prev_button.setEnabled(False)
                self.next_button.setEnabled(False)
            elif self.idx <= 0:
                self.next_button.setEnabled(False)
                self.prev_button.setEnabled(True)
            elif self.idx >= self.data.shape[0]:
                self.next_button.setEnabled(True)
                self.prev_button.setEnabled(False)
            else:
                self.next_button.setEnabled(True)
                self.next_button.setEnabled(True)
        else:
            pass

    def change_idx(self, typ):
        self.check_enabled(typ=typ)
        self.combo_box.blockSignals(True)
        self.combo_box.setCurrentIndex(self.idx)
        self.combo_box.blockSignals(False)
        self.check_enabled(typ=typ, change=False)
        self.show_image()
