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


import xml.etree.ElementTree as et
import pytest
from .. import read_xml


class TestGetAllKeyValue():

    def test_should_return_dose(self):
        root = et.Element('root')
        doc1 = et.SubElement(root, '{http://schemas.microsoft.com/2003/10/Serialization/Arrays}Key')
        doc1.text = 'Dose'
        doc2 = et.SubElement(root, '{http://schemas.microsoft.com/2003/10/Serialization/Arrays}Value')
        doc2.text = '1.0'

        data_dict = {}
        read_xml.get_all_key_value(root, data_dict)

        assert data_dict == {'Dose': '1.0'}

    def test_should_return_empty(self):
        root = et.Element('root')

        data_dict = {}
        read_xml.get_all_key_value(root, data_dict)

        assert data_dict == {}

    def test_should_return_FramesPerFraction_falcon(self):
        root = et.Element('root')
        doc1 = et.SubElement(root, '{http://schemas.microsoft.com/2003/10/Serialization/Arrays}Key')
        doc1.text = 'foo'
        doc2 = et.SubElement(root, '{http://schemas.microsoft.com/2003/10/Serialization/Arrays}Value')
        doc2a = et.SubElement(doc2, '{http://schemas.datacontract.org/2004/07/Fei.Applications.Common.Omp.Interface}DoseFractions')
        doc3 = et.SubElement(doc2a, 'anyType')
        doc4 = et.SubElement(doc3, 'EndFrameNumber')
        doc4.text = '2'
        doc5 = et.SubElement(doc3, 'StartFrameNumber')
        doc5.text = '0'

        data_dict = {}
        read_xml.get_all_key_value(root, data_dict)

        assert data_dict == {'NumberOffractions': '1', 'FramesPerFraction': '3'}

    def test_should_return_FramesPerFraction_k2(self):
        root = et.Element('root')
        doc1 = et.SubElement(root, '{http://schemas.microsoft.com/2003/10/Serialization/Arrays}Key')
        doc1.text = 'foo'
        doc2 = et.SubElement(root, '{http://schemas.microsoft.com/2003/10/Serialization/Arrays}Value')
        doc3 = et.SubElement(doc2, '{http://schemas.datacontract.org/2004/07/Fei.Applications.Common.Omp.Interface}NumberOffractions')
        doc3.text = '3'

        data_dict = {}
        read_xml.get_all_key_value(root, data_dict)

        assert data_dict == {'NumberOffractions': '3', 'FramesPerFraction': '1'}

    def test_should_assert_double_key(self):
        root = et.Element('root')
        doc1 = et.SubElement(root, '{http://schemas.microsoft.com/2003/10/Serialization/Arrays}Key')
        doc1.text = 'foo'
        doc2 = et.SubElement(root, '{http://schemas.microsoft.com/2003/10/Serialization/Arrays}Value')
        doc2.text = '3'
        doc1 = et.SubElement(root, '{http://schemas.microsoft.com/2003/10/Serialization/Arrays}Key')
        doc1.text = 'foo'
        doc2 = et.SubElement(root, '{http://schemas.microsoft.com/2003/10/Serialization/Arrays}Value')
        doc2.text = '4'

        data_dict = {}
        with pytest.raises(AssertionError):
            read_xml.get_all_key_value(root, data_dict)

    def test_should_assert_unequal_key_value_number(self):
        root = et.Element('root')
        doc1 = et.SubElement(root, '{http://schemas.microsoft.com/2003/10/Serialization/Arrays}Key')
        doc1.text = 'foo'
        doc2 = et.SubElement(root, '{http://schemas.microsoft.com/2003/10/Serialization/Arrays}Value')
        doc2.text = '3'
        doc1 = et.SubElement(root, '{http://schemas.microsoft.com/2003/10/Serialization/Arrays}Key')
        doc1.text = 'foo'

        data_dict = {}
        with pytest.raises(AssertionError):
            read_xml.get_all_key_value(root, data_dict)


class TestGetLevel0Xml():

    def test_should_find_key_and_value(self):
        key =  '{http://schemas.microsoft.com/2003/10/Serialization/Arrays}TestRun'
        root = et.Element('root')
        doc1 = et.SubElement(root, key)
        doc1.text = 'foo'

        data_dict = {}
        read_xml.get_level_0_xml(doc1, key, [], data_dict)

        assert data_dict == {'TestRun': 'foo'}

    def test_should_not_find_key_and_value(self):
        key =  '{http://schemas.microsoft.com/2003/10/Serialization/Arrays}TestRun'
        root = et.Element('root')
        doc1 = et.SubElement(root, key)
        doc1.text = 'foo'

        data_dict = {}
        read_xml.get_level_0_xml(root, key, [], data_dict)

        assert data_dict == {}


class TestGetLevel1Xml():

    def test_should_find_key_and_value_one_tag_prefix(self):
        key =  '{http://schemas.microsoft.com/2003/10/Serialization/Arrays}TestRun'
        search_keys = ['{http://schemas.microsoft.com/2003/10/Serialization/Arrays}x']
        sub_keys_values = ['1.00']
        root = et.Element('root')
        doc1 = et.SubElement(root, key)
        for entry1, entry2 in zip(search_keys, sub_keys_values):
            doc = et.SubElement(doc1, entry1)
            doc.text = entry2

        data_dict = {}
        read_xml.get_level_1_xml(doc1, key, search_keys, data_dict)

        assert data_dict == {'TestRun_x': '1.00'}

    def test_should_find_key_and_value_one_no_tag_prefix(self):
        key =  '{http://schemas.microsoft.com/2003/10/Serialization/Arrays}TestRun'
        tree_key = ['{http://schemas.microsoft.com/2003/10/Serialization/Arrays}x']
        search_keys = ['x']
        sub_keys_values = ['1.00']
        root = et.Element('root')
        doc1 = et.SubElement(root, key)
        for entry1, entry2 in zip(tree_key, sub_keys_values):
            doc = et.SubElement(doc1, entry1)
            doc.text = entry2

        data_dict = {}
        read_xml.get_level_1_xml(doc1, key, search_keys, data_dict)

        assert data_dict == {'TestRun_x': '1.00'}

    def test_should_find_key_and_value_multiple(self):
        key =  '{http://schemas.microsoft.com/2003/10/Serialization/Arrays}TestRun'
        search_keys = [
            '{http://schemas.microsoft.com/2003/10/Serialization/Arrays}x',
            '{http://schemas.microsoft.com/2003/10/Serialization/Arrays}y',
            '{http://schemas.microsoft.com/2003/10/Serialization/Arrays}z',
            ]
        sub_keys_values = [
            '1.00',
            '2.00',
            '3.00',
            ]
        root = et.Element('root')
        doc1 = et.SubElement(root, key)
        for entry1, entry2 in zip(search_keys, sub_keys_values):
            doc = et.SubElement(doc1, entry1)
            doc.text = entry2

        data_dict = {}
        read_xml.get_level_1_xml(doc1, key, search_keys, data_dict)

        assert data_dict == {
            'TestRun_x': '1.00',
            'TestRun_y': '2.00',
            'TestRun_z': '3.00',
            }

    def test_should_find_key_and_value_multiple_no_tag_prefix(self):
        key =  '{http://schemas.microsoft.com/2003/10/Serialization/Arrays}TestRun'
        tree_keys = [
            '{http://schemas.microsoft.com/2003/10/Serialization/Arrays}x',
            '{http://schemas.microsoft.com/2003/10/Serialization/Arrays}y',
            '{http://schemas.microsoft.com/2003/10/Serialization/Arrays}z',
            ]
        search_keys = [
            'x',
            'y',
            'z',
            ]
        sub_keys_values = [
            '1.00',
            '2.00',
            '3.00',
            ]
        root = et.Element('root')
        doc1 = et.SubElement(root, key)
        for entry1, entry2 in zip(tree_keys, sub_keys_values):
            doc = et.SubElement(doc1, entry1)
            doc.text = entry2

        data_dict = {}
        read_xml.get_level_1_xml(doc1, key, search_keys, data_dict)

        assert data_dict == {
            'TestRun_x': '1.00',
            'TestRun_y': '2.00',
            'TestRun_z': '3.00',
            }

    def test_should_find_key_and_value_one_both_no_tag_prefix(self):
        key =  '{http://schemas.microsoft.com/2003/10/Serialization/Arrays}TestRun'
        search_keys = ['x']
        sub_keys_values = ['1.00']
        root = et.Element('root')
        doc1 = et.SubElement(root, key)
        for entry1, entry2 in zip(search_keys, sub_keys_values):
            doc = et.SubElement(doc1, entry1)
            doc.text = entry2

        data_dict = {}
        read_xml.get_level_1_xml(doc1, key, search_keys, data_dict)
        assert data_dict == {'TestRun_x': '1.00'}

    def test_should_find_key_and_value_multiple_both_no_tag_prefix(self):
        key =  '{http://schemas.microsoft.com/2003/10/Serialization/Arrays}TestRun'
        search_keys = ['x', 'y', 'z']
        sub_keys_values = ['1.00', '2.00', '3.00']
        root = et.Element('root')
        doc1 = et.SubElement(root, key)
        for entry1, entry2 in zip(search_keys, sub_keys_values):
            doc = et.SubElement(doc1, entry1)
            doc.text = entry2

        data_dict = {}
        read_xml.get_level_1_xml(doc1, key, search_keys, data_dict)
        assert data_dict == {
            'TestRun_x': '1.00',
            'TestRun_y': '2.00',
            'TestRun_z': '3.00',
            }

    def test_should_not_find_main_key(self):
        key =  '{http://schemas.microsoft.com/2003/10/Serialization/Arrays}TestRun'
        search_keys = ['x', 'y', 'z']
        sub_keys_values = ['1.00', '2.00', '3.00']
        root = et.Element('root')
        doc1 = et.SubElement(root, key)
        for entry1, entry2 in zip(search_keys, sub_keys_values):
            doc = et.SubElement(doc1, entry1)
            doc.text = entry2

        data_dict = {}
        read_xml.get_level_1_xml(doc1, 'not_found', search_keys, data_dict)
        assert data_dict == {}

    def test_should_not_find_second_key_no_subkey(self):
        key =  '{http://schemas.microsoft.com/2003/10/Serialization/Arrays}TestRun'
        search_keys = ['x', 'y', 'z']
        sub_keys_values = ['1.00', '2.00', '3.00']
        root = et.Element('root')
        doc1 = et.SubElement(root, key)

        data_dict = {}
        read_xml.get_level_1_xml(doc1, key, search_keys, data_dict)
        assert data_dict == {}

    def test_should_not_find_second_key_wrong_subkey(self):
        key =  '{http://schemas.microsoft.com/2003/10/Serialization/Arrays}TestRun'
        search_keys = ['x', 'y', 'z']
        sub_keys_values = ['1.00', '2.00', '3.00']
        root = et.Element('root')
        doc1 = et.SubElement(root, key)
        for entry1, entry2 in zip(search_keys, sub_keys_values):
            doc = et.SubElement(doc1, entry1)
            doc.text = entry2

        data_dict = {}
        read_xml.get_level_1_xml(doc1, key, ['k'], data_dict)
        assert data_dict == {}

    def test_should_not_find_second_partially_wrong_subkey(self):
        key =  '{http://schemas.microsoft.com/2003/10/Serialization/Arrays}TestRun'
        search_keys = ['x', 'y', 'z']
        sub_keys_values = ['1.00', '2.00', '3.00']
        root = et.Element('root')
        doc1 = et.SubElement(root, key)
        for entry1, entry2 in zip(search_keys, sub_keys_values):
            doc = et.SubElement(doc1, entry1)
            doc.text = entry2

        data_dict = {}
        read_xml.get_level_1_xml(doc1, key, ['x', 'y', 'k'], data_dict)
        assert data_dict == {
            'TestRun_x': '1.00',
            'TestRun_y': '2.00',
            }


class TestGetLevel3Xml():

    def test_should_find_key_and_value_tag_prefix(self):
        key =  '{http://schemas.microsoft.com/2003/10/Serialization/Arrays}TestRun'
        tree_key = ['{http://schemas.microsoft.com/2003/10/Serialization/Arrays}x']
        sub_keys_values = ['1.00']
        root = et.Element('root')
        doc1 = et.SubElement(root, key)
        doc2 = et.SubElement(doc1, 'test1')
        doc3 = et.SubElement(doc2, 'test2')
        for entry1, entry2 in zip(tree_key, sub_keys_values):
            doc = et.SubElement(doc3, entry1)
            doc.text = entry2

        data_dict = {}
        read_xml.get_level_3_xml(doc1, key, tree_key, data_dict)

        assert data_dict == {'test1_test2': '1.00'}


    def test_should_find_key_and_value_no_tag_prefix(self):
        key =  '{http://schemas.microsoft.com/2003/10/Serialization/Arrays}TestRun'
        tree_key = ['{http://schemas.microsoft.com/2003/10/Serialization/Arrays}x']
        search_keys = ['x']
        sub_keys_values = ['1.00']
        root = et.Element('root')
        doc1 = et.SubElement(root, key)
        doc2 = et.SubElement(doc1, 'test1')
        doc3 = et.SubElement(doc2, 'test2')
        for entry1, entry2 in zip(tree_key, sub_keys_values):
            doc = et.SubElement(doc3, entry1)
            doc.text = entry2

        data_dict = {}
        read_xml.get_level_3_xml(doc1, key, search_keys, data_dict)

        assert data_dict == {'test1_test2': '1.00'}


    def test_should_find_key_and_value_both_no_tag_prefix(self):
        key =  '{http://schemas.microsoft.com/2003/10/Serialization/Arrays}TestRun'
        search_keys = ['x']
        sub_keys_values = ['1.00']
        root = et.Element('root')
        doc1 = et.SubElement(root, key)
        doc2 = et.SubElement(doc1, 'test1')
        doc3 = et.SubElement(doc2, 'test2')
        for entry1, entry2 in zip(search_keys, sub_keys_values):
            doc = et.SubElement(doc3, entry1)
            doc.text = entry2

        data_dict = {}
        read_xml.get_level_3_xml(doc1, key, search_keys, data_dict)
        assert data_dict == {'test1_test2': '1.00'}

    def test_should_not_find_main_key(self):
        key =  '{http://schemas.microsoft.com/2003/10/Serialization/Arrays}TestRun'
        search_keys = ['x']
        sub_keys_values = ['1.00']
        root = et.Element('root')
        doc1 = et.SubElement(root, key)
        doc2 = et.SubElement(doc1, 'test1')
        doc3 = et.SubElement(doc2, 'test2')
        for entry1, entry2 in zip(search_keys, sub_keys_values):
            doc = et.SubElement(doc3, entry1)
            doc.text = entry2

        data_dict = {}
        read_xml.get_level_3_xml(doc1, 'not_found', search_keys, data_dict)
        assert data_dict == {}

    def test_should_not_find_second_key_no_subkey(self):
        key =  '{http://schemas.microsoft.com/2003/10/Serialization/Arrays}TestRun'
        search_keys = ['x']
        root = et.Element('root')
        doc1 = et.SubElement(root, key)

        data_dict = {}
        read_xml.get_level_3_xml(doc1, key, search_keys, data_dict)
        assert data_dict == {}

    def test_should_not_find_second_key_deep_2(self):
        key =  '{http://schemas.microsoft.com/2003/10/Serialization/Arrays}TestRun'
        root = et.Element('root')
        doc1 = et.SubElement(root, key)
        doc2 = et.SubElement(doc1, 'test1')

        data_dict = {}
        read_xml.get_level_3_xml(doc1, key, ['k'], data_dict)
        assert data_dict == {}

    def test_should_not_find_second_key_deep_3(self):
        key =  '{http://schemas.microsoft.com/2003/10/Serialization/Arrays}TestRun'
        root = et.Element('root')
        doc1 = et.SubElement(root, key)
        doc2 = et.SubElement(doc1, 'test1')
        doc2 = et.SubElement(doc2, 'test2')

        data_dict = {}
        read_xml.get_level_3_xml(doc1, key, ['k'], data_dict)
        assert data_dict == {}

    def test_should_not_find_second_key_wrong_key(self):
        key =  '{http://schemas.microsoft.com/2003/10/Serialization/Arrays}TestRun'
        search_keys = ['x']
        sub_keys_values = ['1.00']
        root = et.Element('root')
        doc1 = et.SubElement(root, key)
        doc2 = et.SubElement(doc1, 'test1')
        doc3 = et.SubElement(doc2, 'test2')
        for entry1, entry2 in zip(search_keys, sub_keys_values):
            doc = et.SubElement(doc3, entry1)
            doc.text = entry2

        data_dict = {}
        read_xml.get_level_3_xml(doc1, key, ['k'], data_dict)
        assert data_dict == {}
