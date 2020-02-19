from PyQt5.QtWidgets import QPlainTextEdit, QWidget, QHBoxLayout, QLabel, QVBoxLayout, QPushButton
from PyQt5.QtGui import QTextOption
from PyQt5.QtCore import pyqtSlot, QTimer
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
        self.indicator_names = ('sys_log', 'error')

        self.text = QPlainTextEdit(widget)
        self.text.setPlaceholderText('Welcome to TranSPHIRE!')
        self.text.setToolTip('Double click after starting TranSPHIRE in order to show more information')
        self.text.setReadOnly(True)
        self.text.setWordWrapMode(QTextOption.NoWrap)
        layout.addWidget(self.text)

        self.file_name = file_name

        self.indicators = {}
        self.buttons = {}
        if show_indicators:
            self.text.mouseDoubleClickEvent = self.my_click_event

            layout_h1 = QHBoxLayout()

            for entry in self.indicator_names:
                self.indicators[entry] = QLabel()
                self.indicators[entry].setObjectName('status_info')
                self.buttons[entry] = QPushButton('{0}'.format(entry), self)
                self.buttons[entry].setObjectName('button')
                self.buttons[entry].clicked.connect(self.my_click_event)

                layout_h1.addWidget(self.buttons[entry])
                layout_h1.addWidget(self.indicators[entry])
                self.set_indicator(entry, '0')

            layout_h1.addStretch(1)
            layout.addLayout(layout_h1)
            self.change_state(False)

        if self.file_name and os.path.exists(self.file_name):
            with open(self.file_name, 'r') as read:
                self.text.setPlainText(read.read())

    def appendPlainText(self, text):
        try:
            with open(self.file_name, 'a') as write:
                write.write(text)
                write.write('\n')
        except IOError:
            pass
        self.text.appendPlainText(text)

    def set_indicator(self, indicator, text):
        if indicator in self.indicator_names:
            self.indicators[indicator].setText(text)
            if text == '0':
                self.indicators[indicator].setStyleSheet(tu.get_style('white'))
            else:
                self.indicators[indicator].setStyleSheet(tu.get_style('global'))
        else:
            assert False, indicator

    def get_indicator(self, indicator):
        if indicator in self.indicator_names:
            return self.indicators[indicator].text()
        else:
            assert False, indicator

    @pyqtSlot()
    def my_click_event(self, event=None):
        if self.project_path is None:
            return None

        sender = self.sender()
        if sender is None:
            sender = self.text
            file_names = ['log.txt']
        elif sender.text() == 'sys_log':
            file_names = ['sys_log.txt']
        elif sender.text() == 'error':
            file_names = [os.path.join('error', os.path.basename(entry)) for entry in glob.glob(os.path.join(self.project_path, 'error', '*'))]
        else:
            assert False, sender.text()

        sender.setEnabled(False)
        QTimer.singleShot(5000, lambda: sender.setEnabled(True))

        dialog = logviewerdialog.LogViewerDialog(self)
        for file_name in file_names:
            dialog.add_tab(
                LogViewer(file_name=os.path.join(self.project_path, file_name), parent=self),
                os.path.basename(file_name),
                )
        dialog.show()

    def set_project_path(self, project_path):
        self.project_path = project_path
        if not self.file_name:
            self.file_name = os.path.join(self.project_path, 'log.txt')
            if os.path.exists(self.file_name):
                with open(self.file_name, 'r') as read:
                    self.text.setPlainText(read.read())
        self.change_state(True)

    def change_state(self, state):
        self.text.blockSignals(not state)
        for button in self.buttons.values():
            button.setEnabled(state)
            button.blockSignals(not state)
