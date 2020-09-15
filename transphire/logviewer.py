from PyQt5.QtWidgets import QPlainTextEdit, QWidget, QHBoxLayout, QVBoxLayout, QPushButton, QLineEdit
from PyQt5.QtGui import QTextOption, QTextCursor
from PyQt5.QtCore import pyqtSlot, QTimer
import glob
import os
import getpass

from . import transphire_utils as tu
from . import logviewerdialog

class LogViewer(QWidget):

    def __init__(self, show_indicators=False, indicator='', file_name='', parent=None):
        super(LogViewer, self).__init__(parent)

        # Setup layout
        global_layout = QHBoxLayout(self)
        global_layout.setContentsMargins(0, 0, 0, 0)

        widget = QWidget(self)
        widget.setObjectName('logview')
        global_layout.addWidget(widget)

        layout = QVBoxLayout(widget)

        self.project_path = ''
        self.log_path = ''
        self.error_path = ''
        self.indicator_names = ('log', 'error', 'sys_log', 'notes')
        self.indicator = indicator

        self.text = QPlainTextEdit(widget)
        if file_name:
            self.text.setObjectName('dialog')
        else:
            self.text.setObjectName('status')
        self.text.setPlaceholderText('Welcome to TranSPHIRE!')
        self.text.setToolTip('Double click after starting TranSPHIRE in order to show more information')
        self.text.setReadOnly(True)
        self.text.setWordWrapMode(QTextOption.WrapAnywhere)
        layout.addWidget(self.text, stretch=1)

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

        self.update_plain_text(force=True)
        self.timer = QTimer(self)
        self.timer.setInterval(1000)
        self.timer.timeout.connect(self.update_plain_text)
        self.timer.start()

        if self.indicator == 'notes':
            layout_h = QHBoxLayout()
            layout_h.setContentsMargins(0, 0, 0, 0)
            self.input_edit = QLineEdit('', self)
            submit_button = QPushButton('Submit', self)
            submit_button.clicked.connect(self.submit_text)
            layout_h.addWidget(self.input_edit, stretch=1)
            layout_h.addWidget(submit_button)
            layout.addLayout(layout_h)

    @pyqtSlot()
    def update_plain_text(self, force=False):
        if self.file_name and os.path.exists(self.file_name):
            with open(self.file_name, 'r') as read:
                text = read.read()
            if force:
                self.reset_plain_text(text)
            elif text.replace('\n', '').replace(' ', '') != self.text.toPlainText().replace('\n', '').replace(' ', ''):
                self.reset_plain_text(text)

    def reset_plain_text(self, text):
        self.text.setPlainText(text)
        cursor = self.text.textCursor()
        cursor.movePosition(QTextCursor.End)
        self.text.setTextCursor(cursor)

    @pyqtSlot()
    def submit_text(self):
        self.appendPlainText(self.input_edit.text(), indicator='notes', user=True)
        self.input_edit.setText('')

    def appendPlainText(self, text, indicator='log', user=False):
        text_raw = tu.create_log(text)
        prefix, suffix = text_raw.split(' => ', 1)
        if user:
            text = '{}\n{}: {}\n'.format(prefix, getpass.getuser(), suffix)
        else:
            text = '{}\n{}\n'.format(prefix, suffix)
        try:
            with open(self.file_name, 'a+') as write:
                write.write(text)
        except IOError:
            pass
        self.text.appendPlainText(text)
        cursor = self.text.textCursor()
        cursor.movePosition(QTextCursor.End)
        self.text.setTextCursor(cursor)
        print(text)
        if self.project_path:
            self.increment_indicator(indicator)

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
        is_notes = False
        file_path = self.log_path

        if sender_text == 'log':
            file_names = ['log.txt']

        elif sender_text == 'notes':
            is_notes = True
            file_names = ['notes.txt']

        elif sender_text == 'sys_log':
            file_names = ['sys_log.txt']

        elif sender_text == 'error':
            file_names = [os.path.basename(entry) for entry in glob.glob(os.path.join(self.error_path, '*'))]
            file_path = self.error_path

        else:
            assert False, sender.text()

        if not is_notes:
            self.increment_indicator(sender_text, '0')

        sender.setEnabled(False)
        QTimer.singleShot(5000, lambda: sender.setEnabled(True))

        dialog = logviewerdialog.LogViewerDialog(self)
        for file_name in file_names:
            dialog.add_tab(
                LogViewer(file_name=os.path.join(file_path, file_name), indicator=sender_text, parent=self),
                os.path.basename(file_name),
                )
        dialog.show()

    @pyqtSlot(str, str, str)
    def set_project_path(self, project_path, log_path, error_path):
        self.project_path = project_path
        self.log_path = log_path
        self.error_path = error_path
        state = True
        if not self.project_path:
            state = False
            self.file_name = ''
        elif not self.file_name:
            self.file_name = os.path.join(self.log_path, 'log.txt')
            self.update_plain_text(force=True)
        self.change_state(state)

    def change_state(self, state):
        self.text.blockSignals(not state)
        for button, _ in self.buttons.values():
            button.setEnabled(state)
            button.blockSignals(not state)

