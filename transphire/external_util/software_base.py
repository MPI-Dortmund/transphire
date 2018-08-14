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


import abc


class SoftwareBase(abc.ABC):

    @staticmethod
    @abc.abstractmethod
    def extract_time_and_grid_information(root_name):
        return 5, tuple, str

    @staticmethod
    @abc.abstractmethod
    def find_frames(compare_name, extension):
        return 1, list, str

    @staticmethod
    @abc.abstractmethod
    def check_nr_frames(frames, command, expected_frames):
        return 2, tuple, [str, bool]

    @staticmethod
    @abc.abstractmethod
    def find_related_frames_to_jpg(frames_root, root_name, extension):
        return 3, tuple, str

    @staticmethod
    @abc.abstractmethod
    def get_copy_command_for_frames():
        return 1, str, str

    @staticmethod
    @abc.abstractmethod
    def find_all_files(compare_name_meta, compare_name_frames):
        return 2, tuple, set
