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
import subprocess
import json
import numpy as np
import datetime
import re
import shutil
import os
import glob
from PyQt5.QtWidgets import QVBoxLayout, QLabel, QPushButton, QWidget, QLineEdit, QHBoxLayout, QComboBox, QScrollArea, QSpacerItem, QWidgetItem, QCheckBox
from PyQt5.QtGui import QIcon
from PyQt5.QtCore import pyqtSlot, Qt, QSize, pyqtSignal

from . import transphire_utils as tu


class SelectDialog(QWidget):
    """
    Show a message box with an input field.

    Inherits:
    QDialog

    Signals:
    None
    """
    sig_start = pyqtSignal(object)
    sig_new_config = pyqtSignal(str, str)

    def __init__(self, *args, parent=None, **kwargs):
        """
        Initialise layout of the widget.

        Arguments:
        regex - Regularexpression to analyse
        parent - Parent widget

        Returns:
        None
        """
        super(SelectDialog, self).__init__(parent)
        self.columns = 10
        self.settings = None
        self.content = []
        self.widgets_dict = {}
        self.widgets = []
        self.neutral_name = 'neutral'
        self.bad_name = 'bad'
        self.good_name = 'good'
        self.input_name = 'input_files'
        self.model_name = 'model.h5'
        self.config_name = 'config.json'
        self.default_project_name = 'Project'
        self.model_out = None
        self.config_out = None
        self.current_index = 0
        self.layouts = {}
        self.labels = {}
        self.button_dict = {}

        self.current_model = None

        self.log_folder = None
        self.good_folder = None
        self.bad_folder = None
        self.classes_folder = None
        self.settings_file = None
        self.e2proc2d_exec = None
        self.sp_cinderella_train_exec = None
        self.sp_cinderella_predict_exec = None
        self.set_enable = None

        layout = QVBoxLayout(self)
        layout_h0 = QHBoxLayout()
        layout.addLayout(layout_h0)
        layout_h1 = QHBoxLayout()
        layout.addLayout(layout_h1)
        layout_h2 = QHBoxLayout()
        layout.addLayout(layout_h2)
        layout_h3 = QHBoxLayout()
        layout.addLayout(layout_h3)

        btn_done = QPushButton('Retrain', self)
        btn_done.clicked.connect(self.retrain)
        layout_h3.addWidget(btn_done)
        self.content.append(btn_done)

        layout_h3.addStretch(1)

        label_threshold = QLabel('Threshold', self)
        layout_h3.addWidget(label_threshold)
        self.content.append(label_threshold)

        self.threshold_repick = QLineEdit('0.5', self)
        layout_h3.addWidget(self.threshold_repick)
        self.content.append(self.threshold_repick)

        self.button_repick = QPushButton('Repick', self)
        self.button_repick.clicked.connect(self.repick)
        layout_h3.addWidget(self.button_repick)
        self.content.append(self.button_repick)

        btn = QPushButton('Set', self)
        btn.clicked.connect(self.set_settings)
        layout_h3.addWidget(btn)
        self.content.append(btn)

        self.edit = QLineEdit(str(self.columns), self)
        self.edit.editingFinished.connect(self.adjust_all_layouts)
        layout_h0.addWidget(QLabel('Columns:', self))
        layout_h0.addWidget(self.edit)
        self.content.append(self.edit)

        self.combo_text = QComboBox(self)
        self.combo_text.setSizeAdjustPolicy(QComboBox.AdjustToContents)
        self.combo_text.currentTextChanged.connect(self.set_current_folder)
        layout_h0.addWidget(self.combo_text)
        self.content.append(self.combo_text)

        self.btn_update = QPushButton('Update', self)
        self.btn_update.clicked.connect(self.start_retrain)
        layout_h0.addWidget(self.btn_update)
        self.content.append(self.btn_update)

        self.prefer_isac_checkbox = QCheckBox('Prefer ISAC', self)
        self.prefer_isac_checkbox.setToolTip('If Project is selected, prefer ISAC over Cinderella runs. This will put all classes in the neutral position')
        layout_h0.addWidget(self.prefer_isac_checkbox)
        self.content.append(self.prefer_isac_checkbox)

        for current_name in (self.good_name, self.neutral_name, self.bad_name):
            self.labels[current_name] = QLabel(current_name, self)
            self.widgets_dict[current_name] = []
            layout_h1.addWidget(self.labels[current_name])

            widget = QWidget(self)
            scroll_area = QScrollArea(self)
            scroll_area.setWidgetResizable(True)
            scroll_area.setWidget(widget)
            scroll_area.setHorizontalScrollBarPolicy( Qt.ScrollBarAlwaysOn )
            scroll_area.setVerticalScrollBarPolicy( Qt.ScrollBarAlwaysOn)

            self.layouts[current_name] = QVBoxLayout(widget)
            self.layouts[current_name].setSpacing(2)
            self.layouts[current_name].addStretch(1)
            layout_h2.addWidget(scroll_area)

        self.sig_start.connect(self.start_retrain)
        self.adjust_all_layouts()
        self.enable(False)

    @pyqtSlot()
    def set_settings(self):
        try:
            name, threshold = self.combo_text.currentText().rsplit('_', 1)
        except ValueError:
            tu.message('Please provide a repicking run and not {}.'.format(self.default_project_name))
            return
        model = os.path.join(self.log_folder, name, self.model_name)
        self.sig_new_config.emit(model, threshold)
        tu.message('Set model: {}\nSet threshold: {}'.format(model, threshold))

    def enable(self, var, use_all=None):
        if not self.set_enable and var and self.set_enable is not None:
            var = False
        for entry in self.content:
            entry.setEnabled(var)

        if var:
            var = False
            if self.combo_text.currentText() == self.default_project_name:
                var = True
            self.btn_update.setEnabled(var)
            self.prefer_isac_checkbox.setEnabled(var)

    @pyqtSlot(str)
    @pyqtSlot()
    def set_current_folder(self, text=None):
        if text is None:
            text = self.combo_text.currentText()

        var = False
        if text == self.default_project_name:
            var = True
        self.btn_update.setEnabled(var)
        self.prefer_isac_checkbox.setEnabled(var)
        self.start_retrain(input_folder=text)

    def add_combo_item(self, items):
        current_items = [self.combo_text.itemText(idx) for idx in range(self.combo_text.count())]
        current_items.extend(items)
        prev_state = self.combo_text.blockSignals(True)
        self.combo_text.clear()
        self.combo_text.addItems(sorted(list(set(current_items))))
        self.combo_text.blockSignals(prev_state)

    @pyqtSlot(object)
    @pyqtSlot()
    def start_retrain(self, settings=None, input_folder=None):
        if settings is not None:
            self.settings = settings
            file_names = [
                os.path.basename(entry)
                for entry in
                glob.glob(os.path.join(self.settings['log_folder'], 'Retrain', 'RUN_*.*'))
                ]
            self.add_combo_item([self.default_project_name])
            self.add_combo_item(file_names)
        self.clear()
        self.project_folder = self.settings['project_folder']
        self.log_folder = os.path.join(self.settings['log_folder'], 'Retrain')
        self.classes_folder = os.path.join(self.log_folder, 'RUN_{0}')
        self.model_out = os.path.join(self.classes_folder, self.model_name)
        self.config_out = os.path.join(self.classes_folder, self.config_name)

        self.good_folder = os.path.join(self.classes_folder, self.good_name)
        self.bad_folder = os.path.join(self.classes_folder, self.bad_name)

        self.settings_file = os.path.join(self.log_folder, 'tmp_settings.json')
        self.e2proc2d_exec = self.settings['Path']['e2proc2d.py']
        self.sp_cinderella_train_exec = self.settings['Path']['sp_cinderella_train.py']
        try:
            self.sp_cinderella_predict_exec = self.settings['Path'][self.settings['Copy']['Select2d']]
        except KeyError:
            print('In order to use the retrain tool, please provide a program in Copy->Select2d and press: Monitor Start -> Monitor Stop')
            self.set_enable = False
            return
        else:
            self.set_enable = True

        for folder_name in (
                self.log_folder,
                ):
            tu.mkdir_p(folder_name)

        class_2d_folder = []
        select_2d_folder = []
        if input_folder is None or input_folder == self.default_project_name:
            for key in self.settings:
                if key.startswith('scratch_'):
                    continue
                if 'class2d' in key.lower():
                    try:
                        class_2d_folder.extend([
                            entry
                            for entry in
                            glob.glob(
                                os.path.join(
                                    self.settings[key],
                                    '*',
                                    )
                                )
                            if os.path.isdir(entry) and not
                            os.path.basename(entry).startswith('jpg') and not
                            os.path.basename(entry).startswith('overview_plots')
                            ])
                    except IndexError:
                        pass
                elif 'select2d' in key.lower():
                    try:
                        select_2d_folder.extend([
                            entry
                            for entry in
                            glob.glob(
                                os.path.join(
                                    self.settings[key],
                                    '*',
                                    )
                                )
                            if os.path.isdir(entry) and not
                            os.path.basename(entry).startswith('jpg') and not
                            os.path.basename(entry).startswith('overview_plots')
                            ])
                    except IndexError:
                        pass

            if self.prefer_isac_checkbox.isChecked():
                select_basenames = tuple([os.path.basename(entry) for entry in class_2d_folder])
                for entry in select_2d_folder[:]:
                    if os.path.basename(entry) in select_basenames:
                        select_2d_folder.remove(entry)
            else:
                select_basenames = tuple([os.path.basename(entry) for entry in select_2d_folder])
                for entry in class_2d_folder[:]:
                    if os.path.basename(entry) in select_basenames:
                        class_2d_folder.remove(entry)
        else:
            select_2d_folder.append(os.path.join(self.log_folder, input_folder))

        self.fill(class_2d_folder)
        self.fill(select_2d_folder, cinderella=True)
        for label_name in self.labels:
            for idx in reversed(range(self.current_index, len(self.widgets))):
                button = self.widgets[idx]
                self.widgets.remove(button)
                button.setParent(None)
        self.adjust_all_layouts()

    def fill(self, folder, cinderella=False):
        if cinderella:
            labels = (self.good_name,self.bad_name)
        else:
            labels = (self.neutral_name,)

        button_dict = {}
        for sub_folder in folder:
            for label_name in labels:
                suffix = '_{}'.format(label_name) if cinderella else ''
                for file_name in sorted(glob.glob(os.path.join(sub_folder, 'png{}'.format(suffix), '*'))):
                    match = re.search('/([^/]*)-(\d*)\.+png', file_name)
                    if match is None:
                        continue
                    class_id = int(match.group(2))-1
                    class_averages = os.path.join(sub_folder, '' if cinderella else 'ISAC2', match.group(1))
                    try:
                        button = self.widgets[self.current_index]
                        button.isac_class_averages = class_averages
                        button.isac_class_id = class_id
                        button.current_layout = label_name
                    except KeyError:
                        button = MyPushButton(label_name, class_averages, class_id, self)
                        button.sig_click.connect(self.handle_change)
                        self.widgets.append(button)
                    except IndexError:
                        button = MyPushButton(label_name, class_averages, class_id, self)
                        button.sig_click.connect(self.handle_change)
                        self.widgets.append(button)
                    button.setIconSize(QSize(50, 50))
                    button.setToolTip('Class averages: {}\nClass id: {}'.format(class_averages, class_id))
                    button.setIcon(QIcon(file_name))
                    button.setStyleSheet('QPushButton {color: rgba(0, 0, 0 ,0); background-color: rgba(0, 0, 0, 0); border: 0px; border-color: rgba(0, 0, 0, 0); min-width: 50px; max-width: 50px; min-height: 50px; max-height: 50px}')
                    button_dict.setdefault(
                        class_averages,
                        []
                        ).append(button)
                    self.current_index += 1

        try:
            with open(self.settings_file, 'r') as read:
                self.button_dict = json.load(read)
        except FileNotFoundError:
            pass

        for file_name, buttons in button_dict.items():
            try:
                update = os.path.getmtime(file_name) < os.path.getmtime(self.settings_file)
            except FileNotFoundError:
                update = False

            for button in buttons:
                if update:
                    try:
                        button.current_layout = self.button_dict[self.combo_text.currentText()][file_name][str(button.isac_class_id)]
                    except KeyError:
                        pass
                self.add_to_layout(
                    button.current_layout,
                    just_add=button,
                    )

    @pyqtSlot(object, object)
    def handle_change(self, sender, event):
        if sender.current_layout == self.neutral_name:
            if event.button() == Qt.LeftButton:
                self.switch_layout(sender, self.good_name)

            elif event.button() == Qt.RightButton:
                self.switch_layout(sender, self.bad_name)
        else:
            self.switch_layout(sender, self.neutral_name)

    @pyqtSlot()
    def adjust_all_layouts(self):
        try:
            self.columns = int(self.edit.text())
        except Exception as e:
            print(e)
            self.edit.setText(str(self.columns))
            return
        for name in self.layouts:
            self.add_to_layout(name)

    def add_to_layout(self, layout_name, add=None, remove=None, clear=False, just_add=None):
        if just_add:
            self.widgets_dict[layout_name].append(just_add)
            self.layouts[layout_name].addWidget(just_add)
            return

        layout_count = self.layouts[layout_name].count()
        for i in reversed(range(layout_count)):
            item = self.layouts[layout_name].itemAt(i)
            if isinstance(item, QSpacerItem):
                self.layouts[layout_name].removeItem(item)
            elif isinstance(item, QWidgetItem):
                self.layouts[layout_name].removeItem(item)
                #if clear:
                #    item.widget().setParent(None)
            elif isinstance(item, QHBoxLayout):
                for j in reversed(range(item.count())):
                    item_j = item.itemAt(j)
                    if isinstance(item_j, QSpacerItem):
                        item.removeItem(item_j)
                        continue
                    elif isinstance(item_j, QWidgetItem):
                        pass
                        #if clear:
                        #    item_j.widget().setParent(None)
                    elif item_j is None:
                        pass
                    else:
                        assert False, item_j
                self.layouts[layout_name].removeItem(item)
            else:
                assert False, item

        if clear:
            self.widgets_dict[layout_name] = []
            self.current_index = 0
            return
        if remove is not None:
            self.widgets_dict[layout_name].remove(remove)
        if add is not None:
            self.widgets_dict[layout_name].append(add)

        self.labels[layout_name].setText(
            '{}: {}'.format(layout_name, len(self.widgets_dict[layout_name]))
            )
        a = np.array(
            [
                (entry.isac_class_averages, entry.isac_class_id)
                for entry in self.widgets_dict[layout_name]
                ],
            dtype='U5000,i8'
            )
        indices = np.argsort(a, order=['f0', 'f1'])
        self.widgets_dict[layout_name] = np.array(
            self.widgets_dict[layout_name], dtype=np.object
            )[indices].tolist()

        layout = None
        for i in range(len(self.widgets_dict[layout_name])):
            i_hor = i % self.columns
            if i_hor == 0:
                if layout is not None:
                    layout.addStretch(1)
                layout = QHBoxLayout()
                self.layouts[layout_name].addLayout(layout)

            layout.addWidget(self.widgets_dict[layout_name][i])
            self.button_dict.setdefault(
                self.combo_text.currentText(), {}
                ).setdefault(
                    self.widgets_dict[layout_name][i].isac_class_averages,
                    {}
                    )[str(self.widgets_dict[layout_name][i].isac_class_id)] = layout_name

        if layout is not None:
            layout.addStretch(1)
        self.layouts[layout_name].addStretch(1)

        if self.widgets_dict[layout_name]:
            with open(self.settings_file, 'w') as write:
                json.dump(self.button_dict, write, indent=1)
        return self.widgets_dict[layout_name]

    def clear(self):
        for name in self.layouts:
            self.add_to_layout(name, clear=True)

    def switch_layout(self, sender, layout_name):
        self.add_to_layout(sender.current_layout, remove=sender)
        self.add_to_layout(layout_name, add=sender)
        sender.current_layout = layout_name

    @pyqtSlot()
    def retrain(self):
        time_string = datetime.datetime.now().strftime('%Y_%m_%d_%H_%M_%S')
        classes_folder = self.classes_folder.format(time_string)
        good_folder = self.good_folder.format(time_string)
        bad_folder = self.bad_folder.format(time_string)
        model_out = self.model_out.format(time_string)
        config_out = self.config_out.format(time_string)

        original_folder = os.path.join(classes_folder, self.input_name)
        tu.mkdir_p(original_folder)

        self.current_model = model_out

        config_file = os.path.join(
            os.path.dirname(__file__),
            'templates',
            'cinderella_config.json'
            )
        with open(config_file, 'r') as read:
            content = read.read()
        content = content.replace('XXXGOODXXX', good_folder)
        content = content.replace('XXXBADXXX', bad_folder)
        content = content.replace('XXXMODELXXX', model_out)
        with open(config_out, 'w') as write:
            write.write(content)

        for current_name, out_dir_classes in (
                (self.bad_name, bad_folder),
                (self.good_name, good_folder)
                ):
            os.makedirs(out_dir_classes, exist_ok=True)
            index_dict = {}
            widgets = self.add_to_layout(current_name)
            for widget in widgets:
                index_dict.setdefault(widget.isac_class_averages, []).append(
                    widget.isac_class_id
                    )
            for file_name, index_list in index_dict.items():
                out_filename = file_name.replace(self.log_folder, '').replace(self.project_folder, '').replace('/', '_')
                out_symlink = os.path.join(original_folder, out_filename)
                print(out_filename)
                print(out_symlink)
                if not os.path.islink(out_symlink):
                    tu.symlink_rel(file_name, out_symlink)

                out_file = os.path.join(
                    classes_folder,
                    '{}_{}_list.txt'.format(out_filename, current_name)
                    )
                with open(out_file, 'w') as write:
                    write.write('\n'.join(map(str, index_list)))
                cmd = '{} {} {} --list={}'.format(
                    self.e2proc2d_exec,
                    file_name,
                    os.path.join(
                        out_dir_classes,
                        out_filename
                        ),
                    out_file
                    )
                print('Execute:', cmd)
                try:
                    subprocess.call(cmd.split())
                except Exception as e:
                    print(e)
        cmd = '{} -c {}'.format(self.sp_cinderella_train_exec, config_out)
        print('Execute:', cmd)
        try:
            idx = subprocess.call(cmd.split())
        except Exception as e:
            print(e)
        else:
            if not idx:
                self.repick(time_string)

    @pyqtSlot()
    def repick(self, time_string=None):
        try:
            if time_string is None:
                classes_folder = os.path.join(self.log_folder, self.combo_text.currentText().rsplit('_', 1)[0])
            else:
                classes_folder = self.classes_folder.format(time_string)
        except ValueError:
            tu.message('Could not find model for current entry: {}.\nPlease provide a repicking run as starting point.'.format(self.combo_text.currentText()))
            return

        if not os.path.isdir(classes_folder):
            print(classes_folder)
            tu.message('Could not find model for current combo: {}.\nPlease provide a repicking run as starting point.'.format(self.combo_text.currentText()))
            return

        original_folder = os.path.join(classes_folder, self.input_name)
        model_out = os.path.join(classes_folder, self.model_name)
        threshold = float(self.threshold_repick.text())
        output_folder = '{}_{}'.format(classes_folder, threshold)

        if not os.path.isfile(model_out):
            print(classes_folder)
            tu.message('Could not find model for current combo: {}.\nPlease provide a repicking run as starting point.'.format(self.combo_text.currentText()))
            return

        try:
            shutil.rmtree(output_folder)
        except Exception:
            pass

        cmd = '{} -i {} -o {} -w {} -t {}'.format(
            self.sp_cinderella_predict_exec,
            original_folder,
            output_folder,
            model_out,
            threshold,
            )
        print('Execute:', cmd)
        try:
            subprocess.call(cmd.split())
        except Exception as e:
            print(e)

        for entry in glob.glob(os.path.join(output_folder, '*.txt')):
            if not entry.endswith('_index_confidence.txt'):
                continue

            file_name = entry.rsplit('_index_confidence.txt', 1)[0]
            for suffix in ('_good', '_bad'):
                out_folder = os.path.join(output_folder, 'png{}'.format(suffix))
                in_file = '{}{}.hdf'.format(file_name, suffix)
                tu.mkdir_p(out_folder)
                cmd = '{} {} {} --outmode=uint16 --unstacking'.format(
                    self.e2proc2d_exec,
                    in_file,
                    os.path.join(
                        out_folder,
                        '{}.png'.format(os.path.basename(in_file))
                        ),
                    )
                print('Execute:', cmd)
                try:
                    subprocess.call(cmd.split())
                except Exception as e:
                    print(e)

        self.add_combo_item([os.path.basename(output_folder)])
        cur_text = self.combo_text.blockSignals(True)
        self.combo_text.setCurrentText(os.path.basename(output_folder))
        self.combo_text.blockSignals(cur_text)
        self.combo_text.currentTextChanged.emit(os.path.basename(output_folder))

    @pyqtSlot()
    def confirm(self):
        self.sig_new_config.emit(self.model_out, self.threshold)


class MyPushButton(QPushButton):
    sig_click = pyqtSignal(object, object)

    def __init__(self, layout, isac_file_name, isac_id, *args, **kwargs):
        super(MyPushButton, self).__init__(*args, **kwargs)
        self.isac_class_id = isac_id
        self.isac_class_averages = isac_file_name
        self.current_layout = layout

    def mousePressEvent(self, event):
        if event.button() in (Qt.RightButton, Qt.LeftButton):
            self.sig_click.emit(self, event)
