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
import numpy as np
import json
import datetime
import sys
import os
import re
import copy
import shutil
import pexpect as pe
from PyQt5.QtWidgets import (
    QMainWindow,
    QHBoxLayout,
    QVBoxLayout,
    QWidget,
    QFileDialog,
    )
from PyQt5.QtCore import QThread, pyqtSlot, QCoreApplication, QTimer, pyqtSignal

from . import transphire_utils as tu
from . import transphire_import as ti

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
    sig_reset = pyqtSignal(str, object)

    def __init__(
            self, content_raw, content_gui, content_pipeline, settings_folder,
            mount_directory, template_name, version, n_feedbacks, parent=None
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
        self.path = os.getcwd()

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
        self.content_raw = content_raw
        self.content_pipeline=content_pipeline
        self.layout = None
        self.n_feedbacks = n_feedbacks
        function_dict = tu.get_function_dict()
        self.default_types = ['mount', 'process', 'plotting']
        self.types = self.default_types[:]
        for value in function_dict.values():
            if value['typ'] is not None and value['typ'] not in self.types:
                #self.types.append(value['typ'])
                for index in range(self.n_feedbacks+1):
                    self.types.append('{0}_feedback_{1}'.format(value['typ'], index))

        # Settings folder
        self.settings_folder = settings_folder
        self.project_settings_folder = os.path.join(
            settings_folder,
            'PROJECT_SETTINGS'
            )
        try:
            tu.mkdir_p(self.project_settings_folder)
        except PermissionError:
            print('Settings directory is not writable.')
        self.mount_directory = mount_directory
        self.template_name = template_name
        self.temp_save = '{0}/temp_save_{1}'.format(
            self.settings_folder,
            os.uname()[1].replace(' ', '_')
            )

        # Threads
        self.mount_calculation_ssh = None
        self.mount_calculation_get = None
        self.mount_calculation_df = None
        self.timers = {}
        self.workers = {}
        self.threads = {}
        for entry in self.types:
            self.workers[entry] = None
            self.threads[entry] = None
            self.timers[entry] = None
        self.mount_thread_list = None

        self.sig_reset.connect(self.reset_gui)
        self.sig_reset.emit(template_name, None)

    def start_threads(self, content_pipeline):
        """
        Start threads used in TranSPHIRE.

        Arguments:
        content_pipeline - Content used to start processing threads.

        Return:
        None
        """
        # Stop threads if already started.
        for entry in self.types:
            if self.workers[entry] is not None:
                self.workers[entry].setParent(None)

            if self.threads[entry] is not None:
                self.threads[entry].quit()
                self.threads[entry].wait()
                self.threads[entry].setParent(None)

            if self.timers[entry] is not None:
                self.timers[entry].setParent(None)

        if self.mount_thread_list is not None:
            for setting in self.content['Mount'].get_settings():
                for key in setting:
                    thread = self.mount_thread_list[key]['thread']
                    calculator = self.mount_thread_list[key]['object']
                    calculator.kill_thread = True
                    thread.quit()
                    thread.wait()

        for entry in self.types:
            # Create objects used in threads
            if entry == 'mount':
                self.workers[entry] = MountWorker(
                    password=self.password,
                    settings_folder=self.settings_folder,
                    mount_directory=self.mount_directory
                    )
            elif entry == 'process':
                self.workers[entry] = ProcessWorker(
                    password=self.password,
                    content_process=content_pipeline,
                    mount_directory=self.mount_directory
                    )
            elif entry == 'plotting':
                self.workers[entry] = PlotWorker()
            else:
                self.workers[entry] = None

            if entry in self.default_types:
                # Create threads
                self.threads[entry] = QThread(self)
                # Start threads
                self.threads[entry].start()

                # Start objects in threads
                self.workers[entry].moveToThread(self.threads[entry])
            else:
                self.threads[entry] = None

    @pyqtSlot(str, object)
    def reset_gui(self, template_name, load_file):
        """
        Reset the content of the mainwindow.

        Arguments:
        template_name - Name of the template to load
        load_file - Settings file (default None).

        Return:
        None
        """
        self.template_name = template_name
        content_pipeline = self.content_pipeline
        content_gui = tu.get_content_gui(
            content=self.content_raw,
            template_name=template_name,
            n_feedbacks=self.n_feedbacks,
            )
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
        if load_file is not None and load_file:
            self.load(file_name=load_file)
            os.remove(load_file)
        elif os.path.exists('{0}.txt'.format(self.temp_save)) and load_file is None:
            # Result is True if answer is Yes
            result = tu.question(
                head='Restore default values.',
                text='Restore default values?',
                )
            if not result:
                self.load(file_name=self.temp_save)
            else:
                pass
        else:
            pass
        self.workers['mount'].sig_load_save.emit()

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
        value = self.save(file_name=self.temp_save, temp=True, interactive=True)
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

        self.workers['process'].sig_finished.connect(self._finished)
        self.workers['process'].signal_plot.connect(self.workers['plotting'].set_settings)
        self.workers['plotting'].sig_set_visual.connect(self.set_visualisation)

        self.timers['plotting'] = QTimer(self)
        self.timers['plotting'].setInterval(20000)
        self.timers['plotting'].setSingleShot(True)
        self.timers['plotting'].timeout.connect(self.workers['plotting'].sig_calculate.emit)
        self.workers['plotting'].sig_new_round.connect(self.new_round_plot)

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
            self.workers['mount'].sig_calculate_ssh_quota.connect(
                mount_calculator.calculate_ssh_quota
                )
            self.workers['mount'].sig_calculate_df_quota.connect(
                mount_calculator.calculate_df_quota
                )
            self.workers['mount'].sig_calculate_get_quota.connect(
                mount_calculator.calculate_get_quota
                )
        self.content['Mount'].set_threadlist(thread_list=self.mount_thread_list)

    @pyqtSlot()
    def set_visualisation(self):
        self.content['TAB1'].setCurrentIndex(0)
        self.content['TAB1'].setCurrentIndex(3)

    @pyqtSlot()
    def new_round_plot(self):
        self.timers['plotting'].start()

    def abort_finished(self, *args, **kwargs):
        """
        Set the mount worker abort variable to True.

        Arguments:
        None

        Return:
        None
        """
        self.workers['mount'].abort_finished = True

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
        for entry in content_gui:
            if entry['name'] == 'Path':
                exclude_set = tu.get_exclude_set_path(content=entry['content'])
                tu.reduce_path_widget(exclude_set=exclude_set, content=entry['content'])
        for entry in content_gui:
            if entry['name'] == 'Copy':
                tu.reduce_copy_entries(exclude_set=exclude_set, content=entry['content'])
        error_list = []
        tab_list = []
        global_dict = {}
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
            else:
                pass

            layout = entry['layout']
            plot_labels = ''
            plot_name = ''
            try:
                plot_name = layout.replace('Plot ', '')
                if 'feedback' in plot_name:
                    plot_name_labels = plot_name[:-len(' feedback 1')]
                else:
                    plot_name_labels = plot_name
                plot_labels = ti.get_dtype_dict()[
                    tu.get_function_dict()[plot_name_labels]['typ']
                    ]
            except KeyError:
                pass

            # Create widget
            self.content[key] = entry['widget'](
                mount_worker=self.workers['mount'],
                process_worker=self.workers['process'],
                plot_worker=self.workers['plotting'],
                settings_folder=self.settings_folder,
                template_name=self.template_name,
                plot_labels=plot_labels,
                plot_name=plot_name,
                parent=self,
                global_dict=global_dict,
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

            if key.startswith('Cinderella'):
                self.content['Retrain'].sig_new_config.connect(
                    self.content[key].set_new_model
                    )

            if key == 'Copy':
                self.content[key].sig_adjust_tab.connect(self.hide_tab)

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
                self.content[key].worker.sig_reset.connect(
                    self.content[key].reset_plot
                    )
                self.content[key].worker.sig_visible.connect(
                    self.content[key].set_visibility
                    )
            else:
                pass
        self.content['Global'].set_global(global_dict)
        for key in self.content:
            try:
                self.content[key].sig_change_use_movie.connect(self.content['Global'].emit_global)
            except AttributeError:
                pass
        self.content['Copy'].emit_signals()

        return error_list

    @pyqtSlot(object, str)
    def hide_tab(self, sender, text):
        current_key = sender.parent().name
        try:
            for idx, widget in reversed(list(enumerate(self.content[current_key].widgets))):
                if text in ('Later', 'False'):
                    val = True
                else:
                    val = text == widget.name
                index = self.content[current_key].indexOf(widget)
                self.content[current_key].setTabEnabled(index, val)
                if val:
                    self.content[current_key].setCurrentIndex(index)
            self.content[current_key].order_tabs()
        except KeyError:
            pass

    def check_quota(self):
        """
        Check the quota for the project and scratch directory.

        Arguments:
        None

        Return:
        None
        """
        general_settings = self.content['Output'].get_settings()
        notification_settings = self.content['Notification'].get_settings()
        global_settings = {
            'Output': general_settings[0],
            'Notification': notification_settings[0]
            }
        self.workers['mount'].sig_set_settings.emit(global_settings)

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

            file_name = file_name[0]

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

    def set_design(self, settings):
        """
        Load settings from settings file.

        Arguments:
        settings - Settings as dictionary.

        Return:
        None
        """
        for key in settings:
            try:
                self.content[key].set_design(settings[key])
            except KeyError:
                try: # This block has been introduced for backwards compatibility changes.
                    new_key = key.replace(' v', ' >=v')
                    self.content[new_key].set_design(settings[key])
                except KeyError:
                    print('Key', key, 'no longer exists')
                    continue
            except AttributeError:
                pass

    def set_settings(self, settings):
        """
        Load settings from settings file.

        Arguments:
        settings - Settings as dictionary.

        Return:
        None
        """
        keys = list(settings.keys())

        # Move Global to the very end if available to let the dependencies work properly
        try:
            keys.append(keys.pop(keys.index('Global')))
        except ValueError:
            pass
        for key in keys:
            if key in ('End',):
                continue
            else:
                try:
                    self.content[key].set_settings(settings[key])
                except KeyError:
                    try: # This block has been introduced for backwards compatibility changes.
                        new_key = key.replace(' v', ' >=v')
                        self.content[new_key].set_settings(settings[key])
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
        key = None
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

            if key is None:
                continue
            elif key == 'Frames':
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

    def save(self, file_name=None, temp=False, interactive=False, do_message=True):
        """
        Save GUI status to file.

        Arguments:
        file_name - File name to save settings to.
        temp - File is a temporary save file.

        Return:
        True, if saving was succesful.
        """
        if file_name is None:
            interactive = True
            file_name = QFileDialog.getSaveFileName(
                caption='Save settings',
                directory=self.path,
                options=QFileDialog.DontUseNativeDialog,
                filter="Text files (*.txt)"
                )

            file_name = file_name[0]

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
        if interactive:
            pass
        else:
            old_filename, old_ext = os.path.splitext(file_name)
            for number in range(9999):
                file_name = '{0}_{1:05d}{2}'.format(old_filename, number, old_ext)
                if os.path.exists(file_name):
                    continue
                else:
                    break

        error = False
        try:
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
                                if key_entry == 'SSH password':
                                    continue
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
        except Exception as e:
            error = False
            tu.message('Failed to save settings: {0}'.format(e))
        else:
            message_pass = 'Valid settings saved to {0}'.format(file_name)
            message_error = 'Invalid setting detected! Saveing failed!'
            if do_message:
                if error:
                    os.remove(file_name)
                    tu.message(message_error)
                    print(message_error)
                    return False
                else:
                    print(message_pass)
                    if temp:
                        pass
                    else:
                        tu.message(message_pass)
                    return file_name
            else:
                if error:
                    return False, message_error
                else:
                    return file_name, message_pass

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

        if start:
            self.workers['plotting'].sig_reset_list.emit()
            settings, _, _ = self.get_start_settings(monitor=True)
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
                self.workers['process'].sig_start.emit(settings, {})
                self.content['Button'].start_button.setEnabled(False)
                self.content['Button'].stop_button.setEnabled(False)
        else:
            self.workers['process'].stop = True

        if start:
            self.content['Button'].start_monitor_button.setVisible(False)
            self.content['Button'].stop_monitor_button.setVisible(True)
            self.content['Button'].stop_monitor_button.setEnabled(True)
            self.content['Retrain'].sig_start.emit(copy.deepcopy(settings))

    def _extract_settings(self, key, settings, error_list, check_list, external_files):
        try:
            settings_widget = self.content[key].get_settings()
        except AttributeError:
            return
        else:
            settings[key] = {}

        try:
            input_file_names = self.content[key].get_input_names()
        except AttributeError:
            input_file_names = []

        if settings_widget is None:
            self.enable(True)
            error_list.append('{0} needs to have problems fixed!'.format(key))
            return None
        elif key == 'Frames':
            settings_motion = {}
        else:
            pass

        if key == 'Frames':
            skip_name_list = []
        else:
            skip_name_list = tu.get_function_dict()[key]['allow_empty']

        non_global_names_with_global = {}
        for entry in settings_widget:
            for name in sorted(list(entry.keys())):
                if name.endswith('_global'):
                    if entry[name][0] is not None and entry[name][1] and key != 'Global':
                        non_global_names_with_global[entry[name][0]] = name.split('_global')[0]
                    del entry[name]
                    continue

                if key in check_list:
                    if name == 'Number of feedbacks' and int(entry[name]) > self.n_feedbacks:
                        error_list.append(
                            '{0}:{1} is not allowed to be larger than the specified number: {2}!\nCheck the start settings of TranSPHIRE in case you want more feedbacks!'.format(
                                key,
                                name,
                                self.n_feedbacks
                                )
                            )
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

        for global_key, local_key in non_global_names_with_global.items():
            if global_key == 'GPU':
                for entry in settings_widget:
                    try:
                        gpu_splits = int(entry['GPU SPLIT'][0])
                    except KeyError:
                        gpu_splits = 0

                    if gpu_splits != 0:
                        new_gpu = []
                        for i in range(gpu_splits):
                            for gpu_idx in entry[local_key].split():
                                new_gpu.append('{}_{}'.format(gpu_idx, i))
                        entry[local_key] = ' '.join(new_gpu)
                    try:
                        del entry['GPU SPLIT']
                    except KeyError:
                        pass

        for local_key in input_file_names:
            external_files.setdefault(key, {})[local_key] = {}

        for idx, entry in enumerate(settings_widget):
            if key == 'Frames':
                settings_motion[idx] = entry
            else:
                settings[key].update(entry)

        if key == 'Frames':
            settings['motion_frames'] = settings_motion
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
            'Output',
            'Notification'
            ]
        first_round = ['Global']
        for setting in self.content['Copy'].get_settings():
            for value in setting.values():
                if isinstance(value, str) and value not in ('False', 'Later', 'True'):
                    check_list.append(value)

        external_files = {}
        for key in first_round:
            self._extract_settings('Global', settings, error_list, check_list, external_files)
        for key in self.content:
            if key in first_round:
                continue
            self._extract_settings(key, settings, error_list, check_list, external_files)

        settings['motion_frames'] = {
            '0': {
                'first': 1,
                'last': -1,
                'dw': True,
                'default': True
                }
            }
        if error_list and not monitor:
            tu.message('\n'.join(error_list))
            self.enable(True)
            return None, None, None
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
                settings['Output']['Project name']
                ) and not monitor:
            self.enable(True)
            tu.message(
                'Project name needs to match pattern:\n{0}\n For example: {1}'.format(
                    self.project_name_pattern,
                    self.project_name_pattern_example
                    )
                )
            return None, None, None
        else:
            pass

        # Project folder names
        settings['project_base'] = os.path.join(
            settings['Output']['Project directory'],
            settings['Output']['Project name']
            )
        if not os.path.exists(settings['project_base']) and monitor:
            self.enable(True)
            tu.message('Project needs to exists in order to start Monitor mode')
            return None, None, None

        settings['project_folder'] = os.path.join(
            settings['project_base'],
            'TranSPHIRE_results'
            )

        settings['scratch_folder'] = os.path.join(
            settings['Output']['Scratch directory'],
            settings['Output']['Project name'],
            'TranSPHIRE_results'
            )
        folder_dict = {
            'log_folder': 'XXX_Log_files',
            'queue_folder': 'XXX_Queue_files',
            'error_folder': 'XXX_Error_files',
            'tar_folder': 'XXX_Tar_file_folder',
            'stack_folder': '000_Import',
            'meta_folder': '000_Import_meta',
            'set_folder_raw': 'XXX_Settings',
            'restart_backup_folder': 'XXX_Restart_Backup',
            'software_meta_folder': '000_Session_meta',
            }
        for key, value in folder_dict.items():
            settings[key] = os.path.join(
                settings['project_folder'],
                value
                )

        continue_mode = os.path.exists(settings['restart_backup_folder'])

        settings['do_feedback_loop'] = int(settings['Output']['Number of feedbacks'])
        settings['feedback_file'] = os.path.join(settings['log_folder'], 'feedback_log')
        settings['spot_file'] = os.path.join(settings['log_folder'], 'spot_dict.txt')
        settings['data_frame'] = os.path.join(settings['project_folder'], 'data_frame.csv')
        settings['external_log'] = os.path.join(settings['set_folder_raw'], 'external_files.json')
        settings['translation_file'] = os.path.join(settings['project_folder'], 'Valid_micrographs_info.txt')
        settings['translation_file_bad'] = os.path.join(settings['project_folder'], 'Discarded_micrographs_info.txt')

        settings['current_set'] = datetime.datetime.now().strftime('%Y_%m_%d_%H_%M_%S')

        settings['restart_backup_folder'] = os.path.join(settings['restart_backup_folder'], settings['current_set'])
        settings['set_folder'] = os.path.join(settings['set_folder_raw'], settings['current_set'])
        folder_dict['set_folder'] = settings['set_folder']
        folder_dict['restart_backup_folder'] = settings['restart_backup_folder']

        # Move Error files from previous run
        if continue_mode:
            tu.mkdir_p(settings['restart_backup_folder'])
            try:
                tu.copy(
                    settings['error_folder'],
                    settings['restart_backup_folder'],
                    )
                shutil.rmtree(settings['error_folder'])
            except FileNotFoundError:
                pass
            # Copy Queue files from previous run
            try:
                tu.copy(
                    settings['queue_folder'],
                    settings['restart_backup_folder'],
                    )
            except FileNotFoundError:
                pass

        names = [
            entry.replace('_entries', '')
            for entry in settings['Copy']
            if entry.endswith('_entries') and
            entry.replace('_entries', '').replace('_', ' ') in settings['Copy']
            ]
        idx = 0
        settings['plot_emit'] = []
        for entry in names:
            base_dir2 = None
            no_feedback = False
            if 'copy_to_' in entry.lower():
                base_dir = self.mount_directory
                no_feedback = True
            else:
                idx += 1
                base_dir = settings['project_folder']
                base_dir2 = settings['scratch_folder']

            entry_name = '{}_entries'.format(entry)
            prog_name_entries = settings['Copy'][entry_name] if entry_name in settings['Copy'] else [entry]
            for prog_name in prog_name_entries:
                if 'copy_to_' in entry.lower():
                    folder_name = prog_name.replace(' ', '_').replace('>=', '')
                else:
                    folder_name = '{0:03d}_{1}'.format(idx, prog_name.replace(' ', '_').replace('>=', ''))

                for index in range(int(settings['Output']['Number of feedbacks']) + 1):
                    if index == 0:
                        folder_name_tmp = folder_name
                    elif no_feedback:
                        continue
                    else:
                        folder_name_tmp = os.path.join(
                            '000_Feedback_results',
                            '{0}_feedback_{1}'.format(
                                folder_name,
                                int(settings['Output']['Number of feedbacks']) - index + 1
                                )
                            )

                    folder_setting_name = '{0}_folder_feedback_{1}'.format(entry.lower(), index)
                    folder_setting = os.path.join(base_dir, folder_name_tmp)
                    prog_name_feedback = '{} feedback {}'.format(prog_name, int(settings['Output']['Number of feedbacks']) - index + 1) if index != 0 else prog_name
                    settings['plot_emit'].append([prog_name, prog_name_feedback, entry, folder_setting])

                    if prog_name == settings['Copy'][entry.replace('_', ' ')]:
                        settings[folder_setting_name] = folder_setting
                        if base_dir2 is not None:
                            settings['scratch_{0}_folder_feedback_{1}'.format(entry.lower(), index)] = os.path.join(
                                base_dir2,
                                folder_name_tmp
                                )

        return settings, folder_dict, external_files

    @pyqtSlot()
    def start(self):
        settings, folder_dict, external_files = self.get_start_settings()

        # Check for continue mode
        if settings is None:
            return None
        elif os.path.exists(settings['project_folder']):
            result, restart_dict = self.continue_dialog(
                text1='Output project folder already exists!',
                text2='Do you really want to continue the old run?\nType: "YES!"',
                is_restart=True,
                settings=settings,
                )
        else:
            result = True
            restart_dict = {}

        # Start or stop procedure
        if result:
            # Create project and settings folder
            folder_names = ['project_folder', 'scratch_folder']
            folder_names.extend(list(folder_dict.keys()))
            for name in folder_names:
                try:
                    tu.mkdir_p(settings[name])
                except PermissionError as e:
                    print(e)
                    tu.message('You do not have permission to write to your specified project directory! Check the Terminal for the actual error message!')
                    self.enable(True)
                    return None
                except FileNotFoundError as e:
                    print(e)
                    tu.message('Project name cannot be empty! Check the Terminal for the actual error message!')
                    self.enable(True)
                    return None

            for key, local_dict in external_files.items():
                if key in ('Path', 'Compress cmd'):
                    continue
                for local_key, value in local_dict.items():
                    if settings[key][local_key]:
                        value['old_file'] = settings[key][local_key]
                        value['new_file'] = os.path.join(
                            settings['set_folder'],
                            os.path.basename(value['old_file'])
                            )
                        try:
                            tu.copy(value['old_file'], value['new_file'])
                        except FileNotFoundError:
                            tu.message("Input file {} not available!".format(value['old_file']))
                            self.enable(True)
                            return None
                        settings[key][local_key] = 'external_log|||{}'.format(local_key)

            try:
                with open(settings['external_log'], 'r') as read:
                    current_data = json.load(read)
            except FileNotFoundError:
                current_data = {}
            current_data[settings['current_set']] = external_files
            with open(settings['external_log'], 'w') as write:
                json.dump(current_data, write, indent=1)

            self.content['Button'].start_button.setVisible(False)
            self.content['Button'].start_button.setEnabled(False)
            self.content['Button'].stop_button.setVisible(True)
            self.content['Button'].stop_button.setEnabled(True)
            self.content['Button'].start_monitor_button.setEnabled(False)
            self.content['Button'].stop_monitor_button.setEnabled(False)
            self.workers['plotting'].sig_reset_list.emit()
            _, message = self.save(
                file_name=os.path.join(
                    settings['set_folder'],
                    settings['Output']['Project name']
                    ),
                do_message=False
                )
            _, message = self.save(
                file_name=os.path.join(
                    self.project_settings_folder,
                    settings['Output']['Project name']
                    ),
                do_message=False
                )
            with open(os.path.join(settings['set_folder'], 'used_settings.json'), 'w') as write:
                json.dump(settings, write, indent=1)
            settings_copy = copy.deepcopy(settings)
            self.workers['process'].sig_start.emit(settings, restart_dict)
            self.workers['mount'].set_settings(settings=settings_copy)
            self.save_temp_settings()
            tu.message(message)
            self.content['Retrain'].sig_start.emit(settings_copy)
        else:
            tu.message('Input needs to be "YES!" to work')
            self.enable(True)

    def continue_dialog(self, text1, text2, is_stop=False, is_restart=False, settings=None):
        """
        Check if the user wants to run the continue mode.

        Arguments:
        text1 - Dialog window name.
        text2 - Text of the dialog.

        Return:
        True, if the input is YES!
        """
        if is_restart:
            restart_names = tu.get_unique_types()
        else:
            restart_names = np.array([])
        dialog = InputBox(
            is_password=False,
            parent=self,
            is_stop=is_stop,
            restart_names=restart_names,
            settings=settings,
            )
        dialog.setText(text1, text2)
        result = dialog.exec_()

        text = dialog.getText()
        if result and is_restart:
            return bool(text == 'YES!'), dialog.get_restart_dict()
        elif result and is_stop:
            return bool(text == 'YES!'), dialog.abort.isChecked()
        elif result:
            return bool(text == 'YES!')
        elif is_restart:
            return False, {}
        elif is_stop:
            return False, False
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
        result, abort = self.continue_dialog(
            text1='Do you really want to stop?',
            text2='Do you really want to stop!\nType: "YES!"',
            is_stop=True,
            )
        if result:
            self.stop(abort=abort)
        else:
            tu.message('Input needs to be "YES!" to work')

    @pyqtSlot()
    def stop(self, abort=False):
        """
        Stop the process.

        Arguments:
        None

        Return:
        None
        """
        if abort:
            self.workers['process'].abort = True
        if self.workers['process'].stop == False:
            self.workers['process'].stop = True
            self.content['Button'].start_monitor_button.setEnabled(False)
            self.content['Button'].stop_monitor_button.setEnabled(False)
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

        for entry in self.types:
            if self.threads[entry] is not None:
                self.threads[entry].stop = True

                if entry not in self.default_types:
                    self.timers[entry].stop()

        print('Wait for threads to exit.')
        for thread_instance in self.threads.values():
            if thread_instance is not None:
                thread_instance.quit()
                thread_instance.wait()

        print('Wait for thread mount')
        for key in self.content['Mount'].content:
            thread = self.mount_thread_list[key]['thread']
            calculator = self.mount_thread_list[key]['object']
            calculator.kill_thread = True
            thread.quit()
            thread.wait()
        print('Bye Bye')
        super(MainWindow, self).closeEvent(event)

# Objects
from .mountworker import MountWorker
from .processworker import ProcessWorker
from .inputbox import InputBox
from .plotworker import PlotWorker
from .separator import Separator
from .tabdocker import TabDocker
from .mountcalculator import MountCalculator
