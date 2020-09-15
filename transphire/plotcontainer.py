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
from PyQt5.QtCore import pyqtSlot, Qt, QEvent
from PyQt5.QtWidgets import QMainWindow, QDockWidget, QTabWidget, QWidget, QHBoxLayout, QVBoxLayout, QLabel, QStyle, QPushButton


class TwinContainer(QWidget):

    def __init__(self, dock_widget, *args, parent=None, **kwargs):
        super(TwinContainer, self).__init__(parent)
        self.parent = parent
        self.layout = QVBoxLayout(self)
        self.layouts = {}
        self.dock_widget = dock_widget

    def add_to_layout(self, name, widget):
        if name not in self.layouts:
            keys = sorted(list(self.layouts) + [name])
            idx = keys.index(name)
            self.layouts[name] = QHBoxLayout()
            self.layout.insertLayout(idx, self.layouts[name])
        self.layouts[name].addWidget(widget)
        widget.mpl_canvas.sig_twin.connect(self.mouse_twin_event)

    @pyqtSlot(object)
    def mouse_twin_event(self, event):
        if event.button == 1:
            self.parent.select_tab(self.sender())
        elif event.button == 3:
            plot_widget = self.sender().my_parent
            plot_widget.trim_widget.sig_set_state.emit(True)

    def handle_show(self, name, widget, state):
        widget.setVisible(state)
        if state:
            self.layouts[name].addWidget(widget)
        else:
            self.layouts[name].removeWidget(widget)


class PlotContainer(QMainWindow):
    """
    Qwidget in combination with a FigureCanvas.

    Inherits:
    QMainWindow
    """

    def __init__(self, name, content, plot_labels, plot_name, plot_worker, plot_type, layout, *args, parent=None, **kwargs):
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

        self.worker = plot_worker

        self.content = []
        self.dock_widgets = []
        if self.name == 'Overview':
            plot_labels = [[content]]

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

            dock_widget = QDockWidget(label, self)

            custom_title = QWidget(dock_widget)
            layout_custom_title = QHBoxLayout(custom_title)
            layout_custom_title.setContentsMargins(0, 0, 0, 0)
            layout_custom_title.addWidget(QLabel('{} - {}'.format(self.plot_name, label), dock_widget))

            layout_custom_title.addStretch(1)

            button = QPushButton(dock_widget)
            button.my_docker = dock_widget
            button.setStyleSheet('color: rgba(0, 0, 0 ,0); background-color: rgba(0, 0, 0, 0)')
            icon = dock_widget.style().standardIcon(QStyle.SP_TitleBarNormalButton)
            button.setIcon(icon)
            button.clicked.connect(self.set_floating)
            layout_custom_title.addWidget(button)

            dock_widget.setTitleBarWidget(custom_title)

            if label == 'overview':
                widget = TwinContainer(dock_widget=dock_widget, parent=self)
            else:
                if label == 'image':
                    twin_container = None
                else:
                    twin_container = self.parent.content[layout].widget(0).content[0]
                widget = PlotWidget(label=label, plot_typ=content, dock_widget=dock_widget, twin_container=twin_container, parent=self)

            self.content.append(widget)
            dock_widget.setWidget(widget)
            dock_widget.installEventFilter(self)
            dock_widget.setFeatures(QDockWidget.DockWidgetFloatable | QDockWidget.DockWidgetMovable)
            self.dock_widgets.append(dock_widget)
            self.addDockWidget(Qt.BottomDockWidgetArea, dock_widget, Qt.Horizontal)

        for idx in range(1, len(self.dock_widgets)):
            self.tabifyDockWidget(self.dock_widgets[0], self.dock_widgets[idx])
        self.tabifiedDockWidgetActivated.connect(self.synchronize_tabs)
        self.parent.content[self.parent_layout].enable_tab(False)
        self._is_visible = False

    @pyqtSlot()
    def reset_plot(self):
        for entry in self.content:
            entry.do_data_reset()

    @pyqtSlot()
    def set_floating(self):
        self.sender().my_docker.setFloating(not self.sender().my_docker.isFloating())

    @pyqtSlot(str, str, object, str, object)
    def update_figure(self, name, name_no_feedback, data, directory_name, settings):
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
                entry.set_settings(
                    name=name,
                    name_no_feedback=name_no_feedback,
                    data=data,
                    directory_name=directory_name,
                    settings=settings
                    )

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
            if self._is_visible != visible:
                self.parent.content[self.parent_layout].enable_tab(visible)
                if visible:
                    for widget in self.content:
                        widget.show()
                        widget.start_plotting()
                self._is_visible = visible

    @pyqtSlot(object)
    def select_tab(self, widget):
        aim_docker = self.parent.content[self.parent_layout]
        cur_docker = aim_docker
        for _ in range(3):
            tmp_docker = self.parent.content[cur_docker.layout]
            tmp_docker.setCurrentWidget(cur_docker)
            cur_docker = tmp_docker

        docker_to_activate = None
        for idx in range(aim_docker.count()):
            aim_container = aim_docker.widget(idx)
            for entry in aim_container.dock_widgets:
                if entry.widget() == widget.my_parent:
                    docker_to_activate = entry
                    break
            else:
                continue
            break
        assert docker_to_activate is not None, (entry, widget, widget.my_parent)
        self.synchronize_tabs(docker_to_activate)
        aim_docker.setCurrentIndex(idx)

    @pyqtSlot(QDockWidget)
    def synchronize_tabs(self, widget):
        compare_name = widget.windowTitle()
        aim_docker = self.parent.content[self.parent_layout]
        aim_indices = []
        for idx in range(aim_docker.count()):
            tab_text = aim_docker.tabText(idx)
            if self.name == 'Overview':
                if tab_text == 'Plot histogram':
                    aim_indices.append(idx)
                    continue
                elif tab_text == 'Plot per micrograph':
                    aim_indices.append(idx)
                    continue
            elif self.name == 'Plot per micrograph':
                if tab_text == 'Plot histogram':
                    aim_indices.append(idx)
                    break
            elif self.name == 'Plot histogram':
                if tab_text == 'Plot per micrograph':
                    aim_indices.append(idx)
                    break
            else:
                pass

        assert aim_indices is not None
        for aim_idx in aim_indices:
            aim_container = aim_docker.widget(aim_idx)
            aim_container.activate_tab(compare_name)

from .plotwidget import PlotWidget
