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
try:
    from PyQt4.QtCore import pyqtSlot, Qt, QEvent
    from PyQt4.QtGui import QMainWindow, QDockWidget, QTabWidget
except ImportError:
    from PyQt5.QtCore import pyqtSlot, Qt, QEvent
    from PyQt5.QtWidgets import QMainWindow, QDockWidget, QTabWidget
from transphire.plotwidget import PlotWidget


class PlotContainer(QMainWindow):
    """
    Qwidget in combination with a FigureCanvas.

    Inherits:
    QMainWindow
    """

    def __init__(self, content, plot_labels, plot_name, *args, parent=None, **kwargs):
        """
        Initialisation of the PlotContainer widget.

        content - Content for the plotcontainer
        plot_lables - Labels of the plot widget
        plot_name - Name of the associated software
        parent - Parent widget (default None)

        Returns:
        None
        """
        super(PlotContainer, self).__init__(parent)
        self.setCentralWidget(None)
        self.setTabPosition(Qt.TopDockWidgetArea, QTabWidget.North)
        self.plot_name = plot_name

        self.content = []
        dock_widgets = []
        for label in plot_labels:
            label = label[0]
            if label == 'mic_number':
                continue
            elif label == 'file_name':
                continue
            else:
                pass

            widget = PlotWidget(label=label, plot_typ=content, parent=self)
            self.content.append(widget)

            dock_widget = QDockWidget(label, self)
            dock_widget.setWidget(widget)
            dock_widget.installEventFilter(self)
            dock_widget.setFeatures(QDockWidget.DockWidgetFloatable | QDockWidget.DockWidgetMovable)
            dock_widgets.append(dock_widget)
            self.addDockWidget(Qt.TopDockWidgetArea, dock_widget, Qt.Horizontal)

        for idx in range(1, len(dock_widgets)):
            self.tabifyDockWidget(dock_widgets[0], dock_widgets[idx])

    @pyqtSlot(str, object, str, object)
    def update_figure(self, name, data, directory_name, settings):
        """
        Update the figure in the canvas

        name - Name of the program that called this function.
        data - Data to plot.
        directory_name - Directory to save plots to.
        settings - TranSPHIRE settings

        Returns:
        None
        """
        if self.plot_name == name:
            for entry in self.content:
                entry.update_figure(
                    name=name,
                    data=data,
                    directory_name=directory_name,
                    settings=settings
                    )
        else:
            pass

    def eventFilter(self, source, event):
        """
        Override the QMainWindow eventFilter function.

        source - Source that led to the event trigger
        event - Emitted event

        Returns:
        True, if it has been a close event -> Redock widget
        Event, if it is another event
        """
        if event.type() == QEvent.Close and isinstance(source, QDockWidget):
            event.ignore()
            source.setFloating(False)
            return True
        else:
            return super(PlotContainer, self).eventFilter(source, event)

    def enable(self, var, use_all):
        """
        Enable or disable the widgets.

        var - It True, enable widgets, else disable
        use_all - If True, enable/disable all widgets, else only a subset

        Returns:
        None
        """
        for entry in self.content:
            if use_all:
                entry.setEnabled(var)
            else:
                pass
