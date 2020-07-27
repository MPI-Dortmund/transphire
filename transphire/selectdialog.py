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
import os
import glob
from transphire import transphire_utils as tu
from PyQt5.QtWidgets import QDialog, QVBoxLayout, QLabel, QPushButton, QDialogButtonBox, QWidget, QLineEdit, QFileDialog, QCheckBox, QHBoxLayout, QComboBox, QScrollArea, QSpacerItem, QWidgetItem
from PyQt5.QtGui import QIcon
from PyQt5.QtCore import pyqtSlot, Qt, QSize, pyqtSignal


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
        self.widgets = {}
        self.neutral_name = 'neutral'
        self.bad_name = 'bad'
        self.good_name = 'good'
        self.input_name = 'input_files'
        self.model_name = 'model.h5'
        self.model_out = None
        self.layouts = {}
        self.labels = {}
        self.button_dict = {}

        self.time_string = None
        self.current_model = None

        self.log_folder = None
        self.good_folder = None
        self.bad_folder = None
        self.classes_folder = None
        self.settings_file = None
        self.e2proc2d_exec = None
        self.sp_cinderella_train_exec = None
        self.sp_cinderella_predict_exec = None

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

        self.edit = QLineEdit(str(self.columns), self)
        self.edit.editingFinished.connect(self.adjust_all_layouts)
        layout_h0.addWidget(QLabel('Columns:', self))
        layout_h0.addWidget(self.edit)
        btn_update = QPushButton('Update', self)
        btn_update.clicked.connect(self.start_retrain)
        layout_h0.addWidget(btn_update)

        for current_name in (self.good_name, self.neutral_name, self.bad_name):
            self.labels[current_name] = QLabel(current_name, self)
            self.widgets[current_name] = []
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

    def enable(self, var, use_all=None):
        for entry in self.content:
            entry.setEnabled(var)

    @pyqtSlot(object)
    @pyqtSlot()
    def start_retrain(self, settings=None):
        if settings is not None:
            self.settings = settings
        self.clear()
        self.log_folder = os.path.join(self.settings['log_folder'], 'Retrain')
        self.classes_folder = os.path.join(self.log_folder, '{0}')
        self.model_out = os.path.join(self.classes_folder, self.model_name)

        self.good_folder = os.path.join(self.classes_folder, self.good_name)
        self.bad_folder = os.path.join(self.classes_folder, self.bad_name)

        self.settings_file = os.path.join(self.log_folder, 'tmp_settings.json')
        self.e2proc2d_exec = self.settings['Path']['e2proc2d.py']
        self.sp_cinderella_train_exec = self.settings['Path']['sp_cinderella_train.py']
        self.sp_cinderella_predict_exec = self.settings['Path'][self.settings['Copy']['Select2d']]

        for folder_name in (
                self.log_folder,
                ):
            tu.mkdir_p(folder_name)

        class_2d_folder = []
        select_2d_folder = []
        for key in self.settings:
            if 'class2d' in key.lower():
                try:
                    class_2d_folder.append(
                        glob.glob(
                            os.path.join(
                                self.settings[key],
                                '*',
                                )
                            )[0]
                        )
                except IndexError:
                    pass
            elif 'select2d' in key.lower():
                try:
                    select_2d_folder.append(
                        glob.glob(
                            os.path.join(
                                self.settings[key],
                                '*',
                                )
                            )[0]
                        )
                except IndexError:
                    pass

        select_basenames = tuple([os.path.basename(entry) for entry in select_2d_folder])
        for entry in class_2d_folder[:]:
            if os.path.basename(entry) in select_basenames:
                class_2d_folder.remove(entry)

        self.fill(class_2d_folder)
        self.fill(select_2d_folder, cinderella=True)
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
                    class_id = int(re.search('(\d*)\.+png', file_name).group(1))-1
                    class_averages = os.path.join(sub_folder, '' if cinderella else 'ISAC2', 'ordered_class_averages{}.hdf'.format(suffix))
                    button = MyPushButton(label_name, class_averages, class_id, self)
                    button.setIconSize(QSize(50, 50))
                    button.setToolTip('Class averages: {}\nClass id: {}'.format(class_averages, class_id))
                    button.setIcon(QIcon(file_name))
                    button.setStyleSheet('QPushButton {color: rgba(0, 0, 0 ,0); background-color: rgba(0, 0, 0, 0); border: 0px; border-color: rgba(0, 0, 0, 0); min-width: 50px; max-width: 50px; min-height: 50px; max-height: 50px}')
                    button.sig_click.connect(self.handle_change)
                    button_dict.setdefault(class_averages, []).append(button)

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
                        button.current_layout = self.button_dict[file_name][str(button.isac_class_id)]
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
            self.widgets[layout_name].append(just_add)
            self.layouts[layout_name].addWidget(just_add)
            return

        layout_count = self.layouts[layout_name].count()
        for i in reversed(range(layout_count)):
            item = self.layouts[layout_name].itemAt(i)
            if isinstance(item, QSpacerItem):
                self.layouts[layout_name].removeItem(item)
            elif isinstance(item, QWidgetItem):
                self.layouts[layout_name].removeItem(item)
                if clear:
                    item.widget().setParent(None)
            elif isinstance(item, QHBoxLayout):
                for j in reversed(range(item.count())):
                    item_j = item.itemAt(j)
                    if isinstance(item_j, QSpacerItem):
                        item.removeItem(item_j)
                        continue
                    elif isinstance(item_j, QWidgetItem):
                        if clear:
                            item_j.widget().setParent(None)
                    elif item_j is None:
                        pass
                    else:
                        assert False, item_j
                self.layouts[layout_name].removeItem(item)
            else:
                assert False, item

        if clear:
            self.widgets[layout_name] = []
            return
        if remove is not None:
            self.widgets[layout_name].remove(remove)
        if add is not None:
            self.widgets[layout_name].append(add)

        self.labels[layout_name].setText('{}: {}'.format(layout_name, len(self.widgets[layout_name])))
        a = np.array([(entry.isac_class_averages, entry.isac_class_id) for entry in self.widgets[layout_name]], dtype='U200,i8')
        indices = np.argsort(a)
        self.widgets[layout_name] = np.array(self.widgets[layout_name], dtype=np.object)[indices].tolist()

        layout = None
        for i in range(len(self.widgets[layout_name])):
            i_hor = i % self.columns
            if i_hor == 0:
                if layout is not None:
                    layout.addStretch(1)
                layout = QHBoxLayout()
                self.layouts[layout_name].addLayout(layout)

            layout.addWidget(self.widgets[layout_name][i])
            self.button_dict.setdefault(self.widgets[layout_name][i].isac_class_averages, {})[str(self.widgets[layout_name][i].isac_class_id)] = layout_name

        if layout is not None:
            layout.addStretch(1)
        self.layouts[layout_name].addStretch(1)

        if self.widgets[layout_name]:
            with open(self.settings_file, 'w') as write:
                json.dump(self.button_dict, write, indent=1)
        return self.widgets[layout_name]

    def clear(self):
        for name in self.layouts:
            self.add_to_layout(name, clear=True)

    def switch_layout(self, sender, layout_name):
        self.add_to_layout(sender.current_layout, remove=sender)
        self.add_to_layout(layout_name, add=sender)
        sender.current_layout = layout_name

    @pyqtSlot()
    def retrain(self):
        self.time_string = datetime.datetime.now().strftime('%Y_%m_%d_%H_%M_%S')
        classes_folder = self.classes_folder.format(self.time_string)
        good_folder = self.good_folder.format(self.time_string)
        bad_folder = self.bad_folder.format(self.time_string)
        model_out = self.model_out.format(self.time_string)

        original_folder = os.path.join(classes_folder, self.input_name)
        tu.mkdir_p(original_folder)

        self.current_model = model_out

        config_file = os.path.join(
            os.path.dirname(__file__),
            'templates',
            'cinderella_config.json'
            )
        config_out = os.path.realpath(
            os.path.join(self.log_folder, 'config.json')
            )
        with open(config_file, 'r') as read:
            content = read.read()
        content = content.replace('XXXGOODXXX', good_folder)
        content = content.replace('XXXBADXXX', bad_folder)
        content = content.replace('XXXMODELXXX', model_out)
        with open(config_out, 'w') as write:
            write.write(content)

        for current_name, out_dir_classes in ((self.bad_name, bad_folder), (self.good_name, good_folder)):
            os.makedirs(out_dir_classes, exist_ok=True)
            index_dict = {}
            widgets = self.add_to_layout(current_name)
            for widget in widgets:
                index_dict.setdefault(widget.isac_class_averages, []).append(
                    widget.isac_class_id
                    )
            for file_name, index_list in index_dict.items():
                out_symlink = os.path.join(original_folder, file_name.replace('/', '_'))
                if not os.path.islink(out_symlink):
                    tu.symlink_rel(file_name, out_symlink)

                out_file = os.path.join(
                    classes_folder,
                    '{}_{}_list.txt'.format(file_name.replace('/', '_'), current_name)
                    )
                with open(out_file, 'w') as write:
                    write.write('\n'.join(map(str, index_list)))
                cmd = '{} {} {} --list={}'.format(
                    self.e2proc2d_exec,
                    file_name,
                    os.path.join(
                        out_dir_classes,
                        file_name.replace('/', '_')
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
                self.repick()

    @pyqtSlot()
    def repick(self):
        print('repick')

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

