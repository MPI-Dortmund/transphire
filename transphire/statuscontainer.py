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
import os
from PyQt5.QtWidgets import QHBoxLayout, QVBoxLayout, QWidget, QLabel
from PyQt5.QtGui import QImage
from PyQt5.QtCore import pyqtSlot, pyqtSignal
from . import transphire_utils as tu
from . import logviewer as lv


class StatusContainer(QWidget):
    """
    Container for status widgets

    Inherits:
    QWidget

    Signals:
    sig_refresh_quota - Connected to change the quota text (no object)
    """
    sig_refresh_quota = pyqtSignal()

    def __init__(self, content, content_mount, content_pipeline, mount_worker, process_worker, content_font, parent=None, **kwargs):
        """
        Layout for the status container.

        Arguments:
        content - Content to fill the statuscontainer
        content_mount - Content for the mount points
        content_pipeline - Content for the pipeline settings
        mount_worker - MountWorker object
        process_worker - ProcessWorker object
        parent - Parent widget (default None)

        Returns:
        None
        """
        super(StatusContainer, self).__init__(parent)

        # Layout
        central_layout = QVBoxLayout(self)
        central_layout.setContentsMargins(0, 0, 0, 0)
        central_widget = QWidget(self)
        central_widget.setObjectName('central_black')
        central_layout.addWidget(central_widget)

        layout_v1 = QVBoxLayout(central_widget)

        for entry in content:
            for widget in entry:
                for key in widget:
                    if key == 'Image':
                        image = widget[key][0]

        # Global content
        self.content = {}

        # Add em-transfer quota
        self.content['scratch'] = StatusWidget(name='scratch', default_name='Connected', default_quota='-- / --')
        layout_v1.addWidget(self.content['scratch'])

        # Add em-transfer quota
        self.content['project'] = StatusWidget(name='project', default_name='Connected', default_quota='-- / --')
        layout_v1.addWidget(self.content['project'])

        content_temp = []
        for entry in content_mount:
            my_content = {}
            for widget in entry:
                for key in widget:
                    my_content[key] = widget[key]
            content_temp.append(my_content)

        # Content
        for entry in content_temp:
            key = entry['Mount name'][0]
            if not key:
                continue
            elif key == 'HDD':
                max_iter = 6
            else:
                max_iter = 1
            for i in range(max_iter):
                if max_iter == 1:
                    key_name = key
                    key_device = key.replace(' ', '_')
                else:
                    key_name = '{0} {1}'.format(key, i)
                    key_device = key_name.replace(' ', '_')

                mount_worker.sig_add_save.emit(
                    key_device,
                    entry['SSH address'][0],
                    entry['Quota command'][0],
                    entry['Is df giving the right quota?'][0],
                    entry['Quota / TB'][0]
                    )

                self.content[key_device] = StatusWidget(
                    name=key_name, default_name='Not connected', default_quota='-- / --'
                    )
                self.content[key_device].setVisible(False)
                layout_v1.addWidget(self.content[key_device])

        # Add a visual separator
        layout_v1.addWidget(Separator(typ='horizontal', color='grey', parent=self))

        self.content['Feedbacks'] = StatusWidget(name='Feedbacks', default_name='00|00', default_quota='Not running')
        layout_v1.addWidget(self.content['Feedbacks'])
        # Add process status widgets
        for entry in content_pipeline[0]:
            for key in entry:
                if 'WIDGETS' in key:
                    continue
                basename = key
                name = basename
                self.content[name] = StatusWidget(name=name, default_name='00|00', default_quota='Not running')
                layout_v1.addWidget(self.content[name])

        layout_v1.addWidget(Separator(typ='horizontal', color='grey', parent=self))

        self.log_viewer = lv.LogViewer(
            show_indicators=True,
            file_name='',
            parent=self
            )
        layout_v1.addWidget(self.log_viewer, stretch=1)

        # Add picture
        if image and os.path.exists(image):
            pass
        else:
            image = os.path.join(os.path.dirname(__file__), 'images', 'Transphire.png')
        qimage = QImage(image)

        image_height = float(content_font[0][0]['Font'][0]) * 150 / 10
        try:
            image_width = image_height * qimage.width() / qimage.height()
        except ZeroDivisionError:
            tu.message('Chosen picture: "{0}" - No longer available!'.format(image))
            self.log_viewer.appendPlainText('Chosen picture: "{0}" - No longer available!'.format(image))
        else:
            pic_label = QLabel(self)
            pic_label.setObjectName('picture')
            pic_label.setStyleSheet('border-image: url("{0}")'.format(image))
            pic_label.setMaximumHeight(image_height)
            pic_label.setMinimumHeight(image_height)
            pic_label.setMaximumWidth(image_width)
            pic_label.setMinimumWidth(image_width)

            layout_image = QHBoxLayout()
            layout_image.addStretch(1)
            layout_image.addWidget(pic_label)
            layout_image.addStretch(1)

            layout_v1.addLayout(layout_image)

        # Reset quota warning
        mount_worker.quota_warning = True

        # Events
        mount_worker.sig_success.connect(self._mount_success)
        mount_worker.sig_error.connect(self._mount_error)
        mount_worker.sig_info.connect(self._mount_info)
        mount_worker.sig_quota.connect(self.refresh_quota)

        process_worker.sig_status.connect(self._process_success)
        process_worker.sig_set_project_directory.connect(self.log_viewer.set_project_path)
        process_worker.sig_error.connect(self._process_error)

        self.sig_refresh_quota.connect(mount_worker.refresh_quota)

    @pyqtSlot(str, str, str)
    def _mount_success(self, text, device, color):
        """
        Mount was successfull.

        Arguments:
        text - Text to show
        device - Device name
        color - Color of the text

        Returns:
        None
        """
        self.content[device].sig_change_info_name.emit(text, color)
        if color == 'white':
            mount_type = 'Unmount'
            self.content[device].setVisible(False)
        else:
            mount_type = 'Mount'
            self.content[device].setVisible(True)
        if device != 'scratch' and device != 'project':
            self.log_viewer.appendPlainText('{0} {1} successfull!'.format(device, mount_type))
            #tu.message('{0} Mount/Unmount successfull!'.format(device))
        else:
            pass

    @pyqtSlot(str, str)
    def _mount_error(self, text, device):
        """
        Mount was not successfull

        Arguments:
        text - Text to show
        device - Device name

        Returns:
        None
        """
        if device != 'None':
            self.content[device].sig_change_info_name.emit('Not connected', 'red')
        self.log_viewer.appendPlainText(text)
        #tu.message(text)

    @pyqtSlot(str)
    def _mount_info(self, text):
        """
        Information for the user

        Arguments:
        text - Text to show

        Returns:
        None
        """
        self.log_viewer.appendPlainText(text)
        #tu.message(text)

    @pyqtSlot(str, object, str, str)
    def _process_success(self, text, numbers, device, color):
        """
        Success in a process

        Arguments:
        text - Text to show
        device - Device name
        color - Color of the text

        Returns:
        None
        """
        text = text.split()
        quota_list = []
        for entry in numbers:
            try:
                entry = '{0:.0f}'.format(entry)
            except:
                entry = entry
            quota_list.append(entry)

        self.content[device].sig_change_info_name.emit(' '.join(text), color)
        self.content[device].sig_change_info_quota.emit(' | '.join(quota_list), color)
        self.sig_refresh_quota.emit()

    @pyqtSlot(str)
    def _process_error(self, text):
        """
        Error in a process

        Arguments:
        text - Text to show

        Returns:
        None
        """
        self.log_viewer.appendPlainText(text, indicator='error')
        self.sig_refresh_quota.emit()

    @pyqtSlot(str, str, str)
    def refresh_quota(self, text, device, color):
        """
        Refresh the quota

        Arguments:
        text - Text to show
        device - Device name
        color - Color of the text

        Returns:
        None
        """
        self.content[device].sig_change_info_quota.emit(text, color)

from .statuswidget import StatusWidget
from .separator import Separator
