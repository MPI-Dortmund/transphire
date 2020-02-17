from PyQt5.QtWidgets import QPlainTextEdit, QWidget, QHBoxLayout, QLabel, QVBoxLayout
from transphire import transphire_utils as tu

class LogViewer(QWidget):

    def __init__(self, project_path='', indicators=False, file_name='', parent=None):
        super(LogViewer, self).__init__(parent)

        # Setup layout
        global_layout = QHBoxLayout(self)
        global_layout.setContentsMargins(0, 0, 0, 0)

        widget = QWidget(self)
        widget.setObjectName('logview')
        global_layout.addWidget(widget)

        layout = QVBoxLayout(widget)

        self.project_path = project_path

        self.text = QPlainTextEdit(widget)
        self.text.setReadOnly(True)
        self.text.mouseDoubleClickEvent = self.mouseDoubleClickEvent
        layout.addWidget(self.text)

        self.indicators = {}
        if indicators:
            layout_h1 = QHBoxLayout()

            for entry in ('log', 'error'):
                self.indicators[entry] = QLabel()
                layout_h1.addWidget(QLabel('{0}:'.format(entry)))
                layout_h1.addWidget(self.indicators[entry])
                self.set_indicator(entry, '0')

            layout_h1.addStretch(1)
            layout.addLayout(layout_h1)

        if file_name:
            with open(file_name, 'r') as read:
                self.appendPlainText(read.read())

    def appendPlainText(self, text):
        self.text.appendPlainText(text)

    def set_indicator(self, indicator, text):
        if indicator in ('log', 'error'):
            self.indicators[indicator].setText(text)
            if text == '0':
                self.indicators[indicator].setStyleSheet(tu.get_style('unchanged'))
            else:
                self.indicators[indicator].setStyleSheet(tu.get_style('global'))
        else:
            assert False, indicator

    def get_indicator(self, indicator):
        if indicator in ('log', 'error'):
            return self.indicators[indicator].text()
        else:
            assert False, indicator

    def mouseDoubleClickEvent(self, event):
        pass
