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
import typing

import mrcfile
import hyperspy.api as hs # type: ignore
import pandas as pd # type: ignore
import transphire_transform as tt # type: ignore

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
            f'{{{arrays}}}Key': [f'{{{arrays}}}Value'],
            },
        'level 0': {
            f'{{{shared_object}}}AccelerationVoltage': [],
            f'{{{shared_object}}}PreExposureTime': [],
            f'{{{shared_object}}}PreExposurePauseTime': [],
            f'{{{shared_object}}}ApplicationSoftware': [],
            f'{{{shared_object}}}ApplicationSoftwareVersion': [],
            f'{{{shared_object}}}ComputerName': [],
            f'{{{shared_object}}}InstrumentID': [],
            f'{{{shared_object}}}InstrumentModel': [],
            f'{{{shared_object}}}Defocus': [],
            f'{{{shared_object}}}Intensity': [],
            f'{{{shared_object}}}acquisitionDateTime': [],
            f'{{{shared_object}}}NominalMagnification': [],
            },
        'level 1': {
            f'{{{shared_object}}}camera': ['ExposureTime'],
            f'{{{shared_object}}}Binning': ['x', 'y'],
            f'{{{shared_object}}}ReadoutArea': ['height', 'width'],
            f'{{{shared_object}}}Position': ['A', 'B', 'X', 'Y', 'Z'],
            f'{{{shared_object}}}ImageShift': ['_x', '_y'],
            f'{{{shared_object}}}BeamShift': ['_x', '_y'],
            f'{{{shared_object}}}BeamTilt': ['_x', '_y'],
            },
        'level 3': {
            f'{{{shared_object}}}SpatialScale': ['numericValue'],
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
    output_dict: typing.Dict[str, int]

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

    output_dict = {}
    for key, value in group_dict.items():
        output_dict[key] = int(''.join(value.split('_')))

    return pd.DataFrame(output_dict, index=[0])


def get_meta_data__1_8(data_frame: pd.DataFrame) -> None:
    """
    Extract time and grid information from the root_name string.

    Arguments:
    root_name - Name of the file

    Returns:
    hole, grid_number, spot1, spot2, date, time
    """
    data_list: typing.List[pd.DataFrame]

    data_list = []
    if 'MicrographNameXmlRaw' in data_frame.columns.values:
        data_list.append(tt.load_xml(file_name=data_frame['MicrographNameXmlRaw'].iloc[0], level_dict=get_xml_keys()))
        data_list.append(extract_gridsquare_and_spotid__1_8(data_frame['MicrographNameXmlRaw'].iloc[0]))
    elif 'MicrographNameJpgRaw' in data_frame.columns.values:
        data_list.append(extract_gridsquare_and_spotid__1_8(data_frame['MicrographNameJpgRaw'].iloc[0]))
    elif 'MicrographNameMovieRaw' in data_frame.columns.values:
        data_list.append(extract_gridsquare_and_spotid__1_8(data_frame['MicrographNameMovieRaw'].iloc[0]))
    elif 'MicrographNameMrcKriosRaw' in data_frame.columns.values:
        data_list.append(extract_gridsquare_and_spotid__1_8(data_frame['MicrographNameMrcKriosRaw'].iloc[0]))
    elif 'MicrographNameGainRaw' in data_frame.columns.values:
        data_list.append(extract_gridsquare_and_spotid__1_8(data_frame['MicrographNameGainRaw'].iloc[0]))
    elif 'MicrographNameFrameXmlRaw' in data_frame.columns.values:
        data_list.append(extract_gridsquare_and_spotid__1_8(data_frame['MicrographNameFrameXmlRaw'].iloc[0]))

    for frame in data_list:
        for name in frame.columns.values:
            data_frame[name] = frame[name]
    return None


def get_movie__1_8_falcon(data_frame: pd.DataFrame) -> None:
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
        for entry in glob.glob(f'{data_frame["compare_name"].iloc[0]}*_Fractions.*')
        if '.xml' not in entry
        ]
    assert len(fraction_file) == 1
    data_frame['MicrographMovieNameRaw'] = fraction_file[0]
    return None


def get_number_of_frames__1_8_falcon(data_frame: pd.DataFrame) -> None:
    """
    Extract the number of frames of the movie.

    Arguments:
    data_frame - Pandas data frame containing the MicrographMovieNameRaw

    Returns:
    None, Modified in-place
    """
    mic_name: str

    mic_name = data_frame['MicrographMovieNameRaw'].iloc[0]
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


def get_movie__1_8_k2_frames(data_frame: pd.DataFrame) -> None:
    """
    Find the fractions for k2 EPU version 1.8

    Arguments:
    compare_name - Part of the name that is used for comparison.

    Returns:
    List of found movie files
    """
    fraction_files: typing.List[str]
    fraction_file: str
    write: mrcfile.MrcFile

    fraction_files = [
        entry
        for entry in sorted(glob.glob(f'{data_frame["compare_name"].iloc[0]}*-*'))
        if '.xml' not in entry
        ]
    fraction_file = f'{data_frame["compare_name"].iloc[0]}-Fractions.mrc'
    with mrcfile.open(fraction_file) as write:
        pass
    data_frame['MicrographMovieNameRaw'] = fraction_file
