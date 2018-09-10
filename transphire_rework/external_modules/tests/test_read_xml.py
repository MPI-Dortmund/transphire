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


import os
import xml.etree.ElementTree as et
import pytest
from .. import read_xml


THIS_DIR = os.path.dirname(os.path.realpath(__file__))


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


class TestReadXML():

    @pytest.fixture(scope='class')
    def level_dict(self):
        level_dict = {
            'key_value': {
                '{http://schemas.microsoft.com/2003/10/Serialization/Arrays}Key': \
                    '{http://schemas.microsoft.com/2003/10/Serialization/Arrays}Value'
                },
            'level 0': {
                '{http://schemas.datacontract.org/2004/07/Fei.SharedObjects}AccelerationVoltage': [],
                '{http://schemas.datacontract.org/2004/07/Fei.SharedObjects}ApplicationSoftware': [],
                '{http://schemas.datacontract.org/2004/07/Fei.SharedObjects}ApplicationSoftwareVersion': [],
                '{http://schemas.datacontract.org/2004/07/Fei.SharedObjects}ComputerName': [],
                '{http://schemas.datacontract.org/2004/07/Fei.SharedObjects}InstrumentID': [],
                '{http://schemas.datacontract.org/2004/07/Fei.SharedObjects}InstrumentModel': [],
                '{http://schemas.datacontract.org/2004/07/Fei.SharedObjects}InstrumentID': [],
                '{http://schemas.datacontract.org/2004/07/Fei.SharedObjects}Defocus': [],
                '{http://schemas.datacontract.org/2004/07/Fei.SharedObjects}Intensity': [],
                '{http://schemas.datacontract.org/2004/07/Fei.SharedObjects}acquisitionDateTime': [],
                '{http://schemas.datacontract.org/2004/07/Fei.SharedObjects}NominalMagnification': [],
                },
            'level 1': {
                '{http://schemas.datacontract.org/2004/07/Fei.SharedObjects}camera': ['ExposureTime', 'PreExposureTime', 'PreExposurePauseTime'],
                '{http://schemas.datacontract.org/2004/07/Fei.SharedObjects}Binning': ['x', 'y'],
                '{http://schemas.datacontract.org/2004/07/Fei.SharedObjects}ReadoutArea': ['height', 'width'],
                '{http://schemas.datacontract.org/2004/07/Fei.SharedObjects}Position': ['A', 'B', 'X', 'Y', 'Z'],
                '{http://schemas.datacontract.org/2004/07/Fei.SharedObjects}ImageShift': ['_x', '_y'],
                '{http://schemas.datacontract.org/2004/07/Fei.SharedObjects}BeamShift': ['_x', '_y'],
                '{http://schemas.datacontract.org/2004/07/Fei.SharedObjects}BeamTilt': ['_x', '_y'],
                },
            'level 3': {
                '{http://schemas.datacontract.org/2004/07/Fei.SharedObjects}SpatialScale': ['numericValue'],
                }
            }
            
        return level_dict

    def test_epu_1_8_falcon_should_return_filled_dict(self, level_dict):
        file_name = os.path.join(THIS_DIR, "xml_epu_1_8_falcon_2.xml")
        data_dict = read_xml.read_xml(file_name, level_dict)

        return_dict = {
            'DoseOnCamera': '2777.1328318769706',
            'Dose': '1.310205842097034E+23',
            'PhasePlateUsed': 'false',
            'AppliedDefocus': '-1.2E-06',
            'CetaFramesSummed': '1',
            'CetaNoiseReductionEnabled': 'true',
            'ElectronCountingEnabled': 'false',
            'AlignIntegratedImageEnabled': 'false',
            'SuperResolutionFactor': '1',
            'NumberOffractions': '30',
            'FramesPerFraction': '1',
            'AccelerationVoltage': '300000',
            'camera_ExposureTime': '1.49538',
            'camera_PreExposureTime': '0',
            'camera_PreExposurePauseTime': '0',
            'ApplicationSoftware': 'Fei EPU',
            'ApplicationSoftwareVersion': '1.0.2.24',
            'ComputerName': 'TITAN52334050',
            'InstrumentModel': 'TITAN52334050',
            'InstrumentID': '3405',
            'Defocus': '-5.3518729175058636E-06',
            'Intensity': '0',
            'acquisitionDateTime': '2018-07-26T10:10:09.2386864+02:00',
            'NominalMagnification': '47000',
            'Binning_x': '1',
            'Binning_y': '1',
            'ReadoutArea_height': '4096',
            'ReadoutArea_width': '4096',
            'Position_A': '-0.00025304174054',
            'Position_B': '0.01758816',
            'Position_X': '0.0004230068863',
            'Position_Y': '0.00038534540800000004',
            'Position_Z': '-0.0002004311951728',
            'ImageShift_x': '0',
            'ImageShift_y': '0',
            'BeamShift_x': '0.00057684897910803556',
            'BeamShift_y': '-0.0053513972088694572',
            'BeamTilt_x': '0.022405700758099556',
            'BeamTilt_y': '-0.052897602319717407',
            'offset_x': '0',
            'offset_y': '0',
            'pixelSize_x': '1.4558899918970525E-10',
            'pixelSize_y': '1.4558899918970525E-10',
            }

        assert data_dict == return_dict

    def test_epu_1_11_falcon_should_return_filled_dict(self, level_dict):
        file_name = os.path.join(THIS_DIR, "xml_epu_1_11_falcon.xml")
        data_dict = read_xml.read_xml(file_name, level_dict)

        return_dict = {
            'DoseOnCamera': '369.58234062113087',
            'Dose': '2.4137967554022204E+22',
            'PhasePlateUsed': 'false',
            'AppliedDefocus': '-1.8E-06',
            'CetaFramesSummed': '1',
            'CetaNoiseReductionEnabled': 'false',
            'ElectronCountingEnabled': 'false',
            'AlignIntegratedImageEnabled': 'false',
            'SuperResolutionFactor': '1',
            'NumberOffractions': '119',
            'FramesPerFraction': '1',
            'AccelerationVoltage': '200000',
            'camera_ExposureTime': '2.99076',
            'camera_PreExposureTime': '0',
            'camera_PreExposurePauseTime': '0',
            'ApplicationSoftware': 'Fei EPU',
            'ApplicationSoftwareVersion': '1.5.1.50',
            'ComputerName': 'TALOS-9950416',
            'InstrumentModel': 'TALOS-9950416',
            'InstrumentID': '9950416',
            'Defocus': '-1.7465633364799447E-06',
            'Intensity': '0.42227506866503856',
            'acquisitionDateTime': '2018-08-27T18:15:57.2721016+02:00',
            'NominalMagnification': '120000',
            'Binning_x': '1',
            'Binning_y': '1',
            'ReadoutArea_height': '4096',
            'ReadoutArea_width': '4096',
            'Position_A': '9.19453108501629E-05',
            'Position_B': '0',
            'Position_X': '7.5287520000000022E-05',
            'Position_Y': '-2.8958801999999861E-05',
            'Position_Z': '4.3042649999999983E-05',
            'ImageShift_x': '0',
            'ImageShift_y': '0',
            'BeamShift_x': '0.014924436807632446',
            'BeamShift_y': '-0.0010031891288235784',
            'BeamTilt_x': '0.027286317199468613',
            'BeamTilt_y': '0.0871329978108406',
            'offset_x': '0',
            'offset_y': '0',
            'pixelSize_x': '1.237386165753307E-10',
            'pixelSize_y': '1.237386165753307E-10',
            'BinaryResult.Detector': 'BM-Falcon',
            }

        assert data_dict == return_dict

    def test_epu_1_11_falcon_vpp_should_return_filled_dict(self, level_dict):
        file_name = os.path.join(THIS_DIR, "xml_epu_1_11_falcon_vpp.xml")
        data_dict = read_xml.read_xml(file_name, level_dict)

        return_dict = {
            'DoseOnCamera': '351.43162212033525',
            'Dose': '2.2952517368501772E+22',
            'PhasePlateUsed': 'true',
            'PhasePlateApertureName': 'Ph P4',
            'PhasePlatePosition': '0',
            'AppliedDefocus': '-1E-06',
            'CetaFramesSummed': '1',
            'CetaNoiseReductionEnabled': 'false',
            'ElectronCountingEnabled': 'false',
            'AlignIntegratedImageEnabled': 'true',
            'SuperResolutionFactor': '1',
            'NumberOffractions': '40',
            'FramesPerFraction': '2',
            'AccelerationVoltage': '200000',
            'camera_ExposureTime': '2.99076',
            'camera_PreExposureTime': '0',
            'camera_PreExposurePauseTime': '0',
            'ApplicationSoftware': 'Fei EPU',
            'ApplicationSoftwareVersion': '1.5.1.50',
            'ComputerName': 'TALOS-9950416',
            'InstrumentModel': 'TALOS-9950416',
            'InstrumentID': '9950416',
            'Defocus': '-8.5866780888078926E-07',
            'Intensity': '0.42228560518710945',
            'acquisitionDateTime': '2018-08-22T14:56:05.9552508+02:00',
            'NominalMagnification': '120000',
            'Binning_x': '1',
            'Binning_y': '1',
            'ReadoutArea_height': '4096',
            'ReadoutArea_width': '4096',
            'Position_A': '6.7753108501629E-06',
            'Position_B': '0',
            'Position_X': '-0.00016132366499999997',
            'Position_Y': '-0.00026939848199999987',
            'Position_Z': '0.00012551765999999998',
            'ImageShift_x': '0',
            'ImageShift_y': '0',
            'BeamShift_x': '0',
            'BeamShift_y': '0',
            'BeamTilt_x': '0.026570061221718788',
            'BeamTilt_y': '0.0847930982708931',
            'offset_x': '0',
            'offset_y': '0',
            'pixelSize_x': '1.237386165753307E-10',
            'pixelSize_y': '1.237386165753307E-10',
            'BinaryResult.Detector': 'BM-Falcon',
            }

        assert data_dict == return_dict

    def test_epu_1_8_k2_should_return_filled_dict(self, level_dict):
        file_name = os.path.join(THIS_DIR, "xml_epu_1_8_k2.xml")
        data_dict = read_xml.read_xml(file_name, level_dict)

        return_dict = {
            'Dose': '4.4034254472809153E+21',
            'PhasePlateUsed': 'false',
            'AppliedDefocus': '-2E-06',
            'CetaFramesSummed': '1',
            'CetaNoiseReductionEnabled': 'false',
            'ElectronCountingEnabled': 'true',
            'AlignIntegratedImageEnabled': 'false',
            'SuperResolutionFactor': '1',
            'NumberOffractions': '40',
            'FramesPerFraction': '1',
            'AccelerationVoltage': '300000',
            'camera_ExposureTime': '10',
            'camera_PreExposureTime': '0',
            'camera_PreExposurePauseTime': '0',
            'ApplicationSoftware': 'Fei EPU',
            'ApplicationSoftwareVersion': '1.0.2.24',
            'ComputerName': 'TITAN52334050',
            'InstrumentModel': 'TITAN52334050',
            'InstrumentID': '3405',
            'Defocus': '-4.1145761222574709E-06',
            'Intensity': '0',
            'acquisitionDateTime': '2018-07-27T15:03:51.422415+02:00',
            'NominalMagnification': '105000',
            'Binning_x': '1',
            'Binning_y': '1',
            'ReadoutArea_height': '3838',
            'ReadoutArea_width': '3710',
            'Position_A': '-0.00049735790382',
            'Position_B': '0.01758816',
            'Position_X': '0.0001011122438',
            'Position_Y': '0.00018212982400000002',
            'Position_Z': '7.69634926848E-05',
            'ImageShift_x': '0',
            'ImageShift_y': '0',
            'BeamShift_x': '0',
            'BeamShift_y': '0',
            'BeamTilt_x': '0.022405700758099556',
            'BeamTilt_y': '-0.052897602319717407',
            'offset_x': '0',
            'offset_y': '0',
            'pixelSize_x': '1.1202724164993683E-10',
            'pixelSize_y': '1.1202724164993683E-10',
            }

        assert data_dict == return_dict

    def test_epu_1_9_k2_should_return_filled_dict(self, level_dict):
        file_name = os.path.join(THIS_DIR, "xml_epu_1_9_k2.xml")
        data_dict = read_xml.read_xml(file_name, level_dict)

        return_dict = {
            'Dose': '5.0949700264944667E+21',
            'PhasePlateUsed': 'true',
            'AppliedDefocus': '-5E-07',
            'CetaFramesSummed': '1',
            'CetaNoiseReductionEnabled': 'false',
            'ElectronCountingEnabled': 'true',
            'AlignIntegratedImageEnabled': 'false',
            'SuperResolutionFactor': '1',
            'NumberOffractions': '50',
            'FramesPerFraction': '1',
            'AccelerationVoltage': '300000',
            'camera_ExposureTime': '15',
            'camera_PreExposureTime': '0',
            'camera_PreExposurePauseTime': '0',
            'ApplicationSoftware': 'Fei EPU',
            'ApplicationSoftwareVersion': '1.2.0.16',
            'ComputerName': 'TITAN52337040',
            'InstrumentModel': 'TITAN52337040',
            'InstrumentID': '3704',
            'Defocus': '-4.8596167414599369E-06',
            'Intensity': '0.41315126103110034',
            'acquisitionDateTime': '2018-09-06T18:53:08.3688571+02:00',
            'NominalMagnification': '130000',
            'Binning_x': '1',
            'Binning_y': '1',
            'ReadoutArea_height': '3838',
            'ReadoutArea_width': '3710',
            'Position_A': '0.00017930847697997243',
            'Position_B': '0.0169176125',
            'Position_X': '3.8876719700000088E-05',
            'Position_Y': '0.00054299326400000022',
            'Position_Z': '-0.00012699411581439991',
            'ImageShift_x': '0',
            'ImageShift_y': '0',
            'BeamShift_x': '-0.011826804839074612',
            'BeamShift_y': '0.0073098903521895409',
            'BeamTilt_x': '-0.034887045621871948',
            'BeamTilt_y': '0.036312207579612732',
            'offset_x': '0',
            'offset_y': '0',
            'pixelSize_x': '1.0732100624855079E-10',
            'pixelSize_y': '1.0732100624855079E-10',
            }

        assert data_dict == return_dict

