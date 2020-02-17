from PyQt5.QtWidgets import QPlainTextEdit, QWidget, QHBoxLayout, QLabel, QVBoxLayout
from PyQt5.QtGui import QTextOption
from transphire import transphire_utils as tu
from transphire import logviewerdialog
import glob
import os

class LogViewer(QWidget):

    def __init__(self, show_indicators=False, file_name='', parent=None):
        super(LogViewer, self).__init__(parent)

        # Setup layout
        global_layout = QHBoxLayout(self)
        global_layout.setContentsMargins(0, 0, 0, 0)

        widget = QWidget(self)
        widget.setObjectName('logview')
        global_layout.addWidget(widget)

        layout = QVBoxLayout(widget)

        self.project_path = None

        self.text = QPlainTextEdit(widget)
        self.text.setPlaceholderText('Welcome to TranSPHIRE!')
        self.text.setToolTip('Double click in order to show more information about logs and errors')
        self.text.setReadOnly(True)
        self.text.setWordWrapMode(QTextOption.NoWrap)
        layout.addWidget(self.text)

        self.indicators = {}
        if show_indicators:
            self.text.mouseDoubleClickEvent = self.mouseDoubleClickEvent
            self.mouseDoubleClickEvent = self.my_mouseDoubleClickEvent

            layout_h1 = QHBoxLayout()

            for entry in ('log', 'error'):
                self.indicators[entry] = QLabel()
                self.indicators[entry].setObjectName('status_info')
                label = QLabel('{0}:'.format(entry))
                label.setStyleSheet('QLabel {color: white}')
                layout_h1.addWidget(label)
                layout_h1.addWidget(self.indicators[entry])
                self.set_indicator(entry, '0')

            layout_h1.addStretch(1)
            layout.addLayout(layout_h1)

        if file_name and os.path.exists(file_name):
            with open(file_name, 'r') as read:
                self.text.setPlainText(read.read())

    def appendPlainText(self, text):
        self.text.appendPlainText(text)

    def set_indicator(self, indicator, text):
        if indicator in ('log', 'error'):
            self.indicators[indicator].setText(text)
            if text == '0':
                self.indicators[indicator].setStyleSheet(tu.get_style('white'))
            else:
                self.indicators[indicator].setStyleSheet(tu.get_style('global'))
        else:
            assert False, indicator

    def get_indicator(self, indicator):
        if indicator in ('log', 'error'):
            return self.indicators[indicator].text()
        else:
            assert False, indicator

    def my_mouseDoubleClickEvent(self, event):
        self.project_path = '/home/em-transfer-user/projects/2019_11_06_ULTIMATE_TEST_krios1_count_K2'
        dialog = logviewerdialog.LogViewerDialog(self)

        dialog.add_tab(
            LogViewer(file_name=os.path.join(self.project_path, 'log.txt'), parent=self),
            'Log',
            file_name=os.path.join(self.project_path, 'log.txt')
            )

        dialog.add_tab(
            LogViewer(file_name=os.path.join(self.project_path, 'sys_log.txt'), parent=self),
            'Sys_log',
            file_name=os.path.join(self.project_path, 'sys_log.txt')
            )

        for entry in glob.glob(os.path.join(self.project_path, 'error', '*')):
            dialog.add_tab(
                LogViewer(file_name=entry, parent=self),
                os.path.basename(entry),
                file_name=entry
                )
        dialog.show()

    def set_project_path(self, project_path):
        self.project_path = project_path
