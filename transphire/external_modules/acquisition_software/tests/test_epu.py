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
        epu.get_meta_data__1_8(compare_data)
        assert compare_data.equals(pd.DataFrame({}, index=[0]))

    def test_micrograph_name_jpg_raw_returns_correct_gridsquare(self):
        input_file = os.path.join('test1', 'test2', 'test3', 'Images-Disc1', 'GridSquare_123', 'Data', 'FoilHole_28385656_Data_28397105_28397106_20180530_0221.jpg')
        compare_data = pd.DataFrame({'MicrographNameJpgRaw': input_file}, index=[0])
        epu.get_meta_data__1_8(compare_data)
        assert compare_data['GridSquare'].iloc[0] == 123

    def test_micrograph_name_movie_raw_returns_correct_hole(self):
        input_file = os.path.join('test1', 'test2', 'test3', 'Images-Disc1', 'GridSquare_123', 'Data', 'FoilHole_28385656_Data_28397105_28397106_20180530_0221_Fractions.mrc')
        compare_data = pd.DataFrame({'MicrographNameMovieRaw': input_file}, index=[0])
        epu.get_meta_data__1_8(compare_data)
        assert compare_data['HoleNumber'].iloc[0] == 28385656

    def test_micrograph_name_mrc_krios_raw_returns_correct_spot(self):
        input_file = os.path.join('test1', 'test2', 'test3', 'Images-Disc1', 'GridSquare_123', 'Data', 'FoilHole_28385656_Data_28397105_28397106_20180530_0221.mrc')
        compare_data = pd.DataFrame({'MicrographNameMrcKriosRaw': input_file}, index=[0])
        epu.get_meta_data__1_8(compare_data)
        assert compare_data['SpotNumber'].iloc[0] == 2839710528397106

    def test_micrograph_name_gain_raw_returns_correct_date(self):
        input_file = os.path.join('test1', 'test2', 'test3', 'Images-Disc1', 'GridSquare_123', 'Data', 'FoilHole_28385656_Data_28397105_28397106_20180530_0221_gain_ref.dm4')
        compare_data = pd.DataFrame({'MicrographNameGainRaw': input_file}, index=[0])
        epu.get_meta_data__1_8(compare_data)
        assert compare_data['Date'].iloc[0] == 20180530

    def test_micrograph_name_frame_xml_raw_returns_correct_time(self):
        input_file = os.path.join('test1', 'test2', 'test3', 'Images-Disc1', 'GridSquare_123', 'Data', 'FoilHole_28385656_Data_28397105_28397106_20180530_0221_Fractions.xml')
        compare_data = pd.DataFrame({'MicrographNameFrameXmlRaw': input_file}, index=[0])
        epu.get_meta_data__1_8(compare_data)
        assert compare_data['Time'].iloc[0] == 221

    def test_micrograph_name_wrong_returns_empty_data_frame(self):
        input_file = os.path.join('test1', 'test2', 'test3', 'Images-Disc1', 'GridSquare123', 'Data', 'FoilHole28385656_Data_28397105_28397106_20180530_0221_Fractions.mrc')
        compare_data = pd.DataFrame({'MicrographNameFrameXmlRaw': input_file}, index=[0])
        epu.get_meta_data__1_8(compare_data)
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
        epu.get_meta_data__1_8(compare_data)
        print(compare_data.iloc[0])
        print(return_frame.iloc[0])
        assert compare_data[order].equals(return_frame[order])


class TestGetMovie_18falcon:

    def test_search_file_mrc_should_return_file_path(self):
        mrc_file = os.path.join(THIS_DIR, INPUT_TEST_FOLDER, 'epu_1_8_falcon_mrc', 'FoilHole_983503_Data_984274_984275_20171201_1435_Fractions.mrc')
        compare_name = os.path.join(THIS_DIR, INPUT_TEST_FOLDER, 'epu_1_8_falcon_mrc', 'FoilHole_983503_Data_984274_984275')
        assert epu.get_movie__1_8_falcon(compare_name).equals(pd.DataFrame({'MicrographMovieNameRaw': mrc_file}, index=[0]))

    def test_search_file_tif_should_return_file_path(self):
        tif_file = os.path.join(THIS_DIR, INPUT_TEST_FOLDER, 'epu_1_8_falcon_tif', 'FoilHole_983503_Data_984274_984275_20171201_1435_Fractions.tif')
        compare_name = os.path.join(THIS_DIR, INPUT_TEST_FOLDER, 'epu_1_8_falcon_tif', 'FoilHole_983503_Data_984274_984275')
        assert epu.get_movie__1_8_falcon(compare_name).equals(pd.DataFrame({'MicrographMovieNameRaw': tif_file}, index=[0]))

    def test_search_file_tiff_should_return_file_path(self):
        tiff_file = os.path.join(THIS_DIR, INPUT_TEST_FOLDER, 'epu_1_8_falcon_tiff', 'FoilHole_983503_Data_984274_984275_20171201_1435_Fractions.tiff')
        compare_name = os.path.join(THIS_DIR, INPUT_TEST_FOLDER, 'epu_1_8_falcon_tiff', 'FoilHole_983503_Data_984274_984275')
        assert epu.get_movie__1_8_falcon(compare_name).equals(pd.DataFrame({'MicrographMovieNameRaw': tiff_file}, index=[0]))

    def test_search_file_tiff_mutli_should_raise_AssertionError(self):
        compare_name = os.path.join(THIS_DIR, INPUT_TEST_FOLDER, 'epu_1_8_falcon_tiff_multi', 'FoilHole_983503_Data_984274_984275')
        with pytest.raises(AssertionError):
            epu.get_movie__1_8_falcon(compare_name)


class TestGetNumberOfFrames_18falcon:

    def test_read_mrc_header_returns_9(self):
        mrc_file = os.path.join(THIS_DIR, INPUT_TEST_FOLDER, 'epu_1_8_falcon_mrc', 'FoilHole_983503_Data_984274_984275_20171201_1435_Fractions.mrc')
        data_frame = pd.DataFrame({'MicrographMovieNameRaw': mrc_file}, index=[0])
        epu.get_number_of_frames__1_8_falcon(data_frame)
        assert data_frame['FoundNumberOffractions'].iloc[0] == 9

    def test_read_tif_header_returns_9(self):
        mrc_file = os.path.join(THIS_DIR, INPUT_TEST_FOLDER, 'epu_1_8_falcon_tif', 'FoilHole_983503_Data_984274_984275_20171201_1435_Fractions.tif')
        data_frame = pd.DataFrame({'MicrographMovieNameRaw': mrc_file}, index=[0])
        epu.get_number_of_frames__1_8_falcon(data_frame)
        assert data_frame['FoundNumberOffractions'].iloc[0] == 9

    def test_read_tiff_header_returns_9(self):
        mrc_file = os.path.join(THIS_DIR, INPUT_TEST_FOLDER, 'epu_1_8_falcon_tiff', 'FoilHole_983503_Data_984274_984275_20171201_1435_Fractions.tiff')
        data_frame = pd.DataFrame({'MicrographMovieNameRaw': mrc_file}, index=[0])
        epu.get_number_of_frames__1_8_falcon(data_frame)
        assert data_frame['FoundNumberOffractions'].iloc[0] == 9


class TestGetCopyCommand_18falcon:

    def test_function_returns_copy_command(self):
        assert epu.get_copy_command__1_8_falcon() == utils.copy


class TestGetMovie_18falcon:

    def test_search_file_mrc_should_return_file_path(self):
        mrc_file = os.path.join(THIS_DIR, INPUT_TEST_FOLDER, 'epu_1_8_falcon_mrc', 'FoilHole_983503_Data_984274_984275_20171201_1435_Fractions.mrc')
        compare_name_data = os.path.join(THIS_DIR, INPUT_TEST_FOLDER, 'epu_1_8_falcon_mrc', 'FoilHole_983503_Data_984274_984275')
        compare_name = pd.DataFrame({'compare_name': compare_name_data}, index=[0])
        epu.get_movie__1_8_falcon(compare_name)
        assert compare_name['MicrographMovieNameRaw'].iloc[0] == mrc_file

    def test_search_file_tif_should_return_file_path(self):
        tif_file = os.path.join(THIS_DIR, INPUT_TEST_FOLDER, 'epu_1_8_falcon_tif', 'FoilHole_983503_Data_984274_984275_20171201_1435_Fractions.tif')
        compare_name_data = os.path.join(THIS_DIR, INPUT_TEST_FOLDER, 'epu_1_8_falcon_tif', 'FoilHole_983503_Data_984274_984275')
        compare_name = pd.DataFrame({'compare_name': compare_name_data}, index=[0])
        epu.get_movie__1_8_falcon(compare_name)
        assert compare_name['MicrographMovieNameRaw'].iloc[0] == tif_file

    def test_search_file_tiff_should_return_file_path(self):
        tiff_file = os.path.join(THIS_DIR, INPUT_TEST_FOLDER, 'epu_1_8_falcon_tiff', 'FoilHole_983503_Data_984274_984275_20171201_1435_Fractions.tiff')
        compare_name_data = os.path.join(THIS_DIR, INPUT_TEST_FOLDER, 'epu_1_8_falcon_tiff', 'FoilHole_983503_Data_984274_984275')
        compare_name = pd.DataFrame({'compare_name': compare_name_data}, index=[0])
        epu.get_movie__1_8_falcon(compare_name)
        assert compare_name['MicrographMovieNameRaw'].iloc[0] == tiff_file

    def test_search_file_tiff_mutli_should_raise_AssertionError(self):
        compare_name = os.path.join(THIS_DIR, INPUT_TEST_FOLDER, 'epu_1_8_falcon_tiff_multi', 'FoilHole_983503_Data_984274_984275')
        compare_name = pd.DataFrame({'compare_name': compare_name}, index=[0])
        with pytest.raises(AssertionError):
            epu.get_movie__1_8_falcon(compare_name)
