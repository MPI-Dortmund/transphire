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
from . import external_class_software as esoft
from . import external_class_motion as emot
from . import external_class_ctf as ectf
from . import external_class_picking as epick
from . import external_class_compress as ecomp
from . import external_class_copy_extern as ece


class InterfaceClass(abc.ABC):

    @staticmethod
    @abc.abstractmethod
    def run_step():
        return 1, None, None


class TemplateClass(InterfaceClass):

    def __init__(self, class_type: str, function_dict: dict):
        super().__init__()
        type_dict = {
            'software': esoft,
            'motion': emot,
            'ctf': ectf,
            'picking': epick,
            'compress': ecomp,
            'copy_extern': ece,
            }
        self.parent = type_dict[class_type].TemplateClass(function_dict)

    @eutil.check_interface(InterfaceClass)
    def run_step(self, static_args, static_kwargs, name):
        return getattr(self.parent, name)(name, *static_args, **static_kwargs)