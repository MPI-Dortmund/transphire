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


import inspect
import pytest
from .. import external_class as ec
from .. import external_class_software as esoft
from .. import external_class_motion as emot
from .. import external_class_ctf as ectf
from .. import external_class_picking as epick
from .. import external_class_compress as ecomp
from .. import external_class_copy_extern as ece


class DummyFunctions_Software():

    def get_meta_info__dummy(self):
        return 'software_class_get_meta_info'

    def get_frames__dummy(self):
        return 'software_class_get_frames'

    def get_number_of_frames__dummy(self):
        return 'software_class_get_number_of_frames'

    def get_meta_data__dummy(self):
        return 'software_class_get_meta_data'

    def get_command__dummy(self):
        return 'software_class_get_command'


class DummyFunctions_Motion():

    def get_command__dummy(self):
        return 'motion_class_get_command'

    def get_import_data__dummy(self):
        return 'motion_class_get_import_data'

    def get_frame_range__dummy(self):
        return 'motion_class_get_frame_range'


class DummyFunctions_CTF():

    def get_command__dummy(self):
        return 'ctf_class_get_command'

    def get_import_data__dummy(self):
        return 'ctf_class_get_import_data'

    def move_outputs__dummy(self):
        return 'ctf_class_move_outputs'


class DummyFunctions_Picking():

    def get_filter_command__dummy(self):
        return 'picking_class_get_filter_command'

    def get_command__dummy(self):
        return 'picking_class_get_command'

    def get_import_data__dummy(self):
        return 'picking_class_get_import_data'


class DummyFunctions_Compress():

    def get_command__dummy(self):
        return 'compress_class_get_command'


class DummyFunctions_Copy_Extern():

    def get_command__dummy(self):
        return 'copy_extern_class_get_command'

    def tar_files__dummy(self):
        return 'copy_extern_class_tar_files'


def get_dict(dummy_class):
    attributes = [attr[0] for attr in inspect.getmembers(dummy_class) if not attr[0].startswith('__')]
    test_dict = {}
    for attr in attributes:
        name = attr.split('__')[0]
        test_dict[name] = getattr(dummy_class, attr)
    return test_dict


@pytest.fixture(scope='module')
def test_class_software():
    data_software = DummyFunctions_Software()
    test_dict = get_dict(data_software)
    return esoft.TemplateClass(test_dict)


@pytest.fixture(scope='module')
def test_class_template_software():
    data_software = DummyFunctions_Software()
    test_dict = get_dict(data_software)
    return ec.TemplateClass('software', test_dict)


@pytest.fixture(scope='module')
def test_class_motion():
    data_motion = DummyFunctions_Motion()
    test_dict = get_dict(data_motion)
    return emot.TemplateClass(test_dict)


@pytest.fixture(scope='module')
def test_class_template_motion():
    data_software = DummyFunctions_Motion()
    test_dict = get_dict(data_software)
    return ec.TemplateClass('motion', test_dict)


@pytest.fixture(scope='module')
def test_class_ctf():
    data_ctf = DummyFunctions_CTF()
    test_dict = get_dict(data_ctf)
    return ectf.TemplateClass(test_dict)


@pytest.fixture(scope='module')
def test_class_template_ctf():
    data_ctf = DummyFunctions_CTF()
    test_dict = get_dict(data_ctf)
    return ec.TemplateClass('ctf', test_dict)


@pytest.fixture(scope='module')
def test_class_picking():
    data_picking = DummyFunctions_Picking()
    test_dict = get_dict(data_picking)
    return epick.TemplateClass(test_dict)


@pytest.fixture(scope='module')
def test_class_template_picking():
    data_picking = DummyFunctions_Picking()
    test_dict = get_dict(data_picking)
    return ec.TemplateClass('picking', test_dict)


@pytest.fixture(scope='module')
def test_class_compress():
    data_compress = DummyFunctions_Compress()
    test_dict = get_dict(data_compress)
    return ecomp.TemplateClass(test_dict)


@pytest.fixture(scope='module')
def test_class_template_compress():
    data_compress = DummyFunctions_Compress()
    test_dict = get_dict(data_compress)
    return ec.TemplateClass('compress', test_dict)


@pytest.fixture(scope='module')
def test_class_copy_extern():
    data_copy_extern = DummyFunctions_Copy_Extern()
    test_dict = get_dict(data_copy_extern)
    return ece.TemplateClass(test_dict)


@pytest.fixture(scope='module')
def test_class_template_copy_extern():
    data_copy_extern = DummyFunctions_Copy_Extern()
    test_dict = get_dict(data_copy_extern)
    return ec.TemplateClass('copy_extern', test_dict)
