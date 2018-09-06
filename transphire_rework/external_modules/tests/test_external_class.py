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
from .. import external_class as ec


class TestTemplateClass:

    def test_not_known_should_raise_assertion(self):
        test_class = ec.TemplateClass({'now_known': 'worked'})
        with pytest.raises(AssertionError):
            test_class.run_step('now_known')

    def test_get_content_should_return_worked(self):
        test_class = ec.TemplateClass({'get_content': 'worked'})
        assert test_class.run_step('get_content') == 'worked'

    def test_get_final_command_should_return_worked(self):
        test_class = ec.TemplateClass({'get_final_command': 'worked'})
        assert test_class.run_step('get_final_command') == 'worked'

    def test_get_first_command_should_return_worked(self):
        test_class = ec.TemplateClass({'get_first_command': 'worked'})
        assert test_class.run_step('get_first_command') == 'worked'

    def test_get_import_data_should_return_worked(self):
        test_class = ec.TemplateClass({'get_import_data': 'worked'})
        assert test_class.run_step('get_import_data') == 'worked'

    def test_get_name_should_return_worked(self):
        test_class = ec.TemplateClass({'get_name': 'worked'})
        assert test_class.run_step('get_name') == 'worked'

    def test_get_output_files_should_return_worked(self):
        test_class = ec.TemplateClass({'get_output_files': 'worked'})
        assert test_class.run_step('get_output_files') == 'worked'

    def test_get_post_final_command_should_return_worked(self):
        test_class = ec.TemplateClass({'get_post_final_command': 'worked'})
        assert test_class.run_step('get_post_final_command') == 'worked'

    def test_get_post_first_command_should_return_worked(self):
        test_class = ec.TemplateClass({'get_post_first_command': 'worked'})
        assert test_class.run_step('get_post_first_command') == 'worked'

    def test_get_post_second_command_should_return_worked(self):
        test_class = ec.TemplateClass({'get_post_second_command': 'worked'})
        assert test_class.run_step('get_post_second_command') == 'worked'

    def test_get_post_third_command_should_return_worked(self):
        test_class = ec.TemplateClass({'get_post_third_command': 'worked'})
        assert test_class.run_step('get_post_third_command') == 'worked'

    def test_get_pre_final_command_should_return_worked(self):
        test_class = ec.TemplateClass({'get_pre_final_command': 'worked'})
        assert test_class.run_step('get_pre_final_command') == 'worked'

    def test_get_pre_first_command_should_return_worked(self):
        test_class = ec.TemplateClass({'get_pre_first_command': 'worked'})
        assert test_class.run_step('get_pre_first_command') == 'worked'

    def test_get_pre_second_command_should_return_worked(self):
        test_class = ec.TemplateClass({'get_pre_second_command': 'worked'})
        assert test_class.run_step('get_pre_second_command') == 'worked'

    def test_get_pre_third_command_should_return_worked(self):
        test_class = ec.TemplateClass({'get_pre_third_command': 'worked'})
        assert test_class.run_step('get_pre_third_command') == 'worked'

    def test_get_second_command_should_return_worked(self):
        test_class = ec.TemplateClass({'get_second_command': 'worked'})
        assert test_class.run_step('get_second_command') == 'worked'

    def test_get_third_command_should_return_worked(self):
        test_class = ec.TemplateClass({'get_third_command': 'worked'})
        assert test_class.run_step('get_third_command') == 'worked'

    def test_get_type_should_return_worked(self):
        test_class = ec.TemplateClass({'get_type': 'worked'})
        assert test_class.run_step('get_type') == 'worked'

    def test_get_version_should_return_worked(self):
        test_class = ec.TemplateClass({'get_version': 'worked'})
        assert test_class.run_step('get_version') == 'worked'
