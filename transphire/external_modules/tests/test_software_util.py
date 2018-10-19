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


from .. import software
from ..acquisition_software import epu


class TestLoadSoftware_falcon:

    def test_load_software_get_meta_data_18_returns_epus(self):
        assert software.load_software('get_meta_data', 'EPU', 'Falcon', '1.8') == epu.get_meta_data__1_8

    def test_load_software_get_movie_18_returns_epus(self):
        assert software.load_software('get_movie', 'EPU', 'Falcon', '1.8') == epu.get_movie__1_8_falcon

    def test_load_software_get_copy_command_18_returns_epus(self):
        assert software.load_software('get_copy_command', 'EPU', 'Falcon', '1.8') == epu.get_copy_command__1_8

    def test_load_software_get_pattern_18_returns_epus(self):
        assert software.load_software('get_pattern', 'EPU', 'Falcon', '1.8') == epu.get_pattern__1_8

    def test_load_software_get_meta_data_19_returns_epus(self):
        assert software.load_software('get_meta_data', 'EPU', 'Falcon', '1.9') == epu.get_meta_data__1_8

    def test_load_software_get_movie_19_returns_epus(self):
        assert software.load_software('get_movie', 'EPU', 'Falcon', '1.9') == epu.get_movie__1_8_falcon

    def test_load_software_get_copy_command_19_returns_epus(self):
        assert software.load_software('get_copy_command', 'EPU', 'Falcon', '1.9') == epu.get_copy_command__1_8

    def test_load_software_get_pattern_19_returns_epus(self):
        assert software.load_software('get_pattern', 'EPU', 'Falcon', '1.9') == epu.get_pattern__1_8


class TestLoadSoftware_k218:

    def test_load_software_get_meta_data_18_returns_epus(self):
        assert software.load_software('get_meta_data', 'EPU', 'K2', '1.8') == epu.get_meta_data__1_8

    def test_load_software_get_movie_18_returns_epus(self):
        assert software.load_software('get_movie', 'EPU', 'K2', '1.8') == epu.get_movie__1_8_k2

    def test_load_software_get_copy_command_18_returns_epus(self):
        assert software.load_software('get_copy_command', 'EPU', 'K2', '1.8') == epu.get_copy_command__1_8

    def test_load_software_get_pattern_18_returns_epus(self):
        assert software.load_software('get_pattern', 'EPU', 'K2', '1.8') == epu.get_pattern__1_8

    def test_load_software_get_meta_data_19_returns_epus(self):
        assert software.load_software('get_meta_data', 'EPU', 'K2', '1.9') == epu.get_meta_data__1_8

    def test_load_software_get_movie_19_returns_epus(self):
        assert software.load_software('get_movie', 'EPU', 'K2', '1.9') == epu.get_movie__1_9_k2

    def test_load_software_get_copy_command_19_returns_epus(self):
        assert software.load_software('get_copy_command', 'EPU', 'K2', '1.9') == epu.get_copy_command__1_8

    def test_load_software_get_pattern_19_returns_epus(self):
        assert software.load_software('get_pattern', 'EPU', 'K2', '1.9') == epu.get_pattern__1_8
