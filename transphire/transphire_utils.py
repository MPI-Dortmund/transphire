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
import re
import os
import datetime
import copy as copy_mod
import errno
import json
import sys
import shutil
import time

import numpy as np
import pandas as pd

from PyQt5.QtGui import QFont

from . import transphire_content as tc
from . import transphire_plot as tp
from . import transphire_import as ti

VERSION_RE = re.compile('(.*) >=v([\d.]+)')


def symlink_rel(src, dst):
    rel_path_src = os.path.relpath(src, os.path.dirname(dst))
    os.symlink(rel_path_src, dst)
    return os.path.join(rel_path_src, dst)


def rerun_function_in_case_of_error(func):
    def wrapper(*args, **kwargs):
        error_code = []
        for i in range(20):
            try:
                return_value = func(*args, **kwargs)
            except OSError as e:
                error_code.append(str(e))
                print(e)
                time.sleep(0.5)
            else:
                return return_value
        raise BlockingIOError(' --- '.join(error_code))
    return wrapper


def thread_safe(func):
    def wrapper(self, *args, **kwargs):
        self._DataFrame__get_df()
        try:
            return_value = func(self, *args, **kwargs)
        except:
            self._lock.release()
            raise
        else:
            self._DataFrame__set_df()
        return return_value
    return wrapper


class DataFrame(object):

    def __init__(self, manager, file_path):
        super(DataFrame, self).__init__()
        self._lock = manager.RLock()
        self._namespace = manager.Namespace()
        self._file_path = file_path
        self._data_frame = None
        self._namespace.df = None
        self._increment = 5

        self.load_df()

    def __get_df(self):
        self._lock.acquire()
        self._data_frame = self._namespace.df

    def __set_df(self):
        self._namespace.df = self._data_frame
        self._data_frame = None
        self._lock.release()

    def __add_df_column(self, name):
        self._data_frame[name] = np.nan
        self._data_frame[name] = self._data_frame[name].astype(object)

    def __add_df_rows(self, length):
        columns = self._data_frame.columns
        new_data_frame = pd.DataFrame(index=range(length), columns=columns)
        self._data_frame = self._data_frame.append(new_data_frame, ignore_index=True)

    def __save_df(self):
        self._data_frame.to_csv(self._file_path)

    def __check_df(self, index, columns):
        if index not in self._data_frame.index:
            rows_to_add = self._increment * (index // self._increment + 1) - self._data_frame.shape[0]
            self.__add_df_rows(rows_to_add)

        for column in columns:
            try:
                self._data_frame[column]
            except KeyError:
                self.__add_df_column(column)

    @thread_safe
    def get_df(self):
        return self._data_frame

    @thread_safe
    def set_df(self, data_frame):
        self._data_frame = data_frame
        self.__save_df()

    @thread_safe
    def save_df(self):
        self._data_frame.to_csv(self._file_path)

    @thread_safe
    def load_df(self):
        if os.path.exists(self._file_path):
            df = pd.read_csv(self._file_path, index_col=0, dtype=object)
        else:
            df = pd.DataFrame(dtype=object)
        self._data_frame = df

    @thread_safe
    def value_in_column(self, value, column):
        return value in self._data_frame[column].values

    @thread_safe
    def get_values(self, index, columns):
        if isinstance(columns, str):
            columns = [columns]
        self.__check_df(index, columns)

        return self._data_frame.loc[index, list(columns)]

    @thread_safe
    def set_values(self, index, value_dict, do_save=True):
        self.__check_df(index, value_dict.keys())

        for column, value in value_dict.items():
            self._data_frame.loc[index, column] = value
        if do_save:
            self.__save_df()

    @thread_safe
    def append_values(self, value_dict, do_save=True):
        index = self._data_frame[next(iter(value_dict))].last_valid_index() + 1
        self.set_values(index, value_dict, do_save)

    @thread_safe
    def get_index_where(self, column, value, func_type):
        try:
            col = self._data_frame[column].astype(float)
        except:
            col = self._data_frame[column]

        if func_type == 'eq':
            return_value = self._data_frame.index[col == value]
        elif func_type == 'gg':
            return_value = self._data_frame.index[col > value]
        elif func_type == 'll':
            return_value = self._data_frame.index[col < value]
        elif func_type == 'ge':
            return_value = self._data_frame.index[col >= value]
        elif func_type == 'le':
            return_value = self._data_frame.index[col <= value]
        else:
            raise NameError
        return return_value


def get_unique_types():
    valid_sub_items = np.array([value['typ'] for value in get_function_dict().values() if value['typ'] is not None])
    _, unique_idx = np.unique(valid_sub_items, return_index=True)
    return valid_sub_items[np.sort(unique_idx)]


def create_log(*args):
    """
    Add a time string to print statement.

    args - Args to print

    Returns:
    String with added time stemp.
    """
    time_string = datetime.datetime.now().strftime('%Y/%m/%d - %H:%M:%S')
    return '{0} => {1}'.format(time_string, ' '.join([str(entry) for entry in args]))


def find_latest_version(name, dictionary):
    """
    Find the latest matching version key in a dictionary.
    Raises an assertion error it the return_key is not valid.

    name - Name of the program
    dictionary - Dictionary to find the best matching version.

    Returns:
    The best matching version Key.
    """
    valid_versions = []
    for entry in dictionary:
        if name not in entry:
            continue
        prog_name, version = VERSION_RE.search(entry).groups()
        if prog_name == name:
            valid_versions.append(
                tuple(
                    [
                        tuple(
                            [
                                int(num) for num in version.split('.')
                                ]
                            ),
                        entry
                        ]
                    )
                )

    return sorted(valid_versions)[-1][-1]


def find_best_match(name, dictionary):
    """
    Find the best matching version key in a dictionary.
    Raises an assertion error it the return_key is not valid.

    name - Name of the current version.
    dictionary - Dictionary to find the best matching version.

    Returns:
    The best matching version Key.
    """
    prog_name, _ = VERSION_RE.search(name).groups()
    valid_versions = [
        tuple([tuple([int(num) for num in VERSION_RE.search(entry).group(2).split('.')]), entry])
        for entry in dictionary.keys()
        if prog_name in entry
        ]
    return_key = None
    for version, current_key in reversed(sorted(valid_versions)):
        version_string = '.'.join([str(entry) for entry in version])
        if is_higher_version(name, version_string):
            return_key = current_key
            break
    assert return_key is not None, (name, prog_name, valid_versions, dictionary)
    return return_key


def is_higher_version(name, version_ref):
    """
    Compare the versions of software.
    The versions do not need to match in digits.
    v1 > v0, v0.0, v0.0.0
    v1 >= v1
    v1 < v1.0.1

    name - Name of the Software containing the version string, e.g. v1, v1.1, v1.1.1, v1.1.1rc2
    version_ref - reference version as string, e.g. 1, 1.1, 1.1.1

    Returns:
    True if the version is larger than the reference version
    """
    version_comp = VERSION_RE.search(name).group(2)
    version_tuple_comp = tuple([int(entry) for entry in version_comp.split('.')])
    version_tuple_ref = tuple([int(entry) for entry in version_ref.split('.')])
    return version_tuple_comp >= version_tuple_ref


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
    """
    Remove the extension of a file and return the basename without the PATH

    name - Name to remove the extension from

    Returns:
    The name of the file without PATH and extension.
    """
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

    if os.path.isfile(file_in):
        mkdir_p(os.path.dirname(file_out))
        try:
            shutil.copy2(file_in, file_out)
        except PermissionError:
            print('Error with {0}! Switching to copyfile!'.format(file_in))
            shutil.copyfile(file_in, file_out)
        else:
            umask = os.umask(0)
            os.umask(umask)
            os.chmod(file_out, 0o666 & ~umask)
    elif os.path.isdir(file_in):
        copytree(file_in, file_out)

def copytree(root_src_dir, root_dst_dir):
    if os.path.exists(root_dst_dir):
        root_dst_dir = os.path.join(root_dst_dir, os.path.basename(root_src_dir))
        mkdir_p(root_dst_dir)

    for src_dir, dirs, files in os.walk(root_src_dir):
        dst_dir = src_dir.replace(root_src_dir, root_dst_dir, 1)
        if not os.path.exists(dst_dir):
            mkdir_p(dst_dir)
        for file_ in files:
            src_file = os.path.join(src_dir, file_)
            dst_file = os.path.join(dst_dir, file_)
            if os.path.exists(dst_file):
                os.remove(dst_file)
            copy(src_file, dst_file)


def get_function_dict():
    """
    Return a dictionary containing the function to use for specific plots.

    Arguments:
    None

    Return:
    None
    """
    function_dict = {}

    ### Compression programs

    function_dict['Compress cmd'] = {
            'content': tc.default_compress_command_line,
            'executable': True,
            'has_path': False,
            'typ': 'Compress',
            'license': False,
            'category': 'External software',
            'allow_empty': ['--command_uncompress'],
            }

    ### Motion programs

    function_dict['MotionCor2 >=v1.0.0'] = {
            'plot': tp.update_motion,
            'plot_data': ti.import_motion_cor_2_v1_0_0,
            'content': tc.default_motion_cor_2_v1_0_0,
            'executable': True,
            'has_path': 'MotionCor2',
            'typ': 'Motion',
            'license': True,
            'category': 'External software',
            'allow_empty': ['-DefectFile', '-Gain', '-Dark'],
            }
    function_dict['MotionCor2 >=v1.0.5'] = copy_mod.deepcopy(function_dict['MotionCor2 >=v1.0.0'])
    function_dict['MotionCor2 >=v1.0.5']['content'] = tc.default_motion_cor_2_v1_0_5

    function_dict['MotionCor2 >=v1.1.0'] = copy_mod.deepcopy(function_dict['MotionCor2 >=v1.0.0'])
    function_dict['MotionCor2 >=v1.1.0']['content'] = tc.default_motion_cor_2_v1_1_0

    function_dict['MotionCor2 >=v1.2.6'] = copy_mod.deepcopy(function_dict['MotionCor2 >=v1.1.0'])

    function_dict['MotionCor2 >=v1.3.0'] = copy_mod.deepcopy(function_dict['MotionCor2 >=v1.1.0'])
    function_dict['MotionCor2 >=v1.3.0']['content'] = tc.default_motion_cor_2_v1_3_0

    function_dict['Unblur >=v1.0.0'] = {
            'plot': tp.update_motion,
            'plot_data': ti.import_unblur_v1_0_0,
            'content': tc.default_unblur_v1_0_0,
            'executable': True,
            'has_path': 'unblur',
            'typ': 'Motion',
            'license': False,
            'category': 'External software',
            'allow_empty': [],
            }

    ### CTF Programs

    function_dict['CTFFIND4 >=v4.1.8'] = {
            'plot': tp.update_ctf,
            'plot_data': ti.import_ctffind_v4_1_8,
            'content': tc.default_ctffind_4_v4_1_8,
            'executable': True,
            'has_path': 'ctffind',
            'typ': 'CTF',
            'license': False,
            'category': 'External software',
            'allow_empty': ['Gain file'],
            }

    function_dict['CTFFIND4 >=v4.1.10'] = function_dict['CTFFIND4 >=v4.1.8']

    function_dict['CTFFIND4 >=v4.1.13'] = copy_mod.deepcopy(function_dict['CTFFIND4 >=v4.1.8'])

    function_dict['Gctf >=v1.06'] = {
            'plot': tp.update_ctf,
            'plot_data': ti.import_gctf_v1_06,
            'content': tc.default_gctf_v1_06,
            'executable': True,
            'has_path': 'Gctf',
            'typ': 'CTF',
            'license': False,
            'category': 'External software',
            'allow_empty': [],
            'old': False,
            }
    function_dict['Gctf >=v1.18'] = copy_mod.deepcopy(function_dict['Gctf >=v1.06'])
    function_dict['Gctf >=v1.18']['content'] = tc.default_gctf_v1_18

    function_dict['CTER >=v1.0'] = {
            'plot': tp.update_ctf,
            'plot_data': ti.import_cter_v1_0,
            'content': tc.default_cter_v1_0,
            'executable': True,
            'has_path': 'sp_cter.py',
            'typ': 'CTF',
            'license': False,
            'category': 'External software',
            'allow_empty': [],
            }
    function_dict['CTER >=v1.3'] = copy_mod.deepcopy(function_dict['CTER >=v1.0'])

    ### Picking programs

    function_dict['crYOLO >=v1.0.4'] = {
            'plot': tp.update_cryolo_v1_0_4,
            'plot_data': ti.import_cryolo_v1_0_4,
            'content': tc.default_cryolo_v1_0_4,
            'executable': True,
            'has_path': 'cryolo_predict.py',
            'typ': 'Picking',
            'license': True,
            'category': 'External software',
            'allow_empty': [],
            }
    function_dict['crYOLO >=v1.0.5'] = copy_mod.deepcopy(function_dict['crYOLO >=v1.0.4'])

    function_dict['crYOLO >=v1.1.0'] = copy_mod.deepcopy(function_dict['crYOLO >=v1.0.4'])
    function_dict['crYOLO >=v1.1.0']['content'] = tc.default_cryolo_v1_1_0

    function_dict['crYOLO >=v1.2.1'] = copy_mod.deepcopy(function_dict['crYOLO >=v1.0.4'])
    function_dict['crYOLO >=v1.2.1']['content'] = tc.default_cryolo_v1_2_1

    function_dict['crYOLO >=v1.2.2'] = copy_mod.deepcopy(function_dict['crYOLO >=v1.2.1'])
    function_dict['crYOLO >=v1.2.2']['plot_data'] = ti.import_cryolo_v1_2_2

    function_dict['crYOLO >=v1.4.1'] = copy_mod.deepcopy(function_dict['crYOLO >=v1.2.2'])
    function_dict['crYOLO >=v1.4.1']['content'] = tc.default_cryolo_v1_4_1

    function_dict['crYOLO >=v1.5.8'] = copy_mod.deepcopy(function_dict['crYOLO >=v1.2.2'])
    function_dict['crYOLO >=v1.5.8']['content'] = tc.default_cryolo_v1_5_8


    ### Extract programs

    function_dict['WINDOW >=v1.2'] = {
            'plot': tp.update_micrograph,
            'plot_data': ti.import_window_v1_2,
            'content': tc.default_window_1_2,
            'executable': True,
            'has_path': 'sp_window.py',
            'typ': 'Extract',
            'license': False,
            'category': 'External software',
            'allow_empty': [''],
            }


    ### 2D classification programs

    function_dict['ISAC2 >=v1.2'] = {
            'plot': tp.update_batch,
            'plot_data': ti.import_isac_v1_2,
            'content': tc.default_isac2_1_2,
            'executable': True,
            'has_path': 'sp_isac2_gpu.py',
            'typ': 'Class2d',
            'license': False,
            'category': 'External software',
            'allow_empty': [''],
            }


    ### 2D selection programs

    function_dict['Cinderella >=v0.3.1'] = {
            'plot': tp.update_batch,
            'plot_data': ti.import_cinderella_v0_3_1,
            'content': tc.default_cinderella_v0_3_1,
            'executable': True,
            'has_path': 'sp_cinderella_predict.py',
            'typ': 'Select2d',
            'license': False,
            'category': 'External software',
            'allow_empty': [],
            }

    ### 2D train programs

    function_dict['crYOLO_train >=v1.5.4'] = {
            'plot': tp.dummy,
            'plot_data': ti.dummy,
            'content': tc.default_cryolo_train_v1_5_4,
            'executable': True,
            'has_path': 'cryolo_train.py',
            'typ': 'Train2d',
            'license': True,
            'category': 'External software',
            'allow_empty': [],
            }
    function_dict['crYOLO_train >=v1.5.8'] = copy_mod.deepcopy(function_dict['crYOLO_train >=v1.5.4'])
    function_dict['crYOLO_train >=v1.5.8']['content'] = tc.default_cryolo_train_v1_5_8
    function_dict['crYOLO_train >=v1.7.4'] = copy_mod.deepcopy(function_dict['crYOLO_train >=v1.5.4'])
    function_dict['crYOLO_train >=v1.7.4']['content'] = tc.default_cryolo_train_v1_7_4


    ### auto processing programs

    function_dict['sp_auto >=v1.3'] = {
            'plot': tp.update_batch,
            'plot_data': ti.import_auto_sphire_v1_3,
            'content': tc.default_auto_sphire_v1_3,
            'executable': True,
            'has_path': 'sp_auto.py',
            'typ': 'Auto3d',
            'license': False,
            'category': 'External software',
            'allow_empty': [
                'SSH username',
                'SSH password',
                '--mtf',
                'input_volume',
                'input_mask',
                '--rviper_addition',
                '--adjust_rviper_addition',
                '--mask_rviper_addition',
                '--meridien_addition',
                '--sharpening_meridien_addition',
                ],
            }

    ### Other no executable stuff

    function_dict['Pipeline'] = {
            'plot': None,
            'plot_data': None,
            'content': tc.default_pipeline,
            'executable': False,
            'has_path': False,
            'typ': None,
            'license': False,
            'category': 'Internal settings',
            'allow_empty': [],
            }

    function_dict['Global'] = {
            'plot': None,
            'plot_data': None,
            'content': tc.default_global,
            'executable': False,
            'has_path': False,
            'typ': None,
            'license': False,
            'category': 'Internal settings',
            'allow_empty': ['-Gain'],
            }

    function_dict['Input'] = {
            'plot': None,
            'plot_data': None,
            'content': tc.default_input,
            'executable': False,
            'has_path': False,
            'typ': None,
            'license': False,
            'category': 'Internal settings',
            'allow_empty': [],
            }

    function_dict['Output'] = {
            'plot': None,
            'plot_data': None,
            'content': tc.default_general,
            'executable': False,
            'has_path': False,
            'typ': None,
            'license': False,
            'category': 'Internal settings',
            'allow_empty': ['Rename suffix', 'Rename prefix'],
            }

    function_dict['Mount'] = {
            'plot': None,
            'plot_data': None,
            'content': tc.default_mount,
            'executable': False,
            'has_path': False,
            'typ': None,
            'license': False,
            'category': 'TranSPHIRE settings',
            'allow_empty': [],
            }

    function_dict['Notification'] = {
            'plot': None,
            'plot_data': None,
            'content': tc.default_notification,
            'executable': False,
            'has_path': False,
            'typ': None,
            'license': False,
            'category': 'TranSPHIRE settings',
            'allow_empty': [],
            }
    function_dict['Notification_widget'] = {
            'plot': None,
            'plot_data': None,
            'content': tc.default_notification_widget,
            'executable': False,
            'has_path': False,
            'typ': None,
            'license': False,
            'category': 'TranSPHIRE settings',
            'allow_empty': [],
            }
    function_dict['Others'] = {
            'plot': None,
            'plot_data': None,
            'content': tc.default_others,
            'executable': False,
            'has_path': False,
            'typ': None,
            'license': False,
            'category': 'TranSPHIRE settings',
            'allow_empty': [],
            }
    function_dict['Font'] = {
            'plot': None,
            'plot_data': None,
            'content': tc.default_font,
            'executable': False,
            'has_path': False,
            'typ': None,
            'license': False,
            'category': 'TranSPHIRE settings',
            'allow_empty': [],
            }
    function_dict['Copy'] = {
            'plot': None,
            'plot_data': None,
            'content': tc.default_copy,
            'executable': False,
            'has_path': False,
            'typ': None,
            'license': False,
            'category': 'TranSPHIRE settings',
            'allow_empty': [],
            }
    function_dict['Path'] = {
            'plot': None,
            'plot_data': None,
            'content': tc.default_path,
            'executable': False,
            'has_path': False,
            'typ': None,
            'license': False,
            'category': 'TranSPHIRE settings',
            'allow_empty': [],
            }
    for key in function_dict:
        if 'old' in function_dict[key]:
            continue

        try:
            prog_name, _ = VERSION_RE.search(key).groups()
            newest_key = find_latest_version(prog_name, function_dict)
        except AttributeError:
            newest_key = key

        if newest_key == key:
            function_dict[key]['old'] = False
        else:
            function_dict[key]['old'] = True
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
    final_text = split_maximum(text, 80, ' ')
    dialog = MessageBox(is_question=False)
    dialog.setText(None, final_text)
    dialog.exec_()


def split_maximum(text, max_char, split_char=None):
    """
    Split text into chunks of size max_char containing whole words.

    Arguments:
    text - Text to split
    max_char - Maximum number of characters

    Returns:
    Splitted text
    """
    if split_char is None:
        add_char = ' '
    else:
        add_char = split_char
    new_text = []
    try:
        current_line = [text.split(split_char)[0]]
    except IndexError:
        return text
    except AttributeError:
        print(text)
    for entry in text.split(split_char)[1:]:
        if sum(map(len, current_line)) + len(current_line) + len(entry) > max_char:
            new_text.append(add_char.join(current_line))
            current_line = [entry]
        else:
            current_line.append(entry)
    new_text.append(add_char.join(current_line))
    return '\n{0}'.join(new_text).format(add_char if add_char.strip() else '')


def question(head, text):
    """
    Show a questions message box dialog.

    Arguments:
    head - Header of the window
    text - Text with the questions

    Return:
    True if No, False if Yes
    """
    message_box = MessageBox(is_question=True)
    message_box.setText(head, text)
    result = message_box.exec_()
    return result


def get_exclude_set_path(content):
    """
    Check the widget_2 variable, if the program should be loaded or not.

    Argument:
    content - Content as dictionary.

    Return:
    List of names to exclude
    """
    exclude_list = []

    for sub_content in content:
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
                    exclude_list.append('Plot {0}'.format('{0} feedback'.format(key)))
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
    content = {}
    function_dict = get_function_dict()

    for key in function_dict:
        if key in exclude_set:
            continue
        elif function_dict[key]['executable']:
            content.setdefault(function_dict[key]['typ'], []).append(key)

            if function_dict[key]['typ'] is None:
                print(key, 'is executable, but does not have a typ! Exit here!')
                sys.exit(1)
        else:
            pass

    for key, value in content.items():
        content[key] = list(sorted(value))

    return content


def reduce_copy_entries(exclude_set, content):
    """
    Reduce the number of options based on the exclude_set

    Arguments:
    exclude_set - Set of names to not consider
    content - Content of the widgets

    Return:
    None
    """
    valid_sub_items = get_unique_types()
    for item in content:
        for sub_item in item:
            values = None
            for entry in valid_sub_items:
                try:
                    values = sub_item[entry][1]['values']
                except KeyError:
                    continue
                else:
                    break
            if values is not None:
                for key in list(exclude_set):
                    if key in values:
                        values.remove(key)
                if sorted(values) == ['False', 'Later']:
                    sub_item[list(sub_item)[0]][0] = 'False'
                    exclude_set.add(list(sub_item)[0])
                else:
                    sub_item[list(sub_item)[0]][0] = values[0]


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
    default_file = '{0}/content_{1}.txt'.format(settings_folder, name.replace(' ', '_'))
    if not os.path.isfile(default_file):
        default_file = '{0}/SHARED/content_{1}.txt'.format(settings_folder, name.replace(' ', '_').replace('>=', ''))
    try:
        with open(default_file, 'r') as file_r:
            data = json.load(file_r)
    except FileNotFoundError:
        data = []

    return_dict = {
        'Copy_to_work': [],
        'Copy_to_backup': [],
        'Copy_to_hdd': [],
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
        try:
            return_dict[typ].append(name)
        except KeyError:
            return_dict[typ.replace('_', '_to_')].append(name)
    if return_dict['Copy']:
        print('')
        print('Old Copy type detected! Please edit the TranSPHIRE settings and change them to Import')
        print('')
        return_dict['Import'].extend(return_dict['Copy'])
        del return_dict['Copy']
    return return_dict


def get_content_gui(content, template_name, n_feedbacks):
    """
    Create content lists to load the GUI.

    Arguments:
    content - Content as dictionary.
    template_name = Name of the template!

    Return:
    Content as list
    """

    content_extern = reduce_programs()

    gui_content = [
        {
            'name': 'Notification_widget',
            'widget': NotificationContainer,
            'content': content[template_name]['Notification_widget'],
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
            'content_mount': content[template_name]['Mount'],
            'layout': 'TAB1',
            },
        {
            'name': 'Settings',
            'widget': TabDocker,
            'layout': 'TAB1',
            },
        {
            'name': 'Retrain',
            'widget': SelectDialog,
            'layout': 'TAB1',
            },
        {
            'name': 'Visualisation',
            'widget': TabDocker,
            'layout': 'TAB1',
            },
        {
            'name': 'Input',
            'widget': SettingsContainer,
            'content': content[template_name]['Input'],
            'content_mount': content[template_name]['Mount'],
            'layout': 'Settings',
            },
        {
            'name': 'Output',
            'widget': SettingsContainer,
            'content': content[template_name]['Output'],
            'content_others': content[template_name]['Others'],
            'layout': 'Settings',
            },
        {
            'name': 'Global',
            'widget': SettingsContainer,
            'content': content[template_name]['Global'],
            'layout': 'Settings',
            },
        {
            'name': 'Notification',
            'widget': SettingsContainer,
            'content': content[template_name]['Notification'],
            'layout': 'Settings',
            },
        {
            'name': 'Copy',
            'widget': SettingsContainer,
            'content': content[template_name]['Copy'],
            'layout': 'Settings',
            },
        {
            'name': 'Path',
            'widget': SettingsContainer,
            'content': content[template_name]['Path'],
            'layout': 'Settings',
            },
        {
            'name': 'Pipeline',
            'widget': SettingsContainer,
            'content': content[template_name]['Pipeline'],
            'layout': 'Settings',
            },
        ]

    for entry in get_unique_types():
        gui_content.append(
            {
                'name':entry,
                'widget': TabDocker,
                'layout': 'Settings',
                },
            )

    gui_content.extend([
        {
            'name': 'Status',
            'widget': StatusContainer,
            'content': content[template_name]['Others'],
            'content_mount': content[template_name]['Mount'],
            'content_pipeline': content[template_name]['Pipeline'],
            'content_font': content[template_name]['Font'],
            'layout': 'v2',
            },
        ])

    all_content = []
    for entry in get_unique_types():
        all_content.append([entry, content_extern[entry]])
        if not entry.startswith('Compress'):
            gui_content.append(
                {
                    'name': 'Plot {0}'.format(entry),
                    'widget': TabDocker,
                    'layout': 'Visualisation',
                    },
                )

    for typ, content_typ in all_content:
        for input_content in content_typ:
            gui_content.append({
                'name': input_content,
                'widget': SettingsContainer,
                'content': content[template_name][input_content],
                'layout': typ,
                })
            if not input_content.startswith('Compress'):

                for index in range(n_feedbacks+1):
                    if index == 0:
                        feedback_content = input_content
                    else:
                        feedback_content = '{0} feedback {1}'.format(input_content, index)
                    gui_content.append({
                        'name': 'Plot {0}'.format(feedback_content),
                        'widget': TabDocker,
                        'layout': 'Plot {0}'.format(typ),
                        })
                    gui_content.append({
                        'name': 'Overview',
                        'widget': PlotContainer,
                        'content': 'overview',
                        'plot_type': '{0}_feedback_{1}'.format(typ, index),
                        'layout': 'Plot {0}'.format(feedback_content),
                        })
                    gui_content.append({
                        'name': 'Show images',
                        'widget': PlotContainer,
                        'content': 'image',
                        'plot_type': '{0}_feedback_{1}'.format(typ, index),
                        'layout': 'Plot {0}'.format(feedback_content),
                        })
                    gui_content.append({
                        'name': 'Plot per micrograph',
                        'widget': PlotContainer,
                        'content': 'values',
                        'plot_type': '{0}_feedback_{1}'.format(typ, index),
                        'layout': 'Plot {0}'.format(feedback_content),
                        })
                    gui_content.append({
                        'name': 'Plot histogram',
                        'widget': PlotContainer,
                        'content': 'histogram',
                        'plot_type': '{0}_feedback_{1}'.format(typ, index),
                        'layout': 'Plot {0}'.format(feedback_content),
                        })
        #if typ == 'Motion':
        #    gui_content.append({
        #        'name': 'Frames',
        #        'widget': FrameContainer,
        #        'layout': typ,
        #        })

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
        background-image: url("{0}");
        }}
    QWidget#central {{
        background-color: {1};
        border-radius: 15px;
        }}
    QWidget#settings {{
        background-color: {2};
        border-radius: 15px
        }}
    QWidget#tab {{
        background-color: {2};
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
    QLineEdit:disabled {{ background-color: rgba(125, 125, 125) }}
    QComboBox {{ background-color: white }}
    QComboBox:disabled {{ background-color: rgba(125, 125, 125) }}
    QPushButton {{
        background-color: qradialgradient(cx:0.5, cy:0.5, fx:0.5, fy:0.5, radius:1, stop:0 white, stop:1 #f9eeb4);
        border-width: 1px;
        border-style:inset;
        padding: 1px;
        border-radius: 5px
        }}
    QPushButton:checked {{
        background-color: qradialgradient(cx:0.5, cy:0.5, fx:0.5, fy:0.5, radius:1, stop:0 white, stop:1 green);
        border-width: 1px;
        border-style:outset;
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
    settinger_widget_width = float(default[0][idx]['Setting widget'][0])
    settinger2_widget_width = float(default[0][idx]['Setting widget'][0])
    idx += 1
    setting_widget_width_large = float(default[0][idx]['Setting widget large'][0])
    idx += 1
    setting_widget_width_xlarge = float(default[0][idx]['Setting widget xlarge'][0])
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
    setting_widget_width = '{0}px'.format(font * setting_widget_width * adjust_width)
    settinger_widget_width = '{0}px'.format(font * settinger_widget_width * adjust_width * 0.9)
    settinger2_widget_width = '{0}px'.format(font * settinger2_widget_width * adjust_width * 0.1)
    setting_widget_width_large = '{0}px'.format(font * setting_widget_width_large * adjust_width)
    setting_widget_width_xlarge = '{0}px'.format(font * setting_widget_width_xlarge * adjust_width)
    status_name_width = '{0}px'.format(font * status_name_width * adjust_width)
    status_info_width = '{0}px'.format(font * status_info_width * adjust_width)
    status_quota_width = '{0}px'.format(font * status_quota_width * adjust_width)
    tab_width = '{0}px'.format(font * tab_width * adjust_width)
    widget_height_label = '{0}px'.format(font * widget_height * adjust_height / 2)
    widget_height = '{0}px'.format(font * widget_height * adjust_height)
    tab_height = '{0}px'.format(font * tab_height * adjust_height)

    # Style sheet
    style_widgets = """
    QWidget#central_raw {{
        background-image: url("{0}");
        }}
    QWidget#central {{
        background-color: {1};
        border-radius: 15px;
        }}
    QWidget#central_black {{
        background-color: {3};
        border-radius: 15px;
        }}
    QWidget#settings {{
        background-color: {2};
        border-radius: 15px
        }}
    QWidget#tab {{
        background-color: {2};
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

    QTabWidget#bot::pane {{
        border-top: 0px solid #C2C7CB;
        border-bottom: 2px solid #C2C7CB;
        }}

    QTabWidget#vertical::tab-bar {{
        alignment: left;
        }}
    QTabWidget#vertical::pane {{
        border-top: 0px solid #C2C7CB;
        border-left: 2px solid #C2C7CB;
        }}
    QTabWidget#vertical::tab {{
        min-width: 120px;
        }}

    QTabBar {{
        alignment: center;
        background-color: #C2C7CB
        }}
    QTabBar::pane {{
        border-right: 2px solid #C2C7CB;
        }}
    QTabBar::tab {{
        max-width: {4};
        max-height: {5};
        }}
    QTabBar::tab:disabled {{
        color: lightgrey;
        background-color: darkgrey
        }}

    QTabBar#vertical::tab {{
        max-width: {5};
        max-height: {4};
        }}

    QMessageBox {{
        background-image: url("{0}");
        color: white;
        }}
    QFileDialog {{
        background-color: {1}
        }}
    QScrollArea {{ background-color: transparent }}
    QDockWidget {{ background-color: rgb(229, 229, 229) }}

    """.format(
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
    QPushButton#global:checked {{
        background-color: qradialgradient(
            cx:0.5,
            cy:0.5,
            fx:0.5,
            fy:0.5,
            radius:1,
            stop:0 white,
            stop:1 green
            );
        border-width: 1px;
        border-style: outset;
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
    QPushButton#global {{
        min-width: {6};
        max-width: {6};
        max-height: {5}
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
            stop:1 #e34234
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
    QPushButton#button_entry:enabled {{
        background-color: qradialgradient(
            cx:0.5,
            cy:0.5,
            fx:0.5,
            fy:0.5,
            radius:1,
            stop:0 white,
            stop:1 #68a3c3
            );
        }}
    QPushButton#unmount {{
        background-color: qradialgradient(
            cx:0.5,
            cy:0.5,
            fx:0.5,
            fy:0.5,
            radius:8,
            stop:0 white,
            stop:1 #e34234
            );
        max-width: {3};
        min-width: {3}
        }}
    QPushButton#mount {{
        background-color: qradialgradient(
            cx:0.5,
            cy:0.5,
            fx:0.5,
            fy:0.5,
            radius:8,
            stop:0 white,
            stop:1 green
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
        border-color: #e34234;
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
        settinger2_widget_width,
        )

    label_style = """
    QLabel#picture {{ background-color: transparent }}
    QLabel#important {{ font-weight: bold; color: red; background-color: white; qproperty-alignment: AlignCenter }}
    QLabel#status_name {{ max-width: {1}; min-width: {1}; background-color: {0}; min-height: {5}; max-height: {5} }}
    QLabel#status_info {{ max-width: {2}; min-width: {2}; background-color: {0}; min-height: {5}; max-height: {5} }}
    QLabel#status_quota {{ max-width: {3}; min-width: {3}; background-color: {0}; min-height: {5}; max-height: {5} }}
    QLabel#setting {{ max-width: {4}; min-width: {4}; background-color: {0}; min-height: {5}; max-height: {5} }}
    QLabel#setting_large {{ max-width: {6}; min-width: {6}; background-color: {0}; min-height: {5}; max-height: {5} }}
    QLabel#setting_xlarge {{ min-width: {7}; background-color: {0}; min-height: {5}; max-height: {5} }}
    """.format(
        'transparent',
        status_name_width,
        status_info_width,
        status_quota_width,
        setting_widget_width,
        widget_height_label,
        setting_widget_width_large,
        setting_widget_width_xlarge,
        )

    edit_style = """
    QLineEdit {{ max-height: {7}; min-height: {7}; background-color: white }}
    QLineEdit#default_settings {{ min-width: {1}; max-width: 9999; background-color: white }}
    QLineEdit:disabled {{ background-color: {6} }}
    QLineEdit#settinger:enabled {{
        max-width: {9}; min-width: {9}; background-color: {0}; min-height: {7}; max-height: {7}
        }}
    QLineEdit#setting:enabled {{
        max-width: {1}; min-width: {1}; background-color: {0}; min-height: {7}; max-height: {7}
        }}
    QLineEdit#setting_large {{
        max-width: {8}; min-width: {8}
        }}
    QLineEdit#setting_xlarge {{
        min-width: {10}
        }}
    QLineEdit#setting_large:enabled {{
        max-width: {8}; min-width: {8}; background-color: {0}; min-height: {7}; max-height: {7}
        }}
    QLineEdit#setting_xlarge:enabled {{
        min-width: {10}; background-color: {0}; min-height: {7}; max-height: {7}
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
        settinger_widget_width,
        setting_widget_width_xlarge,
        )

    check_style = """
    QCheckBox {{ min-height: {1}; max-height: {1}; background-color: white }}
    QCheckBox#noti_check {{ max-width: {0}; min-width: {0}; background-color: white }}
    """.format(notification_check_width, widget_height)

    combo_style = """
    QComboBox {{ min-width: {4}; max-width: {4}; min-height: {3}; max-height: {3}; background-color: white }}
    QComboBox#settinger {{ min-width: {5}; max-width: {5}; min-height: {3}; max-height: {3}; background-color: white }}
    QComboBox#default_settings {{ min-width: {1}; max-width: 9999; background-color: white }}

    QComboBox:disabled {{ background-color: {2} }}
    QComboBox#settinger:disabled {{ background-color: {2} }}
    QComboBox#default_settings:disabled {{ background-color: {2} }}

    QComboBox QAbstractItemView {{
        background-color: white; selection-color: black; selection-background-color: lightgray
        }}
    QComboBox#noti_edit:enabled {{ max-width: {1}; min-width: {1}; background-color: {0} }}
    """.format(
        '#5d995d',
        notification_edit_width,
        'rgba(150,150,150,200)',
        widget_height,
        setting_widget_width,
        settinger_widget_width,
        )

    tool_style = """
    QToolTip {0}
    """.format(tooltip_style())

    plain_style = """
    QPlainTextEdit#status { background-color: rgba(229, 229, 229, 50); color: white }
    QPlainTextEdit#dialog { background-color: rgba(229, 229, 229, 50); color: black }
    """


    style = '\n'.join([style_widgets, button_style, label_style, edit_style, check_style, combo_style, tool_style, plain_style])
    return style

def tooltip_style():
    return '{ color: black; background-color: white }'


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


def get_color(typ):
    """
    Color defined for the type

    Arguments:
    typ - Typ of color

    Return:
    Color string
    """
    # Color table: https://davidmathlogic.com/colorblind/#%23E34234-%23FFFF00-%23FFFFFF-%23000000-%23B200FF-%2368A3C3-%23C3A368-%23D9D9D9-%23E34234-%2390EE90-%23FF336D-%23FF5C33
    if typ == 'error':
        color = '#e34234'
    elif typ == 'global':
        color = '#FFFF00'
    elif typ == 'white':
        color = '#FFFFFF'
    elif typ == 'unchanged':
        color = '#000000'
    elif typ == 'changed':
        color = 'B200FF'
    elif typ == 'True':
        color = '#68a3c3'
    elif typ == 'False':
        color = '#c3a368'
    elif typ == 'Finished':
        color = '#d9d9d9'
    elif typ == 'Skipped':
        color = '#d9d9d9'
    elif typ == 'Later':
        color = '#d9d9d9'
    elif typ == 'Error':
        color = '#FF5C33'
    elif typ == 'Running':
        color = '#90EE90'
    elif typ == 'Waiting':
        color = '#FFC14D'
    elif typ == 'Stopped':
        color = '#ff5c33'
    else:
        msg = 'Style not known! Go for black!'
        print(msg, ":", typ)
        message(msg)
        color = '#000000'
    return color


def get_style(typ):
    """
    Style colores for the content of widgets.

    Arguments:
    typ - Typ of color

    Return:
    Color string
    """
    color = get_color(typ)

    return 'QPushButton {{color: {0}}} QLabel {{color: {0}}} QLineEdit {{color: {0}}} QComboBox {{color: {0}}}'.format(color)


def rebin(arr, new_shape):
    shape = (new_shape[0], arr.shape[0] // new_shape[0],
             new_shape[1], arr.shape[1] // new_shape[1])
    return arr.reshape(shape).mean(-1).mean(1)

from .messagebox import MessageBox
from .mountcontainer import MountContainer
from .statuscontainer import StatusContainer
from .settingscontainer import SettingsContainer
from .buttoncontainer import ButtonContainer
from .notificationcontainer import NotificationContainer
from .plotcontainer import PlotContainer
from .tabdocker import TabDocker
from .selectdialog import SelectDialog
