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
import pandas as pd
import numpy as np


class TestGetMetaInfo:
    """
    Append xml data to an pandas data frame.
    """

    @pytest.fixture(scope='function')
    def pandas_frame(self):
        columns = [
            'DoseOnCamera',
            'Dose',
            'PhasePlateUsed',
            'AppliedDefocus',
            'pixelSize',
            'ExposureTime',
            'ReadoutArea_height',
            'PreExposureTime',
            'PreExposurePauseTime',
            'ApplicationSoftware',
            'ApplicationSoftwareVersion',
            'AccelerationVoltage',
            'ComputerName',
            'InstrumentModel',
            'InstrumentID',
            'BeamShift_x',
            'BeamShift_y',
            'BeamTilt_x',
            'BeamTilt_y',
            'Defocus',
            'Position_A',
            'Position_B',
            'Position_X',
            'Position_Y',
            'Position_Z',
            'acquisitionDateTime',
            'Intensity',
            'NominalMagnification',
            'NumberOffractions',
            ] 
        data_frame = pd.DataFrame(index=np.arange(10000), columns=columns)
        return data_frame

