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
import re
import os
import glob
from PyQt5.QtWidgets import QDialog, QVBoxLayout, QLabel, QPushButton, QDialogButtonBox, QWidget, QLineEdit, QFileDialog, QCheckBox, QHBoxLayout, QComboBox, QScrollArea, QSpacerItem
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

    def __init__(self, transphire_isac, transphire_cind, parent=None):
        """
        Initialise layout of the widget.

        Arguments:
        regex - Regularexpression to analyse
        parent - Parent widget

        Returns:
        None
        """
        super(SelectDialog, self).__init__(parent)
        self.out_dir = 'OUT'
        self.e2proc2d_exec = '/opt/self_installed_programs/anaconda3/envs/sphire_local_deps14/bin/e2proc2d.py'
        self.sp_cinderella_exec = 'sp_cinderella_train.py'
        self.columns = 10

        layout = QVBoxLayout(self)
        layout_h0 = QHBoxLayout()
        layout.addLayout(layout_h0)
        layout_h1 = QHBoxLayout()
        layout.addLayout(layout_h1)
        layout_h2 = QHBoxLayout()
        layout.addLayout(layout_h2)
        btn_done = QPushButton('Retrain with given information', self)
        btn_done.clicked.connect(self.retrain)
        layout.addWidget(btn_done)

        self.layouts = {}
        self.labels = {}
        self.edit = QLineEdit(str(self.columns), self)
        self.edit.editingFinished.connect(self.adjust_all_layouts)
        layout_h0.addWidget(QLabel('Columns:', self))
        layout_h0.addWidget(self.edit)
        for i in ('bad', 'neutral', 'good'):
            self.labels[i] = QLabel(i, self)
            layout_h1.addWidget(self.labels[i])

            widget = QWidget(self)
            scroll_area = QScrollArea(self)
            scroll_area.setWidgetResizable(True)
            scroll_area.setWidget(widget)
            scroll_area.setHorizontalScrollBarPolicy( Qt.ScrollBarAlwaysOn )
            scroll_area.setVerticalScrollBarPolicy( Qt.ScrollBarAlwaysOn)

            self.layouts[i] = QVBoxLayout(widget)
            self.layouts[i].setSpacing(2)
            self.layouts[i].addStretch(1)
            layout_h2.addWidget(scroll_area)

        self.fill(transphire_isac)
        self.fill(transphire_cind, cinderella=True)

        #for sub_isac in transphire_isac:
        #    for file_name in sorted(glob.glob(os.path.join(sub_isac, 'png', '*'))):
        #        class_id = int(re.search('(\d*)\.\.png', file_name).group(1))-1
        #        class_averages = os.path.join(sub_isac, 'ISAC2', 'ordered_class_averages.hdf')
        #        button = MyPushButton(self.layouts, class_averages, class_id, self)
        #        button.setFixedSize(QSize(50, 50))
        #        button.setIconSize(QSize(50, 50))
        #        button.setToolTip('Class averages: {}\nClass id: {}'.format(class_averages, class_id))
        #        button.setIcon(QIcon(file_name))
        #        button.setStyleSheet('QPushButton {color: rgba(0, 0, 0 ,0); background-color: rgba(0, 0, 0, 0); border: 0px; border-color: rgba(0, 0, 0, 0)}')
        #        button.sig_click.connect(self.handle_change)
        #        self.add_to_layout(button.current_layout, add=button)

        #for sub_isac in transphire_cind:
        #    for i in ('good', 'bad'):
        #        for file_name in sorted(glob.glob(os.path.join(sub_isac, 'png_{}'.format(i), '*'))):
        #            class_id = int(re.search('(\d*)\.\.png', file_name).group(1))-1
        #            class_averages = os.path.join(sub_isac, 'ordered_class_averages_{}.hdf'.format(i))
        #            button = MyPushButton(self.layouts, class_averages, class_id, self)
        #            button.setFixedSize(QSize(50, 50))
        #            button.setIconSize(QSize(50, 50))
        #            button.setToolTip('Class averages: {}\nClass id: {}'.format(class_averages, class_id))
        #            button.setIcon(QIcon(file_name))
        #            button.setStyleSheet('QPushButton {color: rgba(0, 0, 0 ,0); background-color: rgba(0, 0, 0, 0); border: 0px; border-color: rgba(0, 0, 0, 0)}')
        #            button.sig_click.connect(self.handle_change)
        #            self.add_to_layout(i, add=button)

    def fill(self, folder, cinderella=False):
        if cinderella:
            labels = ('good', 'bad')
        else:
            labels = ('neutral',)

        for sub_folder in folder:
            for i in labels:
                suffix = '_{}'.format(i) if cinderella else ''
                for file_name in sorted(glob.glob(os.path.join(sub_folder, 'png{}'.format(suffix), '*'))):
                    class_id = int(re.search('(\d*)\.\.png', file_name).group(1))-1
                    class_averages = os.path.join(sub_folder, '' if cinderella else 'ISAC2', 'ordered_class_averages{}.hdf'.format(suffix))
                    button = MyPushButton(i, class_averages, class_id, self)
                    button.setFixedSize(QSize(50, 50))
                    button.setIconSize(QSize(50, 50))
                    button.setToolTip('Class averages: {}\nClass id: {}'.format(class_averages, class_id))
                    button.setIcon(QIcon(file_name))
                    button.setStyleSheet('QPushButton {color: rgba(0, 0, 0 ,0); background-color: rgba(0, 0, 0, 0); border: 0px; border-color: rgba(0, 0, 0, 0)}')
                    button.sig_click.connect(self.handle_change)
                    self.add_to_layout(i, add=button)

    @pyqtSlot(object, object)
    def handle_change(self, sender, event):
        if sender.current_layout == 'neutral':
            if event.button() == Qt.RightButton:
                self.switch_layout(sender, 'good')

            elif event.button() == Qt.LeftButton:
                self.switch_layout(sender, 'bad')
        else:
            self.switch_layout(sender, 'neutral')

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

    def add_to_layout(self, layout_name, add=None, remove=None, clear=False):
        layout_count = self.layouts[layout_name].count()
        widgets = []
        for i in reversed(range(layout_count)):
            item = self.layouts[layout_name].itemAt(i)
            if isinstance(item, QSpacerItem):
                self.layouts[layout_name].removeItem(item)
            elif isinstance(item, QHBoxLayout):
                for j in range(item.count()):
                    item_j = item.itemAt(j)
                    if isinstance(item_j, QSpacerItem):
                        item.removeItem(item_j)
                        continue
                    widgets.append(item_j.widget())
                self.layouts[layout_name].removeItem(item)
                item.setParent(None)
            else:
                assert False, item

        if clear:
            return

        if remove is not None:
            widgets.remove(remove)
        if add is not None:
            widgets.append(add)

        self.labels[layout_name].setText('{}: {}'.format(layout_name, len(widgets)))
        a = np.array([(entry.isac_class_averages, entry.isac_class_id) for entry in widgets], dtype='U200,i8')
        indices = np.argsort(a)
        widgets = np.array(widgets, dtype=np.object)[indices].tolist()

        layout = None
        for i in range(len(widgets)):
            i_hor = i % self.columns
            if i_hor == 0:
                if layout is not None:
                    layout.addStretch(1)
                layout = QHBoxLayout()
                self.layouts[layout_name].addLayout(layout)
            layout.addWidget(widgets[i])
        if layout is not None:
            layout.addStretch(1)
        self.layouts[layout_name].addStretch(1)
        return widgets

    def clear(self):
        for name in self.layouts:
            self.add_to_layout(name, clear=True)

    def switch_layout(self, sender, layout_name):
        self.add_to_layout(sender.current_layout, remove=sender)
        self.add_to_layout(layout_name, add=sender)
        sender.current_layout = layout_name

    @pyqtSlot()
    def retrain(self):
        config_file = os.path.join(os.path.dirname(__file__), 'support_scripts', 'cinderella_config.json')
        config_out = os.path.join(self.out_dir, 'config.json')
        with open(config_file, 'r') as read:
            content = read.read()
        content = content.replace('XXXGOODXXX', os.path.join(self.out_dir, 'good'))
        content = content.replace('XXXBADXXX', os.path.join(self.out_dir, 'bad'))
        content = content.replace('XXXMODELXXX', os.path.join(self.out_dir, 'model.h5'))
        with open(config_out, 'w') as write:
            write.write(content)
        for i in ('bad', 'good'):
            index_dict = {}
            widgets = self.add_to_layout(i)
            for widget in widgets:
                index_dict.setdefault(widget.isac_class_averages, []).append(widget.isac_class_id)
            for file_name, index_list in index_dict.items():
                out_file = os.path.join(self.out_dir, '{}_{}_list.txt'.format(os.path.basename(file_name), i))
                with open(out_file, 'w') as write:
                    write.write('\n'.join(map(str, index_list)))
                os.system('{} {} {} --list={}'.format(self.e2proc2d_exec, file_name, os.path.join(self.out_dir, i, os.path.basename(file_name)), out_file))
        print('{} -c {}'.format(self.sp_cinderella_exec, config_out))




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

