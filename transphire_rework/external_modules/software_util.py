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
import os
import re
import subprocess
import traceback as tb


def get_xml_keys__epu():
    level_dict = {
        'key_value': {
            '{http://schemas.microsoft.com/2003/10/Serialization/Arrays}Key': \
                '{http://schemas.microsoft.com/2003/10/Serialization/Arrays}Value'
            },
        'level 0': {
            '{http://schemas.datacontract.org/2004/07/Fei.SharedObjects}AccelerationVoltage': [],
            '{http://schemas.datacontract.org/2004/07/Fei.SharedObjects}ExposureTime': [],
            '{http://schemas.datacontract.org/2004/07/Fei.SharedObjects}PreExposureTime': [],
            '{http://schemas.datacontract.org/2004/07/Fei.SharedObjects}PreExposurePauseTime': [],
            '{http://schemas.datacontract.org/2004/07/Fei.SharedObjects}ApplicationSoftware': [],
            '{http://schemas.datacontract.org/2004/07/Fei.SharedObjects}ApplicationSoftwareVersion': [],
            '{http://schemas.datacontract.org/2004/07/Fei.SharedObjects}ComputerName': [],
            '{http://schemas.datacontract.org/2004/07/Fei.SharedObjects}InstrumentID': [],
            '{http://schemas.datacontract.org/2004/07/Fei.SharedObjects}InstrumentModel': [],
            '{http://schemas.datacontract.org/2004/07/Fei.SharedObjects}InstrumentID': [],
            '{http://schemas.datacontract.org/2004/07/Fei.SharedObjects}Defocus': [],
            '{http://schemas.datacontract.org/2004/07/Fei.SharedObjects}Intensity': [],
            '{http://schemas.datacontract.org/2004/07/Fei.SharedObjects}acquisitionDateTime': [],
            '{http://schemas.datacontract.org/2004/07/Fei.SharedObjects}NominalMagnification': [],
            },
        'level 1': {
            '{http://schemas.datacontract.org/2004/07/Fei.SharedObjects}Binning': ['x', 'y'],
            '{http://schemas.datacontract.org/2004/07/Fei.SharedObjects}ReadoutArea': ['height', 'width'],
            '{http://schemas.datacontract.org/2004/07/Fei.SharedObjects}Position': ['A', 'B', 'X', 'Y', 'Z'],
            '{http://schemas.datacontract.org/2004/07/Fei.SharedObjects}ImageShift': ['_x', '_y'],
            '{http://schemas.datacontract.org/2004/07/Fei.SharedObjects}BeamShift': ['_x', '_y'],
            '{http://schemas.datacontract.org/2004/07/Fei.SharedObjects}BeamTilt': ['_x', '_y'],
            },
        'level 3': {
            '{http://schemas.datacontract.org/2004/07/Fei.SharedObjects}SpatialScale': ['numericValue'],
            }
        }



def get_meta_xml__epu_18_falcon2(root_name):
    """
    Extract time and grid information from the root_name string.

    Arguments:
    root_name - Name of the file

    Returns:
    hole, grid_number, spot1, spot2, date, time
    """
    *skip, grid, skip, old_file = \
        os.path.realpath(root_name).split('/')
    grid_number = grid.split('_')[1]
    *skip, hole, skip, spot1, spot2, date, time = old_file.split('_')
    return hole, grid_number, spot1, spot2, date, time


def get_frames__epu18_falcon2(compare_name, extension):
    frames = glob.glob(
        '{0}*_Fractions.{1}'.format(
            compare_name,
            extension
            )
        )
    return frames


def get_number_of_frames__epu18_falcon2(frames, command, expected_nr_frames):
    message = None
    return_value = True
    try:
        output = subprocess.check_output([command, frames[0]], encoding='utf-8')
    except BlockingIOError:
        message = str(tb.format_exc())
        return_value = False

    if not return_value:
        pass
    elif len(frames) != 1:
        message = 'File {{0}} has {0} movie files instead of 1\n'.format(
            len(frames)
            )
        return_value = None
    else:
        number_of_frames = re.match(
            r'.*Number of columns, rows, sections .....[ ]+[0-9]+[ ]+[0-9]+[ ]+([0-9]+).*',
            output
            )
        if not number_of_frames:
            return_value = False
            message = 'Could not read header of file {0}'.format(frames[0])
        elif number_of_frames != expected_nr_frames:
            return_value = None
            message = 'File {{0}} has {0} frames instead of {1}\n'.format(
                number_of_frames.group(1),
                expected_nr_frames
                )

    return message, return_value


def get_meta_data__epu18_falcon2(frames_root, root_name, extension):
    compare_name_frames = frames_root[:-len('_19911213_2019')]
    compare_name_meta = root_name[:-len('_19911213_2019')]
    frames = glob.glob('{0}*_Fractions.{1}'.format(
        compare_name_frames,
        extension
        ))
    return frames, compare_name_frames, compare_name_meta


def get_command__epu18_falcon2():
    return 'rsync'
