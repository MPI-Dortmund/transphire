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


import pytest
from .. import external_class_software as es


class DummyFunctions():

    def get_meta_info__dummy():
        return 'software_get_meta_info'

    def get_frames__dummy():
        return 'software_get_frames'

    def get_number_of_frames__dummy():
        return 'software_get_number_of_frames'

    def get_meta_data__dummy():
        return 'software_get_meta_data'

    def get_command__dummy():
        return 'software_get_command'


class TestTemplateSoftwareClass():

    @pytest.fixture(scope='class')
    def get_test_dict(self):
        return {
            'get_meta_info': DummyFunctions.get_meta_info__dummy,
            'get_frames': DummyFunctions.get_frames__dummy,
            'get_number_of_frames': DummyFunctions.get_number_of_frames__dummy,
            'get_meta_data': DummyFunctions.get_meta_data__dummy,
            'get_command': DummyFunctions.get_command__dummy,
            }

    def test_get_meta_info(self, get_test_dict):
        test = es.TemplateSoftwareClass(get_test_dict)
        test.get_meta_info('get_meta_info') == 'software_get_meta_info'

    def test_get_frames(self, get_test_dict):
        test = es.TemplateSoftwareClass(get_test_dict)
        test.get_frames('get_frames') == 'software_get_frames'

    def test_get_number_of_frames(self, get_test_dict):
        test = es.TemplateSoftwareClass(get_test_dict)
        test.get_number_of_frames('get_number_of_frames') == 'software_get_number_of_frames'

    def test_get_meta_data(self, get_test_dict):
        test = es.TemplateSoftwareClass(get_test_dict)
        test.get_meta_data('get_meta_data') == 'software_get_meta_data'

    def test_get_command(self, get_test_dict):
        test = es.TemplateSoftwareClass(get_test_dict)
        test.get_command('get_command') == 'software_get_command'
