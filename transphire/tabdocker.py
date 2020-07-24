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
from PyQt5.QtWidgets import QWidget, QVBoxLayout, QTabWidget, QTabBar, QStylePainter, QStyleOptionTab, QStyle
from PyQt5.QtCore import QPoint, QRect, pyqtSlot, pyqtSignal


class MyTabBar(QTabBar):

    def __init__(self, parent):
        super(MyTabBar, self).__init__(parent)

    def tabSizeHint(self, index):
        s = super(MyTabBar, self).tabSizeHint(index)
        s.transpose()
        return s

    def paintEvent(self, event):
        painter = QStylePainter(self)
        opt = QStyleOptionTab()

        for i in range(self.count()):
            self.initStyleOption(opt, i)
            painter.drawControl(QStyle.CE_TabBarTabShape, opt)
            painter.save()

            s = opt.rect.size()
            s.transpose()
            r = QRect(QPoint(), s)
            r.moveCenter(opt.rect.center())
            opt.rect = r

            c = self.tabRect(i).center()
            painter.translate(c)
            painter.rotate(90)
            painter.translate(-c)
            painter.drawControl(QStyle.CE_TabBarTabLabel, opt)
            painter.restore()

class TabDocker(QWidget):
    """
    Tab widget for the settingswidgets.

    Inherits:
    QWidget
    """
    sig_start_plot = pyqtSignal()
    latest_active = [None]

    def __init__(self, parent=None, **kwargs):
        """
        Initialise layout for TabDocker

        Arguments:
        parent - Parent widget (default None)

        Return:
        None
        """
        super(TabDocker, self).__init__(parent)
        self.parent = parent
        try:
            self.layout = kwargs['layout']
        except KeyError:
            self.layout = None
        try:
            self.name = kwargs['name']
        except KeyError:
            self.name = None
        self.widgets = []

        layout_tmp = QVBoxLayout(self)
        self.parent_widget = QWidget(self)
        layout_tmp.addWidget(self.parent_widget)
        layout_tmp.setContentsMargins(0, 0, 0, 0)

        layout = QVBoxLayout(self.parent_widget)
        layout.setContentsMargins(0, 0, 0, 0)
        self.tab_widget = QTabWidget(self)
        if self.layout in ('TAB1', 'Settings'):
            tab_bar = MyTabBar(self.tab_widget)
            tab_bar.setObjectName('vertical')
            self.tab_widget.setObjectName('vertical')
            self.tab_widget.setTabBar(tab_bar)
            self.tab_widget.setTabPosition(QTabWidget.West)
        layout.addWidget(self.tab_widget)

        self.tab_widget.currentChanged.connect(self.assign_latest)

    @pyqtSlot(int)
    def assign_latest(self, idx):
        current_name = self.tab_widget.tabText(idx)
        try:
            parent_content = self.parent.content[self.layout].name
        except AttributeError: # Exception for the Default settings dialog
            parent_content = False
        except TypeError: # Exception for the Default settings dialog
            parent_content = False
        except KeyError: # Exception for the main window dialog
            parent_content = False

        check_list = (parent_content, self.name, current_name)

        latest_active = self
        for list_idx, entry in enumerate(check_list):
            if entry == 'Visualisation':
                cur_tab_widget = self.tab_widget.widget(idx)
                try:
                    for i in range(list_idx):
                        idx = cur_tab_widget.currentIndex()
                        cur_tab_widget = cur_tab_widget.widget(idx)
                    latest_active = cur_tab_widget if cur_tab_widget is not None else self
                except:
                    latest_active = self
                break
        if self.latest_active[0] != latest_active:
            self.latest_active[0] = latest_active
            latest_active.sig_start_plot.emit()

    def setCurrentIndex(self, idx):
        """
        Set the current Index of the tab_widget.

        Arguments:
        idx - Index to set

        Returns: Current index of self.tab_widget
        """
        return self.tab_widget.setCurrentIndex(idx)

    def setCurrentWidget(self, widget):
        """
        Set the current widget of the tab_widget.

        Arguments:
        idx - Widget to set

        Returns: Current index of self.tab_widget
        """
        return self.tab_widget.setCurrentWidget(widget)

    def currentIndex(self):
        """
        Get the current Index of the tab_widget.

        Returns: Current index of self.tab_widget
        """
        return self.tab_widget.currentIndex()

    def add_tab(self, widget, name, add_widgets=True):
        """
        Add a new tab to the TabDocker

        Arguments:
        widget - Widget to add
        name - Name of the widget

        Return:
        None
        """
        if isinstance(widget, TabDocker):
            widget.parent_widget.setObjectName('tab')
        else:
            pass
        current_state = self.tab_widget.blockSignals(True)
        index = self.tab_widget.addTab(widget, name)
        if add_widgets:
            self.widgets.append(widget)
        self.tab_widget.blockSignals(current_state)
        self.tab_widget.setTabToolTip(index, name)

    def count(self):
        """
        Return the number of tabs.

        Arguments:
        None

        Returns:
        Number of tabs
        """
        return self.tab_widget.count()

    def widget(self, idx):
        """
        Return the widget that belongs to the idx of tabs.

        Arguments:
        idx - Tab index

        Returns:
        Widget
        """
        return self.tab_widget.widget(idx)

    def setMovable(self, status):
        """
        Set the movable status for the tab widgets

        Arguments:
        status - Boolean variable for the status

        Returns:
        None
        """
        return self.tab_widget.setMovable(status)

    def tabText(self, idx):
        """
        Return the text of the tab at idx

        Arguments:
        idx - Index of the tab

        Returns:
        Text of the tab at position isx
        """
        return self.tab_widget.tabText(idx)

    def setTabText(self, idx, text):
        """
        Set the text for the tab at idx

        Arguments:
        idx - Index of the tab
        text - Text of the tab

        Returns:
        None
        """
        return self.tab_widget.setTabText(idx, text)

    def removeTab(self, idx):
        """
        Remove the widget located at tab idx

        Arguments:
        idx - Idx of the widget

        Returns:
        None
        """
        current_state = self.tab_widget.blockSignals(True)
        idx = self.tab_widget.removeTab(idx)
        self.tab_widget.blockSignals(current_state)
        return idx

    def indexOf(self, widget):
        """
        Get the index of the widget.

        Arguments:
        widget - Adress of the widget

        Returns:
        Index of the widget
        """
        return self.tab_widget.indexOf(widget)

    def setTabPosition(self, position):
        """
        Set the tab position of the Tab bar

        Arguments:
        position - Tab position as string ['North', 'East', 'West', 'South']

        Returns:
        None
        """
        tab_position_dict = {
            'North': QTabWidget.North,
            'South': QTabWidget.South,
            'West': QTabWidget.West,
            'East': QTabWidget.East,
            }
        self.tab_widget.setTabPosition(tab_position_dict[position])

    def setTabEnabled(self, index, state):
        """
        Set the tab position index to the enable state.

        Arguments:
        index - Tab position index
        state - State (True or False)

        Returns:
        None
        """
        self.tab_widget.setTabEnabled(index, state)

    def order_tabs(self):
        current_state = self.tab_widget.blockSignals(True)
        widget_tuple = tuple([
            (
                self.widget(idx).name,
                self.widget(idx),
                self.tab_widget.isTabEnabled(idx)
                )
            for idx in range(self.count())
            ])
        for idx in reversed(range(self.count())):
            self.removeTab(idx)

        for idx, (name, widget, state) in enumerate(sorted(widget_tuple)):
            self.add_tab(widget, name, add_widgets=False)
            self.setTabEnabled(idx, state)
            if state:
                self.setCurrentIndex(idx)
        self.tab_widget.blockSignals(current_state)

    def enable_tab(self, visible):
        """
        Enable or disable the tab.


        Arguments:
        visible - Enable if True, Disable if False
        name - Name of the tab to disable.

        Returns:
        None
        """
        index = self.parent.content[self.layout].indexOf(self)
        if not visible:
            self.parent.content[self.layout].removeTab(index)
        else:
            self.parent.content[self.layout].add_tab(self, self.name)
            self.parent.content[self.layout].order_tabs()

