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


import re
import abc


def check_return(number, type_return, type_entry, return_value):
    if type_return is None:
        assert return_value is type_return
    else:
        assert isinstance(return_value, type_return)

    if number == 1:
        if type_entry is None:
            assert return_value is type_entry
        else:
            assert isinstance(return_value, type_entry)
    else:
        dtypes = []
        if isinstance(type_entry, list):
            dtypes.extend(type_entry)
        else:
            dtypes.extend([type_entry for _ in range(number)])
        assert len(dtypes) == number

        for value, entry in zip(return_value, dtypes):
            if entry is None:
                assert value is None
            else:
                assert isinstance(value, entry)


def check_instance(parent_instance):
    def check_arguments(func):
        def wrap(*args, **kwargs):
            self = args[0]
            args = args[1:]
            func_name = re.match(r'.*\.([^ ]+) .*', str(func)).group(1)
            method = getattr(parent_instance, func_name)
            number, type_return, type_entry = method(*args, **kwargs)
            return_value = func(self, static_args=args, static_kwargs=kwargs, name=func_name)

            check_return(
                number=number,
                type_return=type_return,
                type_entry=type_entry,
                return_value=return_value
                )

            return return_value
        return wrap
    return check_arguments


class ExternalBase(abc.ABC):

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


class TemplateClass(ExternalBase):

    def __init__(self, template_dict):
        self.template_dict = template_dict

    @check_instance(ExternalBase)
    def extract_time_and_grid_information(self, static_args, static_kwargs, name):
        return self.template_dict[name](*static_args, **static_kwargs)

    @check_instance(ExternalBase)
    def find_frames(self, static_args, static_kwargs, name):
        return self.template_dict[name](*static_args, **static_kwargs)

    @check_instance(ExternalBase)
    def check_nr_frames(self, static_args, static_kwargs, name):
        return self.template_dict[name](*static_args, **static_kwargs)

    @check_instance(ExternalBase)
    def find_related_frames_to_jpg(self, static_args, static_kwargs, name):
        return self.template_dict[name](*static_args, **static_kwargs)

    @check_instance(ExternalBase)
    def get_copy_command_for_frames(self, static_args, static_kwargs, name):
        return self.template_dict[name](*static_args, **static_kwargs)

    @check_instance(ExternalBase)
    def find_all_files(self, static_args, static_kwargs, name):
        return self.template_dict[name](*static_args, **static_kwargs)
