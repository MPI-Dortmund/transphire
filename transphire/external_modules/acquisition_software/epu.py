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
import shutil
import traceback as tb
import typing

import hyperspy.api as hs
import pandas as pd
import transphire_transform as tt


from ... import utils


def get_xml_keys() -> typing.Dict[str, typing.Dict[str, typing.List[str]]]:
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
            '{{{0}}}Key'.format(arrays): ['{{{0}}}Value'.format(arrays)],
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


def extract_gridsquare_and_spotid__1_8(file_path: str) -> pd.DataFrame:
    """
    Extract the gridsquare number and the spot id from the file name.

    Arguments:
    file_path - File path of the movie or frame file

    Returns:
    Pandas data frame containing the information.
    """
    match_pattern: typing.Optional[typing.Match[str]]
    group_dict: typing.Dict[str, str]

    match_pattern = re.match(
        ''.join([
            r'.*/GridSquare_(?P<GridSquare>[0-9]+)/Data/FoilHole_(?P<HoleNumber>[0-9]+)_Data_',
            r'(?P<SpotNumber>[0-9]+_[0-9]+)_(?P<Date>[0-9]+)_(?P<Time>[0-9]+).*',
            ]),
        file_path
        )
    if match_pattern:
        group_dict = match_pattern.groupdict()
    else:
        match_pattern = re.match(
            ''.join([
                r'.*/FoilHole_(?P<HoleNumber>[0-9]+)_Data_',
                r'(?P<SpotNumber>[0-9]+_[0-9]+)_(?P<Date>[0-9]+)_(?P<Time>[0-9]+).*',
                ]),
            file_path
            )
        if match_pattern:
            group_dict = match_pattern.groupdict()
        else:
            group_dict = {}
    for key, value in group_dict.items():
        group_dict[key] = int(''.join(value.split('_')))

    return pd.DataFrame(group_dict, index=[0])


def get_meta_data__1_8(
        file_name: typing.Optional[str]=None,
        xml_file: typing.Optional[str]=None,
    ) -> pd.DataFrame:
    """
    Extract time and grid information from the root_name string.

    Arguments:
    root_name - Name of the file

    Returns:
    hole, grid_number, spot1, spot2, date, time
    """
    xml_data: pd.DataFrame
    file_data: pd.DataFrame
    data_list: typing.List[pd.DataFrame]

    data_list = []
    if xml_file is not None:
        data_list.append(tt.load_xml(file_name=xml_file, level_dict=get_xml_keys()))
    if file_name is not None:
        data_list.append(extract_gridsquare_and_spotid__1_8(file_name))
    return pd.concat(data_list, axis=1)


def get_movie__1_8_falcon(
        compare_name: str,
    ) -> typing.List[str]:
    """
    Find the fractions for falcon EPU version 1.8

    Arguments:
    compare_name - Part of the name that is used for comparison

    Returns:
    List of found movie files
    """
    fraction_file: typing.List[str]

    fraction_file = [
        entry
        for entry in glob.glob('{0}_Fractions.*'.format(compare_name))
        if '.xml' not in entry
        ]
    assert len(fraction_file) == 1
    return pd.DataFrame({'MicrographMovieName': fraction_file}, index=[0])


def get_number_of_frames__1_8_falcon(data_frame: pd.DataFrame) -> pd.DataFrame:
    """
    Extract the number of frames of the movie.

    Arguments:
    data_frame - Pandas data frame containing the MicrographMovieName

    Returns:
    None, Modified in-place
    """
    mic_name: str

    mic_name = data_frame['MicrographMovieName'].iloc[0]
    data_frame['FoundNumberOffractions'] = hs.load(mic_name).axes_manager[0].size
    return None


def get_copy_command__1_8_falcon() -> typing.Callable[..., typing.Any]:
    """
    Get the copy command for the micrographs

    Arguments:
    None

    Returns:
    Command for the copying, Command in case copying fails
    """
    return utils.copy
