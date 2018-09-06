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
import matplotlib.pyplot as plt
from matplotlib.backends.backend_qt4agg import (
    FigureCanvasQTAgg as FigureCanvas,
    NavigationToolbar2QT as NavigationToolbar
    )
try:
    from PyQt4.QtGui import QWidget, QVBoxLayout, QHBoxLayout, QComboBox, QPushButton
    from PyQt4.QtCore import pyqtSlot
except ImportError:
    from PyQt5.QtWidgets import QWidget, QVBoxLayout, QHBoxLayout, QComboBox, QPushButton
    from PyQt5.QtCore import pyqtSlot
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

        # Variables
        self.label = label
        self.plot_typ = plot_typ

        # Initialise figure
        self.figure = plt.figure()
        self.ax1 = self.figure.add_subplot(111)
        self.compute_initial_figure()

        # Create canvas for the figure
        self.canvas = FigureCanvas(self.figure)
        self.canvas.setParent(self)
        self.toolbar = NavigationToolbar(self.canvas, self)
        self.canvas.draw_idle()

        layout_v = QVBoxLayout(self)
        # Add for image plot typ
        if self.plot_typ == 'image' and self.label == 'image':
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
        layout_v.addWidget(self.toolbar)
        layout_v.addWidget(self.canvas)


    def compute_corrupted_figure(self, title):
        """
        Compute the corrupted figure shown on startup.

        Arguments:
        None

        Return:
        None
        """
        self.ax1.clear()
        self.ax1.plot([0.5, 0, 0, 0.5], [1, 1, 0, 0], '#68a3c3')
        self.ax1.plot([1, 1.5, 1.5, 1, 1], [0, 0, 1, 1, 0], '#68a3c3')
        self.ax1.plot([2, 2, 2.5, 2.5, 2, 2.5], [0, 1, 1, 0.5, 0.5, 0], '#68a3c3')
        self.ax1.plot([3, 3, 3.5, 3.5, 3, 3.5], [0, 1, 1, 0.5, 0.5, 0], '#68a3c3')
        self.ax1.plot([4, 4, 4.5, 4.5], [1, 0, 0, 1], '#68a3c3')
        self.ax1.plot([5, 5, 5.5, 5.5, 5], [0, 1, 1, 0.5, 0.5], '#68a3c3')
        self.ax1.plot([6, 6.5, 6.25, 6.25], [1, 1, 1, 0], '#68a3c3')
        self.ax1.set_title(title)


    def compute_initial_figure(self):
        """
        Compute the initial figure shown on startup.

        Arguments:
        None

        Return:
        None
        """
        self.ax1.clear()
        self.ax1.plot([0, 0, 0, 0.5, 0.5, 0.5], [0, 1, 0.5, 0.5, 0, 1], '#68a3c3')
        self.ax1.plot([1.5, 1, 1, 1.5, 1, 1, 1.5], [0, 0, 0.5, 0.5, 0.5, 1, 1], '#68a3c3')
        self.ax1.plot([2, 2, 2.5], [1, 0, 0], '#68a3c3')
        self.ax1.plot([3, 3, 3.5], [1, 0, 0], '#68a3c3')
        self.ax1.plot([4, 4.15, 4.35, 4.5, 4.5, 4.35, 4.15, 4, 4], [0.3, 0, 0, 0.3, 0.6, 1, 1, 0.6, 0.3], '#68a3c3')


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
        if name == 'False':
            return None
        elif name == 'Later':
            return None
        elif self.plot_typ == 'values' or self.plot_typ == 'histogram':
            x_values, y_values, label, title = tu.get_function_dict()[name]['plot'](
                data=data,
                settings=settings,
                label=self.label,
                )
            idx_nan = np.isnan(y_values)
            x_values = x_values[~idx_nan]
            y_values = y_values[~idx_nan]

            color = '#68a3c3'

            self.ax1.clear()
            title_list = [title]
            if idx_nan.any():
                title_list.append(
                    '{0} entries not valid due to NAN'.format(idx_nan.sum())
                    )

            if self.plot_typ == 'values':
                x_label = 'Micrograph ID'
                y_label = label
                self.ax1.plot(x_values, y_values, '.', color=color)
            elif self.plot_typ == 'histogram':
                x_label = label
                y_label = 'Nr. of micrographs'
                if np.max(y_values) - np.min(y_values) < 0.001:
                    self.ax1.hist(y_values, 1)
                    self.ax1.set_xlim([np.max(y_values)-1, np.min(y_values)+1])
                elif title == 'Resolution limit':
                    if np.max(y_values) > 20:
                        self.ax1.hist(y_values[y_values <= 20], 100, color=color)
                        title_list.append('{0} micrographs out of range (0,20)'.format(
                            y_values[y_values > 20].shape[0]
                            ))
                    else:
                        self.ax1.hist(y_values, 100, color=color)
                else:
                    self.ax1.hist(y_values, 100, color=color)
            else:
                print('Plotwidget - ', self.plot_typ, ' is not known!!!')
                return None

            self.ax1.grid()
            self.ax1.set_title('\n'.join(title_list))
            self.ax1.set_xlabel(x_label)
            self.ax1.set_ylabel(y_label)
            try:
                self.canvas.draw_idle()
            except RecursionError:
                import sys
                print('sys.getrecursionlimit()')
                print(sys.getrecursionlimit())
                print('self.plot_typ')
                print(self.plot_typ)
                print('label')
                print(label)
                print('x_label')
                print(x_label)
                print('y_label')
                print(y_label)
                print('directory_name')
                print(directory_name)
                print('title')
                print(title)
                print('x_values')
                print(x_values)
                print('len x_values')
                print(len(x_values))
                print('y_values')
                print(y_values)
                print('len y_values')
                print(len(y_values))
                print('COULD NOT DRAW!!!')
                print('Please contact the TranSHPIRE authors!!!')
                print('Restarting TranSPHIRE will fix this issue.')
                return None

            output_name = os.path.join(
                directory_name,
                '{0}_{1}.png'.format(
                    self.label,
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
            print('Plotwidget - ', self.plot_typ, ' is not known!!!')
            return None

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

        self.ax1.clear()
        if self.data['object'][idx] is None:
            try:
                jpg_data = imageio.imread(self.data['image'][idx])
            except Exception as e:
                print('Error loading image: {0} -- Message: {1}'.format(self.data['image'][idx], str(e)))
                self.compute_corrupted_figure(title=self.data['file_name'][idx])
            else:
                self.ax1.imshow(jpg_data)
        else:
                self.ax1.imshow(self.data['object'][idx])
        self.ax1.get_xaxis().set_visible(False)
        self.ax1.get_yaxis().set_visible(False)
        self.ax1.set_title(self.data['file_name'][idx])
        self.canvas.draw_idle()

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
        self.combo_box.setCurrentIndex(self.idx)
        self.show_image()
