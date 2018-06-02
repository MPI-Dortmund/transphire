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
import glob
import re
import numpy as np


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
                header.append((name, '|S200'))
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
    dtype['ctf'] = [
        ('mic_number', '<f8'),
        ('defocus', '<f8'),
        ('defocus_diff', '<f8'),
        ('astigmatism', '<f8'),
        ('phase_shift', '<f8'),
        ('cross_corr', '<f8'),
        ('limit', '<f8'),
        ('file_name', '|S200')
        ]
    dtype['Gctf v1.06'] = [
        ('defocus_1', '<f8'),
        ('defocus_2', '<f8'),
        ('astigmatism', '<f8'),
        ('phase_shift', '<f8'),
        ('cross_corr', '<f8'),
        ('limit', '<f8'),
        ('file_name', '|S200')
        ]
    dtype['Gctf v1.18'] = [
        ('defocus_1', '<f8'),
        ('defocus_2', '<f8'),
        ('astigmatism', '<f8'),
        ('phase_shift', '<f8'),
        ('cross_corr', '<f8'),
        ('limit', '<f8'),
        ('file_name', '|S200')
        ]
    dtype['CTER v1.0'] = [
        ('defocus_1', '<f8'),
        ('defocus_2', '<f8'),
        ('astigmatism', '<f8'),
        ('phase_shift', '<f8'),
        ('cross_corr', '<f8'),
        ('limit', '<f8'),
        ('file_name', '|S200')
        ]
    dtype['CTFFIND4 v4.1.10'] = [
        ('mic_number', '<f8'),
        ('defocus_1', '<f8'),
        ('defocus_2', '<f8'),
        ('astigmatism', '<f8'),
        ('phase_shift', '<f8'),
        ('cross_corr', '<f8'),
        ('limit', '<f8'),
        ('file_name', '|S200')
        ]
    dtype['CTFFIND4 v4.1.8'] = [
        ('mic_number', '<f8'),
        ('defocus_1', '<f8'),
        ('defocus_2', '<f8'),
        ('astigmatism', '<f8'),
        ('phase_shift', '<f8'),
        ('cross_corr', '<f8'),
        ('limit', '<f8'),
        ('file_name', '|S200')
        ]
    dtype['motion'] = [
        ('overall drift', '<f8'),
        ('average drift per frame', '<f8'),
        ('first frame drift', '<f8'),
        ('average drift per frame without first', '<f8'),
        ('file_name', '|S200')
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
        ('file_name', '|S200'),
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
    return dtype_import


def import_ctffind_v4_1_10(ctf_name, directory_name):
    """
    Import ctf information for CTFFIND v4.1.10.
    Defocus in angstrom, phase shift in degree.

    Arguments:
    ctf_name - Name of ctf program
    directory_name - Name of the directory to search for files

    Return:
    Imported data
    """
    return import_ctffind_v4_1_8(ctf_name, directory_name)


def import_ctffind_v4_1_8(ctf_name, directory_name):
    """
    Import ctf information for CTFFIND v4.1.8.
    Defocus in angstrom, phase shift in degree.

    Arguments:
    ctf_name - Name of ctf program
    directory_name - Name of the directory to search for files

    Return:
    Imported data
    """
    files = np.array([
        entry for entry in glob.glob(
            '{0}/*.txt'.format(directory_name)
            ) if '_avrot.txt' not in entry
        ], dtype=str)

    useable_files = []
    for name in files:
        try:
            array = np.genfromtxt(
                name,
                dtype=get_dtype_import_dict()[ctf_name]
                )
        except ValueError:
            continue
        else:
            if array.size > 0:
                useable_files.append(name)
            else:
                continue

    data = np.empty(
        len(useable_files),
        dtype=get_dtype_dict()['ctf']
        )
    data_original = np.empty(
        len(useable_files),
        dtype=get_dtype_dict()[ctf_name]
        )
    data = np.atleast_1d(data)
    data_original = np.atleast_1d(data_original)
    data.fill(0)
    data_original.fill(0)

    for idx, name in sorted(enumerate(useable_files)):

        data_name = np.genfromtxt(
            name,
            dtype=get_dtype_import_dict()[ctf_name]
            )
        data[idx]['file_name'] = name
        input_name = None
        with open(name, 'r') as read:
            for line in read.readlines():
                match_re = re.match('# Input file: (.*?) ; Number of micrographs: 1', line)
                if match_re is not None:
                    input_name = match_re.group(1).encode()
                else:
                    pass
        if input_name is None:
            raise IOError(
                'Could not read {0} file name! Please contact the TranSPHIRE authors!'.format(
                    ctf_name
                    )
                )
        else:
            data_original[idx]['file_name'] = input_name

        for entry in data_name.dtype.names:
            data_original[idx][entry] = data_name[entry]
            if entry == 'defocus_1':
                data[idx]['defocus'] = (data_name['defocus_1']+data_name['defocus_2'])/2
            elif entry == 'defocus_2':
                data[idx]['defocus_diff'] = np.abs(
                    data_name['defocus_1']-data_name['defocus_2']
                    )
            elif entry == 'phase_shift':
                data[idx][entry] = np.degrees(data_name[entry])
            else:
                data[idx][entry] = data_name[entry]

    data = np.sort(data, order='file_name')
    return data, data_original


def import_gctf_v1_18(ctf_name, directory_name):
    """
    Import ctf information for Gctf v1.18.
    Defocus in angstrom, phase shift in degree.

    Arguments:
    ctf_name - Name of ctf program
    directory_name - Name of the directory to search for files

    Return:
    Imported data
    """
    data, data_original = import_gctf_v1_06(ctf_name=ctf_name, directory_name=directory_name)
    return data, data_original


def import_gctf_v1_06(ctf_name, directory_name):
    """
    Import ctf information for Gctf v1.06.
    Defocus in angstrom, phase shift in degree.

    Arguments:
    ctf_name - Name of ctf program
    directory_name - Name of the directory to search for files

    Return:
    Imported data
    """
    files = np.array(
        [
            entry for entry in glob.glob(
                '{0}/*_gctf.star'.format(directory_name)
            )
            ],
        dtype=str
        )

    useable_files = []
    for file_name in files:
        try:
            dtype, max_header = get_header(input_file=file_name)
            data_name = np.genfromtxt(
                file_name,
                dtype=dtype,
                skip_header=max_header
                )
        except ValueError:
            continue
        else:
            if data_name.size > 0:
                useable_files.append(file_name)
            else:
                continue

    data = np.empty(
        len(useable_files),
        dtype=get_dtype_dict()['ctf']
        )
    data_original = np.empty(
        len(useable_files),
        dtype=get_dtype_dict()[ctf_name]
        )
    data = np.atleast_1d(data)
    data_original = np.atleast_1d(data_original)
    data.fill(0)
    data_original.fill(0)

    relion_dict = get_relion_dict()
    for idx, file_name in enumerate(useable_files):
        try:
            dtype, max_header = get_header(input_file=file_name)
        except ValueError:
            print('Could not read header of {0}!'.format(file_name))
            data, data_original =  None, None
            break
        data_name = np.genfromtxt(
            file_name,
            dtype=dtype,
            skip_header=max_header
            )
        for name in data_name.dtype.names:
            try:
                transphire_name = relion_dict[name]
            except KeyError:
                continue

            try:
                data_original[idx][transphire_name] = np.nan_to_num(data_name[name])
            except ValueError:
                data_original[idx][transphire_name] = 0

            if transphire_name == 'defocus_1':
                try:
                    data[idx]['defocus'] = (
                        data_name['_rlnDefocusU']+data_name['_rlnDefocusV']
                        ) / 2
                except ValueError:
                    data[idx][transphire_name] = 0
            elif transphire_name == 'defocus_2':
                try:
                    data[idx]['defocus_diff'] = np.abs(
                        data_name['_rlnDefocusU']-data_name['_rlnDefocusV']
                        )
                except ValueError:
                    data[idx][transphire_name] = 0
            else:
                try:
                    data[idx][transphire_name] = np.nan_to_num(data_name[name])
                except ValueError:
                    data[idx][transphire_name] = 0

    return data, data_original


def import_cter_v1_0(ctf_name, directory_name):
    """
    Import ctf information for CTER v1.0.
    Defocus in angstrom, phase shift in degree.

    Arguments:
    ctf_name - Name of ctf program
    directory_name - Name of the directory to search for files

    Return:
    Imported data
    """
    files = np.array(
        [
            entry for entry in glob.glob('{0}/*/partres.txt'.format(directory_name))
            ],
        dtype=str
        )

    useable_files = []
    for file_name in files:
        try:
            data_name = np.genfromtxt(
                file_name,
                dtype=get_dtype_import_dict()[ctf_name]
                )
        except ValueError:
            continue
        else:
            if data_name.size > 0:
                useable_files.append(file_name)
            else:
                continue

    data = np.empty(
        len(useable_files),
        dtype=get_dtype_dict()['ctf']
        )
    data_original = np.empty(
        len(useable_files),
        dtype=get_dtype_import_dict()[ctf_name]
        )
    data = np.atleast_1d(data)
    data_original = np.atleast_1d(data_original)
    data.fill(0)
    data_original.fill(0)

    for idx, name in sorted(enumerate(useable_files)):
        data_name = np.genfromtxt(
            name,
            dtype=get_dtype_import_dict()[ctf_name]
            )
        for entry in data_name.dtype.names:
            data_original[idx][entry] = data_name[entry]
            if entry == 'defocus':
                data[idx][entry] = data_name[entry] * 10000
            elif entry == 'astigmatism_amplitude':
                data[idx]['defocus_diff'] = data_name[entry] * 10000
            elif entry == 'astigmatism_angle':
                data[idx]['astigmatism'] = 45 - data_name[entry]
            elif entry == 'phase_shift':
                data[idx]['phase_shift'] = data_name[entry]
            elif entry == 'file_name':
                data[idx]['file_name'] = data_name[entry]
            elif entry == 'standard_deviation_defocus':
                data[idx]['cross_corr'] = data_name[entry]
            elif entry == 'limit_defocus_and_astigmatism':
                if data_name[entry] == 0:
                    value = data_name['limit_pixel_error']
                else:
                    value = data_name[entry]

                data[idx]['limit'] = 1 / value
            else:
                continue

    return data, data_original


def import_motion_cor_2_v1_0_0(motion_name, directory_names):
    """
    Import motion information for MotionCor2 v1.0.0.

    Arguments:
    motion_name - Name of motion program
    directory_name - Name of the directory to search for files

    Return:
    Imported data
    """
    files = np.array(
        [
            entry
            for directory_name in directory_names
            for entry in glob.glob('{0}/*-Full.log'.format(directory_name))
            ],
        dtype=str
        )

    useable_files = []
    for name in files:
        try:
            array = np.genfromtxt(
                name,
                dtype=get_dtype_import_dict()[motion_name]
                )
        except ValueError:
            continue
        else:
            if array.size > 0:
                useable_files.append(name)
            else:
                continue

    data = np.empty(
        len(useable_files),
        dtype=get_dtype_dict()['motion']
        )
    data = np.atleast_1d(data)
    for idx, name in enumerate(useable_files):
        data_name = np.genfromtxt(
            name,
            dtype=get_dtype_import_dict()[motion_name]
            )
        data[idx]['file_name'] = name
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

    data = np.sort(data, order='file_name')
    return data


def import_motion_cor_2_v1_0_5(motion_name, directory_names):
    """
    Import motion information for MotionCor2 v1.0.5.

    Arguments:
    ctf_name - Name of ctf program
    directory_name - Name of the directory to search for files

    Return:
    Imported data
    """
    data = import_motion_cor_2_v1_0_0(motion_name=motion_name, directory_names=directory_names)
    return data


def import_motion_cor_2_v1_1_0(motion_name, directory_names):
    """
    Import motion information for MotionCor2 v1.1.0.

    Arguments:
    ctf_name - Name of ctf program
    directory_name - Name of the directory to search for files

    Return:
    Imported data
    """
    data = import_motion_cor_2_v1_0_0(motion_name=motion_name, directory_names=directory_names)
    return data
