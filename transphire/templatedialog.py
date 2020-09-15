import os
import glob
import shutil
from PyQt5.QtWidgets import QDialog, QVBoxLayout, QPushButton, QWidget, QComboBox, QLabel
from PyQt5.QtCore import pyqtSlot

from . import transphire_utils as tu

class TemplateDialog(QDialog):
    """
    TemplateDialog dialog.
    Dialog used to enter the template.

    Inherits from:
    QDialog
    """

    def __init__(self, settings_directory, add_remove=True, parent=None):
        super(TemplateDialog, self).__init__(parent)

        self.settings_directory = settings_directory
        self.template = None
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

        self.templates = sorted([os.path.basename(entry) for entry in glob.glob(os.path.join(settings_directory, '*')) if os.path.isdir(entry)])

        layout.addWidget(QLabel('Available templates:'))

        self.combo_box = QComboBox(parent=self)
        self.combo_box.clear()
        self.combo_box.addItems([entry for entry in self.templates if entry != 'SHARED'])
        layout.addWidget(self.combo_box)

        if add_remove:
            button = QPushButton('New template', self)
            button.clicked.connect(self.add_template)
            layout.addWidget(button)

            button = QPushButton('Copy current template', self)
            button.clicked.connect(self.copy_template)
            layout.addWidget(button)

            button = QPushButton('Remove current template', self)
            button.clicked.connect(self.remove_template)
            layout.addWidget(button)

        button = QPushButton('Choose current template', self)
        button.clicked.connect(self.choose_template)
        layout.addWidget(button)

    @pyqtSlot()
    def choose_template(self):
        self.template = self.combo_box.currentText()
        self.accept()

    @pyqtSlot()
    def remove_template(self):
        text = self.combo_box.currentText()
        if text == 'DEFAULT':
            tu.message('Default template cannot be deleted!')
            return None
        dialog = InputBox(is_password=False, parent=self)
        dialog.setText('Confirm deletion', 'Do you really want to remove delete template {0}? Type in "YES!"'.format(text))
        result = dialog.exec_()
        if result:
            response = dialog.getText()
            if response == 'YES!':
                try:
                    shutil.rmtree(os.path.join(self.settings_directory, text))
                except FileNotFoundError:
                    tu.message('Something is wrong! Template directory could not be removed!')
                else:
                    self.templates.remove(text)
                    self.combo_box.clear()
                    self.combo_box.addItems([entry for entry in self.templates if entry != 'SHARED'])
            else:
                tu.message('Input needs to be "YES!" to work')

    @pyqtSlot()
    def add_template(self):
        dialog = InputBox(is_password=False, parent=self)
        dialog.setText('New template', 'Template name:')
        result = dialog.exec_()

        if result:
            text = dialog.getText().strip()
            if ' ' in text:
                tu.message('There are not whitespaces allowed in the template name!')
            elif 'shared' == text.lower():
                tu.message('Shared is a protected namespace. Please choose another name.')
            elif text in self.templates:
                tu.message('Template name already exists! Please choose another one!')
            else:
                try:
                    os.mkdir(os.path.join(self.settings_directory, text))
                except IOError:
                    tu.message('Something is wrong! Template directory already exists!')
                else:
                    self.templates.append(text)
                    self.combo_box.clear()
                    self.combo_box.addItems([entry for entry in self.templates if entry != 'SHARED'])
                    self.combo_box.setCurrentText(text)

    @pyqtSlot()
    def copy_template(self):
        current_template = self.combo_box.currentText()
        if not current_template:
            tu.message('No template selected!')
            return None

        dialog = InputBox(is_password=False, parent=self)
        dialog.setText('New template', 'Template name:')
        result = dialog.exec_()

        if result:
            text = dialog.getText()
            if ' ' in text:
                tu.message('There are not whitespaces allowed in the template name!')
            elif text in self.templates:
                tu.message('Template name already exists! Please choose another one!')
            else:
                try:
                    shutil.copytree(
                        os.path.join(self.settings_directory, current_template),
                        os.path.join(self.settings_directory, text)
                        )
                except IOError as e:
                    print(e)
                    tu.message('Something is wrong! Template directory already exists!')
                else:
                    self.templates.append(text)
                    self.combo_box.clear()
                    self.combo_box.addItems(self.templates)
                    self.combo_box.setCurrentText(text)

from .inputbox import InputBox

