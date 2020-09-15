from PyQt5.QtWidgets import QWidget, QVBoxLayout, QDialog

from . import tabdocker

class LogViewerDialog(QDialog):


    def __init__(self, parent=None):
        super(LogViewerDialog, self).__init__(parent)

        central_raw_layout = QVBoxLayout(self)
        central_raw_layout.setContentsMargins(0, 0, 0, 0)
        central_widget_raw = QWidget(self)
        central_widget_raw.setObjectName('central_raw')
        central_raw_layout.addWidget(central_widget_raw)

        central_layout = QVBoxLayout(central_widget_raw)
        central_widget = QWidget(self)
        central_widget.setObjectName('central')
        central_layout.addWidget(central_widget)

        layout = QVBoxLayout(central_widget)

        self.tabs = tabdocker.TabDocker(self)
        self.tabs.setObjectName('tab')

        layout.addWidget(self.tabs)

    def add_tab(self, widget, name):
        self.tabs.add_tab(widget, name)

