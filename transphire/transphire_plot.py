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
import numpy as np


def get_mic_number(array, settings, as_int=True):
    """
    Identify the micrograph number out of the name string.

    Arguments:
    array - Array containing information
    settings - User provided settings

    Return:
    Array of micrograph numbers
    """
    error = False
    if as_int:
        out_type = int
    else:
        out_type = str
    if settings['Output']['Rename micrographs'] == 'True':
        number_list = []
        prefix = settings['Output']['Rename prefix']
        suffix = settings['Output']['Rename suffix']
        for entry in array:
            entry = os.path.basename(entry)
            if suffix == '':
                first_part_split = entry.rsplit('.', 1)
            else:
                first_part_split = entry.rsplit(suffix, 1)
            first_part = first_part_split[0]
            if prefix == '':
                number = first_part
            else:
                number = first_part.split(prefix)[-1]
            if as_int:
                try:
                    number = int(number)
                except ValueError:
                    error = True
                    break
            number_list.append(number)
    else:
        number_list = np.arange(len(array))

    if error:
        number_list = np.arange(len(array))
    else:
        pass

    return np.array(number_list).astype(out_type)


def dummy(data, settings, label):
    return '', '', ['', ''], ['', ''], ''


def update_ctf(data, settings, label):
    """
    Update the plot for CTFFIND v4.1.8.

    Arguments:
    data - Data to plot
    settings - User provided settings
    label - Label of the plot

    Return:
    x values, y values, label, title
    """
    x_values = get_mic_number(data['file_name'], settings)
    y_values = data[label]
    if label == 'defocus':
        y_values = y_values / 10000
        label = 'Defocus / mum'
        title = 'Mean defocus'

    elif label == 'defocus_diff':
        y_values = y_values / 10000
        label = 'Defocus diff / mum'
        title = 'Defocus diff'

    elif label == 'astigmatism':
        label = 'Angle / degree'
        title = 'Azimuth of astigmatism'

    elif label == 'phase_shift':
        label = 'Phase shift / degree'
        title = 'Additional phase shift'

    elif label == 'cross_corr':
        label = 'Cross correlation'
        title = 'Cross correlation'

    elif label == 'limit':
        y_values[y_values == np.inf] = 0
        label = 'Resolution limit / A'
        title = 'Resolution limit'

    else:
        raise Exception('Plotwidget: Do not know what to do :O {0}'.format(label))

    return x_values, y_values, ['Micrograph', 'Nr. of Micrographs'], [label, label], title


def update_motion(data, settings, label):
    """
    Update the plot for MotionCor2 v1.0.0.

    Arguments:
    data - Data to plot
    settings - User provided settings
    label - Label of the plot

    Return:
    x values, y values, label, title
    """
    x_values = get_mic_number(data['file_name'], settings)
    y_values = data[label]
    label_y = 'Drift / px'
    if label == 'overall drift':
        title = 'Overall drift'

    elif label == 'average drift per frame':
        title = 'Average drift per frame'

    elif label == 'first frame drift':
        title = 'First frame drift'

    elif label == 'average drift per frame without first':
        title = 'Average drift per frame without first'

    else:
        print('Plotwidget: Do not know what to do :O', label)
        raise Exception

    return x_values, y_values, ['Micrograph', 'Nr. of Micrographs'], [label_y, label_y], title


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
    y_values = data[label]
    x_values = get_mic_number(data['file_name'], settings)
    if label == 'particles':
        title = label
        label_x = ['Micrograph', 'Nr. of Micrographs']
        label_val = label
        label_hist = label
    else:
        title = label
        label_val = 'Mean {}'.format(label)
        label_hist = label
        y_values = np.array([np.mean(entry) for entry in y_values])
        label_x = ['Micrograph', 'Nr. of Particles']
    return x_values, y_values, label_x, [label_val, label_hist], title

def update_micrograph(data, settings, label):
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
    y_values = data[label]
    title = label
    return x_values, y_values, ['Micrograph', 'Nr. of Micrographs'], [label, label], title

def update_batch(data, settings, label):
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
    y_values = data[label]
    title = label
    return x_values, y_values, ['Batch', 'Nr. of Batches'], [label, label], title

