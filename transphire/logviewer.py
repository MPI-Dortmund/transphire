from PyQt5.QtWidgets import QPlainTextEdit, QWidget, QHBoxLayout, QLabel, QVBoxLayout, QPushButton
from PyQt5.QtGui import QTextOption, QTextCursor
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

        self.project_path = ''
        self.indicator_names = ('log', 'error', 'sys_log')

        self.text = QPlainTextEdit(widget)
        if file_name:
            self.text.setObjectName('dialog')
        else:
            self.text.setObjectName('status')
        self.text.setPlaceholderText('Welcome to TranSPHIRE!')
        self.text.setToolTip('Double click after starting TranSPHIRE in order to show more information')
        self.text.setReadOnly(True)
        self.text.setWordWrapMode(QTextOption.WrapAnywhere)
        layout.addWidget(self.text)

        self.file_name = file_name

        self.buttons = {}
        if show_indicators:

            layout_h1 = QHBoxLayout()

            for entry in self.indicator_names:
                template = '{0}: {{0}}'.format(entry)
                self.buttons[entry] = [QPushButton(self), template]
                self.buttons[entry][0].setObjectName('button_entry')
                self.buttons[entry][0].clicked.connect(self.my_click_event)

                layout_h1.addWidget(self.buttons[entry][0])
                self.increment_indicator(entry, '0')

            layout_h1.addStretch(1)
            layout.addLayout(layout_h1)
            self.change_state(False)

        if self.file_name and os.path.exists(self.file_name):
            with open(self.file_name, 'r') as read:
                self.text.setPlainText(read.read())
            cursor = self.text.textCursor()
            cursor.movePosition(QTextCursor.End)
            self.text.setTextCursor(cursor)

    def appendPlainText(self, text):
        try:
            with open(self.file_name, 'a') as write:
                write.write(text)
                write.write('\n')
        except IOError:
            pass
        self.text.appendPlainText(text + '\n')
        cursor = self.text.textCursor()
        cursor.movePosition(QTextCursor.End)
        self.text.setTextCursor(cursor)
        print(text)
        if self.project_path:
            self.increment_indicator('log')

    def increment_indicator(self, indicator, text=''):
        if indicator in self.indicator_names:
            button, template = self.buttons[indicator]
            if text:
                cur_text = text
            else:
                cur_text = str(1 + int(self.get_indicator(indicator)))

            button.setText(template.format(cur_text))
            button.setToolTip(template.format(text))
            if self.get_indicator(indicator) == '0':
                button.setStyleSheet('')
            else:
                button.setStyleSheet(tu.get_style('changed'))
        else:
            assert False, indicator

    def get_indicator(self, indicator):
        if indicator in self.indicator_names:
            return self.buttons[indicator][0].text().split(':')[-1].strip()
        else:
            assert False, indicator

    @pyqtSlot()
    def my_click_event(self, event=None):
        if not self.project_path:
            return None

        sender = self.sender()
        sender_text = sender.text().split(':')[0].strip()
        if sender_text == 'log':
            file_names = ['log.txt']
        elif sender_text == 'sys_log':
            file_names = ['sys_log.txt']
        elif sender_text == 'error':
            file_names = [os.path.join('error', os.path.basename(entry)) for entry in glob.glob(os.path.join(self.project_path, 'error', '*'))]
        else:
            assert False, sender.text()

        self.increment_indicator(sender_text, '0')

        sender.setEnabled(False)
        QTimer.singleShot(5000, lambda: sender.setEnabled(True))

        dialog = logviewerdialog.LogViewerDialog(self)
        for file_name in file_names:
            dialog.add_tab(
                LogViewer(file_name=os.path.join(self.project_path, file_name), parent=self),
                os.path.basename(file_name),
                )
        dialog.show()

    @pyqtSlot(str)
    def set_project_path(self, project_path):
        self.project_path = project_path
        state = True
        if not self.project_path:
            state = False
            self.file_name = ''
        elif not self.file_name:
            self.file_name = os.path.join(self.project_path, 'log.txt')
            if os.path.exists(self.file_name):
                with open(self.file_name, 'r') as read:
                    self.text.setPlainText(read.read())
                cursor = self.text.textCursor()
                cursor.movePosition(QTextCursor.End)
                self.text.setTextCursor(cursor)
        self.change_state(state)

    def change_state(self, state):
        self.text.blockSignals(not state)
        for button, _ in self.buttons.values():
            button.setEnabled(state)
            button.blockSignals(not state)
