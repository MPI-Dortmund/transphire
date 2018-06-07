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
try:
    QT_VERSION = 4
    from PyQt4.QtGui import (
        QMainWindow,
        QHBoxLayout,
        QVBoxLayout,
        QWidget,
        QFileDialog,
        QInputDialog,
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
        QInputDialog,
        )
    from PyQt5.QtCore import QThread, pyqtSlot, QCoreApplication, QTimer

# Objects
from transphire.mountworker import MountWorker
from transphire.processworker import ProcessWorker
from transphire.sudopassworddialog import SudoPasswordDialog
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
            if content['name'] == 'Status':
                for entry in content['content']:
                    for widget in entry:
                        for key in widget:
                            if key == 'Mount/umount needs sudo password?':
                                if widget[key][0] == 'True':
                                    need_sudo_password = True
                                else:
                                    pass
                            else:
                                pass
            elif content['name'] == 'Mount':
                for entry in content['content_mount']:
                    for widget in entry:
                        for key in widget:
                            if key == 'Need sudo for copy?':
                                if widget[key][0] == 'True':
                                    need_sudo_password = True
                                else:
                                    pass
                            else:
                                pass
            else:
                pass

        if need_sudo_password:
            dialog = SudoPasswordDialog(self)
            dialog.exec_()
            if not dialog.result():
                QCoreApplication.instance().quit()
                sys.exit()
            else:
                self.password = dialog.password
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
        self.central_widget = None
        self.content = None
        self.layout = None

        # Settings folder
        self.settings_folder = settings_folder
        self.mount_directory = mount_directory
        self.temp_save = '{0}/temp_save'.format(settings_folder)

        # Threads
        self.mount_worker = None
        self.process_worker = None
        self.plot_worker = None
        self.mount_calculation_ssh = None
        self.mount_calculation_get = None
        self.mount_calculation_df = None
        self.thread_mount = None
        self.thread_process = None
        self.thread_plot = None
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
        if self.plot_worker is not None:
            self.plot_worker.setParent(None)
        if self.thread_mount is not None:
            self.thread_mount.quit()
            self.thread_mount.wait()
            self.thread_mount.setParent(None)
        if self.thread_process is not None:
            self.thread_process.quit()
            self.thread_process.wait()
            self.thread_process.setParent(None)
        if self.thread_plot is not None:
            self.thread_plot.quit()
            self.thread_plot.wait()
            self.thread_plot.setParent(None)
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
        self.plot_worker = PlotWorker()

        # Create threads
        self.thread_mount = QThread(self)
        self.thread_process = QThread(self)
        self.thread_plot = QThread(self)

        # Start threads
        self.thread_mount.start()
        self.thread_process.start()
        self.thread_plot.start()

        # Start objects in threads
        self.mount_worker.moveToThread(self.thread_mount)
        self.process_worker.moveToThread(self.thread_process)
        self.plot_worker.moveToThread(self.thread_plot)

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
            # Result is True if answer is No
            result = tu.question(
                head='Restore previous session.',
                text='Restore previous session?',
                parent=self
                )
            if result:
                pass
            else:
                self.load(file_name=self.temp_save)
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
        self.process_worker.sig_plot_ctf.connect(self.plot_worker.calculate_array_ctf)
        self.process_worker.sig_plot_motion.connect(self.plot_worker.calculate_array_motion)
        self.plot_worker.sig_message.connect(lambda msg: tu.message(msg))

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
        if self.central_widget is not None:
            self.central_widget.setParent(None)
        else:
            pass

        self.central_widget = QWidget(self)
        self.central_widget.setObjectName('central')
        self.setCentralWidget(self.central_widget)

    def set_layout_structure(self):
        """
        Setup the layout structure for the central widget.

        Arguments:
        None

        Return:
        None
        """
        # Layout dictionary
        self.layout = {}
        self.layout['h1'] = QHBoxLayout(self.central_widget)
        self.layout['h2'] = QHBoxLayout()
        self.layout['h3'] = QHBoxLayout()
        self.layout['v'] = QVBoxLayout()

        # Layout architecture
        self.layout['h1'].addLayout(self.layout['v'], stretch=1)
        self.layout['v'].addLayout(self.layout['h2'], stretch=0)
        self.layout['v'].addWidget(
            Separator(typ='horizontal', color='grey'), stretch=0
            )
        self.layout['v'].addLayout(self.layout['h3'], stretch=1)

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
                plot_worker=self.plot_worker,
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
            else:
                self.layout[layout].addWidget(
                    self.content[key]
                    )

            if key == 'Button':
                self.content[key].sig_load.connect(self.load)
                self.content[key].sig_save.connect(self.save)
                self.content[key].sig_start.connect(self.start)
                self.content[key].sig_stop.connect(self.stop_dialog)
                self.content[key].sig_check_quota.connect(self.check_quota)
            else:
                pass

            if key == 'Notification':
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

            if key == 'Plot per micrograph' or key == 'Plot histogram':
                self.plot_worker.sig_data.connect(
                    self.content[key].update_figure
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
        global_settings = self.content['General'].get_settings()
        global_settings = {'General': global_settings[0]}
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
                if key == 'Notification':
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

    @pyqtSlot()
    def start(self):
        """
        Start TranSPHIRE processing.

        Arguments:
        None

        Return:
        None
        """
        self.enable(False)
        settings = {}
        # Load settings to pass them to the working threads
        error_list = []
        skip_list = [
            'Mount',
            'Notification',
            'Path',
            'Frames'
            ]
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
                if key not in skip_list:
                    for name in entry:
                        if not entry[name] and name not in skip_name_list:
                            error_list.append(
                                '{0}:{1} is not allowed to be emtpy!'.format(
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

        # Check for continue mode
        if os.path.exists(settings['project_folder']):
            result = self.continue_dialog(
                text1='Output project folder already exists!',
                text2='Do you really want to continue the old run?\nType: YES!'
                )
            if result:
                result_session = self.continue_dialog(
                    text1='Software metafiles',
                    text2='Software metafiles (Atlas, ...) might be already copied!\n' + \
                        'Do you want to copy them again?\nType: YES!'
                    )
                settings['Copy_software_meta'] = bool(result_session)
            else:
                settings['Copy_software_meta'] = True
        else:
            settings['Copy_software_meta'] = True
            result = True

        # Create project and settings folder
        for name in [
                'project_folder', 'settings_folder',
                'scratch_folder', 'queue_folder', 'error_folder'
                ]:
            try:
                tu.mkdir_p(settings[name])
            except FileNotFoundError:
                tu.message('Project name cannot be empty')
                self.enable(True)
                return None

        # Start or stop procedure
        if result:
            self.content['Button'].start_button.setText('Stop')
            self.plot_worker.settings = settings
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
        dialog = QInputDialog(self)
        result = dialog.getText(self, text1, text2)
        return bool(result[0] == 'YES!')

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
        self.content['Button'].start_button.setEnabled(False)

    @pyqtSlot()
    def _finished(self):
        """
        Rename the Stop Button to start and enable everything.

        Arguments:
        None

        Return:
        None
        """
        self.enable(True)
        self.content['Button'].start_button.setText('Start')
        self.content['Button'].start_button.setEnabled(True)

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
        if self.content['Button'].start_button.text() == 'Stop':
            event.ignore()
            tu.message('First stop the program before closing')
            return None
        elif not self.save_temp_settings():
            result = tu.question(
                head='Error saving file!',
                text='Wrong setting detected! Quit without saving?',
                )
            # Result is true if the answer is No
            if not result:
                pass
            else:
                event.ignore()
                return None
        else:
            pass

        self.thread_mount.quit()
        self.thread_mount.wait()
        self.thread_process.quit()
        self.thread_process.wait()
        self.thread_plot.quit()
        self.thread_plot.wait()
        for key in self.content['Mount'].content:
            thread = self.mount_thread_list[key]['thread']
            calculator = self.mount_thread_list[key]['object']
            calculator.kill_thread = True
            thread.quit()
            thread.wait()
        message = 'Bye Bye'
        print(message)
        super(MainWindow, self).closeEvent(event)
