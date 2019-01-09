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
import numpy as np


def get_mic_number(array, settings):
    """
    Identify the micrograph number out of the name string.

    Arguments:
    array - Array containing information
    settings - User provided settings

    Return:
    Array of micrograph numbers
    """
    error = False
    if settings['General']['Rename micrographs'] == 'True':
        number_list = []
        prefix = settings['General']['Rename prefix']
        suffix = settings['General']['Rename suffix']
        for entry in array:
            if suffix == '':
                first_part = entry.split('.')[0]
            else:
                first_part_split = entry.split(suffix)
                first_part = suffix.join(first_part_split[:-1])
            if prefix == '':
                number = first_part
            else:
                number = first_part.split(prefix)[-1]
            try:
                number_list.append(int(number))
            except ValueError:
                error = True
                break
    else:
        number_list = np.arange(len(array))

    if error:
        number_list = np.arange(len(array))
    else:
        pass

    return np.array(number_list)


def update_cter_v1_0(data, settings, label):
    """
    Update the plot for CTER v1.0.

    Arguments:
    data - Data to plot
    settings - User provided settings
    label - Label of the plot

    Return:
    x values, y values, label, title
    """
    x_values, y_values, label, title = update_ctffind_4_v4_1_8(
        data=data,
        settings=settings,
        label=label
        )
    return x_values, y_values, label, title


def update_gctf_v1_18(data, settings, label):
    """
    Update the plot for Gctf v1.18.

    Arguments:
    data - Data to plot
    settings - User provided settings
    label - Label of the plot

    Return:
    x values, y values, label, title
    """
    x_values, y_values, label, title = update_ctffind_4_v4_1_8(
        data=data,
        settings=settings,
        label=label
        )
    return x_values, y_values, label, title


def update_gctf_v1_06(data, settings, label):
    """
    Update the plot for Gctf v1.06.

    Arguments:
    data - Data to plot
    settings - User provided settings
    label - Label of the plot

    Return:
    x values, y values, label, title
    """
    x_values, y_values, label, title = update_ctffind_4_v4_1_8(
        data=data,
        settings=settings,
        label=label
        )
    return x_values, y_values, label, title


def update_ctffind_4_v4_1_10(data, settings, label):
    """
    Update the plot for CTFFIND v4.1.10.

    Arguments:
    data - Data to plot
    settings - User provided settings
    label - Label of the plot

    Return:
    x values, y values, label, title
    """
    x_values, y_values, label, title = update_ctffind_4_v4_1_8(
        data=data,
        settings=settings,
        label=label
        )
    return x_values, y_values, label, title


def update_ctffind_4_v4_1_8(data, settings, label):
    """
    Update the plot for CTFFIND v4.1.8.

    Arguments:
    data - Data to plot
    settings - User provided settings
    label - Label of the plot

    Return:
    x values, y values, label, title
    """
    if label == 'defocus':
        x_values = get_mic_number(data['file_name'], settings)
        y_values = data['defocus']/10000
        label = 'Defocus / mum'
        title = 'Mean defocus'

    elif label == 'defocus_diff':
        x_values = get_mic_number(data['file_name'], settings)
        y_values = data['defocus_diff'] / 10000
        label = 'Defocus diff / mum'
        title = 'Defocus diff'

    elif label == 'astigmatism':
        x_values = get_mic_number(data['file_name'], settings)
        y_values = data['astigmatism']
        label = 'Angle / degree'
        title = 'Azimuth of astigmatism'

    elif label == 'phase_shift':
        x_values = get_mic_number(data['file_name'], settings)
        y_values = data['phase_shift']
        label = 'Phase shift / degree'
        title = 'Additional phase shift'

    elif label == 'cross_corr':
        x_values = get_mic_number(data['file_name'], settings)
        y_values = data['cross_corr']
        label = 'Cross correlation'
        title = 'Cross correlation'

    elif label == 'limit':
        x_values = get_mic_number(data['file_name'], settings)
        y_values = data['limit']
        y_values[y_values == np.inf] = 0
        label = 'Resolution limit / A'
        title = 'Resolution limit'

    else:
        raise Exception('Plotwidget: Do not know what to do :O {0}'.format(label))

    return x_values, y_values, label, title


def update_motion_cor_2_v1_0_0(data, settings, label):
    """
    Update the plot for MotionCor2 v1.0.0.

    Arguments:
    data - Data to plot
    settings - User provided settings
    label - Label of the plot

    Return:
    x values, y values, label, title
    """
    if label == 'overall drift':
        x_values = get_mic_number(data['file_name'], settings)
        y_values = data['overall drift']
        label = 'Drift / px'
        title = 'Overall drift'

    elif label == 'average drift per frame':
        x_values = get_mic_number(data['file_name'], settings)
        y_values = data['average drift per frame']
        label = 'Drift / px'
        title = 'Average drift per frame'

    elif label == 'first frame drift':
        x_values = get_mic_number(data['file_name'], settings)
        y_values = data['first frame drift']
        label = 'Drift / px'
        title = 'First frame drift'

    elif label == 'average drift per frame without first':
        x_values = get_mic_number(data['file_name'], settings)
        y_values = data['average drift per frame without first']
        label = 'Drift / px'
        title = 'Average drift per frame without first'

    else:
        print('Plotwidget: Do not know what to do :O', label)
        raise Exception

    return x_values, y_values, label, title


def update_motion_cor_2_v1_1_0(data, settings, label):
    """
    Update the plot for MotionCor2 v1.1.0.

    Arguments:
    data - Data to plot
    settings - User provided settings
    label - Label of the plot

    Return:
    x values, y values, label, title
    """
    x_values, y_values, label, title = update_motion_cor_2_v1_0_0(
        data=data,
        settings=settings,
        label=label
        )
    return x_values, y_values, label, title


def update_motion_cor_2_v1_0_5(data, settings, label):
    """
    Update the plot for MotionCor2 v1.0.5.

    Arguments:
    data - Data to plot
    settings - User provided settings
    label - Label of the plot

    Return:
    x values, y values, label, title
    """
    x_values, y_values, label, title = update_motion_cor_2_v1_0_0(
        data=data,
        settings=settings,
        label=label
        )
    return x_values, y_values, label, title


def update_cryolo_v1_2_2(data, settings, label):
    """
    Update the plot for crYOLO v1.2.2.

    Arguments:
    data - Data to plot
    settings - User provided settings
    label - Label of the plot

    Return:
    x values, y values, label, title
    """
    return update_cryolo_v1_0_4(data, settings, label)

def update_cryolo_v1_2_1(data, settings, label):
    """
    Update the plot for crYOLO v1.2.1.

    Arguments:
    data - Data to plot
    settings - User provided settings
    label - Label of the plot

    Return:
    x values, y values, label, title
    """
    return update_cryolo_v1_0_4(data, settings, label)

def update_cryolo_v1_1_0(data, settings, label):
    """
    Update the plot for crYOLO v1.1.0.

    Arguments:
    data - Data to plot
    settings - User provided settings
    label - Label of the plot

    Return:
    x values, y values, label, title
    """
    return update_cryolo_v1_0_4(data, settings, label)

def update_cryolo_v1_0_5(data, settings, label):
    """
    Update the plot for crYOLO v1.0.5.

    Arguments:
    data - Data to plot
    settings - User provided settings
    label - Label of the plot

    Return:
    x values, y values, label, title
    """
    return update_cryolo_v1_0_4(data, settings, label)


def update_cryolo_v1_0_4(data, settings, label):
    """
    Update the plot for crYOLO v1.0.4.

    Arguments:
    data - Data to plot
    settings - User provided settings
    label - Label of the plot

    Return:
    x values, y values, label, title
    """
    x_values = get_mic_number(data['file_name'], settings)
    y_values = data['particles']
    return x_values, y_values, 'Nr. of Particles', 'Total particles: {0}'.format(np.sum(data['particles']))

