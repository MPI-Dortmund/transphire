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
    from PyQt4.QtCore import pyqtSlot, Qt, QEvent, pyqtSignal
    from PyQt4.QtGui import QMainWindow, QDockWidget, QTabWidget
except ImportError:
    from PyQt5.QtCore import pyqtSlot, Qt, QEvent, pyqtSignal
    from PyQt5.QtWidgets import QMainWindow, QDockWidget, QTabWidget
from transphire.plotwidget import PlotWidget


class PlotContainer(QMainWindow):
    """
    Qwidget in combination with a FigureCanvas.

    Inherits:
    QMainWindow
    """
    sig_update_done = pyqtSignal()

    def __init__(self, name, content, plot_labels, plot_name, plot_worker_ctf, plot_worker_motion, plot_worker_picking, plot_type, layout, *args, parent=None, **kwargs):
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
        self.parent_layout = layout
        self.parent = parent
        self.setCentralWidget(None)
        self.setTabPosition(Qt.TopDockWidgetArea, QTabWidget.North)
        self.plot_name = plot_name
        self.name = name

        if plot_type == 'ctf':
            self.worker = plot_worker_ctf
        elif plot_type == 'motion':
            self.worker = plot_worker_motion
        elif plot_type == 'picking':
            self.worker = plot_worker_picking
        else:
            raise Exception('PlotContainer - {0} not known!'.format(plot_type))

        self.content = []
        self.dock_widgets = []
        for label in plot_labels:
            label = label[0]
            if label == 'mic_number':
                continue
            elif label == 'file_name':
                continue
            elif label == 'image' and content != 'image':
                continue
            elif label != 'image' and content == 'image':
                continue
            elif label == 'object':
                continue
            else:
                pass

            widget = PlotWidget(label=label, plot_typ=content, parent=self)
            self.content.append(widget)

            dock_widget = QDockWidget(label, self)
            dock_widget.setWidget(widget)
            dock_widget.installEventFilter(self)
            dock_widget.setFeatures(QDockWidget.DockWidgetFloatable | QDockWidget.DockWidgetMovable)
            self.dock_widgets.append(dock_widget)
            self.addDockWidget(Qt.BottomDockWidgetArea, dock_widget, Qt.Horizontal)

        for idx in range(1, len(self.dock_widgets)):
            self.tabifyDockWidget(self.dock_widgets[0], self.dock_widgets[idx])
        self.tabifiedDockWidgetActivated.connect(self.synchronize_tabs)

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
            self.sig_update_done.emit()
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

    def activate_tab(self, name):
        """
        Activate the tab with the name: name.

        Arguments:
        name - Name of the activation

        Returns:
        None
        """
        for widget in self.dock_widgets:
            if widget.windowTitle() == name:
                widget.show()
                widget.raise_()
                break

    @pyqtSlot(bool, str)
    def set_visibility(self, visible, name):
        if name == self.plot_name:
            self.parent.content[self.parent_layout].enable_tab(visible)

    def synchronize_tabs(self, widget):
        compare_name = widget.windowTitle()
        aim_docker = self.parent.content[self.parent_layout]
        aim_index = None

        for idx in range(aim_docker.count()):
            tab_text = aim_docker.tabText(idx)
            if self.name == 'Plot per micrograph':
                if tab_text == 'Plot histogram':
                    aim_index = idx
                    break
            elif self.name == 'Plot histogram':
                if tab_text == 'Plot per micrograph':
                    aim_index = idx
                    break
            else:
                pass

        assert aim_index is not None
        aim_container = aim_docker.widget(aim_index)
        aim_container.activate_tab(compare_name)
