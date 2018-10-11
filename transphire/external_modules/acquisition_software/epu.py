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
import typing

import pandas as pd
import transphire_transform as tt


def get_xml_keys__1_8() -> typing.Dict[str, typing.Dict[str, typing.List[str]]]:
    """
    Get the xml keys to find the related objects.

    Arguments:
    None

    Returns:
    Dictionary of the important keys and levels
    """
    arrays: str
    shared_object: str
    level_dict: typing.Dict[str, typing.Dict[str, typing.List[str]]]

    arrays = 'http://schemas.microsoft.com/2003/10/Serialization/Arrays'
    shared_object = 'http://schemas.datacontract.org/2004/07/Fei.SharedObjects'
    level_dict = {
        'key_value': {
            '{{{0}}}Key'.format(arrays): ['{{{0}}}Value'],
            },
        'level 0': {
            '{{{0}}}AccelerationVoltage'.format(shared_object): [],
            '{{{0}}}PreExposureTime'.format(shared_object): [],
            '{{{0}}}PreExposurePauseTime'.format(shared_object): [],
            '{{{0}}}ApplicationSoftware'.format(shared_object): [],
            '{{{0}}}ApplicationSoftwareVersion'.format(shared_object): [],
            '{{{0}}}ComputerName'.format(shared_object): [],
            '{{{0}}}InstrumentID'.format(shared_object): [],
            '{{{0}}}InstrumentModel'.format(shared_object): [],
            '{{{0}}}Defocus'.format(shared_object): [],
            '{{{0}}}Intensity'.format(shared_object): [],
            '{{{0}}}acquisitionDateTime'.format(shared_object): [],
            '{{{0}}}NominalMagnification'.format(shared_object): [],
            },
        'level 1': {
            '{{{0}}}camera'.format(shared_object): ['ExposureTime'],
            '{{{0}}}Binning'.format(shared_object): ['x', 'y'],
            '{{{0}}}ReadoutArea'.format(shared_object): ['height', 'width'],
            '{{{0}}}Position'.format(shared_object): ['A', 'B', 'X', 'Y', 'Z'],
            '{{{0}}}ImageShift'.format(shared_object): ['_x', '_y'],
            '{{{0}}}BeamShift'.format(shared_object): ['_x', '_y'],
            '{{{0}}}BeamTilt'.format(shared_object): ['_x', '_y'],
            },
        'level 3': {
            '{{{0}}}SpatialScale'.format(shared_object): ['numericValue'],
            }
        }
    return level_dict


def extract_gridsquare_and_spotid__1_8_falcon(file_path: str) -> pd.DataFrame:
    """
    Extract the gridsquare number and the spot id from the file name.

    Arguments:
    file_path - File path of the movie or frame file

    Returns:
    Pandas data frame containing the information.
    """
    gridsquare: str
    basename

    dirnames, basename = os.path.split(file_path)
    grid_number = grid.split('_')[1]
    *_, hole, _, spot1, spot2, date, time = old_file.split('_')


def get_meta_data__1_8_falcon(root_name: str, xml_file: str) -> pd.DataFrame:
    """
    Extract time and grid information from the root_name string.

    Arguments:
    root_name - Name of the file

    Returns:
    hole, grid_number, spot1, spot2, date, time
    """
    xml_data: pd.DataFrame
    file_data: pd.DataFrame

    xml_data = tt.load_xml(file_name=xml_file, get_xml_keys__1_8())
    file_data = extract_gridsquare_and_spotid__1_8_falcon(root_name)
    return pd.concat([xml_data, file_data], axis=1)


def get_frames__1_8_falcon(compare_name: str, extension: str) -> typing.List[str]:
    """
    Find the fractions for falcon EPU version 1.8

    Arguments:
    compare_name - Part of the name that is used for comparison
    extension - File extension of the frames

    Returns:
    List of found movies
    """
    frames: typing.List[str]

    frames = glob.glob(
        '{0}*_Fractions.{1}'.format(
            compare_name,
            extension
            )
        )
    return frames


def get_number_of_frames__1_8_falcon(
        frames: typing.List[str],
        command: str,
        expected_nr_frames: int
    ) -> typing.Tuple[typing.Optional[str], typing.Optional[bool]]:
    """
    Extract the number of frames of the movie.

    Returns True if the expected number of frames matches
    Returns False if the file does not match or cannot be read
    Returns None if the expected number of frames does not match

    Arguments:
    frames - List of movies
    command - Run the command to find the number of frames
    expected_nr_frames - Expected number of frames

    Returns:
    Message in case something goes wrong, Return value
    """
    message: typing.Optional[str]
    return_value: typing.Optional[bool]
    output: str
    number_of_frames: typing.Optional[typing.Match[str]]

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


def get_compare_names__1_8_falcon(
        frames_name: str,
        meta_name: str,
    ) -> typing.Tuple[str, str, str]:
    """
    Get the meta data related to the found movies.

    Arguments:
    frames_name - Name of the frames/movie file
    meta_name - Name of the meta file

    Returns:
    Compare name for the frames, compare name for the meta, movie extension
    """
    compare_name_frames: str
    compare_name_meta: str
    extension = str

    extension = os.path.splitext(frames_name)[1]
    compare_name_frames = frames_name[:-len('_19911213_2019')]
    compare_name_meta = meta_name[:-len('_19911213_2019')]
    return compare_name_frames, compare_name_meta, extension


def get_copy_command__1_8_falcon() -> str:
    """
    Get the copy command for the micrographs

    Arguments:
    None

    Returns:
    Command for the copying
    """
    return 'rsync'
