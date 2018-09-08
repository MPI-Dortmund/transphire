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

level_dict = {
    'level 0': {
        '{http://schemas.datacontract.org/2004/07/Fei.SharedObjects}AccelerationVoltage': [],
        '{http://schemas.datacontract.org/2004/07/Fei.SharedObjects}ExposureTime': [],
        '{http://schemas.datacontract.org/2004/07/Fei.SharedObjects}PreExposureTime': [],
        '{http://schemas.datacontract.org/2004/07/Fei.SharedObjects}PreExposurePauseTime': [],
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


def get_key_without_prefix(key):
    xml_key_pattern = re.compile(r'.*{.*}(.*)')
    try:
        return_key = xml_key_pattern.match(key).group(1)
    except AttributeError:
        return_key = key
    return return_key.strip().strip('_')


def get_all_key_value(node, data_dict):
    findall_name_key = '{http://schemas.microsoft.com/2003/10/Serialization/Arrays}Key'
    findall_name_value = '{http://schemas.microsoft.com/2003/10/Serialization/Arrays}Value'

    findall_key = node.findall(findall_name_key)
    if findall_key:
        findall_value = node.findall(findall_name_value)
        assert len(findall_key) == len(findall_value)
        for key, value in zip(findall_key, findall_value):
            assert key.text.strip() not in data_dict, f'{key.text.strip()} already in data_dict!'
            if value.text:
                data_dict[key.text.strip()] = value.text.strip()
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
                        data_dict['FramesPerFraction'] = str(int(end) - int(start) + 1)
                        data_dict['NumberOffractions'] = str(len(child))
                    elif child.tag == '{http://schemas.datacontract.org/2004/07/Fei.Applications.Common.Omp.Interface}NumberOffractions':
                        data_dict['NumberOffractions'] = child.text
                        data_dict['FramesPerFraction'] = '1'
    else:
        pass


def get_level_0_xml(node, key, search_keys, data_dict):
    if key == node.tag:
        dict_key = get_key_without_prefix(node.tag)
        if node.text:
            data_dict[dict_key] = node.text.strip()
    else:
        pass


def get_level_1_xml(node, key, search_keys, data_dict):
    if key == node.tag:
        key_1 = get_key_without_prefix(node.tag)
        for child in node:
            key_2 = get_key_without_prefix(child.tag)
            key = '_'.join([key_1, key_2])
            for key_check in search_keys:
                if key_check in child.tag:
                    data_dict[key] = child.text.strip()
    else:
        pass


def get_level_3_xml(node, key, search_keys, data_dict):
    if key == node.tag:
        for child in node:
            key_1 = get_key_without_prefix(child.tag)
            for grand_child in child:
                key_2 = get_key_without_prefix(grand_child.tag)
                key = '_'.join([key_1, key_2])
                for grand_grand_child in grand_child:
                    for key_check in search_keys:
                        if key_check in grand_grand_child.tag:
                            data_dict[key] = grand_grand_child.text.strip()
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

    get_all_key_value(node, data_dict)

    for level_key, level_value in level_dict.items():
        for key, value in level_value.items():
            level_func_dict[level_key](
                node=node,
                key=level_key,
                search_keys=value,
                data_dict=data_dict,
                )

    for child in node:
        recursive_node(
            node=child,
            data_dict=data_dict,
            leve_dict=level_dict,
            level_func_dict=level_func_dict
            )


def read_xml(file_name):

    level_func_dict = {
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
        leve_dict=level_dict,
        level_func_dict=level_func_dict
        )

    if 'DoseOnCamera' not in data_dict:
        data_dict['DoseOnCamera'] = float(data_dict['Dose']) * float(data_dict['pixelSize_x'])**2

    return data_dict
