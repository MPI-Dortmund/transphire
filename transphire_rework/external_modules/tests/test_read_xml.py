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

    def test_single_key_value_should_return_filled_dict(self):
        key = '{http://schemas.microsoft.com/2003/10/Serialization/Arrays}Key'
        value = '{http://schemas.microsoft.com/2003/10/Serialization/Arrays}Value'
        root = et.Element('root')
        doc1 = et.SubElement(root, key)
        doc1.text = 'Dose'
        doc2 = et.SubElement(root, value)
        doc2.text = '1.0'

        data_dict = {}
        read_xml.get_all_key_value(root, key, value, data_dict)

        assert data_dict == {'Dose': '1.0'}

    def test_no_key_should_return_empty_dict(self):
        key = '{http://schemas.microsoft.com/2003/10/Serialization/Arrays}Key'
        value = '{http://schemas.microsoft.com/2003/10/Serialization/Arrays}Value'
        root = et.Element('root')

        data_dict = {}
        read_xml.get_all_key_value(root, key, value, data_dict)

        assert data_dict == {}

    def test_FramesPerFraction_falcon_should_return_filled_dict(self):
        key = '{http://schemas.microsoft.com/2003/10/Serialization/Arrays}Key'
        value = '{http://schemas.microsoft.com/2003/10/Serialization/Arrays}Value'
        root = et.Element('root')
        doc1 = et.SubElement(root, key)
        doc1.text = 'foo'
        doc2 = et.SubElement(root, value)
        doc2a = et.SubElement(doc2, '{http://schemas.datacontract.org/2004/07/Fei.Applications.Common.Omp.Interface}DoseFractions')
        doc3 = et.SubElement(doc2a, 'anyType')
        doc4 = et.SubElement(doc3, 'EndFrameNumber')
        doc4.text = '2'
        doc5 = et.SubElement(doc3, 'StartFrameNumber')
        doc5.text = '0'

        data_dict = {}
        read_xml.get_all_key_value(root, key, value, data_dict)

        assert data_dict == {'NumberOffractions': '1', 'FramesPerFraction': '3'}

    def test_FramesPerFraction_k2_should_return_filled_dict(self):
        key = '{http://schemas.microsoft.com/2003/10/Serialization/Arrays}Key'
        value = '{http://schemas.microsoft.com/2003/10/Serialization/Arrays}Value'
        root = et.Element('root')
        doc1 = et.SubElement(root, key)
        doc1.text = 'foo'
        doc2 = et.SubElement(root, value)
        doc3 = et.SubElement(doc2, '{http://schemas.datacontract.org/2004/07/Fei.Applications.Common.Omp.Interface}NumberOffractions')
        doc3.text = '3'

        data_dict = {}
        read_xml.get_all_key_value(root, key, value, data_dict)

        assert data_dict == {'NumberOffractions': '3', 'FramesPerFraction': '1'}

    @pytest.mark.filterwarnings("ignore:Warning")
    def test_unknown_subvalue_should_return_empty_dict(self):
        key = '{http://schemas.microsoft.com/2003/10/Serialization/Arrays}Key'
        value = '{http://schemas.microsoft.com/2003/10/Serialization/Arrays}Value'
        root = et.Element('root')
        doc1 = et.SubElement(root, key)
        doc1.text = 'foo'
        doc2 = et.SubElement(root, value)
        doc3 = et.SubElement(doc2, '{http://schemas.datacontract.org/2004/07/Fei.Applications.Common.Omp.Interface}Unknown')
        doc3.text = '3'

        data_dict = {}
        read_xml.get_all_key_value(root, key, value, data_dict)

        assert data_dict == {}

    def test_double_key_should_raise_attributeerror(self):
        key = '{http://schemas.microsoft.com/2003/10/Serialization/Arrays}Key'
        value = '{http://schemas.microsoft.com/2003/10/Serialization/Arrays}Value'
        root = et.Element('root')
        doc1 = et.SubElement(root, key)
        doc1.text = 'foo'
        doc2 = et.SubElement(root, value)
        doc2.text = '3'
        doc1 = et.SubElement(root, key)
        doc1.text = 'foo'
        doc2 = et.SubElement(root, value)
        doc2.text = '4'

        data_dict = {}
        with pytest.raises(AttributeError):
            read_xml.get_all_key_value(root, key, value, data_dict)

    def test_unequal_key_value_number_should_raise_assertionerror(self):
        key = '{http://schemas.microsoft.com/2003/10/Serialization/Arrays}Key'
        value = '{http://schemas.microsoft.com/2003/10/Serialization/Arrays}Value'
        root = et.Element('root')
        doc1 = et.SubElement(root, key)
        doc1.text = 'foo'
        doc2 = et.SubElement(root, value)
        doc2.text = '3'
        doc1 = et.SubElement(root, key)
        doc1.text = 'foo'

        data_dict = {}
        with pytest.raises(AssertionError):
            read_xml.get_all_key_value(root, key, value, data_dict)


class TestGetLevel0Xml():

    def test_key_exists_should_return_filled_dict(self):
        key =  '{http://schemas.microsoft.com/2003/10/Serialization/Arrays}TestRun'
        root = et.Element('root')
        doc1 = et.SubElement(root, key)
        doc1.text = 'foo'

        data_dict = {}
        read_xml.get_level_0_xml(doc1, key, [], data_dict)

        assert data_dict == {'TestRun': 'foo'}

    def test_key_not_exists_should_return_empty_dict(self):
        key =  '{http://schemas.microsoft.com/2003/10/Serialization/Arrays}TestRun'
        root = et.Element('root')
        doc1 = et.SubElement(root, key)
        doc1.text = 'foo'

        data_dict = {}
        read_xml.get_level_0_xml(root, key, [], data_dict)

        assert data_dict == {}

    def test_key_exists_twice_should_raise_attributeerror(self):
        key =  '{http://schemas.microsoft.com/2003/10/Serialization/Arrays}TestRun'
        root = et.Element('root')
        doc1 = et.SubElement(root, key)
        doc1.text = 'foo'

        data_dict = {}
        read_xml.get_level_0_xml(doc1, key, [], data_dict)
        with pytest.raises(AttributeError):
            read_xml.get_level_0_xml(doc1, key, [], data_dict)


class TestGetLevel1Xml():

    def test_key_exists_single_search_key_tag_prefix_single_tree_key_tag_prefix_should_return_filled_dict(self):
        key =  '{http://schemas.microsoft.com/2003/10/Serialization/Arrays}TestRun'
        tree_keys = ['{http://schemas.microsoft.com/2003/10/Serialization/Arrays}x']
        search_keys = ['{http://schemas.microsoft.com/2003/10/Serialization/Arrays}x']
        sub_keys_values = ['1.00']
        root = et.Element('root')
        doc1 = et.SubElement(root, key)
        for entry1, entry2 in zip(tree_keys, sub_keys_values):
            doc = et.SubElement(doc1, entry1)
            doc.text = entry2

        data_dict = {}
        read_xml.get_level_1_xml(doc1, key, search_keys, data_dict)

        assert data_dict == {'TestRun_x': '1.00'}

    def test_key_exists_single_search_key_no_tag_prefix_single_tree_key_tag_prefix_should_return_filled_dict(self):
        key =  '{http://schemas.microsoft.com/2003/10/Serialization/Arrays}TestRun'
        tree_keys = ['{http://schemas.microsoft.com/2003/10/Serialization/Arrays}x']
        search_keys = ['x']
        sub_keys_values = ['1.00']
        root = et.Element('root')
        doc1 = et.SubElement(root, key)
        for entry1, entry2 in zip(tree_keys, sub_keys_values):
            doc = et.SubElement(doc1, entry1)
            doc.text = entry2

        data_dict = {}
        read_xml.get_level_1_xml(doc1, key, search_keys, data_dict)

        assert data_dict == {'TestRun_x': '1.00'}

    def test_key_exists_single_search_key_tag_prefix_single_tree_key_no_tag_prefix_should_return_filled_dict(self):
        key =  '{http://schemas.microsoft.com/2003/10/Serialization/Arrays}TestRun'
        tree_keys = ['x']
        search_keys = ['{http://schemas.microsoft.com/2003/10/Serialization/Arrays}x']
        sub_keys_values = ['1.00']
        root = et.Element('root')
        doc1 = et.SubElement(root, key)
        for entry1, entry2 in zip(tree_keys, sub_keys_values):
            doc = et.SubElement(doc1, entry1)
            doc.text = entry2

        data_dict = {}
        read_xml.get_level_1_xml(doc1, key, search_keys, data_dict)

        assert data_dict == {'TestRun_x': '1.00'}

    def test_key_exists_single_search_key_no_tag_prefix_single_tree_key_no_tag_prefix_should_return_filled_dict(self):
        key =  '{http://schemas.microsoft.com/2003/10/Serialization/Arrays}TestRun'
        tree_keys = ['x']
        search_keys = ['x']
        sub_keys_values = ['1.00']
        root = et.Element('root')
        doc1 = et.SubElement(root, key)
        for entry1, entry2 in zip(tree_keys, sub_keys_values):
            doc = et.SubElement(doc1, entry1)
            doc.text = entry2

        data_dict = {}
        read_xml.get_level_1_xml(doc1, key, search_keys, data_dict)

        assert data_dict == {'TestRun_x': '1.00'}

    def test_key_exists_multiple_search_key_tag_prefix_multiple_tree_key_tag_prefix_should_return_filled_dict(self):
        key =  '{http://schemas.microsoft.com/2003/10/Serialization/Arrays}TestRun'
        tree_keys = []
        tree_keys.append('{http://schemas.microsoft.com/2003/10/Serialization/Arrays}x')
        tree_keys.append('{http://schemas.microsoft.com/2003/10/Serialization/Arrays}y')
        tree_keys.append('{http://schemas.microsoft.com/2003/10/Serialization/Arrays}z')
        search_keys = []
        search_keys.append('{http://schemas.microsoft.com/2003/10/Serialization/Arrays}x')
        search_keys.append('{http://schemas.microsoft.com/2003/10/Serialization/Arrays}y')
        search_keys.append('{http://schemas.microsoft.com/2003/10/Serialization/Arrays}z')
        sub_keys_values = []
        sub_keys_values.append('1.00')
        sub_keys_values.append('2.00')
        sub_keys_values.append('3.00')
        root = et.Element('root')
        doc1 = et.SubElement(root, key)
        for entry1, entry2 in zip(tree_keys, sub_keys_values):
            doc = et.SubElement(doc1, entry1)
            doc.text = entry2

        data_dict = {}
        read_xml.get_level_1_xml(doc1, key, search_keys, data_dict)

        assert data_dict == {'TestRun_x': '1.00', 'TestRun_y': '2.00', 'TestRun_z': '3.00'}

    def test_key_exists_multiple_search_key_no_tag_prefix_multiple_tree_key_tag_prefix_should_return_filled_dict(self):
        key =  '{http://schemas.microsoft.com/2003/10/Serialization/Arrays}TestRun'
        tree_keys = []
        tree_keys.append('{http://schemas.microsoft.com/2003/10/Serialization/Arrays}x')
        tree_keys.append('{http://schemas.microsoft.com/2003/10/Serialization/Arrays}y')
        tree_keys.append('{http://schemas.microsoft.com/2003/10/Serialization/Arrays}z')
        search_keys = []
        search_keys.append('x')
        search_keys.append('y')
        search_keys.append('z')
        sub_keys_values = []
        sub_keys_values.append('1.00')
        sub_keys_values.append('2.00')
        sub_keys_values.append('3.00')
        root = et.Element('root')
        doc1 = et.SubElement(root, key)
        for entry1, entry2 in zip(tree_keys, sub_keys_values):
            doc = et.SubElement(doc1, entry1)
            doc.text = entry2

        data_dict = {}
        read_xml.get_level_1_xml(doc1, key, search_keys, data_dict)

        assert data_dict == {'TestRun_x': '1.00', 'TestRun_y': '2.00', 'TestRun_z': '3.00'}

    def test_key_exists_multiple_search_key_tag_prefix_multiple_tree_no_key_tag_prefix_should_return_filled_dict(self):
        key =  '{http://schemas.microsoft.com/2003/10/Serialization/Arrays}TestRun'
        tree_keys = []
        tree_keys.append('{http://schemas.microsoft.com/2003/10/Serialization/Arrays}x')
        tree_keys.append('{http://schemas.microsoft.com/2003/10/Serialization/Arrays}y')
        tree_keys.append('{http://schemas.microsoft.com/2003/10/Serialization/Arrays}z')
        search_keys = []
        search_keys.append('x')
        search_keys.append('y')
        search_keys.append('z')
        sub_keys_values = []
        sub_keys_values.append('1.00')
        sub_keys_values.append('2.00')
        sub_keys_values.append('3.00')
        root = et.Element('root')
        doc1 = et.SubElement(root, key)
        for entry1, entry2 in zip(tree_keys, sub_keys_values):
            doc = et.SubElement(doc1, entry1)
            doc.text = entry2

        data_dict = {}
        read_xml.get_level_1_xml(doc1, key, search_keys, data_dict)

        assert data_dict == {'TestRun_x': '1.00', 'TestRun_y': '2.00', 'TestRun_z': '3.00'}

    def test_key_exists_multiple_search_no_key_tag_prefix_multiple_tree_no_key_tag_prefix_should_return_filled_dict(self):
        key =  '{http://schemas.microsoft.com/2003/10/Serialization/Arrays}TestRun'
        tree_keys = []
        tree_keys.append('x')
        tree_keys.append('y')
        tree_keys.append('z')
        search_keys = []
        search_keys.append('x')
        search_keys.append('y')
        search_keys.append('z')
        sub_keys_values = []
        sub_keys_values.append('1.00')
        sub_keys_values.append('2.00')
        sub_keys_values.append('3.00')
        root = et.Element('root')
        doc1 = et.SubElement(root, key)
        for entry1, entry2 in zip(tree_keys, sub_keys_values):
            doc = et.SubElement(doc1, entry1)
            doc.text = entry2

        data_dict = {}
        read_xml.get_level_1_xml(doc1, key, search_keys, data_dict)

        assert data_dict == {'TestRun_x': '1.00', 'TestRun_y': '2.00', 'TestRun_z': '3.00'}

    def test_key_exists_multiple_search_key_tag_prefix_multiple_tree_partially_no_key_tag_prefix_should_return_filled_dict(self):
        key =  '{http://schemas.microsoft.com/2003/10/Serialization/Arrays}TestRun'
        tree_keys = []
        tree_keys.append('{http://schemas.microsoft.com/2003/10/Serialization/Arrays}x')
        tree_keys.append('y')
        tree_keys.append('{http://schemas.microsoft.com/2003/10/Serialization/Arrays}z')
        search_keys = []
        search_keys.append('x')
        search_keys.append('y')
        search_keys.append('z')
        sub_keys_values = []
        sub_keys_values.append('1.00')
        sub_keys_values.append('2.00')
        sub_keys_values.append('3.00')
        root = et.Element('root')
        doc1 = et.SubElement(root, key)
        for entry1, entry2 in zip(tree_keys, sub_keys_values):
            doc = et.SubElement(doc1, entry1)
            doc.text = entry2

        data_dict = {}
        read_xml.get_level_1_xml(doc1, key, search_keys, data_dict)

        assert data_dict == {'TestRun_x': '1.00', 'TestRun_y': '2.00', 'TestRun_z': '3.00'}

    def test_key_exists_multiple_search_key_partially_tag_prefix_multiple_tree_partially_no_key_tag_prefix_should_return_filled_dict(self):
        key =  '{http://schemas.microsoft.com/2003/10/Serialization/Arrays}TestRun'
        tree_keys = []
        tree_keys.append('{http://schemas.microsoft.com/2003/10/Serialization/Arrays}x')
        tree_keys.append('y')
        tree_keys.append('{http://schemas.microsoft.com/2003/10/Serialization/Arrays}z')
        search_keys = []
        search_keys.append('{http://schemas.microsoft.com/2003/10/Serialization/Arrays}x')
        search_keys.append('y')
        search_keys.append('z')
        sub_keys_values = []
        sub_keys_values.append('1.00')
        sub_keys_values.append('2.00')
        sub_keys_values.append('3.00')
        root = et.Element('root')
        doc1 = et.SubElement(root, key)
        for entry1, entry2 in zip(tree_keys, sub_keys_values):
            doc = et.SubElement(doc1, entry1)
            doc.text = entry2

        data_dict = {}
        read_xml.get_level_1_xml(doc1, key, search_keys, data_dict)

        assert data_dict == {'TestRun_x': '1.00', 'TestRun_y': '2.00', 'TestRun_z': '3.00'}

    def test_key_exists_multiple_search_key_partially_tag_prefix_multiple_tree_no_key_tag_prefix_should_return_filled_dict(self):
        key =  '{http://schemas.microsoft.com/2003/10/Serialization/Arrays}TestRun'
        tree_keys = []
        tree_keys.append('{http://schemas.microsoft.com/2003/10/Serialization/Arrays}x')
        tree_keys.append('y')
        tree_keys.append('{http://schemas.microsoft.com/2003/10/Serialization/Arrays}z')
        search_keys = []
        search_keys.append('{http://schemas.microsoft.com/2003/10/Serialization/Arrays}x')
        search_keys.append('y')
        search_keys.append('z')
        sub_keys_values = []
        sub_keys_values.append('1.00')
        sub_keys_values.append('2.00')
        sub_keys_values.append('3.00')
        root = et.Element('root')
        doc1 = et.SubElement(root, key)
        for entry1, entry2 in zip(tree_keys, sub_keys_values):
            doc = et.SubElement(doc1, entry1)
            doc.text = entry2

        data_dict = {}
        read_xml.get_level_1_xml(doc1, key, search_keys, data_dict)

        assert data_dict == {'TestRun_x': '1.00', 'TestRun_y': '2.00', 'TestRun_z': '3.00'}

    def test_key_exists_less_search_no_key_tag_prefix_multiple_tree_no_key_tag_prefix_should_return_filled_dict(self):
        key =  '{http://schemas.microsoft.com/2003/10/Serialization/Arrays}TestRun'
        tree_keys = []
        tree_keys.append('x')
        tree_keys.append('y')
        tree_keys.append('z')
        search_keys = []
        search_keys.append('x')
        sub_keys_values = []
        sub_keys_values.append('1.00')
        sub_keys_values.append('2.00')
        sub_keys_values.append('3.00')
        root = et.Element('root')
        doc1 = et.SubElement(root, key)
        for entry1, entry2 in zip(tree_keys, sub_keys_values):
            doc = et.SubElement(doc1, entry1)
            doc.text = entry2

        data_dict = {}
        read_xml.get_level_1_xml(doc1, key, search_keys, data_dict)

        assert data_dict == {'TestRun_x': '1.00'}

    def test_key_exists_multiple_search_no_key_tag_prefix_less_tree_no_key_tag_prefix_should_return_filled_dict(self):
        key =  '{http://schemas.microsoft.com/2003/10/Serialization/Arrays}TestRun'
        tree_keys = []
        tree_keys.append('x')
        search_keys = []
        search_keys.append('x')
        search_keys.append('y')
        search_keys.append('z')
        sub_keys_values = []
        sub_keys_values.append('1.00')
        sub_keys_values.append('2.00')
        sub_keys_values.append('3.00')
        root = et.Element('root')
        doc1 = et.SubElement(root, key)
        for entry1, entry2 in zip(tree_keys, sub_keys_values):
            doc = et.SubElement(doc1, entry1)
            doc.text = entry2

        data_dict = {}
        read_xml.get_level_1_xml(doc1, key, search_keys, data_dict)

        assert data_dict == {'TestRun_x': '1.00'}

    def test_key_exists_wrong_search_no_key_tag_prefix_multiple_tree_no_key_tag_prefix_should_return_empty_dict(self):
        key =  '{http://schemas.microsoft.com/2003/10/Serialization/Arrays}TestRun'
        tree_keys = []
        tree_keys.append('x')
        tree_keys.append('y')
        tree_keys.append('z')
        search_keys = []
        search_keys.append('k')
        sub_keys_values = []
        sub_keys_values.append('1.00')
        sub_keys_values.append('2.00')
        sub_keys_values.append('3.00')
        root = et.Element('root')
        doc1 = et.SubElement(root, key)
        for entry1, entry2 in zip(tree_keys, sub_keys_values):
            doc = et.SubElement(doc1, entry1)
            doc.text = entry2

        data_dict = {}
        read_xml.get_level_1_xml(doc1, key, search_keys, data_dict)

        assert data_dict == {}

    def test_key_not_exists_should_return_empty_dict(self):
        key =  '{http://schemas.microsoft.com/2003/10/Serialization/Arrays}TestRun'
        tree_keys = []
        tree_keys.append('x')
        tree_keys.append('y')
        tree_keys.append('z')
        search_keys = []
        search_keys.append('k')
        sub_keys_values = []
        sub_keys_values.append('1.00')
        sub_keys_values.append('2.00')
        sub_keys_values.append('3.00')
        root = et.Element('root')
        doc1 = et.SubElement(root, key)
        for entry1, entry2 in zip(tree_keys, sub_keys_values):
            doc = et.SubElement(doc1, entry1)
            doc.text = entry2

        data_dict = {}
        read_xml.get_level_1_xml(doc1, 'does not exists', search_keys, data_dict)

        assert data_dict == {}


class TestGetLevel3Xml():

    def test_key_exists_single_search_key_tag_prefix_single_tree_key_tag_prefix_should_return_filled_dict(self):
        key =  '{http://schemas.microsoft.com/2003/10/Serialization/Arrays}TestRun'
        tree_keys = ['{http://schemas.microsoft.com/2003/10/Serialization/Arrays}x']
        search_keys = ['{http://schemas.microsoft.com/2003/10/Serialization/Arrays}x']
        sub_keys_values = ['1.00']
        root = et.Element('root')
        doc1 = et.SubElement(root, key)
        doc2 = et.SubElement(doc1, 'test1')
        doc3 = et.SubElement(doc2, 'test2')
        for entry1, entry2 in zip(tree_keys, sub_keys_values):
            doc = et.SubElement(doc3, entry1)
            doc.text = entry2

        data_dict = {}
        read_xml.get_level_3_xml(doc1, key, search_keys, data_dict)

        assert data_dict == {'test1_test2': '1.00'}

    def test_key_exists_single_search_key_no_tag_prefix_single_tree_key_tag_prefix_should_return_filled_dict(self):
        key =  '{http://schemas.microsoft.com/2003/10/Serialization/Arrays}TestRun'
        tree_keys = ['{http://schemas.microsoft.com/2003/10/Serialization/Arrays}x']
        search_keys = ['x']
        sub_keys_values = ['1.00']
        root = et.Element('root')
        doc1 = et.SubElement(root, key)
        doc2 = et.SubElement(doc1, 'test1')
        doc3 = et.SubElement(doc2, 'test2')
        for entry1, entry2 in zip(tree_keys, sub_keys_values):
            doc = et.SubElement(doc3, entry1)
            doc.text = entry2

        data_dict = {}
        read_xml.get_level_3_xml(doc1, key, search_keys, data_dict)

        assert data_dict == {'test1_test2': '1.00'}

    def test_key_exists_single_search_key_tag_prefix_single_tree_key_no_tag_prefix_should_return_filled_dict(self):
        key =  '{http://schemas.microsoft.com/2003/10/Serialization/Arrays}TestRun'
        tree_keys = ['x']
        search_keys = ['{http://schemas.microsoft.com/2003/10/Serialization/Arrays}x']
        sub_keys_values = ['1.00']
        root = et.Element('root')
        doc1 = et.SubElement(root, key)
        doc2 = et.SubElement(doc1, 'test1')
        doc3 = et.SubElement(doc2, 'test2')
        for entry1, entry2 in zip(tree_keys, sub_keys_values):
            doc = et.SubElement(doc3, entry1)
            doc.text = entry2

        data_dict = {}
        read_xml.get_level_3_xml(doc1, key, search_keys, data_dict)

        assert data_dict == {'test1_test2': '1.00'}

    def test_key_exists_single_search_key_no_tag_prefix_single_tree_key_no_tag_prefix_should_return_filled_dict(self):
        key =  '{http://schemas.microsoft.com/2003/10/Serialization/Arrays}TestRun'
        tree_keys = ['x']
        search_keys = ['x']
        sub_keys_values = ['1.00']
        root = et.Element('root')
        doc1 = et.SubElement(root, key)
        doc2 = et.SubElement(doc1, 'test1')
        doc3 = et.SubElement(doc2, 'test2')
        for entry1, entry2 in zip(tree_keys, sub_keys_values):
            doc = et.SubElement(doc3, entry1)
            doc.text = entry2

        data_dict = {}
        read_xml.get_level_3_xml(doc1, key, search_keys, data_dict)

        assert data_dict == {'test1_test2': '1.00'}

    def test_key_not_exists_should_return_empty_dict(self):
        key =  '{http://schemas.microsoft.com/2003/10/Serialization/Arrays}TestRun'
        tree_keys = []
        tree_keys.append('x')
        tree_keys.append('y')
        tree_keys.append('z')
        search_keys = []
        search_keys.append('k')
        sub_keys_values = []
        sub_keys_values.append('1.00')
        sub_keys_values.append('2.00')
        sub_keys_values.append('3.00')
        root = et.Element('root')
        doc1 = et.SubElement(root, key)
        doc2 = et.SubElement(doc1, 'test1')
        doc3 = et.SubElement(doc2, 'test2')
        for entry1, entry2 in zip(tree_keys, sub_keys_values):
            doc = et.SubElement(doc3, entry1)
            doc.text = entry2

        data_dict = {}
        read_xml.get_level_3_xml(doc1, 'not known', search_keys, data_dict)

        assert data_dict == {}

    def test_nesting_1_should_return_empty_dict(self):
        key =  '{http://schemas.microsoft.com/2003/10/Serialization/Arrays}TestRun'
        tree_keys = []
        tree_keys.append('x')
        tree_keys.append('y')
        tree_keys.append('z')
        search_keys = []
        search_keys.append('k')
        sub_keys_values = []
        sub_keys_values.append('1.00')
        sub_keys_values.append('2.00')
        sub_keys_values.append('3.00')
        root = et.Element('root')
        doc1 = et.SubElement(root, key)
        doc2 = et.SubElement(doc1, 'test1')

        data_dict = {}
        read_xml.get_level_3_xml(doc1, key, search_keys, data_dict)

        assert data_dict == {}

    def test_nesting_2_should_return_empty_dict(self):
        key =  '{http://schemas.microsoft.com/2003/10/Serialization/Arrays}TestRun'
        tree_keys = []
        tree_keys.append('x')
        tree_keys.append('y')
        tree_keys.append('z')
        search_keys = []
        search_keys.append('k')
        sub_keys_values = []
        sub_keys_values.append('1.00')
        sub_keys_values.append('2.00')
        sub_keys_values.append('3.00')
        root = et.Element('root')
        doc1 = et.SubElement(root, key)
        doc2 = et.SubElement(doc1, 'test1')
        doc3 = et.SubElement(doc2, 'test2')

        data_dict = {}
        read_xml.get_level_3_xml(doc1, key, search_keys, data_dict)

        assert data_dict == {}

    def test_nesting_3_wrong_key_should_return_empty_dict(self):
        key =  '{http://schemas.microsoft.com/2003/10/Serialization/Arrays}TestRun'
        tree_keys = []
        tree_keys.append('x')
        tree_keys.append('y')
        tree_keys.append('z')
        search_keys = []
        search_keys.append('k')
        sub_keys_values = []
        sub_keys_values.append('1.00')
        sub_keys_values.append('2.00')
        sub_keys_values.append('3.00')
        root = et.Element('root')
        doc1 = et.SubElement(root, key)
        doc2 = et.SubElement(doc1, 'test1')
        doc3 = et.SubElement(doc2, 'test2')
        for entry1, entry2 in zip(tree_keys, sub_keys_values):
            doc = et.SubElement(doc3, entry1)
            doc.text = entry2

        data_dict = {}
        read_xml.get_level_3_xml(doc1, key, search_keys, data_dict)

        assert data_dict == {}

    def test_nesting_4_wrong_key_should_return_empty_dict(self):
        key =  '{http://schemas.microsoft.com/2003/10/Serialization/Arrays}TestRun'
        tree_keys = []
        tree_keys.append('x')
        tree_keys.append('y')
        tree_keys.append('z')
        search_keys = []
        search_keys.append('k')
        sub_keys_values = []
        sub_keys_values.append('1.00')
        sub_keys_values.append('2.00')
        sub_keys_values.append('3.00')
        root = et.Element('root')
        doc1 = et.SubElement(root, key)
        doc2 = et.SubElement(doc1, 'test1')
        doc3 = et.SubElement(doc2, 'test2')
        doc4 = et.SubElement(doc3, 'test3')
        doc5 = et.SubElement(doc4, 'test4')

        data_dict = {}
        read_xml.get_level_3_xml(doc1, key, search_keys, data_dict)

        assert data_dict == {}


class TestAddToDict():

    def test_new_key_should_return_filled_dict(self):
        data_dict = {}
        key = 'a'
        value = 'b'
        read_xml.add_to_dict(data_dict, key, value)
        assert data_dict == {'a': 'b'}

    def test_double_key_should_attributeerror(self):
        data_dict = {'a': 'c'}
        key = 'a'
        value = 'b'
        with pytest.raises(AttributeError):
            read_xml.add_to_dict(data_dict, key, value)

class TestGetKeyWithouPrefix():

    def test_key_with_prefix_should_return_key_without_prefix(self):
        key = '{prefix}test'
        assert read_xml.get_key_without_prefix(key) == 'test'

    def test_key_without_prefix_should_return_key_without_prefix(self):
        key = 'test'
        assert read_xml.get_key_without_prefix(key) == 'test'

    def test_key_with_leading_trailing_whitespaces_should_return_key_without_leading_trailing_whitespaces(self):
        key = '  test  '
        assert read_xml.get_key_without_prefix(key) == 'test'

    def test_key_with_leading_trailing_underscore_should_return_key_without_leading_trailing_underscore(self):
        key = '__test__'
        assert read_xml.get_key_without_prefix(key) == 'test'

    def test_key_with_mixed_leading_trailing_underscore_should_return_key_without_leading_trailing_underscore(self):
        key = ' __test__ '
        assert read_xml.get_key_without_prefix(key) == 'test'


class TestRecursiveNode():

    @pytest.fixture(scope='class')
    def level_func_dict(self):
        return {
            'key_value': read_xml.get_all_key_value,
            'level 0': read_xml.get_level_0_xml,
            'level 1': read_xml.get_level_1_xml,
            'level 3': read_xml.get_level_3_xml,
            }

    @pytest.fixture(scope='class')
    def root(self):
        root = et.Element('root')

        sub_level_key = et.SubElement(root, '{http://schemas.microsoft.com/2003/10/Serialization/Arrays}Key')
        sub_level_key.text = 'key'
        sub_level_value = et.SubElement(root, '{http://schemas.microsoft.com/2003/10/Serialization/Arrays}Value')
        sub_level_value.text = 'value'

        sub_level_3_0 = et.SubElement(root, 'sub_level_3_0')
        sub_level_3_0.text = 'sub_level_3_0'

        sub_level_3_1 = et.SubElement(sub_level_3_0, 'sub_level_3_1')
        sub_level_3_1.text = 'sub_level_3_1'

        sub_level_3_2 = et.SubElement(sub_level_3_1, 'sub_level_3_2')
        sub_level_3_2.text = 'sub_level_3_2'

        sub_level_3_3 = et.SubElement(sub_level_3_2, 'sub_level_3_3')
        sub_level_3_3.text = 'sub_level_3_3'

        sub_level_0 = et.SubElement(root, 'sub_level_0')
        sub_level_0.text = 'sub_level_0'

        sub_level_1_0 = et.SubElement(root, 'sub_level_1_0')
        sub_level_1_0.text = 'sub_level_1_0'

        sub_level_1_1 = et.SubElement(sub_level_1_0, 'sub_level_1_1')
        sub_level_1_1.text = 'sub_level_1_1'

        return root

    def test_nested_node_key_value_should_return_filled_dict(self, level_func_dict, root):
        level_dict = {
            'key_value': {
                '{http://schemas.microsoft.com/2003/10/Serialization/Arrays}Key': \
                    '{http://schemas.microsoft.com/2003/10/Serialization/Arrays}Value'
                }
            }
        data_dict = {}

        read_xml.recursive_node(root, data_dict, level_dict, level_func_dict)

        assert data_dict == {'key': 'value'}

    def test_nested_node_level_0_should_return_filled_dict(self, level_func_dict, root):
        level_dict = {'level 0': {'sub_level_0': []}}
        data_dict = {}

        read_xml.recursive_node(root, data_dict, level_dict, level_func_dict)

        assert data_dict == {'sub_level_0': 'sub_level_0'}

    def test_nested_node_level_1_should_return_filled_dict(self, level_func_dict, root):
        level_dict = {'level 1': {'sub_level_1_0': ['sub_level_1_1']}}
        data_dict = {}

        read_xml.recursive_node(root, data_dict, level_dict, level_func_dict)

        assert data_dict == {'sub_level_1_0_sub_level_1_1': 'sub_level_1_1'}

    def test_nested_node_level_3_should_return_filled_dict(self, level_func_dict, root):
        level_dict = {'level 3': {'sub_level_3_0': ['sub_level_3_3']}}
        data_dict = {}

        read_xml.recursive_node(root, data_dict, level_dict, level_func_dict)

        assert data_dict == {'sub_level_3_1_sub_level_3_2': 'sub_level_3_3'}
