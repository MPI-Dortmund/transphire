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


class TestTemplateClass_Software():

    def test_get_meta_info(self, test_class_template_software):
        assert test_class_template_software.run_step('get_meta_info') == 'software_class_get_meta_info'

    def test_get_frames(self, test_class_template_software):
        assert test_class_template_software.run_step('get_frames') == 'software_class_get_frames'

    def test_get_number_of_frames(self, test_class_template_software):
        assert test_class_template_software.run_step('get_number_of_frames') == 'software_class_get_number_of_frames'

    def test_get_meta_data(self, test_class_template_software):
        assert test_class_template_software.run_step('get_meta_data') == 'software_class_get_meta_data'

    def test_get_command(self, test_class_template_software):
        assert test_class_template_software.run_step('get_command') == 'software_class_get_command'


class TestTemplateClass_Motion():

    def test_get_import_data(self, test_class_template_motion):
        assert test_class_template_motion.run_step('get_import_data') == 'motion_class_get_import_data'

    def test_get_command(self, test_class_template_motion):
        assert test_class_template_motion.run_step('get_command') == 'motion_class_get_command'

    def test_get_frame_range(self, test_class_template_motion):
        assert test_class_template_motion.run_step('get_frame_range') == 'motion_class_get_frame_range'


class TestTemplateClass_CTF():

    def test_get_import_data(self, test_class_template_ctf):
        assert test_class_template_ctf.run_step('get_import_data') == 'ctf_class_get_import_data'

    def test_get_command(self, test_class_template_ctf):
        assert test_class_template_ctf.run_step('get_command') == 'ctf_class_get_command'

    def test_move_outputs(self, test_class_template_ctf):
        assert test_class_template_ctf.run_step('move_outputs') == 'ctf_class_move_outputs'


class TestTemplateClass_Picking():

    def test_get_import_data(self, test_class_template_picking):
        assert test_class_template_picking.run_step('get_import_data') == 'picking_class_get_import_data'

    def test_get_command(self, test_class_template_picking):
        assert test_class_template_picking.run_step('get_command') == 'picking_class_get_command'

    def test_get_filter_command(self, test_class_template_picking):
        assert test_class_template_picking.run_step('get_filter_command') == 'picking_class_get_filter_command'


class TestTemplateClass_Compress():

    def test_get_command(self, test_class_template_compress):
        assert test_class_template_compress.run_step('get_command') == 'compress_class_get_command'


class TestTemplateClass_Copy_Extern():

    def test_tar_files(self, test_class_template_copy_extern):
        assert test_class_template_copy_extern.run_step('tar_files') == 'copy_extern_class_tar_files'

    def test_get_command(self, test_class_template_copy_extern):
        assert test_class_template_copy_extern.run_step('get_command') == 'copy_extern_class_get_command'


class TestTemplateClass_Unknown():

    def test_class_unknown(self):
        with pytest.raises(KeyError):
            ec.TemplateClass('unknown', {})
