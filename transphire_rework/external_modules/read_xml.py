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
import re
import warnings


def get_key_without_prefix(key):
    xml_key_pattern = re.compile(r'.*{.*}(.*)')
    try:
        return_key = xml_key_pattern.match(key).group(1)
    except AttributeError:
        return_key = key
    return return_key.strip().strip('_')


def add_to_dict(data_dict, key, value):
    if key.strip() in data_dict:
        raise AttributeError(f'Key: {key} already exists in data_dict!')
    else:
        data_dict[key.strip()] = value.strip()


def get_all_key_value(node, key, search_keys, data_dict):
    findall_name_key = key
    findall_name_value = search_keys

    findall_key = node.findall(findall_name_key)
    if findall_key:
        findall_value = node.findall(findall_name_value)
        assert len(findall_key) == len(findall_value)
        for key, value in zip(findall_key, findall_value):
            if value.text:
                add_to_dict(data_dict, key.text, value.text)
            else:
                for child in value:
                    if child.tag == '{http://schemas.datacontract.org/2004/07/Fei.Applications.Common.Omp.Interface}DoseFractions':
                        start = None
                        end = None
                        for grand_child in child.iter():
                            if 'StartFrameNumber' in grand_child.tag:
                                start = grand_child.text.strip()
                            if 'EndFrameNumber' in grand_child.tag:
                                end = grand_child.text.strip()
                            if start and end:
                                break
                        frames_per_fraction = str(int(end) - int(start) + 1)
                        number_of_fractions = str(len(child))
                    elif child.tag == '{http://schemas.datacontract.org/2004/07/Fei.Applications.Common.Omp.Interface}NumberOffractions':
                        frames_per_fraction = '1'
                        number_of_fractions = child.text
                    else:
                        warnings.warn(f'Warning: "{child.tag}" not yet known in if-else branches!')
                        continue
                    add_to_dict(data_dict, 'NumberOffractions', number_of_fractions)
                    add_to_dict(data_dict, 'FramesPerFraction', frames_per_fraction)
    else:
        pass


def get_level_0_xml(node, key, search_keys, data_dict):
    if key == node.tag:
        dict_key = get_key_without_prefix(node.tag)
        if node.text:
            add_to_dict(data_dict, dict_key, node.text)
    else:
        pass


def get_level_1_xml(node, key, search_keys, data_dict):
    search_keys_no_prefix = [get_key_without_prefix(search_key) for search_key in search_keys]
    if key == node.tag:
        key_1 = get_key_without_prefix(node.tag)
        for child in node:
            key_2 = get_key_without_prefix(child.tag)
            combined_key = '_'.join([key_1, key_2])
            for key_check in search_keys_no_prefix:
                if key_check == key_2:
                    add_to_dict(data_dict, combined_key, child.text)
    else:
        pass


def get_level_3_xml(node, key, search_keys, data_dict):
    search_keys_no_prefix = [get_key_without_prefix(search_key) for search_key in search_keys]
    if key == node.tag:
        for child in node:
            key_1 = get_key_without_prefix(child.tag)
            for grand_child in child:
                key_2 = get_key_without_prefix(grand_child.tag)
                key = '_'.join([key_1, key_2])
                for grand_grand_child in grand_child:
                    test_tag = get_key_without_prefix(grand_grand_child.tag)
                    for key_check in search_keys_no_prefix:
                        if key_check == test_tag:
                            add_to_dict(data_dict, key, grand_grand_child.text)
    else:
        pass


def recursive_node(node, data_dict, level_dict, level_func_dict):
    """
    Find all xml information recursively.

    Arguments:
    node - Current node to search
    data_dict - Dictionary containing the extracted data

    Returns:
    None - Dictionary will be modified inplace
    """

    for level_key, level_value in level_dict.items():
        for key, value in level_value.items():
            level_func_dict[level_key](
                node=node,
                key=key,
                search_keys=value,
                data_dict=data_dict,
                )

    for child in node:
        recursive_node(
            node=child,
            data_dict=data_dict,
            level_dict=level_dict,
            level_func_dict=level_func_dict
            )


def read_xml(file_name, level_dict):

    level_func_dict = {
        'key_value': get_all_key_value,
        'level 0': get_level_0_xml,
        'level 1': get_level_1_xml,
        'level 3': get_level_3_xml,
        }

    tree = et.parse(file_name)
    root = tree.getroot()
    data_dict = {}
    recursive_node(
        node=root,
        data_dict=data_dict,
        level_dict=level_dict,
        level_func_dict=level_func_dict
        )

    return data_dict
