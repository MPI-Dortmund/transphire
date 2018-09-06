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
    from PyQt4.QtGui import QHBoxLayout, QWidget, QPushButton, QApplication
    from PyQt4.QtCore import pyqtSlot, pyqtSignal
except ImportError:
    from PyQt5.QtWidgets import QHBoxLayout, QWidget, QPushButton, QApplication
    from PyQt5.QtCore import pyqtSlot, pyqtSignal
from transphire.loadwindow import DefaultSettings
from transphire import transphire_utils as tu


class ButtonContainer(QWidget):
    """
    ButtonContainer widget.

    Inherits from:
    QWidget

    Buttons:
    Save - Save settings
    Load - Load settings
    Default settings - Change default settings
    About - Show about information
    Check quota - Check the quota of current project and scratch directory
    Start/Stop - Start/Stop processing

    Signals:
    sig_load - Emited when the Load Button is clicked (No object)
    sig_save - Emited when the Save Button is clicked (No object)
    sig_start - Emited when the Start Button is clicked (No object)
    sig_stop - Emited when the Stop Button is clicked (No object)
    sig_check_quota - Emited when the Check quota Button is clicked (No object)
    """
    sig_load = pyqtSignal()
    sig_save = pyqtSignal()
    sig_start = pyqtSignal()
    sig_stop = pyqtSignal()
    sig_monitor_start = pyqtSignal()
    sig_monitor_stop = pyqtSignal()
    sig_check_quota = pyqtSignal()

    def __init__(self, parent=None, **kwargs):
        """
        Setup the layout for the widget

        Arguments:
        parent - Parent widget (default None)
        kwargs - Unused arguments for easier automatisation

        Return:
        None
        """
        super(ButtonContainer, self).__init__(parent)

        # Variables
        kwargs = kwargs
        self.parent = parent

        # Setup layout
        layout = QHBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)

        # About button
        self.show_about = QPushButton('About', self)
        self.show_about.clicked.connect(self._show_about)
        self.show_about.setObjectName('button')
        layout.addWidget(self.show_about)

        # Load button
        self.load_button = QPushButton('Load', self)
        self.load_button.clicked.connect(self.sig_load.emit)
        self.load_button.setObjectName('button')
        layout.addWidget(self.load_button)

        # Save button
        self.save_button = QPushButton('Save', self)
        self.save_button.clicked.connect(self.sig_save.emit)
        self.save_button.setObjectName('button')
        layout.addWidget(self.save_button)

        # Default settings button
        self.default_settings = QPushButton('Default settings', self)
        self.default_settings.clicked.connect(self._modify_settings)
        self.default_settings.setObjectName('button')
        layout.addWidget(self.default_settings)
        layout.addStretch(1)

        # Check quota button
        self.check_quota = QPushButton('Check quota', self)
        self.check_quota.clicked.connect(self.sig_check_quota.emit)
        self.check_quota.setObjectName('button')
        layout.addWidget(self.check_quota)


        # Start/Stop monitor button
        self.start_monitor_button = QPushButton('Monitor', self)
        self.start_monitor_button.clicked.connect(self._start_stop)
        self.start_monitor_button.setObjectName('start')
        self.start_monitor_button.setVisible(True)
        self.start_monitor_button.setEnabled(True)
        layout.addWidget(self.start_monitor_button)

        self.stop_monitor_button = QPushButton('Monitor', self)
        self.stop_monitor_button.clicked.connect(self._start_stop)
        self.stop_monitor_button.setObjectName('stop')
        self.stop_monitor_button.setVisible(False)
        self.stop_monitor_button.setEnabled(False)
        layout.addWidget(self.stop_monitor_button)

        # Start/Stop button
        self.start_button = QPushButton('Start', self)
        self.start_button.clicked.connect(self._start_stop)
        self.start_button.setObjectName('start')
        self.start_button.setVisible(True)
        self.start_button.setEnabled(True)
        layout.addWidget(self.start_button)

        self.stop_button = QPushButton('Stop', self)
        self.stop_button.clicked.connect(self._start_stop)
        self.stop_button.setObjectName('stop')
        self.stop_button.setVisible(False)
        self.stop_button.setEnabled(False)
        layout.addWidget(self.stop_button)

        # Final stretch

    @pyqtSlot()
    def _modify_settings(self):
        """
        Open default settings dialog.
        Called when the Default settings button is clicked.

        Arguments:
        None

        Return:
        None
        """

        temp_save_file = 'temp_reset_save_1'
        content, apply = DefaultSettings.get_content_default(
            edit_settings=True,
            apply=True,
            settings_folder=self.parent.settings_folder
            )
        if not apply:
            tu.message('Restart GUI to apply saved changes')

        elif apply:
            content_gui = tu.get_content_gui(content=content)
            self.parent.enable(var=False, use_all=True)
            # result is True if No is chosen
            result = tu.question(
                head='Keep current values',
                text='Do you want to keep your current settings?\n' +
                'Otherwhise they will be overwritten by the default values.',
                parent=self
                )
            app = QApplication.instance()
            app.setStyleSheet(
                tu.look_and_feel(app=app, default=content['Font'])
                )

            if not result:
                self.parent.save(temp_save_file)
                self.parent.reset_gui(
                    content_gui=content_gui,
                    content_pipeline=content['Pipeline'],
                    load_file=temp_save_file
                    )
            else:
                self.parent.reset_gui(
                    content_gui=content_gui,
                    content_pipeline=content['Pipeline'],
                    load_file=None
                    )

        else:
            pass

    @pyqtSlot()
    def _start_stop(self):
        """
        Start or stop the process dependent on the current button text.
        This method is called when the Start/Stop button is pressed.

        Arguments:
        None

        Return:
        None
        """
        if self.sender().text() == 'Start':
            self.sig_start.emit()
        elif self.sender().text() == 'Stop':
            self.sig_stop.emit()
        elif self.sender().text() == 'Monitor' and self.sender().objectName() == 'start':
            self.sig_monitor_start.emit()
        elif self.sender().text() == 'Monitor' and self.sender().objectName() == 'stop':
            self.sig_monitor_stop.emit()
        else:
            print(
                'Button text not known!',
                'Stopping now, but please contact the TranSPHIRE Authors',
                self.sender().text()
                )
            self.sig_stop.emit()

    def enable(self, var, use_all):
        """
        Enable or disable the buttons.

        Arguments:
        var - State of buttons (True or False)
        use_all - Disable all buttons (True) or only some (False)

        Return:
        None
        """
        assert var is True or var is False, 'Unknown option for var'
        assert use_all is True or use_all is False, 'Unknown option for use_all'
        if use_all:
            self.load_button.setEnabled(var)
            self.save_button.setEnabled(var)
            self.default_settings.setEnabled(var)
            self.start_button.setEnabled(var)
            self.stop_button.setEnabled(var)
            self.start_monitor_button.setEnabled(var)
            self.stop_monitor_button.setEnabled(var)
            self.show_about.setEnabled(var)
            self.check_quota.setEnabled(var)
        else:
            self.load_button.setEnabled(var)
            self.save_button.setEnabled(var)
            self.check_quota.setEnabled(var)
            self.default_settings.setEnabled(var)

    @staticmethod
    def _show_about():
        """
        Show the about text.

        Arguments:
        None

        Return:
        None
        """
        text = (
            "\n"
            "TranSPHIRE is supposed to help with the cryo-EM data collection\n"
            "Copyright (C) 2017 Markus Stabrin\n"
            "\n"
            "This program is free software: you can redistribute it and/or modify\n"
            "it under the terms of the GNU General Public License as published by\n"
            "the Free Software Foundation, either version 3 of the License, or\n"
            "(at your option) any later version.\n"
            "\n"
            "This program is distributed in the hope that it will be useful,\n"
            "but WITHOUT ANY WARRANTY; without even the implied warranty of\n"
            "MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the\n"
            "GNU General Public License for more details.\n"
            "\n"
            "You should have received a copy of the GNU General Public License\n"
            "along with this program.  If not, see <http://www.gnu.org/licenses/>.\n"
            )
        tu.message(text)
