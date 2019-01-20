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
import glob
import re
import numpy as np
from transphire import transphire_utils as tu


def get_header(input_file):
    """
    Extract header information from a relion star file.

    Arguments:
    input_file - Input star file

    Return:
    Color string
    """
    with open(input_file, 'r') as read:
        lines = read.readlines()
    header = []
    idx = None
    for idx, line in enumerate(lines):
        line = line.lstrip().rstrip()
        if line.startswith('_rln'):
            name = line.split()[0]
            name = name.replace('_rlnFinalResolution', '_rlnCtfMaxResolution')
            if name == '_rlnMicrographName' or \
                    name == '_rlnCtfImage':
                header.append((name, '|U1200'))
            else:
                header.append((name, '<f8'))
        elif line == '' or line == 'data_' or line == 'loop_':
            continue
        else:
            break

    if idx is None:
        raise ValueError
    else:
        return header, idx


def get_dtype_dict():
    """
    Dtype of the data plot array.

    Arguments:
    None

    Return:
    Dtype dict
    """
    dtype = {}
    dtype['motion'] = [
        ('overall drift', '<f8'),
        ('average drift per frame', '<f8'),
        ('first frame drift', '<f8'),
        ('average drift per frame without first', '<f8'),
        ('file_name', '|U1200'),
        ('image', '|U1200'),
        ]
    dtype['ctf'] = [
        ('mic_number', '<f8'),
        ('defocus', '<f8'),
        ('defocus_diff', '<f8'),
        ('astigmatism', '<f8'),
        ('phase_shift', '<f8'),
        ('cross_corr', '<f8'),
        ('limit', '<f8'),
        ('file_name', '|U1200'),
        ('image', '|U1200'),
        ]
    dtype['picking'] = [
        ('particles', '<i8'),
        ('file_name', '|U1200'),
        ('image', '|U1200'),
        ]
    dtype['Gctf v1.06'] = [
        ('defocus_1', '<f8'),
        ('defocus_2', '<f8'),
        ('astigmatism', '<f8'),
        ('phase_shift', '<f8'),
        ('cross_corr', '<f8'),
        ('limit', '<f8'),
        ('file_name', '|U1200')
        ]
    dtype['Gctf v1.18'] = [
        ('defocus_1', '<f8'),
        ('defocus_2', '<f8'),
        ('astigmatism', '<f8'),
        ('phase_shift', '<f8'),
        ('cross_corr', '<f8'),
        ('limit', '<f8'),
        ('file_name', '|U1200')
        ]
    dtype['CTER v1.0'] = [
        ('defocus_1', '<f8'),
        ('defocus_2', '<f8'),
        ('astigmatism', '<f8'),
        ('phase_shift', '<f8'),
        ('cross_corr', '<f8'),
        ('limit', '<f8'),
        ('file_name', '|U1200')
        ]
    dtype['CTFFIND4 v4.1.10'] = [
        ('mic_number', '<f8'),
        ('defocus_1', '<f8'),
        ('defocus_2', '<f8'),
        ('astigmatism', '<f8'),
        ('phase_shift', '<f8'),
        ('cross_corr', '<f8'),
        ('limit', '<f8'),
        ('file_name', '|U1200')
        ]
    dtype['CTFFIND4 v4.1.8'] = [
        ('mic_number', '<f8'),
        ('defocus_1', '<f8'),
        ('defocus_2', '<f8'),
        ('astigmatism', '<f8'),
        ('phase_shift', '<f8'),
        ('cross_corr', '<f8'),
        ('limit', '<f8'),
        ('file_name', '|U1200')
        ]
    dtype['crYOLO v1.0.4'] = [
        ('coord_x', '<f8'),
        ('coord_y', '<f8'),
        ('box_x', '<f8'),
        ('box_y', '<f8'),
        ('file_name', '|U1200'),
        ]
    dtype['crYOLO v1.0.5'] = [
        ('coord_x', '<f8'),
        ('coord_y', '<f8'),
        ('box_x', '<f8'),
        ('box_y', '<f8'),
        ('file_name', '|U1200'),
        ]
    dtype['crYOLO v1.1.0'] = [
        ('coord_x', '<f8'),
        ('coord_y', '<f8'),
        ('box_x', '<f8'),
        ('box_y', '<f8'),
        ('file_name', '|U1200'),
        ]
    return dtype


def get_transphire_dict():
    """
    Translate transphire ctf dict into relion star file information.

    Arguments:
    None

    Return:
    Dtype dict
    """
    transphire_dict = {}
    transphire_dict = {
        'defocus_1': '_rlnDefocusU',
        'defocus_2': '_rlnDefocusV',
        'defocus': '_rlnDefocusU',
        'defocus_diff': '_rlnDefocusV',
        'astigmatism': '_rlnDefocusAngle',
        'phase_shift': '_rlnPhaseShift',
        'cross_corr': '_rlnCtfFigureOfMerit',
        'limit': '_rlnCtfMaxResolution',
        'file_name': '_rlnMicrographName',
        }
    return transphire_dict


def get_relion_dict():
    """
    Translate relion star file information to dtype dict.

    Arguments:
    None

    Return:
    Dtype dict
    """
    relion_dict = {}
    relion_dict = {
        '_rlnDefocusU': 'defocus_1',
        '_rlnDefocusV': 'defocus_2',
        '_rlnDefocusAngle': 'astigmatism',
        '_rlnPhaseShift': 'phase_shift',
        '_rlnCtfFigureOfMerit': 'cross_corr',
        '_rlnCtfMaxResolution': 'limit',
        '_rlnMicrographName': 'file_name',
        }
    return relion_dict


def get_dtype_import_dict():
    """
    Dtype of the file to import.

    Arguments:
    None

    Return:
    Dtype dict
    """
    dtype_import = {}
    dtype_import['CTER v1.0'] = [
        ('defocus', '<f8'),
        ('cs', '<f8'),
        ('volt', '<f8'),
        ('apix', '<f8'),
        ('bfac', '<f8'),
        ('amplitude_contrast', '<f8'),
        ('astigmatism_amplitude', '<f8'),
        ('astigmatism_angle', '<f8'),
        ('standard_deviation_defocus', '<f8'),
        ('standard_deviation_amplitude_contrast', '<f8'),
        ('standard_deviation_astigmatism_amplitude', '<f8'),
        ('standard_deviation_astigmatism_angle', '<f8'),
        ('coefficient_of_variation_of_defocus', '<f8'),
        ('coefficient_of_astigmatism_amplitude', '<f8'),
        ('limit_defocus', '<f8'),
        ('limit_defocus_and_astigmatism', '<f8'),
        ('limit_pixel_error', '<f8'),
        ('limit_maximum', '<f8'),
        ('reserved_spot', '<f8'),
        ('const_amplitude_contrast', '<f8'),
        ('phase_shift', '<f8'),
        ('file_name', '|U1200'),
        ]
    dtype_import['Gctf v1.06'] = [
        ('defocus_1', '<f8'),
        ('defocus_2', '<f8'),
        ('astigmatism', '<f8'),
        ('phase_shift', '<f8'),
        ('cross_corr', '<f8'),
        ('limit', '<f8')
        ]
    dtype_import['Gctf v1.18'] = [
        ('defocus_1', '<f8'),
        ('defocus_2', '<f8'),
        ('astigmatism', '<f8'),
        ('phase_shift', '<f8'),
        ('cross_corr', '<f8'),
        ('limit', '<f8')
        ]
    dtype_import['CTFFIND4 v4.1.10'] = [
        ('mic_number', '<f8'),
        ('defocus_1', '<f8'),
        ('defocus_2', '<f8'),
        ('astigmatism', '<f8'),
        ('phase_shift', '<f8'),
        ('cross_corr', '<f8'),
        ('limit', '<f8')
        ]
    dtype_import['CTFFIND4 v4.1.8'] = [
        ('mic_number', '<f8'),
        ('defocus_1', '<f8'),
        ('defocus_2', '<f8'),
        ('astigmatism', '<f8'),
        ('phase_shift', '<f8'),
        ('cross_corr', '<f8'),
        ('limit', '<f8')
        ]
    dtype_import['MotionCor2 v1.0.0'] = [
        ('frame_number', '<f8'),
        ('shift_x', '<f8'),
        ('shift_y', '<f8')
        ]
    dtype_import['MotionCor2 v1.0.5'] = [
        ('frame_number', '<f8'),
        ('shift_x', '<f8'),
        ('shift_y', '<f8')
        ]
    dtype_import['MotionCor2 v1.1.0'] = [
        ('frame_number', '<f8'),
        ('shift_x', '<f8'),
        ('shift_y', '<f8')
        ]
    dtype_import['crYOLO v1.0.4'] = [
        ('coord_x', '<f8'),
        ('coord_y', '<f8'),
        ('box_x', '<f8'),
        ('box_y', '<f8'),
        ]
    dtype_import['crYOLO v1.0.5'] = [
        ('coord_x', '<f8'),
        ('coord_y', '<f8'),
        ('box_x', '<f8'),
        ('box_y', '<f8'),
        ]
    dtype_import['crYOLO v1.1.0'] = [
        ('coord_x', '<f8'),
        ('coord_y', '<f8'),
        ('box_x', '<f8'),
        ('box_y', '<f8'),
        ]
    return dtype_import


def import_ctffind_v4_1_10(name, directory_name):
    """
    Import ctf information for CTFFIND v4.1.10.
    Defocus in angstrom, phase shift in degree.

    Arguments:
    name - Name of ctf program
    directory_name - Name of the directory to search for files

    Return:
    Imported data
    """
    return import_ctffind_v4_1_8(name, directory_name)


def import_ctffind_v4_1_8(name, directory_name):
    """
    Import ctf information for CTFFIND v4.1.8.
    Defocus in angstrom, phase shift in degree.

    Arguments:
    name - Name of ctf program
    directory_name - Name of the directory to search for files

    Return:
    Imported data
    """
    files = [
        entry for entry in glob.glob(
        '{0}/*.txt'.format(directory_name)
        ) if not entry.endswith('_avrot.txt')
        ]

    useable_files = []
    for file_name in files:
        try:
            data_name = np.genfromtxt(
                file_name,
                dtype=get_dtype_import_dict()[name],
                )
        except ValueError:
            continue
        except IOError:
            continue
        else:
            if data_name.size > 0:
                useable_files.append([file_name, data_name])
            else:
                continue

    useable_files_jpg = [
        tu.get_name(entry)
        for entry in glob.glob(os.path.join(directory_name, 'jpg*', '*.jpg'))
        ]
    useable_files = [
        [file_name, data_name]
        for file_name, data_name in sorted(useable_files)
        if tu.get_name(file_name) in useable_files_jpg
        ]

    data = np.zeros(
        len(useable_files),
        dtype=get_dtype_dict()['ctf']
        )
    data_original = np.zeros(
        len(useable_files),
        dtype=get_dtype_dict()[name]
        )
    data = np.atleast_1d(data)
    data_original = np.atleast_1d(data_original)
    data.fill(0)
    data_original.fill(0)

    file_names_jpg = [os.path.basename(os.path.splitext(entry[0])[0]) for entry in useable_files]
    jpgs = sorted([os.path.basename(entry) for entry in glob.glob(os.path.join(directory_name, 'jpg*'))])
    jpg_names = [';;;'.join([os.path.join(directory_name, jpg_dir_name, '{0}.jpg'.format(entry)) for jpg_dir_name in jpgs]) for entry in file_names_jpg]

    match_re = re.compile('# Input file: (.*?) ; Number of micrographs: 1')

    file_names = []
    for file_name, _ in useable_files:
        with open(file_name, 'r') as read:
            content = read.read()
        file_names.append(match_re.search(content).group(1))

    data_original['file_name'] = file_names
    data['file_name'] = file_names
    for dtype_name in data_original.dtype.names:
        if dtype_name == 'file_name':
            continue
        if dtype_name == 'phase_shift':
            data_original[dtype_name] = [np.degrees(entry[1][dtype_name]) for entry in useable_files]
        else:
            data_original[dtype_name] = [entry[1][dtype_name] for entry in useable_files]

        if dtype_name == 'defocus_1':
            data['defocus'] = [(entry[1]['defocus_2'] + entry[1]['defocus_1']) / 2 for entry in useable_files]
        elif dtype_name == 'defocus_2':
            data['defocus_diff'] = [entry[1]['defocus_2'] - entry[1]['defocus_1'] for entry in useable_files]
        elif dtype_name == 'phase_shift':
            data[dtype_name] = [np.degrees(entry[1][dtype_name]) for entry in useable_files]
        else:
            data[dtype_name] = [entry[1][dtype_name] for entry in useable_files]
    data['image'] = jpg_names

    #for idx, file_name in sorted(enumerate(useable_files)):

    #    try:
    #        data_name = np.genfromtxt(
    #            file_name,
    #            dtype=get_dtype_import_dict()[name],
    #            )
    #    except IOError:
    #        continue
    #    else:
    #        if data_name.size == 0:
    #            continue
    #        else:
    #            pass

    #    data[idx]['file_name'] = file_name
    #    input_name = None

    #    with open(file_name, 'r') as read:
    #        for line in read.readlines():
    #            match_re = re.match('# Input file: (.*?) ; Number of micrographs: 1', line)
    #            if match_re is not None:
    #                input_name = match_re.group(1)
    #            else:
    #                pass
    #    if input_name is None:
    #        raise IOError(
    #            'Could not read {0} file name! Please contact the TranSPHIRE authors! -- {1}'.format(
    #                name,
    #                file_name
    #                )
    #            )
    #    else:
    #        data_original[idx]['file_name'] = input_name

    #    for entry in data_name.dtype.names:
    #        if entry == 'phase_shift':
    #            data_original[idx][entry] = np.degrees(data_name[entry])
    #        else:
    #            data_original[idx][entry] = data_name[entry]

    #        if entry == 'defocus_1':
    #            data[idx]['defocus'] = (data_name['defocus_1']+data_name['defocus_2'])/2
    #        elif entry == 'defocus_2':
    #            data[idx]['defocus_diff'] = data_name['defocus_2']-data_name['defocus_1']
    #        elif entry == 'phase_shift':
    #            data[idx][entry] = np.degrees(data_name[entry])
    #        else:
    #            data[idx][entry] = data_name[entry]

    #    jpg_name = os.path.join(
    #        directory_name,
    #        'jpg*',
    #        '{0}.jpg'.format(os.path.basename(os.path.splitext(file_name)[0]))
    #        )
    #    data[idx]['image'] = ';;;'.join(glob.glob(jpg_name))

    data = np.sort(data, order='file_name')
    data_original = np.sort(data_original, order='file_name')
    return data, data_original


def import_gctf_v1_18(name, directory_name):
    """
    Import ctf information for Gctf v1.18.
    Defocus in angstrom, phase shift in degree.

    Arguments:
    name - Name of ctf program
    directory_name - Name of the directory to search for files

    Return:
    Imported data
    """
    data, data_original = import_gctf_v1_06(name=name, directory_name=directory_name)
    return data, data_original


def import_gctf_v1_06(name, directory_name):
    """
    Import ctf information for Gctf v1.06.
    Defocus in angstrom, phase shift in degree.

    Arguments:
    name - Name of ctf program
    directory_name - Name of the directory to search for files

    Return:
    Imported data
    """
    suffix = '_gctf'

    useable_files = []
    for file_name in sorted(glob.glob('{0}/*{1}.star'.format(directory_name, suffix))):
        try:
            dtype, max_header = get_header(input_file=file_name)
            data_name = np.genfromtxt(
                file_name,
                dtype=dtype,
                skip_header=max_header,
                )
        except ValueError:
            continue
        except IOError:
            continue
        else:
            if data_name.size > 0:
                useable_files.append([file_name, data_name])
            else:
                continue

    useable_files_jpg = [
        tu.get_name(entry)
        for entry in glob.glob(os.path.join(directory_name, 'jpg*', '*.jpg'))
        ]
    useable_files = [
        [file_name, data_name]
        for file_name, data_name in sorted(useable_files)
        if tu.get_name(tu.get_name(file_name)) in useable_files_jpg
        ]

    data = np.zeros(
        len(useable_files),
        dtype=get_dtype_dict()['ctf']
        )
    data_original = np.zeros(
        len(useable_files),
        dtype=get_dtype_dict()[name]
        )
    data = np.atleast_1d(data)
    data_original = np.atleast_1d(data_original)
    data.fill(0)
    data_original.fill(0)
    if not useable_files:
        return None, None

    file_names_jpg = [tu.get_name(tu.get_name(entry[0])) for entry in useable_files]
    jpgs = sorted([os.path.basename(entry) for entry in glob.glob(os.path.join(directory_name, 'jpg*'))])
    jpg_names = [';;;'.join([os.path.join(directory_name, jpg_dir_name, '{0}.jpg'.format(entry)) for jpg_dir_name in jpgs]) for entry in file_names_jpg]

    relion_dict = get_relion_dict()
    for dtype_name in useable_files[0][1].dtype.names:
        try:
            transphire_name = relion_dict[dtype_name]
        except KeyError:
            continue

        try:
            data_original[transphire_name] = np.nan_to_num([entry[1][dtype_name] for entry in useable_files])
        except ValueError:
            data_original[transphire_name] = 0

        if transphire_name == 'defocus_1':
            data['defocus'] = [(entry[1]['_rlnDefocusU']+entry[1]['_rlnDefocusV']) / 2 for entry in useable_files]
        elif transphire_name == 'defocus_2':
            data['defocus_diff'] = [entry[1]['_rlnDefocusV']-entry[1]['_rlnDefocusU'] for entry in useable_files]
        else:
            data[transphire_name] = np.nan_to_num([entry[1][dtype_name] for entry in useable_files])
    data['image'] = jpg_names

    #for idx, file_name in enumerate(useable_files):
    #    try:
    #        dtype, max_header = get_header(input_file=file_name)
    #    except ValueError:
    #        print('Could not read header of {0}!'.format(file_name))
    #        data, data_original =  None, None
    #        break

    #    try:
    #        data_name = np.genfromtxt(
    #            file_name,
    #            dtype=dtype,
    #            skip_header=max_header,
    #            )
    #    except IOError:
    #        continue
    #    else:
    #        if data_name.size == 0:
    #            continue
    #        else:
    #            pass

    #    for dtype_name in data_name.dtype.names:
    #        try:
    #            transphire_name = relion_dict[dtype_name]
    #        except KeyError:
    #            continue

    #        try:
    #            data_original[idx][transphire_name] = np.nan_to_num(data_name[dtype_name])
    #        except ValueError:
    #            data_original[idx][transphire_name] = 0

    #        if transphire_name == 'defocus_1':
    #            try:
    #                data[idx]['defocus'] = (
    #                    data_name['_rlnDefocusU']+data_name['_rlnDefocusV']
    #                    ) / 2
    #            except ValueError:
    #                data[idx][transphire_name] = 0
    #        elif transphire_name == 'defocus_2':
    #            try:
    #                data[idx]['defocus_diff'] = data_name['_rlnDefocusV']-data_name['_rlnDefocusU']
    #            except ValueError:
    #                data[idx][transphire_name] = 0
    #        else:
    #            try:
    #                data[idx][transphire_name] = np.nan_to_num(data_name[dtype_name])
    #            except ValueError:
    #                data[idx][transphire_name] = 0

    #    jpg_name = os.path.join(
    #        directory_name,
    #        'jpg*',
    #        '{0}.jpg'.format(tu.get_name(tu.get_name(file_name)))
    #        )
    #    data[idx]['image'] = ';;;'.join(glob.glob(jpg_name))

    data = np.sort(data, order='file_name')
    data_original = np.sort(data_original, order='file_name')
    return data, data_original


def import_cter_v1_0(name, directory_name):
    """
    Import ctf information for CTER v1.0.
    Defocus in angstrom, phase shift in degree.

    Arguments:
    name - Name of ctf program
    directory_name - Name of the directory to search for files

    Return:
    Imported data
    """

    useable_files = []
    for file_name in sorted(glob.glob('{0}/*/partres.txt'.format(directory_name))):
        try:
            data_name = np.genfromtxt(
                file_name,
                dtype=get_dtype_import_dict()[name],
                )
        except ValueError:
            continue
        except IOError:
            continue
        else:
            if data_name.size > 0:
                useable_files.append([file_name, data_name])
            else:
                continue

    useable_files_jpg = [
        tu.get_name(entry)
        for entry in glob.glob(os.path.join(directory_name, 'jpg*', '*.jpg'))
        ]
    useable_files = [
        [file_name, data_name]
        for file_name, data_name in useable_files
        if os.path.split(os.path.dirname(file_name))[-1] in useable_files_jpg
        ]

    data = np.zeros(
        len(useable_files),
        dtype=get_dtype_dict()['ctf']
        )
    data_original = np.zeros(
        len(useable_files),
        dtype=get_dtype_import_dict()[name]
        )
    data = np.atleast_1d(data)
    data_original = np.atleast_1d(data_original)
    data.fill(0)
    data_original.fill(0)

    file_names_jpg = [os.path.split(os.path.dirname(entry[0]))[-1] for entry in useable_files]
    jpgs = sorted([os.path.basename(entry) for entry in glob.glob(os.path.join(directory_name, 'jpg*'))])
    jpg_names = [';;;'.join([os.path.join(directory_name, jpg_dir_name, '{0}.jpg'.format(entry)) for jpg_dir_name in jpgs if os.path.exists(os.path.join(directory_name, jpg_dir_name, '{0}.jpg'.format(entry)))]) for entry in file_names_jpg]


    for dtype_name in data_original.dtype.names:
        data_original[dtype_name] = [entry[1][dtype_name] for entry in useable_files]
        if dtype_name == 'defocus':
            data['defocus'] = [entry[1][dtype_name] * 10000 for entry in useable_files]
        elif dtype_name == 'astigmatism_amplitude':
            data['defocus_diff'] = [entry[1][dtype_name] * 10000 for entry in useable_files]
        elif dtype_name == 'astigmatism_angle':
            data['astigmatism'] = [45 - entry[1][dtype_name] for entry in useable_files]
        elif dtype_name == 'phase_shift':
            data['phase_shift'] = [entry[1][dtype_name] for entry in useable_files]
        elif dtype_name == 'file_name':
            data['file_name'] = [entry[1][dtype_name] for entry in useable_files]
        elif dtype_name == 'standard_deviation_defocus':
            data['cross_corr'] = [entry[1][dtype_name] for entry in useable_files]
        elif dtype_name == 'limit_defocus_and_astigmatism':
            data['limit'] = [1 / entry[1][dtype_name] if entry[1][dtype_name] != 0 else 1 / entry[1]['limit_pixel_error'] for entry in useable_files]
        else:
            continue
    data['image'] = jpg_names

    #for idx, file_name in sorted(enumerate(useable_files)):
    #    try:
    #        data_name = np.genfromtxt(
    #            file_name,
    #            dtype=get_dtype_import_dict()[name],
    #            )
    #    except IOError:
    #        continue
    #    else:
    #        if data_name.size == 0:
    #            continue
    #        else:
    #            pass

    #    for entry in data_name.dtype.names:
    #        data_original[idx][entry] = data_name[entry]
    #        if entry == 'defocus':
    #            data[idx][entry] = data_name[entry] * 10000
    #        elif entry == 'astigmatism_amplitude':
    #            data[idx]['defocus_diff'] = data_name[entry] * 10000
    #        elif entry == 'astigmatism_angle':
    #            data[idx]['astigmatism'] = 45 - data_name[entry]
    #        elif entry == 'phase_shift':
    #            data[idx]['phase_shift'] = data_name[entry]
    #        elif entry == 'file_name':
    #            data[idx]['file_name'] = data_name[entry]
    #        elif entry == 'standard_deviation_defocus':
    #            data[idx]['cross_corr'] = data_name[entry]
    #        elif entry == 'limit_defocus_and_astigmatism':
    #            if data_name[entry] == 0:
    #                value = data_name['limit_pixel_error']
    #            else:
    #                value = data_name[entry]

    #            data[idx]['limit'] = 1 / value
    #        else:
    #            continue

    #    jpg_name = os.path.join(
    #        directory_name,
    #        'jpg*',
    #        '{0}.jpg'.format(os.path.split(os.path.dirname(file_name))[-1])
    #        )
    #    data[idx]['image'] = ';;;'.join(glob.glob(jpg_name))

    data = np.sort(data, order='file_name')
    data_original = np.sort(data_original, order='file_name')
    return data, data_original


def import_motion_cor_2_v1_0_0(name, directory_name):
    """
    Import motion information for MotionCor2 v1.0.0.

    Arguments:
    name - Name of motion program
    directory_name - Name of the directory to search for files

    Return:
    Imported data
    """
    directory_names = glob.glob('{0}/*_with_DW_log'.format(directory_name))
    files = np.array(
        [
            entry
            for directory_name in directory_names
            for entry in glob.glob('{0}/*-Full.log'.format(directory_name))
            ],
        dtype=str
        )

    useable_files = []
    for file_name in files:
        try:
            array = np.genfromtxt(
                file_name,
                dtype=get_dtype_import_dict()[name]
                )
        except ValueError:
            continue
        except IOError:
            continue
        else:
            if array.size > 0:
                useable_files.append(file_name)
            else:
                continue

    useable_files_jpg = set([
        tu.get_name(entry)
        for entry in glob.glob(os.path.join(directory_name, 'jpg*', '*.jpg'))
        ])
    useable_files = [
        file_name
        for file_name in sorted(useable_files)
        if tu.get_name(tu.get_name(file_name)) in useable_files_jpg
        ]

    data = np.zeros(
        len(useable_files),
        dtype=get_dtype_dict()['motion']
        )
    data = np.atleast_1d(data)
    data_original = []
    for idx, file_name in enumerate(useable_files):
        try:
            data_name = np.genfromtxt(
                file_name,
                dtype=get_dtype_import_dict()[name]
                )
        except IOError:
            continue
        else:
            if data_name.size == 0:
                continue
            else:
                pass

        data_original.append([data_name['shift_x'], data_name['shift_y']])
        data[idx]['file_name'] = file_name
        shift_x = np.array([
            data_name['shift_x'][i+1] - data_name['shift_x'][i] \
            for i in range(0, int(data_name['frame_number'][-1]-1))
            ])
        shift_y = np.array([
            data_name['shift_y'][i+1] - data_name['shift_y'][i] \
            for i in range(0, int(data_name['frame_number'][-1]-1))
            ])
        for entry in data.dtype.names:
            if entry == 'overall drift':
                data[idx][entry] = np.sum(np.sqrt(shift_x**2 + shift_y**2))
            elif entry == 'average drift per frame':
                data[idx][entry] = np.sum(np.sqrt(shift_x**2 + shift_y**2))/len(shift_x)
            elif entry == 'first frame drift':
                data[idx][entry] = np.sqrt(shift_x[0]**2 + shift_y[0]**2)
            elif entry == 'average drift per frame without first':
                data[idx][entry] = np.sum(np.sqrt(shift_x[1:]**2 + shift_y[1:]**2))/len(shift_x)
            else:
                pass

        jpg_name = os.path.join(
            directory_name,
            'jpg*',
            '{0}.jpg'.format(tu.get_name(tu.get_name(file_name)))
            )
        data[idx]['image'] = ';;;'.join(glob.glob(jpg_name))

    sort_idx = np.argsort(data, order='file_name')
    data = data[sort_idx]
    data_original = np.array(data_original)[sort_idx]
    return data, data_original


def import_motion_cor_2_v1_0_5(name, directory_name):
    """
    Import motion information for MotionCor2 v1.0.5.

    Arguments:
    name - Name of ctf program
    directory_name - Name of the directory to search for files

    Return:
    Imported data
    """
    data, data_original = import_motion_cor_2_v1_0_0(name=name, directory_name=directory_name)
    return data, data_original


def import_motion_cor_2_v1_1_0(name, directory_name):
    """
    Import motion information for MotionCor2 v1.1.0.

    Arguments:
    name - Name of ctf program
    directory_name - Name of the directory to search for files

    Return:
    Imported data
    """
    data, data_original = import_motion_cor_2_v1_0_0(name=name, directory_name=directory_name)
    return data, data_original


def import_cryolo_v1_0_5(name, directory_name):
    """
    Import picking information for crYOLO v1.0.5.

    Arguments:
    name - Name of picking program
    directory_name - Name of the directory to search for files

    Return:
    Imported data
    """
    return import_cryolo_v1_0_4(name, directory_name)


def import_cryolo_v1_1_0(name, directory_name):
    """
    Import picking information for crYOLO v1.1.0.

    Arguments:
    name - Name of picking program
    directory_name - Name of the directory to search for files

    Return:
    Imported data
    """
    return import_cryolo_v1_0_4(name, directory_name)


def import_cryolo_v1_2_2(name, directory_name):
    """
    Import picking information for crYOLO v1.2.2.

    Arguments:
    name - Name of picking program
    directory_name - Name of the directory to search for files

    Return:
    Imported data
    """
    return import_cryolo_v1_0_4(name, directory_name, sub_directory='EMAN')


def import_cryolo_v1_2_1(name, directory_name):
    """
    Import picking information for crYOLO v1.2.2.

    Arguments:
    name - Name of picking program
    directory_name - Name of the directory to search for files

    Return:
    Imported data
    """
    return import_cryolo_v1_0_4(name, directory_name)


def import_cryolo_v1_0_4(name, directory_name, sub_directory=''):
    """
    Import picking information for crYOLO v1.0.4.

    Arguments:
    name - Name of picking program
    directory_name - Name of the directory to search for files

    Return:
    Imported data
    """
    box_files = glob.glob(os.path.join(directory_name, sub_directory, '*.{0}'.format('box')))
    if not box_files:
        box_files = glob.glob(os.path.join(directory_name, sub_directory, '*.{0}'.format('txt')))

    files_box = np.array(box_files)
    useable_files = []
    for file_name in files_box:
        try:
            data_imported = np.genfromtxt(file_name)
        except ValueError:
            useable_files.append([os.path.splitext(os.path.basename(file_name))[0], 0])
        except IOError:
            continue
        else:
            useable_files.append([os.path.splitext(os.path.basename(file_name))[0], data_imported.shape[0]])

    useable_files_jpg = [
        tu.get_name(entry)
        for entry in glob.glob(os.path.join(directory_name, 'jpg*', '*.jpg'))
        ]
    useable_files = [
        [file_name, size]
        for file_name, size in sorted(useable_files)
        if tu.get_name(file_name) in useable_files_jpg
        ]

    data = np.zeros(
        len(useable_files),
        dtype=get_dtype_dict()['picking']
        )
    data = np.atleast_1d(data)
    file_names = [entry[0] for entry in useable_files]
    jpgs = sorted([os.path.basename(entry) for entry in glob.glob(os.path.join(directory_name, 'jpg*'))])
    jpg_names = [';;;'.join([os.path.join(directory_name, jpg_dir_name, '{0}.jpg'.format(entry)) for jpg_dir_name in jpgs]) for entry in file_names]
    sizes = [entry[1] for entry in useable_files]
    data['file_name'] = file_names
    data['particles'] = sizes
    data['image'] = jpg_names
    #for idx, entry in enumerate(useable_files):
    #    file_name = entry[0]
    #    size = entry[1]
    #    jpg_name = os.path.join(
    #        directory_name,
    #        'jpg*',
    #        '{0}.jpg'.format(file_name)
    #        )
    #    data[idx]['file_name'] = file_name
    #    data[idx]['particles'] = size
    #    data[idx]['image'] = ';;;'.join(glob.glob(jpg_name))

    data_original = None

    data = np.sort(data, order='file_name')
    return data, data_original
