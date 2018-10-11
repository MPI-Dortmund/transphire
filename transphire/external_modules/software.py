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


import typing

from transphire_transform.dump_load import util

from .acquisition_software import epu


def load_software(
        function_name: str,
        software: str,
        camera: str,
        version: typing.Optional[str]=None
    ) -> typing.Any:
    """
    Create a cter partres file based on the cter_data information.
    By default, the latest cter version is assumed.

    Arguments:
    file_name - Path to the output partres file.
    version - Cter version default the latest version

    Returns:
    Pandas dataframe containing the ctffind file information
    """
    function_dict: typing.Dict[
        str,
        typing.Dict[
            str,
            typing.Dict[
                str,
                typing.Dict[
                    str,
                    typing.Callable[
                        ...,
                        typing.Any
                        ]
                    ]
                ]
            ]
        ]
    function: typing.Dict[
        str,
        typing.Callable[
            ...,
            typing.Any
            ]
        ]

    function_dict = {
        'EPU': {
            'Falcon': {
                '1.8': {
                    'get_meta_data': epu.get_meta_data__1_8_falcon,
                    'get_frames': epu.get_frames__1_8_falcon,
                    'get_number_of_frames': epu.get_number_of_frames__1_8_falcon,
                    'get_compare_names': epu.get_compare_names__1_8_falcon,
                    'get_copy_command': epu.get_copy_command__1_8_falcon,
                    },
                },
            },
        }

    function_dict = util.extract_function_from_function_dict(
        function_dict[software][camera],
        version
        )
    return function_dict[function_name]
