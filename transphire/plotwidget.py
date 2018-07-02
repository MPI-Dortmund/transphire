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
import warnings
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
        self.compute_initial_figure()

        # Create canvas for the figure
        self.canvas = FigureCanvas(self.figure)
        self.canvas.setParent(self)
        self.toolbar = NavigationToolbar(self.canvas, self)
        self.canvas.draw()

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
            self.prev_button.clicked.connect(lambda: self.change_idx('prev'))
            layout_h.addWidget(self.prev_button)
            self.next_button = QPushButton('Next', self)
            self.next_button.clicked.connect(lambda: self.change_idx('next'))
            layout_h.addWidget(self.next_button)
            self.reset_button = QPushButton('Reset', self)
            self.reset_button.clicked.connect(lambda: self.change_idx('reset'))
            layout_h.addWidget(self.reset_button)
            layout_h.addStretch(1)
            layout_v.addLayout(layout_h)

        # Fill layout
        layout_v.addWidget(self.toolbar)
        layout_v.addWidget(self.canvas)


    def compute_initial_figure(self):
        """
        Compute the initial figure shown on startup.

        Arguments:
        None

        Return:
        None
        """
        self.figure.clear()
        ax1 = self.figure.add_subplot(111)
        ax1.plot([0, 0, 0, 0.5, 0.5, 0.5], [0, 1, 0.5, 0.5, 0, 1], 'b')
        ax1.plot([1.5, 1, 1, 1.5, 1, 1, 1.5], [0, 0, 0.5, 0.5, 0.5, 1, 1], 'b')
        ax1.plot([2, 2, 2.5], [1, 0, 0], 'b')
        ax1.plot([3, 3, 3.5], [1, 0, 0], 'b')
        ax1.plot([4, 4.15, 4.35, 4.5, 4.5, 4.35, 4.15, 4, 4], [0.3, 0, 0, 0.3, 0.6, 1, 1, 0.6, 0.3], 'b')

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
                label=self.label
                )

            self.figure.clear()
            ax1 = self.figure.add_subplot(111)

            if self.plot_typ == 'values':
                x_label = 'Micrograph ID'
                y_label = label
                ax1.plot(x_values, y_values, '.')
            elif self.plot_typ == 'histogram':
                x_label = label
                y_label = 'Nr. of micrographs'
                if np.max(y_values) - np.min(y_values) < 0.001:
                    ax1.hist(y_values, 1)
                    ax1.set_xlim([np.max(y_values)-1, np.min(y_values)+1])
                else:
                    ax1.hist(y_values, 100)
            else:
                print('Plotwidget - ', self.plot_typ, ' is not known!!!')
                return None

            ax1.grid()
            ax1.set_title(title)
            ax1.set_xlabel(x_label)
            ax1.set_ylabel(y_label)
            self.canvas.draw()

            output_name = '{0}/{1}_{2}.png'.format(
                directory_name,
                self.label,
                self.plot_typ
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

            self.combo_box.clear()
            files = [self.default_value]
            files.extend(self.data['file_name'].tolist())
            self.combo_box.addItems(files)

            self.idx = self.combo_box.findText(current_text)
            self.combo_box.setCurrentIndex(self.idx)

            self.show_image()

        else:
            print('Plotwidget - ', self.plot_typ, ' is not known!!!')
            return None

    @pyqtSlot()
    def show_image(self):
        if self.data.shape[0] == 0:
            return None
        else:
            pass
        self.figure.clear()
        ax1 = self.figure.add_subplot(111)

        if str(self.combo_box.currentText()) == self.default_value:
            idx = 0
        else:
            idx = self.idx-1
        ax1.imshow(self.data['image'][idx])

        ax1.get_xaxis().set_visible(False)
        ax1.get_yaxis().set_visible(False)
        ax1.set_title(self.data['file_name'][idx])
        self.canvas.draw()

    def change_idx(self, typ):
        if typ == 'next':
            if self.idx <= 0:
                pass
            else:
                self.idx -= 1
        elif typ == 'prev':
            if self.idx >= self.data.shape[0]:
                pass
            else:
                self.idx += 1
        elif typ == 'combo':
            self.idx = self.combo_box.currentIndex()
            if self.idx < 0:
                self.idx = 0
        elif typ == 'reset':
            self.idx = 0
        else:
            pass
        self.combo_box.setCurrentIndex(self.idx)
        self.show_image()
