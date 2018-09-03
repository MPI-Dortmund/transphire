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
from . import external_class_util as eu
from . import external_class_software as es


class InterfaceClass(abc.ABC):

    @staticmethod
    @abc.abstractmethod
    def run_step():
        return 1, None, None


class TemplateClass(InterfaceClass, es.TemplateSoftwareClass):

    def __init__(self, function_dict):
        super().__init__(function_dict)

    @eu.check_interface(InterfaceClass)
    def run_step(self, static_args, static_kwargs, name):
        return getattr(super(), name)(name, *static_args, **static_kwargs)
