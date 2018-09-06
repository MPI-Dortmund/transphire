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


class TestTemplateSoftwareClass():

    def test_get_meta_info(self, test_class_software):
        test_class_software.get_meta_info('get_meta_info') == 'software_class_get_meta_info'

    def test_get_frames(self, test_class_software):
        test_class_software.get_frames('get_frames') == 'software_class_get_frames'

    def test_get_number_of_frames(self, test_class_software):
        test_class_software.get_number_of_frames('get_number_of_frames') == 'software_class_get_number_of_frames'

    def test_get_meta_data(self, test_class_software):
        test_class_software.get_meta_data('get_meta_data') == 'software_class_get_meta_data'

    def test_get_command(self, test_class_software):
        test_class_software.get_command('get_command') == 'software_class_get_command'
