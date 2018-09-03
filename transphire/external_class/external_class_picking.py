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
from . import external_class_util as eutil


class InterfaceClass(abc.ABC):

    @staticmethod
    @abc.abstractmethod
    def get_filter_command():
        return 1, None, None

    @staticmethod
    @abc.abstractmethod
    def get_import_data():
        return 1, None, None

    @staticmethod
    @abc.abstractmethod
    def get_command():
        return 1, None, None


class TemplateClass(InterfaceClass):

    def __init__(self, template_dict):
        self.template_dict = template_dict

    @eutil.check_interface(InterfaceClass)
    def get_filter_command(self, static_args, static_kwargs, name):
        return self.template_dict[name](*static_args, **static_kwargs)

    @eutil.check_interface(InterfaceClass)
    def get_import_data(self, static_args, static_kwargs, name):
        return self.template_dict[name](*static_args, **static_kwargs)

    @eutil.check_interface(InterfaceClass)
    def get_command(self, static_args, static_kwargs, name):
        return self.template_dict[name](*static_args, **static_kwargs)
