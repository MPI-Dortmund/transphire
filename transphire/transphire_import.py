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
import os
import glob
import re
import numpy as np

from . import transphire_utils as tu


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
    dtype['Motion'] = [
        ('overall drift', '<f8'),
        ('average drift per frame', '<f8'),
        ('first frame drift', '<f8'),
        ('average drift per frame without first', '<f8'),
        ('file_name', '|U1200'),
        ('image', '|U1200'),
        ]

    dtype['CTF'] = [
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

    dtype['Picking'] = [
        ('confidence', 'O'),
        ('box_x', 'O'),
        ('box_y', 'O'),
        ('particles', '<i8'),
        ('file_name', '|U1200'),
        ('image', '|U1200'),
        ]

    dtype['Extract'] = [
        ('accepted', '<i8'),
        ('rejected', '<i8'),
        ('file_name', '|U1200'),
        ('image', '|U1200'),
        ]

    dtype['Class2d'] = [
        ('classes', '<i8'),
        ('accepted', '<i8'),
        ('rejected', '<i8'),
        ('file_name', '|U1200'),
        ('image', '|U1200'),
        ]

    dtype['Train2d'] = [
        ('loss', '<f8'),
        ('file_name', '|U1200'),
        ]

    dtype['Auto3d'] = [
        ('resolution', '<f8'),
        ('file_name', '|U1200'),
        ('image', '|U1200'),
        ]

    dtype['Select2d'] = [
        ('accepted', '<i8'),
        ('accepted_percent', '<i8'),
        ('particles_accepted', '<i8'),
        ('particles_accepted_percent', '<i8'),
        ('rejected', '<i8'),
        ('rejected_percent', '<i8'),
        ('particles_rejected', '<i8'),
        ('particles_rejected_percent', '<i8'),
        ('file_name', '|U1200'),
        ('image', '|U1200'),
        ]

    dtype['Gctf >=v1.06'] = [
        ('defocus_1', '<f8'),
        ('defocus_2', '<f8'),
        ('astigmatism', '<f8'),
        ('phase_shift', '<f8'),
        ('cross_corr', '<f8'),
        ('limit', '<f8'),
        ('file_name', '|U1200')
        ]

    dtype['CTER >=v1.0'] = [
        ('defocus_1', '<f8'),
        ('defocus_2', '<f8'),
        ('astigmatism', '<f8'),
        ('phase_shift', '<f8'),
        ('cross_corr', '<f8'),
        ('limit', '<f8'),
        ('file_name', '|U1200')
        ]

    dtype['CTFFIND4 >=v4.1.8'] = [
        ('mic_number', '<f8'),
        ('defocus_1', '<f8'),
        ('defocus_2', '<f8'),
        ('astigmatism', '<f8'),
        ('phase_shift', '<f8'),
        ('cross_corr', '<f8'),
        ('limit', '<f8'),
        ('file_name', '|U1200')
        ]

    dtype['crYOLO >=v1.0.4'] = [
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
    dtype_import['CTER >=v1.0'] = [
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

    dtype_import['Gctf >=v1.06'] = [
        ('defocus_1', '<f8'),
        ('defocus_2', '<f8'),
        ('astigmatism', '<f8'),
        ('phase_shift', '<f8'),
        ('cross_corr', '<f8'),
        ('limit', '<f8')
        ]

    dtype_import['CTFFIND4 >=v4.1.8'] = [
        ('mic_number', '<f8'),
        ('defocus_1', '<f8'),
        ('defocus_2', '<f8'),
        ('astigmatism', '<f8'),
        ('phase_shift', '<f8'),
        ('cross_corr', '<f8'),
        ('limit', '<f8')
        ]

    dtype_import['MotionCor2 >=v1.0.0'] = [
        ('frame_number', '<f8'),
        ('shift_x', '<f8'),
        ('shift_y', '<f8')
        ]

    dtype_import['Unblur >=v1.0.0'] = [
        ('frame_number', '<i8'),
        ('shift_x', '<f8'),
        ('shift_y', '<f8')
        ]

    dtype_import['crYOLO >=v1.0.4'] = [
        ('coord_x', '<f8'),
        ('coord_y', '<f8'),
        ('box_x', '<f8'),
        ('box_y', '<f8'),
        ]
    return dtype_import


def dummy(name, name_no_feedback, settings, directory_name, import_name='', send_data=None):
    if send_data is None:
        return None, None
    else:
        send_data.send((None, None))


def import_isac_v1_2(name, name_no_feedback, settings, directory_name, import_name='', send_data=None):
    files = [
        entry for entry in glob.glob(
        '{0}/*/ISAC2'.format(directory_name)
        )
        ]
    useable_files = []
    for file_name in files:
        try:
            with open(os.path.join(file_name, 'processed_images.txt'), 'r') as read:
                accepted = len([entry for entry in read.readlines() if entry.strip()])
        except FileNotFoundError:
            accepted = 0
        except Exception as e:
            print('File corrupt: {} - {}'.format(file_name, str(e)))
        try:
            with open(os.path.join(file_name, 'not_processed_images.txt'), 'r') as read:
                rejected = len([entry for entry in read.readlines() if entry.strip()])
        except FileNotFoundError:
            rejected = 0
        except Exception as e:
            print('File corrupt: {} - {}'.format(file_name, str(e)))
        classes = len([entry for entry in glob.glob(
            '{0}/png/*'.format(os.path.dirname(file_name))
            )])
        useable_files.append([os.path.dirname(file_name), accepted, rejected, classes])

    useable_files_jpg = [
        tu.get_name(entry)
        for entry in glob.glob(os.path.join(directory_name, 'jpg*', '*.jpg'))
        ]

    useable_files = [
        [entry[0], entry[1], entry[2], entry[3]]
        for entry in sorted(useable_files)
        if tu.get_name(entry[0]) in useable_files_jpg
        ]

    data = np.zeros(
        len(useable_files),
        dtype=get_dtype_dict()['Class2d']
        )
    data = np.atleast_1d(data)
    data.fill(0)

    file_names_jpg = [tu.get_name(entry[0]) for entry in useable_files]
    jpgs = sorted([
        os.path.basename(entry)
        for entry in glob.glob(os.path.join(directory_name, 'jpg*'))
        ])
    jpg_names = [
        ';;;'.join([
            os.path.join(directory_name, jpg_dir_name, '{0}.jpg'.format(entry))
            for jpg_dir_name in jpgs
            ])
        for entry in file_names_jpg
        ]

    for idx, entry in enumerate(useable_files):
        data['file_name'][idx] = entry[0]
        data['accepted'][idx] = entry[1]
        data['rejected'][idx] = entry[2]
        data['classes'][idx] = entry[3]
    data['image'] = jpg_names

    data = np.sort(data, order='file_name')
    if send_data is None:
        return data, data
    else:
        send_data.send((data, data))


def import_cinderella_v0_3_1(name, name_no_feedback, settings, directory_name, import_name='', send_data=None):
    files = [
        entry for entry in glob.glob(
        '{0}/{1}*_transphire.log'.format(directory_name, import_name)
        )
        ]
    useable_files = []
    for file_name in files:
        try:
            with open(file_name, 'r') as read:
                # Regex documentation can be found here: https://regex101.com/r/MxOgyg/3
                match = re.search(
                    '^\s*Good(?: classes|):\s*(\d+) .*$(?:\n|\r\n)(?:\n|\r\n)(?:\n|\r\n)^\s*Bad(?: classes|):\s*(\d+) .*$(?:\n|\r\n)(?:\n|\r\n)^Bad Particles(?:\n|\r\n)(\d+)(?:\n|\r\n)Good Particles(?:\n|\r\n)(\d+)$',
                    read.read(),
                    re.MULTILINE
                    )
        except FileNotFoundError:
            continue
        except Exception as e:
            print('File corrupt: {} - {}'.format(file_name, str(e)))
        if match is not None:
            useable_files.append([file_name, int(match.group(1)), int(match.group(2)), int(match.group(3)), int(match.group(4))])

    useable_files_jpg = [
        tu.get_name(entry).replace('_good', '').replace('_bad', '')
        for entry in glob.glob(os.path.join(directory_name, 'jpg*', '*.jpg'))
        ]

    useable_files = [
        [entry[0].replace('_transphire', ''), entry[1], entry[2], entry[3], entry[4]]
        for entry in sorted(useable_files)
        if tu.get_name(entry[0]).replace('_transphire', '') in useable_files_jpg
        ]

    data = np.zeros(
        len(useable_files),
        dtype=get_dtype_dict()['Select2d']
        )
    data = np.atleast_1d(data)
    data.fill(0)

    file_names_jpg = [tu.get_name(entry[0]) for entry in useable_files]
    jpgs = sorted([
        os.path.basename(entry)
        for entry in glob.glob(os.path.join(directory_name, 'jpg*'))
        ])
    jpg_names = [
        ';;;'.join([
            os.path.join(directory_name, jpg_dir_name, '{0}_bad.jpg'.format(entry))
            if idx == 0
            else
            os.path.join(directory_name, jpg_dir_name, '{0}_good.jpg'.format(entry))
            for idx, jpg_dir_name in enumerate(jpgs)
            ])
        for entry in file_names_jpg
        ]

    for idx, entry in enumerate(useable_files):
        data['file_name'][idx] = entry[0]
        data['accepted'][idx] = entry[1]
        data['rejected'][idx] = entry[2]
        data['accepted_percent'][idx] = 100 * entry[1] / (entry[1] + entry[2])
        data['rejected_percent'][idx] = 100 * entry[2] / (entry[1] + entry[2])
        data['particles_rejected'][idx] = entry[3]
        data['particles_accepted'][idx] = entry[4]
        data['particles_rejected_percent'][idx] = 100 * entry[3] / (entry[3] + entry[4])
        data['particles_accepted_percent'][idx] = 100 * entry[4] / (entry[3] + entry[4])
    data['image'] = jpg_names

    data = np.sort(data, order='file_name')
    if send_data is None:
        return data, data
    else:
        send_data.send((data, data))


def import_window_v1_2(name, name_no_feedback, settings, directory_name, import_name='', send_data=None):
    files = [
        entry for entry in glob.glob(
        '{0}/{1}*_transphire.log'.format(directory_name, import_name)
        )
        ]
    useable_files = []
    for file_name in files:
        try:
            with open(file_name, 'r') as read:
                match = re.search(
                    '^.*Processed\s+:\s+(\d+).*$(?:\n|\r\n)^.*Rejected by out of boundary\s+:\s+(\d+).*$',
                    read.read(),
                    re.MULTILINE
                    )
        except FileNotFoundError:
            continue
        except Exception as e:
            print('File corrupt: {} - {}'.format(file_name, str(e)))
        if match is not None:
            useable_files.append([file_name, match.group(1), match.group(2)])

    useable_files_jpg = [
        tu.get_name(entry)
        for entry in glob.glob(os.path.join(directory_name, 'jpg*', '*.jpg'))
        ]

    useable_files = [
        [entry[0].replace('_transphire', ''), entry[1], entry[2]]
        for entry in sorted(useable_files)
        if tu.get_name(entry[0]).replace('_transphire', '') in useable_files_jpg
        ]

    data = np.zeros(
        len(useable_files),
        dtype=get_dtype_dict()['Extract']
        )
    data = np.atleast_1d(data)
    data.fill(0)

    file_names_jpg = [tu.get_name(entry[0]) for entry in useable_files]
    jpgs = sorted([
        os.path.basename(entry)
        for entry in glob.glob(os.path.join(directory_name, 'jpg*'))
        ])
    jpg_names = [
        ';;;'.join([
            os.path.join(directory_name, jpg_dir_name, '{0}.jpg'.format(entry))
            for jpg_dir_name in jpgs
            ])
        for entry in file_names_jpg
        ]

    for idx, entry in enumerate(useable_files):
        data['file_name'][idx] = entry[0]
        data['accepted'][idx] = entry[1]
        data['rejected'][idx] = entry[2]
    data['image'] = jpg_names

    data = np.sort(data, order='file_name')
    if send_data is None:
        return data, data
    else:
        send_data.send((data, data))


def import_ctffind_v4_1_8(name, name_no_feedback, settings, directory_name, import_name='', send_data=None):
    """
    Import ctf information for CTFFIND v4.1.8.
    Defocus in angstrom, phase shift in degree.

    Arguments:
    name - Name of ctf program
    directory_name - Name of the directory to search for files

    Return:
    Imported data
    """
    dtype_import_dict_name = tu.find_best_match(name_no_feedback, get_dtype_import_dict())
    dtype_dict_name = tu.find_best_match(name_no_feedback, get_dtype_dict())
    files = [
        entry for entry in glob.glob(
        '{0}/{1}*.txt'.format(directory_name, import_name)
        ) if not entry.endswith('_avrot.txt') and not '_transphire_' in entry
        ]

    useable_files = []
    for file_name in files:
        try:
            data_name = np.genfromtxt(
                file_name,
                dtype=get_dtype_import_dict()[dtype_import_dict_name],
                )
        except ValueError:
            continue
        except IOError:
            continue
        except Exception as e:
            print('File corrupt: {} - {}'.format(file_name, str(e)))
        else:
            if data_name.size > 0:
                useable_files.append([file_name, data_name])
            else:
                continue

    useable_files_jpg = set([
        tu.get_name(entry)
        for entry in glob.glob(os.path.join(directory_name, 'jpg*', '*.jpg'))
        ])
    useable_files_json = set([
        tu.get_name(entry)
        for entry in glob.glob(os.path.join(directory_name, 'json*', '*.json'))
        ])
    if not import_name: 
        useable_files = [
            entry
            for entry in sorted(useable_files)
            if tu.get_name(entry[0]) in useable_files_jpg and
            tu.get_name(entry[0]) in useable_files_json
            ]

    data = np.zeros(
        len(useable_files),
        dtype=get_dtype_dict()['CTF']
        )
    data_original = np.zeros(
        len(useable_files),
        dtype=get_dtype_dict()[dtype_dict_name]
        )
    data = np.atleast_1d(data)
    data_original = np.atleast_1d(data_original)
    data.fill(0)
    data_original.fill(0)

    match_re = re.compile('# Input file: (.*?)\s+; Number of micrographs: 1')

    file_names = []
    jpg_json_data = []
    jpg_dirs = glob.glob(os.path.join(directory_name, 'jpg*'))
    json_dirs = glob.glob(os.path.join(directory_name, 'json*'))
    for file_name, _ in useable_files:
        with open(file_name, 'r') as read:
            content = read.read()
        file_names.append(match_re.search(content, re.S).group(1))

        file_name_base = tu.get_name(file_name)
        jpgs = [os.path.join(jpg_name, '{}.jpg'.format(file_name_base)) for jpg_name in jpg_dirs]
        json = [os.path.join(json_name, '{}.json'.format(file_name_base)) for json_name in json_dirs]
        jpg_json_data.append(';;;'.join(jpgs + json))

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
    data['image'] = jpg_json_data

    data = np.sort(data, order='file_name')
    data_original = np.sort(data_original, order='file_name')
    if send_data is None:
        return data, data_original
    else:
        send_data.send((data, data_original))


def import_gctf_v1_06(name, name_no_feedback, settings, directory_name, import_name='', send_data=None):
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
    dtype_dict_name = tu.find_best_match(name_no_feedback, get_dtype_dict())

    useable_files = []
    for file_name in sorted(glob.glob('{0}/{1}*{2}.star'.format(directory_name, import_name, suffix))):
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
        except Exception as e:
            print('File corrupt: {} - {}'.format(file_name, str(e)))
        else:
            if data_name.size > 0:
                useable_files.append([file_name, data_name])
            else:
                continue

    useable_files_jpg = set([
        tu.get_name(entry)
        for entry in glob.glob(os.path.join(directory_name, 'jpg*', '*.jpg'))
        ])
    useable_files_json = set([
        tu.get_name(entry)
        for entry in glob.glob(os.path.join(directory_name, 'json*', '*.json'))
        ])
    if not import_name: 
        useable_files = [
            file_name
            for file_name in sorted(useable_files)
            if tu.get_name(file_name) in useable_files_jpg and
            tu.get_name(file_name) in useable_files_json
            ]

    data = np.zeros(
        len(useable_files),
        dtype=get_dtype_dict()['CTF']
        )
    data_original = np.zeros(
        len(useable_files),
        dtype=get_dtype_dict()[dtype_dict_name]
        )
    data = np.atleast_1d(data)
    data_original = np.atleast_1d(data_original)
    data.fill(0)
    data_original.fill(0)
    if not useable_files:
        if send_data is None:
            return None, None
        else:
            send_data.send((None, None))

    jpg_json_data = []
    for entry in sorted(useable_files):
        file_name_base = tu.get_name(file_name)
        jpgs = glob.glob(os.path.join(directory_name, 'jpg*', '{}.jpg'.format(file_name_base)))
        json = glob.glob(os.path.join(directory_name, 'json*', '{}.json'.format(file_name_base)))
        jpg_json_data.append(';;;'.join(jpgs + json))

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
            data[transphire_name] = [entry[1][dtype_name] for entry in useable_files]
            try:
                data[transphire_name][np.isinf(data[transphire_name])] = 0 # Set infinity to 0 to avoid histogram problems
            except TypeError:
                pass
            data[transphire_name] = np.nan_to_num(data[transphire_name], copy=False)

    data['image'] = jpg_json_data

    data = np.sort(data, order='file_name')
    data_original = np.sort(data_original, order='file_name')
    if send_data is None:
        return data, data_original
    else:
        send_data.send((data, data_original))


def import_cter_v1_0(name, name_no_feedback, settings, directory_name, import_name='', send_data=None):
    """
    Import ctf information for CTER v1.0.
    Defocus in angstrom, phase shift in degree.

    Arguments:
    name - Name of ctf program
    directory_name - Name of the directory to search for files

    Return:
    Imported data
    """
    dtype_import_dict_name = tu.find_best_match(name_no_feedback, get_dtype_import_dict())

    useable_files = []
    for file_name in sorted(glob.glob('{0}/{1}*/partres.txt'.format(directory_name, import_name))):
        try:
            data_name = np.genfromtxt(
                file_name,
                dtype=get_dtype_import_dict()[dtype_import_dict_name],
                )
        except ValueError:
            continue
        except IOError:
            continue
        except Exception as e:
            print('File corrupt: {} - {}'.format(file_name, str(e)))
        else:
            if data_name.size > 0:
                useable_files.append([os.path.dirname(file_name), data_name])
            else:
                continue

    useable_files_jpg = set([
        tu.get_name(entry)
        for entry in glob.glob(os.path.join(directory_name, 'jpg*', '*.jpg'))
        ])
    useable_files_json = set([
        tu.get_name(entry)
        for entry in glob.glob(os.path.join(directory_name, 'json*', '*.json'))
        ])
    if not import_name: 
        useable_files = [
            file_name
            for file_name in sorted(useable_files)
            if tu.get_name(file_name[0]) in useable_files_jpg and
            tu.get_name(file_name[0]) in useable_files_json
            ]

    data = np.zeros(
        len(useable_files),
        dtype=get_dtype_dict()['CTF']
        )
    data_original = np.zeros(
        len(useable_files),
        dtype=get_dtype_import_dict()[dtype_import_dict_name]
        )
    data = np.atleast_1d(data)
    data_original = np.atleast_1d(data_original)
    data.fill(0)
    data_original.fill(0)

    jpg_json_data = []
    for file_name in sorted(useable_files):
        file_name_base = tu.get_name(file_name[0])
        jpgs = glob.glob(os.path.join(directory_name, 'jpg*', '{}.jpg'.format(file_name_base)))
        json = glob.glob(os.path.join(directory_name, 'json*', '{}.json'.format(file_name_base)))
        jpg_json_data.append(';;;'.join(jpgs + json))


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
    data['image'] = jpg_json_data

    data = np.sort(data, order='file_name')
    data_original = np.sort(data_original, order='file_name')
    if send_data is None:
        return data, data_original
    else:
        send_data.send((data, data_original))


def import_motion_cor_2_v1_0_0(name, name_no_feedback, settings, directory_name, import_name='', send_data=None):
    """
    Import motion information for MotionCor2 v1.0.0.

    Arguments:
    name - Name of motion program
    directory_name - Name of the directory to search for files

    Return:
    Imported data
    """
    dtype_import_dict_name = tu.find_best_match(name_no_feedback, get_dtype_import_dict())

    directory_names = glob.glob('{0}/*_with*_DW_log'.format(directory_name))
    files = np.array(
        [
            entry
            for directory_name in directory_names
            for entry in glob.glob('{0}/{1}*-Full.log'.format(directory_name, import_name))
            ],
        dtype=str
        )

    useable_files = []
    for file_name in files:
        try:
            array = np.genfromtxt(
                file_name,
                dtype=get_dtype_import_dict()[dtype_import_dict_name]
                )
        except ValueError:
            continue
        except IOError:
            continue
        except Exception as e:
            print('File corrupt: {} - {}'.format(file_name, str(e)))
        else:
            if array.size > 0:
                useable_files.append(file_name)
            else:
                continue

    useable_files_jpg = set([
        tu.get_name(entry)
        for entry in glob.glob(os.path.join(directory_name, 'jpg*', '*.jpg'))
        ])
    useable_files_json = set([
        tu.get_name(entry)
        for entry in glob.glob(os.path.join(directory_name, 'json*', '*.json'))
        ])
    if not import_name: 
        useable_files = [
            file_name
            for file_name in sorted(useable_files)
            if tu.get_name(tu.get_name(file_name)) in useable_files_jpg and
            tu.get_name(tu.get_name(file_name)) in useable_files_json
            ]

    data = np.zeros(
        len(useable_files),
        dtype=get_dtype_dict()['Motion']
        )
    data = np.atleast_1d(data)
    data_original = []
    for idx, file_name in enumerate(useable_files):
        try:
            data_name = np.genfromtxt(
                file_name,
                dtype=get_dtype_import_dict()[dtype_import_dict_name]
                )
        except IOError:
            continue
        else:
            if data_name.size == 0:
                continue
            else:
                pass

        data_original.append([data_name['shift_x'], data_name['shift_y']])
        data[idx]['file_name'] = file_name.rsplit('0-', 1)[0]
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
        json_name = os.path.join(
            directory_name,
            'json*',
            '{0}.json'.format(tu.get_name(tu.get_name(file_name)))
            )
        data[idx]['image'] = ';;;'.join(glob.glob(jpg_name) + glob.glob(json_name))

    sort_idx = np.argsort(data, order='file_name')
    data = data[sort_idx]
    data_original = np.array(data_original)[sort_idx]
    if send_data is None:
        return data, data_original
    else:
        send_data.send((data, data_original))


def import_cryolo_v1_2_2(name, name_no_feedback, settings, directory_name, import_name='', send_data=None):
    """
    Import picking information for crYOLO v1.2.2.

    Arguments:
    name - Name of picking program
    directory_name - Name of the directory to search for files

    Return:
    Imported data
    """
    return import_cryolo_v1_0_4(
        name,
        name_no_feedback,
        settings,
        directory_name,
        sub_directory=['CBOX', 'EMAN', 'EMAN_HELIX_SEGMENTED'],
        import_name=import_name,
        send_data=send_data
        )


def import_cryolo_v1_0_4(name, name_no_feedback, settings, directory_name, import_name='', send_data=None, sub_directory=None, ):
    """
    Import picking information for crYOLO v1.0.4.

    Arguments:
    name - Name of picking program
    directory_name - Name of the directory to search for files

    Return:
    Imported data
    """

    if sub_directory is None:
        sub_directory=['']
    box_files = []
    for dir_name in sub_directory:
        is_break = False
        for ext_name in ('cbox', 'box', 'txt'):
            box_files = glob.glob(os.path.join(
                directory_name,
                dir_name,
                '{0}*.{1}'.format(import_name, ext_name)
                ))
            if box_files:
                is_break = True
                break
        if is_break:
            break

    files_box = np.array(box_files)
    useable_files = []
    for file_name in files_box:
        try:
            data_imported = np.genfromtxt(file_name)
        except ValueError:
            useable_files.append([os.path.splitext(os.path.basename(file_name))[0], 0, np.array([0])])
        except IOError:
            continue
        except Exception as e:
            print('File corrupt: {} - {}'.format(file_name, str(e)))
        else:
            if file_name.endswith('.cbox') and data_imported.size != 0:
                data_cbox = np.atleast_2d(data_imported)[:, 4]
                data_box_x = np.atleast_2d(data_imported)[:, 5]
                data_box_y = np.atleast_2d(data_imported)[:, 6]
            else:
                data_cbox = np.array([0])
                data_box_x = np.array([0])
                data_box_y = np.array([0])
            useable_files.append([os.path.splitext(os.path.basename(file_name))[0], data_imported.shape[0], data_cbox, data_box_x, data_box_y])

    useable_files_jpg = [
        tu.get_name(entry)
        for entry in glob.glob(os.path.join(directory_name, 'jpg*', '*.jpg'))
        ]
    useable_files = [
        entry
        for entry in sorted(useable_files)
        if tu.get_name(entry[0]) in useable_files_jpg
        ]

    data = np.zeros(
        len(useable_files),
        dtype=get_dtype_dict()['Picking']
        )
    data = np.atleast_1d(data)
    file_names = [entry[0] for entry in useable_files]
    jpgs = sorted([os.path.basename(entry) for entry in glob.glob(os.path.join(directory_name, 'jpg*'))])
    jpg_names = [';;;'.join([os.path.join(directory_name, jpg_dir_name, '{0}.jpg'.format(entry)) for jpg_dir_name in jpgs]) for entry in file_names]
    data['file_name'] = file_names
    data['confidence'] = [entry[2] for entry in useable_files]
    data['box_x'] = [entry[3] for entry in useable_files]
    data['box_y'] = [entry[4] for entry in useable_files]
    data['particles'] = [entry[1] for entry in useable_files]
    data['image'] = jpg_names

    data_original = None

    data = np.sort(data, order='file_name')
    if send_data is None:
        return data, data_original
    else:
        send_data.send((data, data_original))


def import_unblur_v1_0_0(name, name_no_feedback, settings, directory_name, import_name='', send_data=None):
    """
    Import motion information for cisTEM Unblur v1.0.0.

    Arguments:
    name - Name of motion program
    directory_name - Name of the directory to search for files

    Return:
    Imported data
    """
    dtype_import_dict_name = tu.find_best_match(name_no_feedback, get_dtype_import_dict())

    directory_names = glob.glob('{0}/*_with*_DW_log'.format(directory_name))
    files = np.array(
        [
            entry
            for directory_name in directory_names
            for entry in glob.glob('{0}/{1}*_transphire.log'.format(directory_name, import_name))
            ],
        dtype=str
        )

    useable_files = []
    re_comp = re.compile('^image #(?P<frame>\d+) = (?P<xshift>[-\d.]+), (?P<yshift>[-\d.]+)$', re.M) # https://regex101.com/r/jmBPfH/1/ regex explanation
    for file_name in files:
        try:
            with open(file_name, 'r') as read:
                content = read.read()
        except ValueError:
            continue
        except IOError:
            continue
        except Exception as e:
            print('File corrupt: {} - {}'.format(file_name, str(e)))
        else:
            if len(re_comp.findall(content)) > 0:
                useable_files.append(file_name)
            else:
                continue

    useable_files_jpg = set([
        tu.get_name(entry)
        for entry in glob.glob(os.path.join(directory_name, 'jpg*', '*.jpg'))
        ])
    useable_files_json = set([
        tu.get_name(entry)
        for entry in glob.glob(os.path.join(directory_name, 'json*', '*.json'))
        ])
    if not import_name: 
        useable_files = [
            file_name
            for file_name in sorted(useable_files)
            if tu.get_name(tu.get_name(file_name)) in useable_files_jpg and
            tu.get_name(tu.get_name(file_name)) in useable_files_json
            ]

    data = np.zeros(
        len(useable_files),
        dtype=get_dtype_dict()['Motion']
        )
    data = np.atleast_1d(data)
    data_original = []
    for idx, file_name in enumerate(useable_files):
        try:
            with open(file_name, 'r') as read:
                content = read.read()
        except ValueError:
            continue
        except IOError:
            continue
        else:
            matches = re_comp.findall(content)
            if len(matches) > 0:
                pass
            else:
                continue

        shift_x = []
        shift_y = []
        frame_list = []
        for match in matches:
            if int(match[0])+1 in frame_list:
                break
            shift_x.append(float(match[1]))
            shift_y.append(float(match[2]))
            frame_list.append(int(match[0])+1)

        data_name = np.empty(
            len(shift_x),
            dtype=get_dtype_import_dict()[dtype_import_dict_name]
            )
        data_name['shift_x'] = shift_x
        data_name['shift_y'] = shift_y
        data_name['frame_number'] = frame_list

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
        json_name = os.path.join(
            directory_name,
            'json*',
            '{0}.json'.format(tu.get_name(tu.get_name(file_name)))
            )
        data[idx]['image'] = ';;;'.join(glob.glob(jpg_name) + glob.glob(json_name))

    sort_idx = np.argsort(data, order='file_name')
    data = data[sort_idx]
    data_original = np.array(data_original)[sort_idx]
    if send_data is None:
        return data, data_original
    else:
        send_data.send((data, data_original))


def import_auto_sphire_v1_3(name, name_no_feedback, settings, directory_name, import_name='', send_data=None):
    """
    Import motion information for auto_sphire.py version 1.3

    Arguments:
    name - Name of motion program
    directory_name - Name of the directory to search for files

    Return:
    Imported data
    """

    mount_work = directory_name.replace(
        settings['Output']['Project directory'],
        settings['copy_to_work_folder_feedback_0'],
        )
    directory_names = glob.glob(os.path.join(mount_work, '{0}*_FILES'.format(import_name)))

    useable_files = []
    for entry in directory_names:
        if glob.glob(os.path.join(entry[:-6], '*_SHARPENING/vol_combined.hdf')):
            useable_files.append(entry[:-6])

    final_resolution = []
    final_jpg = []
    final_file_name = []
    for entry in useable_files:
        jpg_file = os.path.join(
            directory_name,
            'jpg',
            '{}.jpg'.format(os.path.basename(entry))
            )
        jpg_file_log = os.path.join(
            directory_name,
            'jpg',
            '{}.log'.format(os.path.basename(entry))
            )
        if not os.path.isfile(jpg_file):
            tu.mkdir_p(os.path.join(directory_name, 'jpg'))
            with open(jpg_file_log, 'w') as write:
                subprocess.call(
                    '{0} --script "{1}/support_scripts/chimerax.py {2} {3}" --nogui --offscreen'.format(
                        settings['Path']['chimerax'],
                        os.path.dirname(__file__),
                        glob.glob(os.path.join(entry, '*_SHARPENING/vol_combined.hdf'))[0],
                        jpg_file,
                        ),
                    shell=True,
                    stdout=write,
                    stderr=write,
                    )

        log_file = glob.glob(os.path.join(entry, '*_SHARPENING/log.txt'))[0]
        with open(log_file, 'r') as read:
            content = read.read()
        resolution = re.search('^.*FSC masked halves :.* 0\.143:\s*([.\d]*)A$', content, re.M).group(1) # https://regex101.com/r/6xdngz/1/

        final_resolution.append(float(resolution))
        final_jpg.append(';;;'.join([jpg_file]))
        final_file_name.append(tu.get_name(entry).replace('AUTOSPHIRE_', ''))

    data = np.zeros(
        len(final_jpg),
        dtype=get_dtype_dict()['Auto3d']
        )
    data = np.atleast_1d(data)
    data['resolution'] = final_resolution
    data['image'] = final_jpg
    data['file_name'] = final_file_name

    sort_idx = np.argsort(data, order='file_name')
    data = data[sort_idx]
    data_original = data
    if send_data is None:
        return data, data_original
    else:
        send_data.send((data, data_original))
