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
    from PyQt4.QtGui import QWidget, QVBoxLayout, QHBoxLayout, QComboBox, QPushButton
    from PyQt4.QtCore import pyqtSlot
    from matplotlib.backends.backend_qt4agg import (
        FigureCanvasQTAgg as FigureCanvas,
        NavigationToolbar2QT as NavigationToolbar
        )
except ImportError:
    from PyQt5.QtWidgets import QWidget, QVBoxLayout, QHBoxLayout, QComboBox, QPushButton
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
        self.img = None
        self.figure, self.axis = plt.subplots()
        for entry in self.compute_initial_figure():
            x = entry[0]
            y = entry[1]
            self.axis.plot(x, y, color=self.color)

        canvas = FigureCanvas(self.figure)
        canvas.setParent(self)
        toolbar = NavigationToolbar(canvas, self)
        self.figure.canvas.draw()

        if plot_typ == 'image':
            self.axis.get_xaxis().set_visible(False)
            self.axis.get_yaxis().set_visible(False)

        layout_v = QVBoxLayout(self)
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

        # Fill layout
        layout_v.addWidget(toolbar)
        layout_v.addWidget(canvas)

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
            y_values
        ):
        change = False

        if self.x_min is None and self.x_max is None:
            self.x_min = new_x_min - 0.5
            self.x_max = new_x_max + 0.5
            change = True

        if self.y_min is None and self.y_max is None:
            self.y_min = new_y_min - 0.5
            self.y_max = new_y_max + 0.5
            change = True

        if self.plot_typ == 'values':
            if self.line is None:
                # dummy plot to get the line
                self.axis.clear()
                self.line, = self.axis.plot([0], [1], '.', color=self.color)
                self.axis.grid()
                self.axis.set_xlabel('Micrograph ID')
                self.axis.set_xlim([self.x_min, self.x_max])
                self.axis.set_ylim([self.y_min, self.y_max])
                change = True
            if self.label is None:
                self.label = new_label
                self.axis.set_ylabel(self.label)
                change = True
            if self.title is None:
                self.axis.set_title(new_title)
                change = True

        elif self.plot_typ == 'histogram':
            if self.x_min > new_x_min or self.x_max < new_x_max or self.line is None:
                self.axis.clear()
                self.rects = self.axis.bar(
                        x_values[:-1],
                        y_values,
                        facecolor=self.color,
                        edgecolor='k'
                        )
                self.axis.grid()
                self.axis.set_ylabel('Nr. of micrographs')
                self.axis.set_xlim([self.x_min, self.x_max])
                self.axis.set_ylim([self.y_min, self.y_max])
                change = True
            if self.label is None:
                self.label = new_label
                self.axis.set_xlabel(self.label)
                change = True
            if self.title is None:
                self.axis.set_title(new_title)
                change = True

        if new_x_max - new_x_min < 0.001:
            self.x_min = new_x_min - 0.5
            self.x_max = new_x_max + 0.5
            self.axis.set_xlim([self.x_min, self.x_max])
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
            self.axis.set_xlim([self.x_min, self.x_max])
            change = True


        if new_y_max - new_y_min < 0.001:
            self.y_min = new_y_min - 0.5
            self.y_max = new_y_max + 0.5
            self.axis.set_ylim([self.y_min, self.y_max])
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
            self.axis.set_ylim([self.y_min, self.y_max])
            change = True

        return change

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
            x_values, y_values, label, title = tu.get_function_dict()[name]['plot'](
                data=data,
                settings=settings,
                label=self.plot_label,
                )
            idx_nan = np.isnan(y_values)
            x_values_raw = x_values[~idx_nan]
            y_values_raw = y_values[~idx_nan]
            if self.plot_typ == 'values':
                y_values = y_values_raw
                x_values = x_values_raw
            elif self.plot_typ == 'histogram':
                y_values, x_values = np.histogram(y_values_raw)
            change = self.prepare_axis(
                np.min(x_values),
                np.max(x_values),
                np.min(y_values),
                np.max(y_values),
                label,
                title,
                x_values,
                y_values
                )

            if self.plot_typ == 'values':
                self.line.set_data(x_values, y_values)
                self.axis.draw_artist(self.axis.patch)
                self.axis.draw_artist(self.line)
            elif self.plot_typ == 'histogram':
                [rect.set_height(y1) for rect, y1 in zip(self.rects, y_values)]

            #if change:
            #    self.figure.canvas.draw()
            #self.figure.canvas.update()
            self.figure.canvas.flush_events()

            output_name = os.path.join(
                directory_name,
                '{0}_{1}.png'.format(
                    self.plot_label,
                    self.plot_typ
                    )
                )
            try:
                self.figure.savefig(output_name.replace(' ', '_'))
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
            files.extend(self.data['file_name'].tolist())
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

        title = self.data['file_name'][idx]
        jpg_data = self.data['object'][idx]
        if self.data['object'][idx] is None:
            try:
                jpg_data = imageio.imread(self.data['image'][idx])
            except Exception as e:
                print('Error loading image: {0} -- Message: {1}'.format(self.data['image'][idx], str(e)))
                self.axis.clear()
                for entry in self.compute_corrupted_figure():
                    x = entry[0]
                    y = entry[1]
                    self.axis.plot(x, y, color=self.color)
                self.img = None
            else:
                if self.img is None:
                    self.img = self.axis.imshow(jpg_data)
                else:
                    self.img.set_data(jpg_data)
        else:
            if self.img is None:
                self.img = self.axis.imshow(jpg_data)
            else:
                self.img.set_data(jpg_data)
        self.axis.set_title(title)
        #self.figure.canvas.draw()
        #self.figure.canvas.update()
        self.figure.canvas.flush_events()

    def change_idx(self, typ):
        if typ == 'next':
            if self.idx <= 0 and self.idx >= self.data.shape[0]:
                self.prev_button.setEnabled(False)
                self.next_button.setEnabled(False)
            elif self.idx <= 0:
                self.next_button.setEnabled(False)
            else:
                self.prev_button.setEnabled(True)
                self.idx -= 1
        elif typ == 'prev':
            if self.idx <= 0 and self.idx >= self.data.shape[0]:
                self.prev_button.setEnabled(False)
                self.next_button.setEnabled(False)
            elif self.idx >= self.data.shape[0]:
                self.prev_button.setEnabled(False)
            else:
                self.next_button.setEnabled(True)
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
        self.combo_box.blockSignals(True)
        self.combo_box.setCurrentIndex(self.idx)
        self.combo_box.blockSignals(False)
        self.show_image()
