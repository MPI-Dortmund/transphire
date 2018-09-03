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
from .. import external_class_motion as em
from .. import external_class_software as es
from .. import external_class as ec


class DummyFunctions_Motion():

    def get_command__dummy(self):
        return 'motion_class_get_command'

    def get_import_data__dummy(self):
        return 'motion_class_get_import_data'

    def get_frame_range__dummy(self):
        return 'motion_class_get_frame_range'


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


def get_dict(dummy_class):
    attributes = [attr[0] for attr in inspect.getmembers(dummy_class) if not attr[0].startswith('__')]
    test_dict = {}
    for attr in attributes:
        name = attr.split('__')[0]
        test_dict[name] = getattr(dummy_class, attr)
    return test_dict


@pytest.fixture(scope='module')
def test_class_motion():
    data_motion = DummyFunctions_Motion()
    test_dict = get_dict(data_motion)
    return em.TemplateMotionClass(test_dict)


@pytest.fixture(scope='module')
def test_class_template_motion():
    data_software = DummyFunctions_Motion()
    test_dict = get_dict(data_software)
    return ec.TemplateClass('motion', test_dict)


@pytest.fixture(scope='module')
def test_class_software():
    data_software = DummyFunctions_Software()
    test_dict = get_dict(data_software)
    return es.TemplateSoftwareClass(test_dict)


@pytest.fixture(scope='module')
def test_class_template_software():
    data_software = DummyFunctions_Software()
    test_dict = get_dict(data_software)
    return ec.TemplateClass('software', test_dict)
