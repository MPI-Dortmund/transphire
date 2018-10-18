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

import hyperspy.api as hs
import numpy as np
import pandas as pd
import pytest

from .... import utils
from .. import epu

THIS_DIR = os.path.dirname(os.path.realpath(__file__))
INPUT_TEST_FOLDER = '../../../../test_files'

class TestGetXmlKeys_18:

    def test_calling_function_returns_dict(self):
        level_dict = {
            'key_value': {
                '{http://schemas.microsoft.com/2003/10/Serialization/Arrays}Key': ['{http://schemas.microsoft.com/2003/10/Serialization/Arrays}Value'],
                },
            'level 0': {
                '{http://schemas.datacontract.org/2004/07/Fei.SharedObjects}AccelerationVoltage': [],
                '{http://schemas.datacontract.org/2004/07/Fei.SharedObjects}PreExposureTime': [],
                '{http://schemas.datacontract.org/2004/07/Fei.SharedObjects}PreExposurePauseTime': [],
                '{http://schemas.datacontract.org/2004/07/Fei.SharedObjects}ApplicationSoftware': [],
                '{http://schemas.datacontract.org/2004/07/Fei.SharedObjects}ApplicationSoftwareVersion': [],
                '{http://schemas.datacontract.org/2004/07/Fei.SharedObjects}ComputerName': [],
                '{http://schemas.datacontract.org/2004/07/Fei.SharedObjects}InstrumentID': [],
                '{http://schemas.datacontract.org/2004/07/Fei.SharedObjects}InstrumentModel': [],
                '{http://schemas.datacontract.org/2004/07/Fei.SharedObjects}Defocus': [],
                '{http://schemas.datacontract.org/2004/07/Fei.SharedObjects}Intensity': [],
                '{http://schemas.datacontract.org/2004/07/Fei.SharedObjects}acquisitionDateTime': [],
                '{http://schemas.datacontract.org/2004/07/Fei.SharedObjects}NominalMagnification': [],
                },
            'level 1': {
                '{http://schemas.datacontract.org/2004/07/Fei.SharedObjects}camera': ['ExposureTime'],
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

        assert epu.get_xml_keys() == level_dict


class TestExtractGridsquareAndSpotid_18:

    def test_file_name_returns_data_frame(self):
        input_file = os.path.join('test1', 'test2', 'test3', 'Images-Disc1', 'GridSquare_123', 'Data', 'FoilHole_28385656_Data_28397105_28397106_20180530_0221_Fractions.mrc')
        assert isinstance(epu.extract_gridsquare_and_spotid__1_8(input_file), pd.DataFrame)

    def test_file_name_returns_correct_gridsquare(self):
        input_file = os.path.join('test1', 'test2', 'test3', 'Images-Disc1', 'GridSquare_123', 'Data', 'FoilHole_28385656_Data_28397105_28397106_20180530_0221_Fractions.mrc')
        assert epu.extract_gridsquare_and_spotid__1_8(input_file)['GridSquare'].iloc[0] == 123

    def test_file_name_returns_correct_hole(self):
        input_file = os.path.join('test1', 'test2', 'test3', 'Images-Disc1', 'GridSquare_123', 'Data', 'FoilHole_28385656_Data_28397105_28397106_20180530_0221_Fractions.mrc')
        assert epu.extract_gridsquare_and_spotid__1_8(input_file)['HoleNumber'].iloc[0] == 28385656

    def test_file_name_returns_correct_spot(self):
        input_file = os.path.join('test1', 'test2', 'test3', 'Images-Disc1', 'GridSquare_123', 'Data', 'FoilHole_28385656_Data_28397105_28397106_20180530_0221_Fractions.mrc')
        assert epu.extract_gridsquare_and_spotid__1_8(input_file)['SpotNumber'].iloc[0] == 2839710528397106

    def test_file_name_returns_correct_date(self):
        input_file = os.path.join('test1', 'test2', 'test3', 'Images-Disc1', 'GridSquare_123', 'Data', 'FoilHole_28385656_Data_28397105_28397106_20180530_0221_Fractions.mrc')
        assert epu.extract_gridsquare_and_spotid__1_8(input_file)['Date'].iloc[0] == 20180530

    def test_file_name_returns_correct_time(self):
        input_file = os.path.join('test1', 'test2', 'test3', 'Images-Disc1', 'GridSquare_123', 'Data', 'FoilHole_28385656_Data_28397105_28397106_20180530_0221_Fractions.mrc')
        assert epu.extract_gridsquare_and_spotid__1_8(input_file)['Time'].iloc[0] == 221

    def test_file_name_returns_no_gridsquare(self):
        input_file = os.path.join('test1', 'test2', 'test3', 'Images-Disc1', 'GridSquare123', 'Data', 'FoilHole_28385656_Data_28397105_28397106_20180530_0221_Fractions.mrc')
        assert 'GridSquare' not in epu.extract_gridsquare_and_spotid__1_8(input_file).columns.names

    def test_file_name_no_grid_returns_correct_hole(self):
        input_file = os.path.join('test1', 'test2', 'test3', 'Images-Disc1', 'GridSquare123', 'Data', 'FoilHole_28385656_Data_28397105_28397106_20180530_0221_Fractions.mrc')
        assert epu.extract_gridsquare_and_spotid__1_8(input_file)['HoleNumber'].iloc[0] == 28385656

    def test_file_name_no_grid_returns_correct_spot(self):
        input_file = os.path.join('test1', 'test2', 'test3', 'Images-Disc1', 'GridSquare123', 'Data', 'FoilHole_28385656_Data_28397105_28397106_20180530_0221_Fractions.mrc')
        assert epu.extract_gridsquare_and_spotid__1_8(input_file)['SpotNumber'].iloc[0] == 2839710528397106

    def test_file_name_no_grid_returns_correct_date(self):
        input_file = os.path.join('test1', 'test2', 'test3', 'Images-Disc1', 'GridSquare123', 'Data', 'FoilHole_28385656_Data_28397105_28397106_20180530_0221_Fractions.mrc')
        assert epu.extract_gridsquare_and_spotid__1_8(input_file)['Date'].iloc[0] == 20180530

    def test_file_name_no_grid_returns_correct_time(self):
        input_file = os.path.join('test1', 'test2', 'test3', 'Images-Disc1', 'GridSquare123', 'Data', 'FoilHole_28385656_Data_28397105_28397106_20180530_0221_Fractions.mrc')
        assert epu.extract_gridsquare_and_spotid__1_8(input_file)['Time'].iloc[0] == 221

    def test_file_name_wrong_returns_empty_data_frame(self):
        input_file = os.path.join('test1', 'test2', 'test3', 'Images-Disc1', 'GridSquare123', 'Data', 'FoilHole28385656_Data_28397105_28397106_20180530_0221_Fractions.mrc')
        assert epu.extract_gridsquare_and_spotid__1_8(input_file).equals(pd.DataFrame({}, index=[0]))


class TestGetMetaData_18:

    def test_empty_frame_return_empty_data_frame(self):
        compare_data = pd.DataFrame({}, index=[0])
        epu.get_meta_data__1_8(compare_data, index=0)
        assert compare_data.equals(pd.DataFrame({}, index=[0]))

    def test_micrograph_name_jpg_raw_row_returns_correct_gridsquare(self):
        input_file = os.path.join('test1', 'test2', 'test3', 'Images-Disc1', 'GridSquare_123', 'Data', 'FoilHole_28385656_Data_28397105_28397106_20180530_0221.jpg')
        input_file_2 = os.path.join('test1', 'test2', 'test3', 'Images-Disc1', 'GridSquare_456', 'Data', 'FoilHole_28385657_Data_28397105_28397106_20180530_0221.jpg')
        compare_data = pd.DataFrame({'MicrographNameJpgRaw': [input_file, input_file_2]})
        epu.get_meta_data__1_8(compare_data, index=1)
        assert compare_data['GridSquare'].iloc[1] == 456

    def test_micrograph_name_jpg_raw_returns_correct_gridsquare(self):
        input_file = os.path.join('test1', 'test2', 'test3', 'Images-Disc1', 'GridSquare_123', 'Data', 'FoilHole_28385656_Data_28397105_28397106_20180530_0221.jpg')
        compare_data = pd.DataFrame({'MicrographNameJpgRaw': input_file}, index=[0])
        epu.get_meta_data__1_8(compare_data, index=0)
        assert compare_data['GridSquare'].iloc[0] == 123

    def test_micrograph_name_movie_raw_returns_correct_hole(self):
        input_file = os.path.join('test1', 'test2', 'test3', 'Images-Disc1', 'GridSquare_123', 'Data', 'FoilHole_28385656_Data_28397105_28397106_20180530_0221_Fractions.mrc')
        compare_data = pd.DataFrame({'MicrographNameMovieRaw': input_file}, index=[0])
        epu.get_meta_data__1_8(compare_data, index=0)
        assert compare_data['HoleNumber'].iloc[0] == 28385656

    def test_micrograph_name_mrc_krios_raw_returns_correct_spot(self):
        input_file = os.path.join('test1', 'test2', 'test3', 'Images-Disc1', 'GridSquare_123', 'Data', 'FoilHole_28385656_Data_28397105_28397106_20180530_0221.mrc')
        compare_data = pd.DataFrame({'MicrographNameMrcKriosRaw': input_file}, index=[0])
        epu.get_meta_data__1_8(compare_data, index=0)
        assert compare_data['SpotNumber'].iloc[0] == 2839710528397106

    def test_micrograph_name_gain_raw_returns_correct_date(self):
        input_file = os.path.join('test1', 'test2', 'test3', 'Images-Disc1', 'GridSquare_123', 'Data', 'FoilHole_28385656_Data_28397105_28397106_20180530_0221_gain_ref.dm4')
        compare_data = pd.DataFrame({'MicrographNameGainRaw': input_file}, index=[0])
        epu.get_meta_data__1_8(compare_data, index=0)
        assert compare_data['Date'].iloc[0] == 20180530

    def test_micrograph_name_frame_xml_raw_returns_correct_time(self):
        input_file = os.path.join('test1', 'test2', 'test3', 'Images-Disc1', 'GridSquare_123', 'Data', 'FoilHole_28385656_Data_28397105_28397106_20180530_0221_Fractions.xml')
        compare_data = pd.DataFrame({'MicrographNameFrameXmlRaw': input_file}, index=[0])
        epu.get_meta_data__1_8(compare_data, index=0)
        assert compare_data['Time'].iloc[0] == 221

    def test_micrograph_name_wrong_returns_empty_data_frame(self):
        input_file = os.path.join('test1', 'test2', 'test3', 'Images-Disc1', 'GridSquare123', 'Data', 'FoilHole28385656_Data_28397105_28397106_20180530_0221_Fractions.mrc')
        compare_data = pd.DataFrame({'MicrographNameFrameXmlRaw': input_file}, index=[0])
        epu.get_meta_data__1_8(compare_data, index=0)
        assert compare_data.equals(pd.DataFrame({'MicrographNameFrameXmlRaw': input_file}, index=[0]))

    def test_xml_file_and_empty_xml_returns_correct_values(self):
        xml_file = os.path.join(THIS_DIR, INPUT_TEST_FOLDER, 'epu_1_8_falcon_mrc', 'FoilHole_983503_Data_984274_984275_20171201_1435.xml')
        return_dict_xml = {
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

        return_dict_data = {
            'HoleNumber': 983503,
            'SpotNumber': 984274984275,
            'Date': 20171201,
            'Time': 1435,
            }

        order = list(return_dict_xml.keys()) + list(return_dict_data.keys())
        return_frame_xml = pd.DataFrame(return_dict_xml, index=[0])
        return_frame_data = pd.DataFrame(return_dict_data, index=[0])
        return_frame = pd.concat([return_frame_xml, return_frame_data], axis=1)

        compare_data = pd.DataFrame({'MicrographNameXmlRaw': xml_file}, index=[0])
        epu.get_meta_data__1_8(compare_data, index=0)
        assert compare_data[order].equals(return_frame[order])


class TestGetMovie_18falcon:

    def test_search_file_mrc_index_1_should_return_9_frames(self):
        mrc_file = os.path.join(THIS_DIR, INPUT_TEST_FOLDER, 'epu_1_8_falcon_mrc', 'FoilHole_983503_Data_984274_984275_20171201_1435_Fractions.mrc')
        compare_name = os.path.join(THIS_DIR, INPUT_TEST_FOLDER, 'epu_1_8_falcon_mrc', 'FoilHole_983503_Data_984274_984275')
        compare_name = pd.DataFrame({'compare_name': compare_name}, index=[0, 1])
        epu.get_movie__1_8_falcon(compare_name, index=1)
        assert compare_name['FoundNumberOfFractions'].iloc[1] == 9

    def test_search_file_mrc_index_1_should_return_file_path(self):
        mrc_file = os.path.join(THIS_DIR, INPUT_TEST_FOLDER, 'epu_1_8_falcon_mrc', 'FoilHole_983503_Data_984274_984275_20171201_1435_Fractions.mrc')
        compare_name = os.path.join(THIS_DIR, INPUT_TEST_FOLDER, 'epu_1_8_falcon_mrc', 'FoilHole_983503_Data_984274_984275')
        compare_name = pd.DataFrame({'compare_name': compare_name}, index=[0, 1])
        epu.get_movie__1_8_falcon(compare_name, index=1)
        assert compare_name['MicrographMovieNameRaw'].iloc[1] == mrc_file

    def test_search_file_mrc_should_return_file_path(self):
        mrc_file = os.path.join(THIS_DIR, INPUT_TEST_FOLDER, 'epu_1_8_falcon_mrc', 'FoilHole_983503_Data_984274_984275_20171201_1435_Fractions.mrc')
        compare_name = os.path.join(THIS_DIR, INPUT_TEST_FOLDER, 'epu_1_8_falcon_mrc', 'FoilHole_983503_Data_984274_984275')
        compare_name = pd.DataFrame({'compare_name': compare_name}, index=[0])
        epu.get_movie__1_8_falcon(compare_name, index=0)
        assert compare_name['MicrographMovieNameRaw'].iloc[0] == mrc_file

    def test_search_file_mrc_multi_should_return_file_path(self):
        mrc_file = os.path.join(THIS_DIR, INPUT_TEST_FOLDER, 'epu_1_8_falcon_mrc_multi', 'FoilHole_983503_Data_984274_984275_20171201_1435_Fractions.mrc')
        mrc_file_2 = os.path.join(THIS_DIR, INPUT_TEST_FOLDER, 'epu_1_8_falcon_mrc_multi', 'FoilHole_983504_Data_984274_984275_20171201_1435_Fractions.mrc')
        compare_name = os.path.join(THIS_DIR, INPUT_TEST_FOLDER, 'epu_1_8_falcon_mrc_multi', 'FoilHole_983503_Data_984274_984275')
        compare_name_2 = os.path.join(THIS_DIR, INPUT_TEST_FOLDER, 'epu_1_8_falcon_mrc_multi', 'FoilHole_983504_Data_984274_984275')
        compare_name = pd.DataFrame({'compare_name': [compare_name, compare_name_2]})
        epu.get_movie__1_8_falcon(compare_name, index=1)
        assert compare_name['MicrographMovieNameRaw'].iloc[1] == mrc_file_2

    def test_search_file_tif_should_return_file_path(self):
        tif_file = os.path.join(THIS_DIR, INPUT_TEST_FOLDER, 'epu_1_8_falcon_tif', 'FoilHole_983503_Data_984274_984275_20171201_1435_Fractions.tif')
        compare_name = os.path.join(THIS_DIR, INPUT_TEST_FOLDER, 'epu_1_8_falcon_tif', 'FoilHole_983503_Data_984274_984275')
        compare_name = pd.DataFrame({'compare_name': compare_name}, index=[0])
        epu.get_movie__1_8_falcon(compare_name, index=0)
        assert compare_name['MicrographMovieNameRaw'].iloc[0] == tif_file

    def test_search_file_tiff_should_return_file_path(self):
        tiff_file = os.path.join(THIS_DIR, INPUT_TEST_FOLDER, 'epu_1_8_falcon_tiff', 'FoilHole_983503_Data_984274_984275_20171201_1435_Fractions.tiff')
        compare_name = os.path.join(THIS_DIR, INPUT_TEST_FOLDER, 'epu_1_8_falcon_tiff', 'FoilHole_983503_Data_984274_984275')
        compare_name = pd.DataFrame({'compare_name': compare_name}, index=[0])
        epu.get_movie__1_8_falcon(compare_name, index=0)
        assert compare_name['MicrographMovieNameRaw'].iloc[0] == tiff_file

    def test_search_file_tiff_mutli_should_raise_AssertionError(self):
        compare_name = os.path.join(THIS_DIR, INPUT_TEST_FOLDER, 'epu_1_8_falcon_tiff_multi', 'FoilHole_983503_Data_984274_984275')
        compare_name = pd.DataFrame({'compare_name': compare_name}, index=[0])
        with pytest.raises(AssertionError):
            epu.get_movie__1_8_falcon(compare_name, index=0)


class TestGetNumberOfFrames_18falcon:

    def test_read_mrc_header_returns_9(self):
        mrc_file = os.path.join(THIS_DIR, INPUT_TEST_FOLDER, 'epu_1_8_falcon_mrc', 'FoilHole_983503_Data_984274_984275_20171201_1435_Fractions.mrc')
        data_frame = pd.DataFrame({'MicrographMovieNameRaw': mrc_file}, index=[0])
        epu.get_number_of_frames__1_8_falcon(data_frame, index=0)
        assert data_frame['FoundNumberOfFractions'].iloc[0] == 9

    def test_read_tif_header_returns_9(self):
        mrc_file = os.path.join(THIS_DIR, INPUT_TEST_FOLDER, 'epu_1_8_falcon_tif', 'FoilHole_983503_Data_984274_984275_20171201_1435_Fractions.tif')
        data_frame = pd.DataFrame({'MicrographMovieNameRaw': mrc_file}, index=[0])
        epu.get_number_of_frames__1_8_falcon(data_frame, index=0)
        assert data_frame['FoundNumberOfFractions'].iloc[0] == 9

    def test_read_tiff_header_returns_9(self):
        mrc_file = os.path.join(THIS_DIR, INPUT_TEST_FOLDER, 'epu_1_8_falcon_tiff', 'FoilHole_983503_Data_984274_984275_20171201_1435_Fractions.tiff')
        data_frame = pd.DataFrame({'MicrographMovieNameRaw': mrc_file}, index=[0])
        epu.get_number_of_frames__1_8_falcon(data_frame, index=0)
        assert data_frame['FoundNumberOfFractions'].iloc[0] == 9

    def test_read_tiff_header_index_1_should_return_9(self):
        mrc_file = os.path.join(THIS_DIR, INPUT_TEST_FOLDER, 'epu_1_8_falcon_tiff', 'FoilHole_983503_Data_984274_984275_20171201_1435_Fractions.tiff')
        data_frame = pd.DataFrame({'MicrographMovieNameRaw': mrc_file}, index=[0, 1])
        epu.get_number_of_frames__1_8_falcon(data_frame, index=1)
        assert data_frame['FoundNumberOfFractions'].iloc[1] == 9


class TestGetCopyCommand_18:

    def test_function_returns_copy_command(self):
        assert epu.get_copy_command__1_8() == utils.copy


class TestGetMovie_18k2:

    def test_search_file_multi_1_mrc_should_return_file_path(self, tmpdir):
        output_file = tmpdir.join('test_search_file_mrc_should_return_file_path_1')
        output_file_2 = tmpdir.join('test_search_file_mrc_should_return_file_path_2')
        compare_name_data = os.path.join(THIS_DIR, INPUT_TEST_FOLDER, 'epu_1_8_k2_multi', 'FoilHole_983503_Data_984274_984275')
        compare_name_data_2 = os.path.join(THIS_DIR, INPUT_TEST_FOLDER, 'epu_1_8_k2_multi', 'FoilHole_983504_Data_984274_984275')
        compare_name = pd.DataFrame({'compare_name': [compare_name_data, compare_name_data_2], 'OutputStackFolder': [output_file, output_file_2]})
        epu.get_movie__1_8_k2(compare_name, index=1)
        assert compare_name['MicrographMovieNameRaw'].iloc[1] == f'{output_file_2}_Fractions.mrc'

    def test_search_file_multi_0_mrc_should_return_file_path(self, tmpdir):
        output_file = tmpdir.join('test_search_file_mrc_should_return_file_path_1')
        output_file_2 = tmpdir.join('test_search_file_mrc_should_return_file_path_2')
        compare_name_data = os.path.join(THIS_DIR, INPUT_TEST_FOLDER, 'epu_1_8_k2', 'FoilHole_983503_Data_984274_984275')
        compare_name_data_2 = os.path.join(THIS_DIR, INPUT_TEST_FOLDER, 'epu_1_8_k2', 'FoilHole_983504_Data_984274_984275')
        compare_name = pd.DataFrame({'compare_name': [compare_name_data, compare_name_data_2], 'OutputStackFolder': [output_file, output_file_2]})
        epu.get_movie__1_8_k2(compare_name, index=0)
        assert compare_name['MicrographMovieNameRaw'].iloc[0] == f'{output_file}_Fractions.mrc'

    def test_search_file_mrc_should_return_file_path(self, tmpdir):
        output_file = tmpdir.join('test_search_file_mrc_should_return_file_path')
        compare_name_data = os.path.join(THIS_DIR, INPUT_TEST_FOLDER, 'epu_1_8_k2', 'FoilHole_983503_Data_984274_984275')
        compare_name = pd.DataFrame({'compare_name': compare_name_data, 'OutputStackFolder': output_file}, index=[0])
        epu.get_movie__1_8_k2(compare_name, index=0)
        assert compare_name['MicrographMovieNameRaw'].iloc[0] == f'{output_file}_Fractions.mrc'


    def test_output_file_should_have_9_entries(self, tmpdir):
        output_file = tmpdir.join('test_output_file_should_have_9_entries')
        compare_name_data = os.path.join(THIS_DIR, INPUT_TEST_FOLDER, 'epu_1_8_k2', 'FoilHole_983503_Data_984274_984275')
        compare_name = pd.DataFrame({'compare_name': compare_name_data, 'OutputStackFolder': output_file}, index=[0])
        epu.get_movie__1_8_k2(compare_name, index=0)
        assert hs.load(f'{output_file}_Fractions.mrc').axes_manager[0].size == 9


    def test_first_data_entry_is_same_as_first_original_data(self, tmpdir):
        output_file = tmpdir.join('test_first_data_entry_is_same_as_first_original_data')
        compare_name_data = os.path.join(THIS_DIR, INPUT_TEST_FOLDER, 'epu_1_8_k2', 'FoilHole_983503_Data_984274_984275')
        compare_name = pd.DataFrame({'compare_name': compare_name_data, 'OutputStackFolder': output_file}, index=[0])
        epu.get_movie__1_8_k2(compare_name, index=0)
        assert np.array_equal(hs.load(f'{output_file}_Fractions.mrc').data[0], hs.load(f'{compare_name_data}_20171201_1435-1.mrc').data[0])


    def test_last_data_entry_is_same_as_last_original_data(self, tmpdir):
        output_file = tmpdir.join('test_last_data_entry_is_same_as_first_original_data')
        compare_name_data = os.path.join(THIS_DIR, INPUT_TEST_FOLDER, 'epu_1_8_k2', 'FoilHole_983503_Data_984274_984275')
        compare_name = pd.DataFrame({'compare_name': compare_name_data, 'OutputStackFolder': output_file}, index=[0])
        epu.get_movie__1_8_k2(compare_name, index=0)
        assert np.array_equal(hs.load(f'{output_file}_Fractions.mrc').data[-1], hs.load(f'{compare_name_data}_20171201_1435-9.mrc').data[0])


    def test_first_data_entry_unordered_should_be_same_as_first_original_data(self, tmpdir):
        output_file = tmpdir.join('test_first_data_entry_unordered_should_be_same_as_first_original_data')
        compare_name_data = os.path.join(THIS_DIR, INPUT_TEST_FOLDER, 'epu_1_8_k2_unordered', 'FoilHole_983503_Data_984274_984275')
        compare_name = pd.DataFrame({'compare_name': compare_name_data, 'OutputStackFolder': output_file}, index=[0])
        epu.get_movie__1_8_k2(compare_name, index=0)
        assert np.array_equal(hs.load(f'{output_file}_Fractions.mrc').data[0], hs.load(f'{compare_name_data}_20171201_1435-2.mrc').data[0])


    def test_last_data_entry_should_be_same_as_last_original_data(self, tmpdir):
        output_file = tmpdir.join('test_last_data_entry_is_same_as_first_original_data')
        compare_name_data = os.path.join(THIS_DIR, INPUT_TEST_FOLDER, 'epu_1_8_k2_unordered', 'FoilHole_983503_Data_984274_984275')
        compare_name = pd.DataFrame({'compare_name': compare_name_data, 'OutputStackFolder': output_file}, index=[0])
        epu.get_movie__1_8_k2(compare_name, index=0)
        assert np.array_equal(hs.load(f'{output_file}_Fractions.mrc').data[-1], hs.load(f'{compare_name_data}_20171201_1435-10.mrc').data[0])

    def test_last_data_entry_should_be_same_as_last_original_data_index_1(self, tmpdir):
        output_file = tmpdir.join('test_last_data_entry_is_same_as_first_original_data')
        compare_name_data = os.path.join(THIS_DIR, INPUT_TEST_FOLDER, 'epu_1_8_k2_unordered', 'FoilHole_983503_Data_984274_984275')
        compare_name = pd.DataFrame({'compare_name': compare_name_data, 'OutputStackFolder': output_file}, index=[0, 1])
        epu.get_movie__1_8_k2(compare_name, index=1)
        assert np.array_equal(hs.load(f'{output_file}_Fractions.mrc').data[-1], hs.load(f'{compare_name_data}_20171201_1435-10.mrc').data[0])


class TestGetNumberOfFrames_18k2:

    def test_correct_number_returns_correct_value(self):
        compare_name = pd.DataFrame({}, index=[0])
        epu.get_number_of_frames__1_8_k2(['a', 'b', 'c'], compare_name, index=0)
        assert compare_name.equals(pd.DataFrame({'FoundNumberOfFractions': 3}, index=[0]))

    def test_correct_number_returns_correct_value_index_1(self):
        compare_name = pd.DataFrame({}, index=[0, 1])
        epu.get_number_of_frames__1_8_k2(['a', 'b', 'c'], compare_name, index=1)
        assert compare_name.equals(pd.DataFrame({'FoundNumberOfFractions': [np.nan_to_num(-np.inf), 3]}, index=[0, 1]).astype(int))


class TestGetMovie_19k2:

    def test_search_file_mrc_index_0_should_return_file_path(self):
        mrc_file = os.path.join(THIS_DIR, INPUT_TEST_FOLDER, 'epu_1_9_k2', 'FoilHole_983503_Data_984274_984275_20171201_1435-0000.mrc')
        mrc_file_2 = os.path.join(THIS_DIR, INPUT_TEST_FOLDER, 'epu_1_9_k2', 'FoilHole_983504_Data_984274_984275_20171201_1435-0000.mrc')
        compare_name = os.path.join(THIS_DIR, INPUT_TEST_FOLDER, 'epu_1_9_k2', 'FoilHole_983503_Data_984274_984275')
        compare_name_2 = os.path.join(THIS_DIR, INPUT_TEST_FOLDER, 'epu_1_9_k2', 'FoilHole_983504_Data_984274_984275')
        compare_data = pd.DataFrame({'compare_name': [compare_name, compare_name_2]})
        epu.get_movie__1_9_k2(compare_data, index=0)
        assert compare_data['MicrographMovieNameRaw'].iloc[0] == mrc_file

    def test_search_file_mrc_index_1_should_return_file_path(self):
        mrc_file = os.path.join(THIS_DIR, INPUT_TEST_FOLDER, 'epu_1_9_k2', 'FoilHole_983503_Data_984274_984275_20171201_1435-0000.mrc')
        mrc_file_2 = os.path.join(THIS_DIR, INPUT_TEST_FOLDER, 'epu_1_9_k2', 'FoilHole_983504_Data_984274_984275_20171201_1435-0000.mrc')
        compare_name = os.path.join(THIS_DIR, INPUT_TEST_FOLDER, 'epu_1_9_k2', 'FoilHole_983503_Data_984274_984275')
        compare_name_2 = os.path.join(THIS_DIR, INPUT_TEST_FOLDER, 'epu_1_9_k2', 'FoilHole_983504_Data_984274_984275')
        compare_data = pd.DataFrame({'compare_name': [compare_name, compare_name_2]})
        epu.get_movie__1_9_k2(compare_data, index=1)
        assert compare_data['MicrographMovieNameRaw'].iloc[1] == mrc_file_2

    def test_search_file_mrc_index_1_should_return_9_frames(self):
        mrc_file = os.path.join(THIS_DIR, INPUT_TEST_FOLDER, 'epu_1_9_k2', 'FoilHole_983503_Data_984274_984275_20171201_1435-0000.mrc')
        mrc_file_2 = os.path.join(THIS_DIR, INPUT_TEST_FOLDER, 'epu_1_9_k2', 'FoilHole_983504_Data_984274_984275_20171201_1435-0000.mrc')
        compare_name = os.path.join(THIS_DIR, INPUT_TEST_FOLDER, 'epu_1_9_k2', 'FoilHole_983503_Data_984274_984275')
        compare_name_2 = os.path.join(THIS_DIR, INPUT_TEST_FOLDER, 'epu_1_9_k2', 'FoilHole_983504_Data_984274_984275')
        compare_data = pd.DataFrame({'compare_name': [compare_name, compare_name_2]})
        epu.get_movie__1_9_k2(compare_data, index=1)
        assert compare_data['FoundNumberOfFractions'].iloc[1] == 9
