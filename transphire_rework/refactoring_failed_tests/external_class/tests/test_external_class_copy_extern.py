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


class TestTemplateCopyExternClass():

    def test_tar_files(self, test_class_copy_extern):
        assert test_class_copy_extern.tar_files('tar_files') == 'copy_extern_class_tar_files'

    def test_get_command(self, test_class_copy_extern):
        assert test_class_copy_extern.get_command('get_command') == 'copy_extern_class_get_command'
