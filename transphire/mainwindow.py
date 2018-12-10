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
import sys
import os
import re
import pexpect as pe
try:
    QT_VERSION = 4
    from PyQt4.QtGui import (
        QMainWindow,
        QHBoxLayout,
        QVBoxLayout,
        QWidget,
        QFileDialog,
        )
    from PyQt4.QtCore import QThread, pyqtSlot, QCoreApplication, QTimer
except ImportError:
    QT_VERSION = 5
    from PyQt5.QtWidgets import (
        QMainWindow,
        QHBoxLayout,
        QVBoxLayout,
        QWidget,
        QFileDialog,
        )
    from PyQt5.QtCore import QThread, pyqtSlot, QCoreApplication, QTimer

# Objects
from transphire.mountworker import MountWorker
from transphire.processworker import ProcessWorker
from transphire.inputbox import InputBox
from transphire.plotworker import PlotWorker
from transphire.separator import Separator
from transphire.tabdocker import TabDocker
from transphire.mountcalculator import MountCalculator
from transphire import transphire_utils as tu
from transphire import transphire_import as ti


class MainWindow(QMainWindow):
    """
    MainWindow widget.
    Connects GUI and worker threads.

    Inherits from:
    QMainWindow

    Buttons:
    None

    Signals:
    None
    """

    def __init__(
            self, content_gui, content_pipeline, settings_folder,
            mount_directory, version, parent=None
            ):
        """
        Setup the layout for the widget

        Arguments:
        content_gui - Content used to create the GUI outfit.
        content_pipeline - Content used to start processing threads.
        settings_folder - Name of the folder containing settings.
        mount_directory - Name of the folder containing mount points.
        version - Version of TranSPHIRE.
        parent - Parent widget (default None)

        Return:
        None
        """
        super(MainWindow, self).__init__(parent)

        # Ask for sudo password if needed
        self.password = ''
        need_sudo_password = False
        for content in content_gui:
            if content['name'] == 'Mount':
                for entry in content['content_mount']:
                    for widget in entry:
                        for key in widget:
                            if key == 'Need sudo for copy?':
                                if widget[key][0] == 'True':
                                    need_sudo_password = True
                                else:
                                    pass
                            elif key == 'Need sudo for mount?':
                                if widget[key][0] == 'True':
                                    need_sudo_password = True
                                else:
                                    pass
                            else:
                                pass
            else:
                pass

        if need_sudo_password:
            while True:
                dialog = InputBox(is_password=True, parent=self)
                dialog.setText('Sudo password', 'Please provide the sudo password for mount/copy!')
                dialog.exec_()
                if not dialog.result():
                    QCoreApplication.instance().quit()
                    sys.exit()
                else:
                    self.password = dialog.getText()
                    child = pe.spawnu('sudo -S -k ls')
                    child.sendline(self.password)
                    try:
                        idx = child.expect(
                            [
                                pe.EOF,
                                'sudo: 1 incorrect password attempt',
                                'Sorry, try again'
                                ],
                            timeout=10
                            )
                    except pe.exceptions.TIMEOUT:
                        print('Wrong sudo password!')
                        tu.message('Wrong sudo password!')
                    else:
                        if idx == 0:
                            break
                        else:
                            print('Wrong sudo password!')
                            tu.message('Wrong sudo password!')
        else:
            pass

        # Start TranSPHIRE from HOME directory.
        self.path = os.environ['HOME']

        # Window title
        self.setWindowTitle(
            '{0} v{1} - {2} - {3}'.format(
                'TranSPHIRE',
                version,
                self.path,
                os.uname()[1]
                )
            )

        # Initiate contents
        self.central_widget_raw = None
        self.central_widget = None
        self.content = None
        self.layout = None

        # Settings folder
        self.settings_folder = settings_folder
        self.mount_directory = mount_directory
        self.temp_save = '{0}/temp_save'.format(settings_folder)

        # Threads
        self.timer_ctf = None
        self.timer_motion = None
        self.timer_picking = None
        self.mount_worker = None
        self.process_worker = None
        self.plot_worker_ctf = None
        self.plot_worker_motion = None
        self.plot_worker_picking = None
        self.mount_calculation_ssh = None
        self.mount_calculation_get = None
        self.mount_calculation_df = None
        self.thread_mount = None
        self.thread_process = None
        self.thread_plot_ctf = None
        self.thread_plot_motion = None
        self.thread_plot_picking = None
        self.mount_thread_list = None

        # Fill GUI
        self.reset_gui(
            content_gui=content_gui, content_pipeline=content_pipeline
            )

    def start_threads(self, content_pipeline):
        """
        Start threads used in TranSPHIRE.

        Arguments:
        content_pipeline - Content used to start processing threads.

        Return:
        None
        """
        # Stop threads if already started.
        if self.mount_worker is not None:
            self.mount_worker.setParent(None)

        if self.process_worker is not None:
            self.process_worker.setParent(None)

        if self.plot_worker_ctf is not None:
            self.plot_worker_ctf.setParent(None)

        if self.plot_worker_motion is not None:
            self.plot_worker_motion.setParent(None)

        if self.plot_worker_picking is not None:
            self.plot_worker_picking.setParent(None)

        if self.thread_mount is not None:
            self.thread_mount.quit()
            self.thread_mount.wait()
            self.thread_mount.setParent(None)

        if self.thread_process is not None:
            self.thread_process.quit()
            self.thread_process.wait()
            self.thread_process.setParent(None)

        if self.thread_plot_ctf is not None:
            self.thread_plot_ctf.quit()
            self.thread_plot_ctf.wait()
            self.thread_plot_ctf.setParent(None)

        if self.thread_plot_motion is not None:
            self.thread_plot_motion.quit()
            self.thread_plot_motion.wait()
            self.thread_plot_motion.setParent(None)

        if self.thread_plot_picking is not None:
            self.thread_plot_picking.quit()
            self.thread_plot_picking.wait()
            self.thread_plot_picking.setParent(None)

        if self.timer_ctf is not None:
            self.timer_ctf.setParent(None)

        if self.timer_motion is not None:
            self.timer_motion.setParent(None)

        if self.timer_picking is not None:
            self.timer_picking.setParent(None)

        if self.mount_thread_list is not None:
            for setting in self.content['Mount'].get_settings():
                for key in setting:
                    thread = self.mount_thread_list[key]['thread']
                    calculator = self.mount_thread_list[key]['object']
                    calculator.kill_thread = True
                    thread.quit()
                    thread.wait()

        # Create objects used in threads
        self.mount_worker = MountWorker(
            password=self.password,
            settings_folder=self.settings_folder,
            mount_directory=self.mount_directory
            )
        self.process_worker = ProcessWorker(
            password=self.password,
            content_process=content_pipeline,
            mount_directory=self.mount_directory
            )
        self.plot_worker_ctf = PlotWorker()
        self.plot_worker_motion = PlotWorker()
        self.plot_worker_picking = PlotWorker()

        # Create threads
        self.thread_mount = QThread(self)
        self.thread_process = QThread(self)
        self.thread_plot_ctf = QThread(self)
        self.thread_plot_motion = QThread(self)
        self.thread_plot_picking = QThread(self)

        # Start threads
        self.thread_mount.start()
        self.thread_process.start()
        self.thread_plot_ctf.start()
        self.thread_plot_motion.start()
        self.thread_plot_picking.start()

        # Start objects in threads
        self.mount_worker.moveToThread(self.thread_mount)
        self.process_worker.moveToThread(self.thread_process)
        self.plot_worker_ctf.moveToThread(self.thread_plot_ctf)
        self.plot_worker_motion.moveToThread(self.thread_plot_motion)
        self.plot_worker_picking.moveToThread(self.thread_plot_picking)

    def reset_gui(self, content_gui, content_pipeline, load_file=None):
        """
        Reset the content of the mainwindow.

        Arguments:
        content_gui - Content used to fill the GUI.
        content_pipeline - Content used to start processing threads.
        load_file - Settings file (default None).

        Return:
        None
        """
        # Fill MainWindow
        self.set_central_widget()
        self.set_layout_structure()
        self.start_threads(content_pipeline=content_pipeline)
        postprocess_content = self.fill_content(content_gui=content_gui)
        self.postprocess_content(postprocess_content)

        for content in content_gui:
            if content['name'] == 'Status':
                for entry in content['content']:
                    for widget in entry:
                        for key in widget:
                            if key == 'Project name pattern':
                                self.project_name_pattern = widget[key][0]
                            elif key == 'Project name pattern example':
                                self.project_name_pattern_example = widget[key][0]
                            else:
                                pass
            else:
                pass

        # Load settings saved in load_file
        if load_file is not None:
            self.load(file_name=load_file)
            os.remove('{0}.txt'.format(load_file))
        elif os.path.exists('{0}.txt'.format(self.temp_save)):
            # Result is True if answer is Yes
            result = tu.question(
                head='Restore default values.',
                text='Restore default values?',
                parent=self
                )
            if not result:
                self.load(file_name=self.temp_save)
            else:
                pass
        else:
            pass
        self.mount_worker.sig_load_save.emit()

    def save_temp_settings(self):
        """
        Save the status of the GUI in a temp file.

        Arguments:
        None

        Return:
        True, if saving was succesful.
        """
        if os.path.exists('{0}.txt'.format(self.temp_save)):
            os.remove('{0}.txt'.format(self.temp_save))
        else:
            pass
        value = self.save(file_name=self.temp_save, temp=True)
        return value

    def postprocess_content(self, error_list):
        """
        Do postprocessing of creating GUI content, like connecting signals.

        Arguments:
        error_list - List of errors that occured.

        Return:
        True, if saving was succesful.
        """
        for entry in error_list:
            tu.message(entry)

        self.process_worker.sig_finished.connect(self._finished)
        self.process_worker.sig_plot_ctf.connect(self.plot_worker_ctf.set_settings)
        self.process_worker.sig_plot_motion.connect(self.plot_worker_motion.set_settings)
        self.process_worker.sig_plot_picking.connect(self.plot_worker_picking.set_settings)

        self.timer_ctf = QTimer(self)
        self.timer_ctf.setInterval(30000)
        self.timer_ctf.timeout.connect(self.plot_worker_ctf.sig_calculate.emit)
        self.timer_ctf.start()

        self.timer_motion = QTimer(self)
        self.timer_motion.setInterval(30000)
        self.timer_motion.timeout.connect(self.plot_worker_motion.sig_calculate.emit)
        QTimer.singleShot(10000, self.timer_motion.start)

        self.timer_picking = QTimer(self)
        self.timer_picking.setInterval(30000)
        self.timer_picking.timeout.connect(self.plot_worker_picking.sig_calculate.emit)
        QTimer.singleShot(20000, self.timer_picking.start)

        self.mount_thread_list = {}
        for key in self.content['Mount'].content:
            thread = QThread(self)
            thread.start()
            mount_calculator = MountCalculator(name=key)
            mount_calculator.moveToThread(thread)
            self.mount_thread_list[key] = {
                'thread': thread,
                'object': mount_calculator
                }
            mount_calculator.sig_finished.connect(
                self.content['Status'].refresh_quota
                )
            mount_calculator.sig_finished.connect(
                self.abort_finished
                )
            self.mount_worker.sig_calculate_ssh_quota.connect(
                mount_calculator.calculate_ssh_quota
                )
            self.mount_worker.sig_calculate_df_quota.connect(
                mount_calculator.calculate_df_quota
                )
            self.mount_worker.sig_calculate_get_quota.connect(
                mount_calculator.calculate_get_quota
                )
        self.content['Mount'].set_threadlist(thread_list=self.mount_thread_list)

    def abort_finished(self, *args, **kwargs):
        """
        Set the mount worker abort variable to True.

        Arguments:
        None

        Return:
        None
        """
        self.mount_worker.abort_finished = True

    def set_central_widget(self):
        """
        Reset the central widget of the MainWindow.

        Arguments:
        None

        Return:
        None
        """
        if self.central_widget_raw is not None:
            self.central_widget_raw.setParent(None)
        else:
            pass
        if self.central_widget is not None:
            self.central_widget.setParent(None)
        else:
            pass

        self.central_widget_raw = QWidget(self)
        self.central_widget_raw.setObjectName('central_raw')
        self.setCentralWidget(self.central_widget_raw)
        layout = QVBoxLayout(self.central_widget_raw)
        self.central_widget = QWidget(self.central_widget_raw)
        self.central_widget.setObjectName('central')
        layout.addWidget(self.central_widget)

    def set_layout_structure(self):
        """
        Setup the layout structure for the central widget.

        Arguments:
        None

        Return:
        None
        """
        # Layout dictionary
        widget_layout_h2 = QWidget(self)
        widget_layout_h3 = QWidget(self)
        widget_layout_h4 = QWidget(self)
        widget_layout_v1 = QWidget(self)
        widget_layout_v1_a = QWidget(self)
        widget_layout_v2 = QWidget(self)

        self.layout = {}
        self.layout['h1'] = QHBoxLayout(self.central_widget)
        self.layout['h2'] = QHBoxLayout(widget_layout_h2)
        self.layout['h3'] = QHBoxLayout(widget_layout_h3)
        self.layout['h4'] = QHBoxLayout(widget_layout_h4)
        self.layout['v1'] = QVBoxLayout(widget_layout_v1)
        self.layout['v1_a'] = QVBoxLayout(widget_layout_v1_a)
        self.layout['v2'] = QVBoxLayout(widget_layout_v2)

        self.layout['h2'].setContentsMargins(0, 0, 0, 0)
        self.layout['h3'].setContentsMargins(0, 0, 0, 0)
        self.layout['h4'].setContentsMargins(0, 0, 0, 0)
        self.layout['v1'].setContentsMargins(0, 0, 0, 0)
        self.layout['v1_a'].setContentsMargins(0, 0, 0, 0)
        self.layout['v2'].setContentsMargins(0, 0, 0, 0)


        # Layout architecture
        self.layout['h1'].addWidget(widget_layout_v1, stretch=1)
        self.layout['h1'].addWidget(
            Separator(
                typ='vertical',
                color='black',
                left=widget_layout_v1,
                right=widget_layout_v2,
                ),
            stretch=0
            )
        self.layout['h1'].addWidget(widget_layout_v2, stretch=0)

        self.layout['v1_a'].addWidget(widget_layout_h2, stretch=0)
        self.layout['v1_a'].addWidget(
            Separator(
                typ='horizontal',
                color='grey',
                up=widget_layout_h2,
                down=widget_layout_h3,
                ),
            stretch=0
            )
        self.layout['v1_a'].addWidget(widget_layout_h3, stretch=0)

        self.layout['v1'].addWidget(widget_layout_v1_a, stretch=0)
        self.layout['v1'].addWidget(
            Separator(
                typ='horizontal',
                color='grey',
                up=widget_layout_v1_a,
                down=widget_layout_h4,
                ),
            stretch=0
            )
        self.layout['v1'].addWidget(widget_layout_h4, stretch=1)

    def fill_content(self, content_gui):
        """
        Fill the layouts of the central widget.

        Arguments:
        content_gui - Content used to create the GUI outfit.

        Return:
        List of errors that occured.
        """
        self.content = {}
        exclude_set = tu.get_exclude_set(content=content_gui)
        error_list = []
        tab_list = []
        for entry in content_gui:
            key = entry['name']

            if key in exclude_set:
                continue
            elif entry['layout'] in exclude_set:
                continue
            elif key == 'Stretch':
                layout = entry['layout']
                self.layout[layout].addStretch(1)
                continue
            elif key == 'Separator':
                layout = entry['layout']
                separator = entry['separator']
                self.layout[layout].addWidget(separator)
                continue
            elif key == 'Path':
                tu.reduce_path_widget(exclude_set=exclude_set, content=entry['content'])
            elif key == 'Copy':
                tu.reduce_copy_entries(exclude_set=exclude_set, content=entry['content'])
            else:
                pass

            layout = entry['layout']
            plot_labels = ''
            plot_name = ''
            try:
                plot_name = layout.replace('Plot ', '')
                plot_labels = ti.get_dtype_dict()[
                    tu.get_function_dict()[plot_name]['typ']
                    ]
            except KeyError:
                pass

            # Create widget
            self.content[key] = entry['widget'](
                mount_worker=self.mount_worker,
                process_worker=self.process_worker,
                plot_worker_ctf=self.plot_worker_ctf,
                plot_worker_motion=self.plot_worker_motion,
                plot_worker_picking=self.plot_worker_picking,
                settings_folder=self.settings_folder,
                plot_labels=plot_labels,
                plot_name=plot_name,
                parent=self,
                **entry
                )

            if isinstance(self.content[key], TabDocker):
                tab_list.append(key)
            else:
                pass

            if layout in tab_list:
                self.content[layout].add_tab(self.content[key], key)
                self.content[key].setObjectName('tabbed')
            else:
                self.layout[layout].addWidget(
                    self.content[key]
                    )

            if key == 'Button':
                self.content[key].sig_load.connect(self.load)
                self.content[key].sig_save.connect(self.save)
                self.content[key].sig_start.connect(self.start)
                self.content[key].sig_stop.connect(self.stop_dialog)
                self.content[key].sig_monitor_start.connect(lambda: self.monitor(start=True))
                self.content[key].sig_monitor_stop.connect(lambda: self.monitor(start=False))
                self.content[key].sig_check_quota.connect(self.check_quota)
            else:
                pass

            if key == 'Notification_widget':
                self.content[key].update_telegram()
                self.content[key].update_email()
                self.content[key].update()
                self.content[key].sig_stop.connect(self.stop)
                timer = QTimer(self)
                timer.setInterval(20000)
                timer.timeout.connect(self.content[key].get_telegram_messages)
                timer.start()
            else:
                pass

            if key == 'Plot per micrograph' or \
                    key == 'Plot histogram' or \
                    key == 'Show images':
                self.content[key].worker.sig_data.connect(
                    self.content[key].update_figure
                    )
                self.content[key].sig_update_done.connect(self.content[key].worker.reset_running)
                self.content[key].worker.sig_visible.connect(
                    self.content[key].set_visibility
                    )
            else:
                pass

        return error_list

    def check_quota(self):
        """
        Check the quota for the project and scratch directory.

        Arguments:
        None

        Return:
        None
        """
        general_settings = self.content['General'].get_settings()
        notification_settings = self.content['Notification'].get_settings()
        global_settings = {
            'General': general_settings[0],
            'Notification': notification_settings[0]
            }
        self.mount_worker.sig_set_settings.emit(global_settings)

    def load(self, file_name=None):
        """
        Load settings from settings file.

        Arguments:
        file_name - Name of the file (default None)

        Return:
        None
        """
        if file_name is None:
            file_name = QFileDialog.getOpenFileName(
                caption='Load settings',
                directory=self.path,
                options=QFileDialog.DontUseNativeDialog
                )

            if QT_VERSION == 4:
                file_name = file_name
            elif QT_VERSION == 5:
                file_name = file_name[0]
            else:
                raise ImportError('QT version unknown! Please contact the transphire authors!')

            if not file_name:
                return
            else:
                pass

        if file_name.endswith('.txt'):
            pass
        elif os.path.exists(file_name):
            pass
        else:
            file_name = '{0}.txt'.format(file_name)


        settings = []
        with open(file_name, 'r') as read:
            for line in read:
                line = line.replace('\n', '')
                key, *value = line.split('\t')
                if isinstance(value, list):
                    settings.append([key, *value])
                else:
                    settings.append([key, value])

        settings = self.settings_to_dict(settings=settings)
        self.set_settings(settings=settings)

    def set_settings(self, settings):
        """
        Load settings from settings file.

        Arguments:
        settings - Settings as dictionary.

        Return:
        None
        """
        for key in settings:
            if key == 'End':
                continue
            else:
                try:
                    self.content[key].set_settings(settings[key])
                except KeyError:
                    print('Key', key, 'no longer exists')
                    continue

    @staticmethod
    def settings_to_dict(settings):
        """
        Make the settings readable for the widgets set settings method.

        Arguments:
        settings - Settings as dictionary.

        Return:
        None
        """
        settings_dict = {}
        idx = -1
        while idx < len(settings)-1:
            idx += 1
            if settings[idx][0] == '###':
                key = settings[idx][1]
                if key == 'Frames':
                    settings_dict[key] = []
                else:
                    settings_dict[key] = {}
                continue

            if len(settings[idx]) == 1:
                settings[idx].append('')

            if key == 'Frames':
                setting = {}
                setting[settings[idx][0]] = settings[idx][1]
                for i in range(3):
                    idx += 1
                    setting[settings[idx][0]] = settings[idx][1]
                settings_dict[key].append(setting)
            else:
                if key == 'Notification_widget':
                    settings_dict[key].update({settings[idx][0]: [
                        settings[idx][1],
                        settings[idx][2]
                        ]})
                else:
                    settings_dict[key].update({
                        settings[idx][0]: settings[idx][1]
                        })

        return settings_dict

    def save(self, file_name=None, temp=False):
        """
        Save GUI status to file.

        Arguments:
        file_name - File name to save settings to.
        temp - File is a temporary save file.

        Return:
        True, if saving was succesful.
        """
        if file_name is None:
            file_name = QFileDialog.getSaveFileName(
                caption='Save settings',
                directory=self.path,
                options=QFileDialog.DontUseNativeDialog,
                filter="Text files (*.txt)"
                )

            if QT_VERSION == 4:
                file_name = file_name
            elif QT_VERSION == 5:
                file_name = file_name[0]
            else:
                raise ImportError('QT version unknown! Please contact the transphire authors!')

            if not file_name:
                return None
            else:
                pass
        else:
            pass

        if file_name.endswith('.txt'):
            pass
        else:
            file_name = '{0}.txt'.format(file_name)

        # Do not override settings
        if os.path.exists(file_name):
            old_filename = file_name
            for number in range(9999):
                file_name = '{0}_{1}'.format(old_filename, number)
                if os.path.exists(file_name):
                    continue
                else:
                    break
        else:
            pass

        error = False
        with open(file_name, 'w') as write:
            for key in self.content:
                if key == 'Mount':
                    continue
                else:
                    pass
                try:
                    settings = self.content[key].get_settings()
                except AttributeError:
                    continue
                if settings is not None:
                    write.write('###\t{0}\n'.format(key))
                    for entry in settings:
                        for key_entry in entry:
                            write.write(
                                '{0}\t{1}\n'.format(key_entry, entry[key_entry])
                                )
                else:
                    error = True
                    message = 'Setting of {0} not valid!'.format(key)
                    tu.message(message)
                    continue
            write.write('###\tEnd\n')
            write.write('The\tEnd\n')

        message_pass = 'Valid settings saved to {0}'.format(file_name)
        message_error = 'Invalid setting detected! Saveing failed!'
        if error:
            os.remove(file_name)
            tu.message(message_error)
            print(message_error)
            return False
        else:
            if temp:
                pass
            else:
                tu.message(message_pass)
            print(message_pass)
            return True

    def monitor(self, start):
        """
        Start the TranSPHIRE monitor processing.

        Arguments:
        start - True if start, False if stop

        Returns:
        None
        """
        self.enable(False)
        self.content['Button'].start_monitor_button.setEnabled(False)
        self.content['Button'].stop_monitor_button.setEnabled(False)

        self.plot_worker_ctf.sig_reset_list.emit()
        self.plot_worker_motion.sig_reset_list.emit()
        self.plot_worker_picking.sig_reset_list.emit()
        if start:
            settings = self.get_start_settings(monitor=True)
            if settings is None:
                tu.message('Please fill non emtpy entries.')
                self.enable(True)
                self.content['Button'].start_monitor_button.setEnabled(True)
                start = False
            elif not os.path.exists(settings['project_folder']):
                tu.message('Project folder does not exists. Cannot monitor session.')
                self.enable(True)
                self.content['Button'].start_monitor_button.setEnabled(True)
                start = False
            else:
                self.process_worker.sig_start.emit(settings)
                self.content['Button'].start_button.setEnabled(False)
                self.content['Button'].stop_button.setEnabled(False)
        else:
            self.process_worker.stop = True

        if start:
            self.content['Button'].start_monitor_button.setVisible(False)
            self.content['Button'].stop_monitor_button.setVisible(True)
            self.content['Button'].stop_monitor_button.setEnabled(True)
        else:
            pass

    @pyqtSlot()
    def get_start_settings(self, monitor=False):
        """
        Start TranSPHIRE processing.

        Arguments:
        None

        Return:
        None
        """
        self.enable(False)
        settings = {}
        settings['Monitor'] = monitor
        # Load settings to pass them to the working threads
        error_list = []
        check_list = [
            'General',
            'Notification'
            ]
        for setting in self.content['Copy'].get_settings():
            for value in setting.values():
                if isinstance(value, str) and value not in ('False', 'Later', 'True'):
                    check_list.append(value)
        for key in self.content:
            try:
                settings_widget = self.content[key].get_settings()
            except AttributeError:
                continue
            else:
                settings[key] = {}

            if settings_widget is None:
                self.enable(True)
                return None
            elif key == 'Frames':
                settings_motion = {}
            else:
                pass

            if key == 'Frames':
                skip_name_list = []
            else:
                skip_name_list = tu.get_function_dict()[key]['allow_empty']

            for entry in settings_widget:
                if key in check_list:
                    for name in entry:
                        if not entry[name] and name not in skip_name_list:
                            error_list.append(
                                '{0}:{1} is not allowed to be empty!'.format(
                                    key,
                                    name
                                    )
                                )
                        else:
                            pass
                else:
                    pass

            for idx, entry in enumerate(settings_widget):
                if key == 'Frames':
                    settings_motion[idx] = entry
                else:
                    settings[key].update(entry)

            if key == 'Frames':
                settings['motion_frames'] = settings_motion
            else:
                pass

        if error_list:
            tu.message('\n'.join(error_list))
            self.enable(True)
            return None
        else:
            pass

        # Get mount information
        for key in settings['Mount']:
            device_name = key.replace(' ', '_')
            save_file = os.path.join(self.settings_folder, device_name)
            try:
                with open(save_file, 'r') as read:
                    lines = read.readlines()
            except FileNotFoundError:
                continue
            for line in lines:
                name = line.split('\t')[0]
                settings['user_{0}'.format(device_name)] = name
        settings['user_Later'] = None

        if not re.match(
                self.project_name_pattern,
                settings['General']['Project name']
                ):
            self.enable(True)
            tu.message(
                'Project name needs to match pattern:\n{0}\n For example: {1}'.format(
                    self.project_name_pattern,
                    self.project_name_pattern_example
                    )
                )
            return None
        else:
            pass

        # Project folder names
        settings['project_folder'] = os.path.join(
            settings['General']['Project directory'],
            settings['General']['Project name']
            )
        settings['compress_folder'] = os.path.join(
            settings['General']['Project directory'],
            settings['General']['Project name']
            )
        settings['motion_folder'] = os.path.join(
            settings['General']['Project directory'],
            settings['General']['Project name']
            )
        settings['ctf_folder'] = os.path.join(
            settings['General']['Project directory'],
            settings['General']['Project name']
            )
        settings['picking_folder'] = os.path.join(
            settings['General']['Project directory'],
            settings['General']['Project name']
            )
        settings['scratch_folder'] = os.path.join(
            settings['General']['Scratch directory'],
            settings['General']['Project name']
            )
        settings['Copy_hdd_folder'] = self.mount_directory
        settings['Copy_backup_folder'] = self.mount_directory
        settings['Copy_work_folder'] = self.mount_directory
        settings['settings_folder'] = os.path.join(
            settings['project_folder'],
            'settings'
            )
        settings['queue_folder'] = os.path.join(
            settings['project_folder'],
            'queue'
            )
        settings['error_folder'] = os.path.join(
            settings['project_folder'],
            'error'
            )
        settings['tar_folder'] = os.path.join(
            settings['project_folder'], 'tar_folder'
            )
        return settings

    @pyqtSlot()
    def start(self):
        settings = self.get_start_settings()

        # Check for continue mode
        if settings is None:
            tu.message('Please fill non emtpy entries.')
            result = False
        elif os.path.exists(settings['project_folder']):
            result = self.continue_dialog(
                text1='Output project folder already exists!',
                text2='Do you really want to continue the old run?\nType: YES!'
                )
            #if result:
            #    result_session = self.continue_dialog(
            #        text1='Software metafiles',
            #        text2='Software metafiles (Atlas, ...) might be already copied!\n' + \
            #            'Do you want to copy them again?\nType: YES!'
            #        )
            #    settings['Copy_software_meta'] = bool(result_session)
            #else:
            #    settings['Copy_software_meta'] = True
        else:
            result = True

        # Start or stop procedure
        if result:
            # Create project and settings folder
            for name in [
                    'project_folder', 'settings_folder',
                    'scratch_folder', 'queue_folder', 'error_folder', 'tar_folder',
                    ]:
                try:
                    tu.mkdir_p(settings[name])
                except FileNotFoundError:
                    tu.message('Project name cannot be empty')
                    self.enable(True)
                    return None

            self.content['Button'].start_button.setVisible(False)
            self.content['Button'].start_button.setEnabled(False)
            self.content['Button'].stop_button.setVisible(True)
            self.content['Button'].stop_button.setEnabled(True)
            self.content['Button'].start_monitor_button.setEnabled(False)
            self.content['Button'].stop_monitor_button.setEnabled(False)
            self.plot_worker_ctf.reset_list()
            self.plot_worker_motion.reset_list()
            self.plot_worker_picking.reset_list()
            self.process_worker.sig_start.emit(settings)
            self.mount_worker.set_settings(settings=settings)
            self.save(
                file_name=os.path.join(
                    settings['settings_folder'],
                    settings['General']['Project name']
                    )
                )
            self.save_temp_settings()
        else:
            tu.message('Input needs to be "YES!" to work')
            self.enable(True)

    def continue_dialog(self, text1, text2):
        """
        Check if the user wants to run the continue mode.

        Arguments:
        text1 - Dialog window name.
        text2 - Text of the dialog.

        Return:
        True, if the input is YES!
        """
        dialog = InputBox(is_password=False, parent=self)
        dialog.setText(text1, text2)
        result = dialog.exec_()

        if result:
            text = dialog.getText()
            return bool(text == 'YES!')
        else:
            return False

    @pyqtSlot()
    def stop_dialog(self):
        """
        Check if the user really wants to stop the process.

        Arguments:
        None

        Return:
        None
        """
        result = self.continue_dialog(
            text1='Do you really want to stop?',
            text2='Do you really want to stop!\nType: YES!'
            )
        if result:
            self.stop()
        else:
            tu.message('Input needs to be "YES!" to work')

    @pyqtSlot()
    def stop(self):
        """
        Stop the process.

        Arguments:
        None

        Return:
        None
        """
        self.process_worker.stop = True
        self.content['Button'].start_monitor_button.setEnabled(False)
        self.content['Button'].stop_monitor_button.setEnabled(False)
        self.content['Button'].start_button.setEnabled(False)
        self.content['Button'].stop_button.setEnabled(False)

    @pyqtSlot()
    def _finished(self):
        """
        Rename the Stop Button to start and enable everything.

        Arguments:
        None

        Return:
        None
        """
        self.content['Button'].stop_button.setVisible(False)
        self.content['Button'].start_button.setVisible(True)
        self.content['Button'].start_button.setEnabled(True)
        self.content['Button'].stop_button.setEnabled(False)

        self.content['Button'].stop_monitor_button.setVisible(False)
        self.content['Button'].start_monitor_button.setVisible(True)
        self.content['Button'].start_monitor_button.setEnabled(True)
        self.content['Button'].stop_monitor_button.setEnabled(False)
        self.enable(True)

    @pyqtSlot(bool)
    def enable(self, var, use_all=False):
        """Enable or disable widgets

        Arguments:
        var - Enable status of the widgets.
        use_all - Disable/Enable everything (Default False)

        Return:
        None
        """
        for key in self.content:
            try:
                self.content[key].enable(var=var, use_all=use_all)
            except AttributeError:
                continue

    def closeEvent(self, event):
        """
        Quit threads before close and check if the process is still running

        Arguments:
        event - QCloseEvent.

        Return:
        None
        """
        if self.content['Button'].stop_button.isVisible() or \
                self.content['Button'].stop_monitor_button.isVisible():
            event.ignore()
            tu.message('First stop the program before closing')
            return None
        elif not self.save_temp_settings():
            result = tu.question(
                head='Error saving file!',
                text='Wrong setting detected! Quit without saving?',
                )
            # Result is true if the answer is Yes
            if result:
                pass
            else:
                event.ignore()
                return None
        else:
            pass

        self.thread_plot_ctf.stop = True
        self.thread_plot_picking.stop = True
        self.thread_plot_motion.stop = True

        self.timer_ctf.stop()
        self.timer_motion.stop()
        self.timer_picking.stop()

        self.thread_mount.quit()
        self.thread_process.quit()
        self.thread_plot_ctf.quit()
        self.thread_plot_motion.quit()
        self.thread_plot_picking.quit()

        print('Wait for thread mount')
        self.thread_mount.wait()
        print('Wait for thread process')
        self.thread_process.wait()
        print('Wait for thread ctf')
        self.thread_plot_ctf.wait()
        print('Wait for thread motion')
        self.thread_plot_motion.wait()
        print('Wait for thread picking')
        self.thread_plot_picking.wait()

        print('Wait for thread mount')
        for key in self.content['Mount'].content:
            thread = self.mount_thread_list[key]['thread']
            calculator = self.mount_thread_list[key]['object']
            calculator.kill_thread = True
            thread.quit()
            thread.wait()
        print('Bye Bye')
        super(MainWindow, self).closeEvent(event)
