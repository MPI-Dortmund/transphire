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

import transphire.external_util.software_base as tsb
import transphire.external_util.class_util as tcu
import transphire.external_util.software_util as tsu

class SoftwareClass(tsb.SoftwareBase):

    @staticmethod
    @tcu.check_instance(tsb.SoftwareBase)
    def extract_time_and_grid_information(static_args, static_kwargs):
        return tsu.extract_time_grid_epu_18_falcon2(*static_args, **static_kwargs)

    @staticmethod
    @tcu.check_instance(tsb.SoftwareBase)
    def find_frames(static_args, static_kwargs):
        return tsu.find_frames_epu18_falcon2(*static_args, **static_kwargs)

    @staticmethod
    @tcu.check_instance(tsb.SoftwareBase)
    def check_nr_frames(static_args, static_kwargs):
        return tsu.check_nr_frames_epu18_falcon2(*static_args, **static_kwargs)

    @staticmethod
    @tcu.check_instance(tsb.SoftwareBase)
    def find_related_frames_to_jpg(static_args, static_kwargs):
        return tsu.find_related_frames_epu18_falcon2(*static_args, **static_kwargs)

    @staticmethod
    @tcu.check_instance(tsb.SoftwareBase)
    def get_copy_command_for_frames(static_args, static_kwargs):
        return tsu.get_copy_command_epu18_falcon2(*static_args, **static_kwargs)

    @staticmethod
    @tcu.check_instance(tsb.SoftwareBase)
    def find_all_files(static_args, static_kwargs):
        return tsu.find_frames_epu18_falcon2(*static_args, **static_kwargs)
