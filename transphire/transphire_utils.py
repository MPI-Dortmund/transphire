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
import errno
import json
import sys
import shutil

import numpy as np

try:
    QT_VERSION = 4
    from PyQt4.QtGui import QFont
except ImportError:
    QT_VERSION = 5
    from PyQt5.QtGui import QFont

from transphire.messagebox import MessageBox
from transphire.mountcontainer import MountContainer
from transphire.statuscontainer import StatusContainer
from transphire.settingscontainer import SettingsContainer
from transphire.framecontainer import FrameContainer
from transphire.buttoncontainer import ButtonContainer
from transphire.notificationcontainer import NotificationContainer
from transphire.plotcontainer import PlotContainer
from transphire.tabdocker import TabDocker
from transphire import transphire_content as tc
from transphire import transphire_plot as tp
from transphire import transphire_import as ti


def normalize_image(data, apix=1.0, min_res=30, real=True):
    if real:
        pass
    else:
        box_x = data.shape[0]
        box_x_half = box_x / 2
        box_y = data.shape[1]
        box_y_half = box_y / 2

        min_freq = (apix / min_res)**2

        mask = np.ones((data.shape[0], data.shape[1]), dtype=bool)
        for idx_x in range(mask.shape[0]):
            for idx_y in range(mask.shape[1]):
                x = (idx_x - box_x_half) / box_x
                y = (idx_y - box_y_half) / box_y
                radius = x**2+y**2
                if radius < min_freq:
                    mask[idx_x, idx_y] = 0
                elif np.abs(idx_x - box_x_half) < 0:
                    mask[idx_x, idx_y] = 0
                elif np.abs(idx_y - box_y_half) < 0:
                    mask[idx_x, idx_y] = 0
        data[~mask] = np.median(data[mask])
        data = np.sqrt(data)

    return data


def get_name(name):
    return os.path.basename(os.path.splitext(name)[0])


def copy(file_in, file_out):
    """
    Copy file_in to a new location.

    Arguments:
    file_in - Input file
    file_out - Output file

    Return:
    None
    """

    try:
        shutil.copy2(file_in, file_out)
    except PermissionError:
        print('Error with {0}! Switching to copyfile!'.format(file_in))
        shutil.copyfile(file_in, file_out)
    else:
        umask = os.umask(0)
        os.umask(umask)
        os.chmod(file_out, 0o666 & ~umask)


def get_function_dict():
    """
    Return a dictionary containing the function to use for specific plots.

    Arguments:
    None

    Return:
    None
    """
    function_dict = {
        'CTFFIND4 v4.1.10': {
            'plot': tp.update_ctffind_4_v4_1_10,
            'plot_data': ti.import_ctffind_v4_1_10,
            'content': tc.default_ctffind_4_v4_1_10,
            'executable': True,
            'typ': 'ctf',
            'allow_empty': ['Gain file'],
            },
        'CTFFIND4 v4.1.8': {
            'plot': tp.update_ctffind_4_v4_1_8,
            'plot_data': ti.import_ctffind_v4_1_8,
            'content': tc.default_ctffind_4_v4_1_8,
            'executable': True,
            'typ': 'ctf',
            'allow_empty': ['Gain file'],
            },
        'Gctf v1.18': {
            'plot': tp.update_gctf_v1_18,
            'plot_data': ti.import_gctf_v1_18,
            'content': tc.default_gctf_v1_18,
            'executable': True,
            'typ': 'ctf',
            'allow_empty': [],
            },
        'Gctf v1.06': {
            'plot': tp.update_gctf_v1_06,
            'plot_data': ti.import_gctf_v1_06,
            'content': tc.default_gctf_v1_06,
            'executable': True,
            'typ': 'ctf',
            'allow_empty': [],
            },
        'CTER v1.0': {
            'plot': tp.update_cter_v1_0,
            'plot_data': ti.import_cter_v1_0,
            'content': tc.default_cter_v1_0,
            'executable': True,
            'typ': 'ctf',
            'allow_empty': [],
            },
        'MotionCor2 v1.0.0': {
            'plot': tp.update_motion_cor_2_v1_0_0,
            'plot_data': ti.import_motion_cor_2_v1_0_0,
            'content': tc.default_motion_cor_2_v1_0_0,
            'executable': True,
            'typ': 'motion',
            'allow_empty': ['-DefectFile', '-Gain'],
            },
        'MotionCor2 v1.0.5': {
            'plot': tp.update_motion_cor_2_v1_0_5,
            'plot_data': ti.import_motion_cor_2_v1_0_5,
            'content': tc.default_motion_cor_2_v1_0_5,
            'executable': True,
            'typ': 'motion',
            'allow_empty': ['-Dark', '-DefectFile', '-Gain'],
            },
        'MotionCor2 v1.1.0': {
            'plot': tp.update_motion_cor_2_v1_1_0,
            'plot_data': ti.import_motion_cor_2_v1_1_0,
            'content': tc.default_motion_cor_2_v1_1_0,
            'executable': True,
            'typ': 'motion',
            'allow_empty': ['-Dark', '-DefectFile', '-Gain'],
            },
        'crYOLO v1.0.4': {
            'plot': tp.update_cryolo_v1_0_4,
            'plot_data': ti.import_cryolo_v1_0_4,
            'content': tc.default_cryolo_v1_0_4,
            'executable': True,
            'typ': 'picking',
            'allow_empty': [],
            },
        'crYOLO v1.0.5': {
            'plot': tp.update_cryolo_v1_0_5,
            'plot_data': ti.import_cryolo_v1_0_5,
            'content': tc.default_cryolo_v1_0_5,
            'executable': True,
            'typ': 'picking',
            'allow_empty': [],
            },
        'crYOLO v1.1.0': {
            'plot': tp.update_cryolo_v1_1_0,
            'plot_data': ti.import_cryolo_v1_1_0,
            'content': tc.default_cryolo_v1_1_0,
            'executable': True,
            'typ': 'picking',
            'allow_empty': [],
            },
        'crYOLO v1.2.1': {
            'plot': tp.update_cryolo_v1_2_1,
            'plot_data': ti.import_cryolo_v1_2_1,
            'content': tc.default_cryolo_v1_2_1,
            'executable': True,
            'typ': 'picking',
            'allow_empty': [],
            },
        'crYOLO v1.2.2': {
            'plot': tp.update_cryolo_v1_2_2,
            'plot_data': ti.import_cryolo_v1_2_2,
            'content': tc.default_cryolo_v1_2_2,
            'executable': True,
            'typ': 'picking',
            'allow_empty': [],
            },
        'Mount': {
            'plot': None,
            'plot_data': None,
            'content': tc.default_mount,
            'executable': False,
            'typ': None,
            'allow_empty': [],
            },
        'Pipeline': {
            'plot': None,
            'plot_data': None,
            'content': tc.default_pipeline,
            'executable': False,
            'typ': None,
            'allow_empty': [],
            },
        'General': {
            'plot': None,
            'plot_data': None,
            'content': tc.default_general,
            'executable': False,
            'typ': None,
            'allow_empty': ['Rename suffix'],
            },
        'Notification': {
            'plot': None,
            'plot_data': None,
            'content': tc.default_notification,
            'executable': False,
            'typ': None,
            'allow_empty': [],
            },
        'Notification_widget': {
            'plot': None,
            'plot_data': None,
            'content': tc.default_notification_widget,
            'executable': False,
            'typ': None,
            'allow_empty': [],
            },
        'Others': {
            'plot': None,
            'plot_data': None,
            'content': tc.default_others,
            'executable': False,
            'typ': None,
            'allow_empty': [],
            },
        'Font': {
            'plot': None,
            'plot_data': None,
            'content': tc.default_font,
            'executable': False,
            'typ': None,
            'allow_empty': [],
            },
        'Copy': {
            'plot': None,
            'plot_data': None,
            'content': tc.default_copy,
            'executable': False,
            'typ': None,
            'allow_empty': [],
            },
        'Path': {
            'plot': None,
            'plot_data': None,
            'content': tc.default_path,
            'executable': False,
            'typ': None,
            'allow_empty': [],
            },
        }
    return function_dict


def mkdir_p(path):
    """
    Create output directories recursively.

    Arguments:
    path - Directory path to create

    Return:
    None
    """
    try:
        os.makedirs(path)
    except OSError as exc:
        if exc.errno == errno.EEXIST and os.path.lexists(path):
            pass
        else:
            raise


def message(text):
    """
    Show a text in a message box.

    Arguments:
    text - Text shown in the message box

    Return:
    None
    """
    final_text = []
    for line in text.splitlines():
        final_text.append('\n'.join([line[i:i+80] for i in range(0, len(line), 80)]))

    dialog = MessageBox(is_question=False)
    dialog.setText(None, '\n'.join(final_text))
    dialog.exec_()


def question(head, text, parent):
    """
    Show a questions message box dialog.

    Arguments:
    head - Header of the window
    text - Text with the questions

    Return:
    True if No, False if Yes
    """
    if QT_VERSION == 4:
        message_box = MessageBox(is_question=True)
        message_box.setText(head, text)
        result = message_box.exec_()
    elif QT_VERSION == 5:
        message_box = MessageBox(is_question=True)
        message_box.setText(head, text)
        result = message_box.exec_()
    else:
        raise ImportError('QT version unknown! Please contact the transphire authors!')
    return result


def get_exclude_set(content):
    """
    Check the widget_2 variable, if the program should be loaded or not.

    Argument:
    content - Content as dictionary.

    Return:
    List of names to exclude
    """
    exclude_list = []
    content_with_content = []
    for entry in content:
        try:
            content_with_content.append(entry['content'])
        except KeyError:
            continue

    for entry in content_with_content:
        if not isinstance(entry, list):
            continue
        else:
            pass
        for sub_content in entry:
            for entry2 in sub_content:
                for key in entry2:
                    widget_2 = entry2[key][1]['widget_2']
                    if widget_2 is None:
                        continue
                    elif widget_2 == 'Main':
                        continue
                    elif widget_2 == 'Advanced' or widget_2 == 'Rare':
                        exclude_list.append(key)
                        exclude_list.append('Plot {0}'.format(key))
                    else:
                        print(
                            'TransphireUtils: widget_2 content unknown! Exit here!',
                            widget_2
                            )
                        sys.exit(1)
    return set(exclude_list)


def reduce_programs(exclude_set=None):
    """
    Reduce the number of programs to the users preferences.

    Arguments:
    exclude_set - Set of names to not consider

    Return:
    List of content for motion, List of content for ctf
    """
    if exclude_set is None:
        exclude_set = set([])
    else:
        exclude_set = exclude_set
    content_motion = []
    content_ctf = []
    content_picking = []
    function_dict = get_function_dict()

    for key in function_dict:
        if key in exclude_set:
            continue
        elif function_dict[key]['executable']:
            if function_dict[key]['typ'] == 'motion':
                content_motion.append(key)
            elif function_dict[key]['typ'] == 'ctf':
                content_ctf.append(key)
            elif function_dict[key]['typ'] == 'picking':
                content_picking.append(key)
            elif function_dict[key]['typ'] is None:
                print(key, 'is executable, but does not have a typ! Exit here!')
                sys.exit(1)
            else:
                print(key, 'has an unknown typ:', function_dict[key]['typ'], '! Exit here!')
                sys.exit(1)
        else:
            pass

    return sorted(content_motion), sorted(content_ctf), sorted(content_picking)


def reduce_copy_entries(exclude_set, content):
    """
    Reduce the number of options based on the exclude_set

    Arguments:
    exclude_set - Set of names to not consider
    content - Content of the widgets

    Return:
    None
    """
    for item in content:
        for sub_item in item:
            if 'Motion' in sub_item:
                name = 'Motion'
            elif 'CTF' in sub_item:
                name = 'CTF'
            elif 'Picking' in sub_item:
                name = 'Picking'
            else:
                continue

            values = sub_item[name][1]['values']
            for key in exclude_set:
                if key in values:
                    values.remove(key)


def reduce_path_widget(exclude_set, content):
    """
    Reduce the number of paths based on the exclude_set

    Arguments:
    exclude_set - Set of names to not consider
    content - Content of the widgets

    Return:
    None
    """
    for item in content:
        for sub_item in item:
            keys_to_delete = []
            for key in sub_item:
                if key in exclude_set:
                    keys_to_delete.append(key)
            for key in keys_to_delete:
                del sub_item[key]


def get_key_names(settings_folder, name):
    """
    Extract mount names from related settings file.

    Arguments:
    None

    Return:
    List of mount names
    """
    default_file = '{0}/content_{1}.txt'.format(settings_folder, name)
    try:
        with open(default_file, 'r') as file_r:
            data = json.load(file_r)
    except FileNotFoundError:
        data = []

    return_dict = {
        'Copy_work': [],
        'Copy_backup': [],
        'Copy_hdd': [],
        'Import': [],
        'Copy': [],
        }
    for entry in data:
        name = None
        typ = None
        for widget in entry:
            for key in widget:
                if key == 'Mount name':
                    name = widget[key][0]
                elif key == 'Typ':
                    typ = widget[key][0]
                else:
                    pass
        return_dict[typ].append(name)
    if return_dict['Copy']:
        print('')
        print('Old Copy type detected! Please edit the TranSPHIRE settings and change them to Import')
        print('')
        return_dict['Import'].extend(return_dict['Copy'])
        del return_dict['Copy']
    return return_dict


def get_content_gui(content):
    """
    Create content lists to load the GUI.

    Arguments:
    content - Content as dictionary.

    Return:
    Content as list
    """

    content_motion, content_ctf, content_picking = reduce_programs()

    gui_content = [
        {
            'name': 'Notification_widget',
            'widget': NotificationContainer,
            'content': content['Notification_widget'],
            'layout': 'h2',
            },
        {
            'name': 'Button',
            'widget': ButtonContainer,
            'layout': 'h3',
            },
        {
            'name': 'TAB1',
            'widget': TabDocker,
            'layout': 'h4',
            },
        {
            'name': 'Mount',
            'widget': MountContainer,
            'content_mount': content['Mount'],
            'layout': 'TAB1',
            },
        {
            'name': 'Settings',
            'widget': TabDocker,
            'layout': 'TAB1',
            },
        {
            'name': 'Visualisation',
            'widget': TabDocker,
            'layout': 'TAB1',
            },
        {
            'name': 'General',
            'widget': SettingsContainer,
            'content': content['General'],
            'content_others': content['Others'],
            'layout': 'Settings',
            },
        {
            'name': 'Notification',
            'widget': SettingsContainer,
            'content': content['Notification'],
            'layout': 'Settings',
            },
        {
            'name': 'Copy',
            'widget': SettingsContainer,
            'content': content['Copy'],
            'layout': 'Settings',
            },
        {
            'name': 'Path',
            'widget': SettingsContainer,
            'content': content['Path'],
            'layout': 'Settings',
            },
        {
            'name': 'Motion',
            'widget': TabDocker,
            'layout': 'Settings',
            },
        {
            'name': 'CTF',
            'widget': TabDocker,
            'layout': 'Settings',
            },
        {
            'name': 'Picking',
            'widget': TabDocker,
            'layout': 'Settings',
            },
        {
            'name': 'Status',
            'widget': StatusContainer,
            'content': content['Others'],
            'content_mount': content['Mount'],
            'content_pipeline': content['Pipeline'],
            'content_font': content['Font'],
            'layout': 'v2',
            },
        {
            'name': 'Plot Motion',
            'widget': TabDocker,
            'layout': 'Visualisation',
            },
        {
            'name': 'Plot CTF',
            'widget': TabDocker,
            'layout': 'Visualisation',
            },
        {
            'name': 'Plot Picking',
            'widget': TabDocker,
            'layout': 'Visualisation',
            },
        ]

    all_content = []
    all_content.append(['Motion', content_motion])
    all_content.append(['CTF', content_ctf])
    all_content.append(['Picking', content_picking])
    for typ, content_typ in all_content:
        for input_content in content_typ:
            gui_content.append({
                'name': input_content,
                'widget': SettingsContainer,
                'content': content[input_content],
                'layout': typ,
                })
            gui_content.append({
                'name': 'Plot {0}'.format(input_content),
                'widget': TabDocker,
                'layout': 'Plot {0}'.format(typ),
                })
            gui_content.append({
                'name': 'Show images',
                'widget': PlotContainer,
                'content': 'image',
                'plot_type': typ.lower(),
                'layout': 'Plot {0}'.format(input_content),
                })
            gui_content.append({
                'name': 'Plot per micrograph',
                'widget': PlotContainer,
                'content': 'values',
                'plot_type': typ.lower(),
                'layout': 'Plot {0}'.format(input_content),
                })
            gui_content.append({
                'name': 'Plot histogram',
                'widget': PlotContainer,
                'content': 'histogram',
                'plot_type': typ.lower(),
                'layout': 'Plot {0}'.format(input_content),
                })
        if typ == 'Motion':
            gui_content.append({
                'name': 'Frames',
                'widget': FrameContainer,
                'layout': typ,
                })

    return gui_content


def look_and_feel_small(app, font=None):
    """
    Look and feel for the default settings dialog.

    Arguments:
    app - QApplication.
    font - User provided font size (default None)

    Return:
    Style sheet
    """
    if font is None:
        font = 5
    else:
        font = float(font)
    font_type = QFont('Verdana', font, 63)
    font_type.setStyleStrategy(QFont.PreferAntialias)
    app.setFont(font_type)
    style_widgets = """
    QWidget#central_raw {{
        background-image: url("{1}");
        }}
    QWidget#central {{
        background-color: {2};
        border-radius: 15px;
        }}
    QWidget#settings {{
        background-color: {3};
        border-radius: 15px
        }}
    QWidget#tab {{
        background-color: {3};
        border-radius: 15px
        }}
    QTabWidget::pane {{
        border-top: 2px solid #C2C7CB;
        }}
    QTabWidget::tab {{
        min-width: 120px;
        }}
    QTabBar {{
        background-color: #C2C7CB
        }}
    QTabBar::pane {{
        border-top: 2px solid #C2C7CB;
        }}
    QTabBar::tab {{
        min-width: 120px;
        }}

    QLineEdit {{ background-color: white }}
    QComboBox {{ background-color: white }}
    QPushButton {{
        background-color: qradialgradient(cx:0.5, cy:0.5, fx:0.5, fy:0.5, radius:1, stop:0 white, stop:1 #f9eeb4);
        border-width: 1px;
        border-style:inset;
        padding: 1px;
        border-radius: 5px
        }}
    QPushButton:pressed {{
        background-color: qradialgradient(cx:0.5, cy:0.5, fx:0.5, fy:0.5, radius:1, stop:0 white, stop:1 pink);
        border-width: 1px;
        border-style:outset;
        padding: 1px;
        border-radius: 5px
        }}
    """.format(
        'lightgrey',
        '{0}/images/sxgui_background.png'.format(os.path.dirname(__file__)),
        'rgba(229, 229, 229, 192)',
        'rgba(229, 229, 229, 120)',
        )
    return style_widgets


def look_and_feel(app, font=None, adjust_width=None, adjust_height=None, default=None):
    """
    Look and feel.

    Arguments:
    app - QApplication.
    font - User provided font size (default None)
    adjust_width - User provided width adjustment (default None)
    adjust_height - User provided height adjustment (default None)
    default - Default values (default None)

    Return:
    Style sheet
    """
    idx = 0
    if font is not None:
        font = float(font)
    else:
        font = float(default[0][idx]['Font'][0])
    idx += 1
    if adjust_width is not None:
        adjust_width = float(adjust_width)
    else:
        adjust_width = float(default[0][idx]['Width adjustment'][0])
    idx += 1
    if adjust_height is not None:
        adjust_height = float(adjust_height)
    else:
        adjust_height = float(default[0][idx]['Height adjustment'][0])

    idx += 1
    start_button_width = float(default[0][idx]['Start button'][0])
    idx += 1
    notification_edit_width = float(default[0][idx]['Notification edit'][0])
    idx += 1
    notification_check_width = float(default[0][idx]['Notification check'][0])
    idx += 1
    notification_button_width = float(default[0][idx]['Notification button'][0])
    idx += 1
    mount_button_width = float(default[0][idx]['Mount button'][0])
    idx += 1
    frame_entry_width = float(default[0][idx]['Frame entry'][0])
    idx += 1
    frame_button_width = float(default[0][idx]['Frame button'][0])
    idx += 1
    frame_label_width = float(default[0][idx]['Frame label'][0])
    idx += 1
    setting_widget_width = float(default[0][idx]['Setting widget'][0])
    idx += 1
    setting_widget_width_large = float(default[0][idx]['Setting widget large'][0])
    idx += 1
    status_name_width = float(default[0][idx]['Status name'][0])
    idx += 1
    status_info_width = float(default[0][idx]['Status info'][0])
    idx += 1
    status_quota_width = float(default[0][idx]['Status quota'][0])
    idx += 1
    tab_width = float(default[0][idx]['Tab width'][0])
    idx += 1
    widget_height = float(default[0][idx]['Widget height'][0])
    idx += 1
    tab_height = float(default[0][idx]['Tab height'][0])

    font_type = QFont('Verdana', font, 63)
    font_type.setStyleStrategy(QFont.PreferAntialias)
    app.setFont(font_type)
    start_button_width = '{0}px'.format(font * start_button_width * adjust_width)
    notification_edit_width = '{0}px'.format(font * notification_edit_width * adjust_width)
    notification_check_width = '{0}px'.format(font * notification_check_width * adjust_width)
    notification_button_width = '{0}px'.format(font * notification_button_width * adjust_width)
    mount_button_width = '{0}px'.format(font * mount_button_width * adjust_width)
    frame_entry_width = '{0}px'.format(font * frame_entry_width * adjust_width)
    frame_button_width = '{0}px'.format(font * frame_button_width * adjust_width)
    frame_label_width = '{0}px'.format(font * frame_label_width * adjust_width)
    setting_widget_width_large = '{0}px'.format(font * setting_widget_width_large * adjust_width)
    setting_widget_width = '{0}px'.format(font * setting_widget_width * adjust_width)
    status_name_width = '{0}px'.format(font * status_name_width * adjust_width)
    status_info_width = '{0}px'.format(font * status_info_width * adjust_width)
    status_quota_width = '{0}px'.format(font * status_quota_width * adjust_width)
    tab_width = '{0}px'.format(font * tab_width * adjust_width)
    widget_height = '{0}px'.format(font * widget_height * adjust_height)
    tab_height = '{0}px'.format(font * tab_height * adjust_height)

    # Style sheet
    style_widgets = """
    QWidget#central_raw {{
        background-image: url("{1}");
        }}
    QWidget#central {{
        background-color: {2};
        border-radius: 15px;
        }}
    QWidget#central_black {{
        background-color: {4};
        border-radius: 15px;
        }}
    QWidget#settings {{
        background-color: {3};
        border-radius: 15px
        }}
    QWidget#tab {{
        background-color: {3};
        border-radius: 15px
        }}
    QTabWidget::tab-bar {{
        alignment: center;
        }}
    QTabWidget::pane {{
        border-top: 2px solid #C2C7CB;
        }}
    QTabWidget::tab {{
        min-width: 120px;
        }}
    QTabBar {{
        alignment: center;
        background-color: #C2C7CB
        }}
    QTabBar::pane {{
        border-top: 2px solid #C2C7CB;
        }}
    QTabBar::tab {{
        max-width: {5};
        max-height: {6};
        }}
    QMessageBox {{
        background-image: url("{1}");
        color: white;
        }}
    QFileDialog {{
        background-color: {2}
        }}
    QScrollArea {{ background-color: transparent }}
    QDockWidget {{ background-color: rgb(229, 229, 229) }}

    """.format(
        'lightgrey',
        '{0}/images/sxgui_background.png'.format(os.path.dirname(__file__)),
        'rgba(229, 229, 229, 192)',
        'rgba(229, 229, 229, 120)',
        'rgba(0, 0, 0, 153)',
        tab_width,
        tab_height,
        )

    button_style = """
    QPushButton {{ min-height: {5}}}
    QPushButton {{
        background-color: qradialgradient(
            cx:0.5,
            cy:0.5,
            fx:0.5,
            fy:0.5,
            radius:1,
            stop:0 white,
            stop:1 #f9eeb4
            );
        border-width: 1px;
        border-style: inset;
        padding: 1px;
        border-radius: 5px
        }}
    QPushButton:pressed {{
        background-color: qradialgradient(
            cx:0.5,
            cy:0.5,
            fx:0.5,
            fy:0.5,
            radius:1,
            stop:0 white,
            stop:1 pink
            );
        border-width: 1px;
        border-style: outset;
        padding: 1px;
        border-radius: 5px
        }}
    QPushButton#start {{
        background-color: qradialgradient(
            cx:0.5,
            cy:0.5,
            fx:0.5,
            fy:0.5,
            radius:1,
            stop:0 white,
            stop:1 green
            );
        min-width: {0};
        max-width: {0};
        max-height: {5}
        }}
    QPushButton#stop {{
        background-color: qradialgradient(
            cx:0.5,
            cy:0.5,
            fx:0.5,
            fy:0.5,
            radius:1,
            stop:0 white,
            stop:1 red
            );
        min-width: {0};
        max-width: {0};
        max-height: {5}
        }}
    QPushButton#button {{ min-width: {0}; max-width: {0} }}
    QPushButton#frame {{
        background-color: qradialgradient(
            cx:0.5,
            cy:0.5,
            fx:0.5,
            fy:0.5,
            radius:1,
            stop:0 white,
            stop:1 #68a3c3
            );
        max-width: {1};
        min-width: {1}
        }}
    QPushButton#button_entry {{
        background-color: qradialgradient(
            cx:0.5,
            cy:0.5,
            fx:0.5,
            fy:0.5,
            radius:1,
            stop:0 white,
            stop:1 #68a3c3
            );
        max-width: {2};
        min-width: {2}
        }}
    QPushButton#mount {{
        background-color: qradialgradient(
            cx:0.5,
            cy:0.5,
            fx:0.5,
            fy:0.5,
            radius:1,
            stop:0 white,
            stop:1 #68a3c3
            );
        max-width: {3};
        min-width: {3}
        }}
    QPushButton#notification {{ max-width: {4}; min-width: {4} }}
    QPushButton#sep {{
        color: white;
        background-color: black;
        border-color: green;
        border-width: 1px;
        border-style: inset;
        padding: 0px;
        border-radius: 0px
        }}
    QPushButton#sep:checked {{
        color: white;
        background-color: black;
        border-color: red;
        border-width: 1px;
        border-style: outset;
        padding: 0px;
        border-radius: 0px
        }}
    """.format(
        start_button_width,
        frame_label_width,
        frame_button_width,
        mount_button_width,
        notification_button_width,
        widget_height,
        )

    label_style = """
    QLabel#picture {{ background-color: transparent }}
    QLabel#status_name {{ max-width: {1}; min-width: {1}; background-color: {0}; min-height: {5}; max-height: {5} }}
    QLabel#status_info {{ max-width: {2}; min-width: {2}; background-color: {0}; min-height: {5}; max-height: {5} }}
    QLabel#status_quota {{ max-width: {3}; min-width: {3}; background-color: {0}; min-height: {5}; max-height: {5} }}
    QLabel#setting {{ max-width: {4}; min-width: {4}; background-color: {0}; min-height: {5}; max-height: {5} }}
    QLabel#setting_large {{ max-width: {6}; min-width: {6}; background-color: {0}; min-height: {5}; max-height: {5} }}
    """.format(
        'transparent',
        status_name_width,
        status_info_width,
        status_quota_width,
        setting_widget_width,
        widget_height,
        setting_widget_width_large,
        )

    edit_style = """
    QLineEdit {{ max-height: {7}; min-height: {7}; background-color: white }}
    QLineEdit#default_settings {{ min-width: {1}; max-width: 9999; background-color: white }}
    QLineEdit:disabled {{ background-color: {6} }}
    QLineEdit#setting:enabled {{
        max-width: {1}; min-width: {1}; background-color: {0}; min-height: {7}; max-height: {7}
        }}
    QLineEdit#setting_large:enabled {{
        max-width: {8}; min-width: {8}; background-color: {0}; min-height: {7}; max-height: {7}
        }}
    QLineEdit#noti_edit:enabled {{
        max-width: {2}; min-width: {2}; background-color: {5}; min-height: {7}; max-height: {7}
        }}
    QLineEdit#frame:enabled {{
        max-width: {3}; min-width: {3}; background-color: {0}; min-height: {7}; max-height: {7}
        }}
    QLineEdit#entry:enabled {{
        max-width: {4}; min-width: {4}; background-color: {0}; min-height: {7}; max-height: {7}
        }}
    """.format(
        'white',
        setting_widget_width,
        notification_edit_width,
        frame_label_width,
        frame_entry_width,
        '#5d995d',
        'rgba(150,150,150)',
        widget_height,
        setting_widget_width_large,
        )

    check_style = """
    QCheckBox {{ min-height: {1}; max-height: {1}; background-color: white }}
    QCheckBox#noti_check {{ max-width: {0}; min-width: {0}; background-color: white }}
    """.format(notification_check_width, widget_height)

    combo_style = """
    QComboBox {{ min-width: {4}; max-width: {4}; min-height: {3}; max-height: {3}; background-color: white }}
    QComboBox QAbstractItemView {{
        background-color: white; selection-color: black; selection-background-color: lightgray
        }}
    QComboBox#default_settings {{ min-width: {1}; max-width: 9999; background-color: white }}
    QComboBox:disabled {{ background-color: {2} }}
    QComboBox#noti_edit:enabled {{ max-width: {1}; min-width: {1}; background-color: {0} }}
    """.format(
        '#5d995d',
        notification_edit_width,
        'rgba(150,150,150,200)',
        widget_height,
        setting_widget_width
        )

    style = '\n'.join([style_widgets, button_style, label_style, edit_style, check_style, combo_style])
    return style


def check_instance(value, typ):
    """
    Check typ of value

    Arguments:
    value - Value to check
    typ - Type to check

    Return:
    Bool
    """
    if isinstance(typ, list):
        value_split = value.split(' ')
        for entry, var in zip(typ, value_split):
            try:
                entry(var)
            except ValueError:
                return False
            else:
                pass
    else:
        try:
            typ(value)
        except ValueError:
            return False
        else:
            pass
    return True


def get_style(typ):
    """
    Style colores for the content of widgets.

    Arguments:
    typ - Typ of color

    Return:
    Color string
    """
    if typ == 'error':
        color = 'red'
    elif typ == 'unchanged':
        color = 'black'
    elif typ == 'changed':
        color = 'purple'
    elif typ == 'True':
        color = '#68a3c3'
    elif typ == 'False':
        color = '#c3a368'
    else:
        msg = 'Style not known! Go for black!'
        print(msg)
        message(msg)
        color = 'black'

    return 'color: {0}'.format(color)


def rebin(arr, new_shape):
    shape = (new_shape[0], arr.shape[0] // new_shape[0],
             new_shape[1], arr.shape[1] // new_shape[1])
    return arr.reshape(shape).mean(-1).mean(1)
