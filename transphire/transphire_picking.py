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
import json
import os
import imageio
import numpy as np

from . import transphire_utils as tu


def get_picking_command(file_input, new_name, settings, queue_com, name):
    """
    Create the picking command based on the picking software.

    file_input - Input name of the file for ctf estimation
    new_name - Output file
    settings - TranSPHIRE settings
    queue_com - Queue for communication
    name - Name of process

    Returns:
    Picking command
    File to check vor validation if the process was successful
    """
    picking_name = settings['Copy']['Picking']
    command = None
    block_gpu = None
    gpu_list = None
    if tu.is_higher_version(picking_name, '1.4.1'):
        command, gpu = create_cryolo_v1_4_1_command(
            picking_name=picking_name,
            file_input=file_input,
            file_output=new_name,
            settings=settings,
            name=name,
            )
        check_files = []
        if '_' in gpu:
            if float(settings[picking_name]['--gpu_fraction']) == 1:
                raise UserWarning('Sub GPUs are only supported if the --gpu_fraction option is not equal 1')
            block_gpu = True
        else:
            block_gpu = True
        gpu_list = gpu.split()

    elif tu.is_higher_version(picking_name, '1.1'):
        command, gpu = create_cryolo_v1_1_0_command(
            picking_name=picking_name,
            file_input=file_input,
            file_output=new_name,
            settings=settings,
            name=name,
            )
        if '_' in gpu:
            raise UserWarning('Sub GPUs are only supported in crYOLO version >=1.4.1')
        check_files = []
        block_gpu = True
        gpu_list = gpu.split()

    elif tu.is_higher_version(picking_name, '1.0'):
        command, gpu = create_cryolo_v1_0_4_command(
            picking_name=picking_name,
            file_input=file_input,
            file_output=new_name,
            settings=settings,
            name=name,
            )
        if '_' in gpu:
            raise UserWarning('Sub GPUs are only supported in crYOLO version >=1.4.1')
        check_files = []
        block_gpu = True
        gpu_list = gpu.split()

    else:
        message = '\n'.join([
            '{0}: Not known!'.format(settings['Copy']['Picking']),
            'Please contact the TranSPHIRE authors!'
            ])
        queue_com['error'].put(
            message,
            name
            )
        IOError(message)

    assert command is not None, 'command not specified: {0}'.format(picking_name)
    assert block_gpu is not None, 'block_gpu not specified: {0}'.format(picking_name)
    assert gpu_list is not None, 'gpu_list not specified: {0}'.format(picking_name)

    return command, check_files, block_gpu, gpu_list


def find_logfiles(root_path, file_name, settings, queue_com, name):
    """
    Find logfiles related to the produced CTF files.

    root_path - Root path of the file
    file_name - File name of the ctf file.
    settings - TranSPHIRE settings
    queue_com - Queue for communication
    name - Name of process

    Returns:
    list of log files
    """
    folder_name = 'picking_folder_feedback_{0}'.format(settings['do_feedback_loop'].value)
    log_files = None
    copied_log_files = None
    picking_name = settings['Copy']['Picking']
    picking_root_path = os.path.join(settings[folder_name], file_name)
    if tu.is_higher_version(picking_name, '1.4.1'):
        if settings[picking_name]['--filament'] == 'True':
            folder_names = (
                ('EMAN_HELIX_SEGMENTED', 'box'),
                ('EMAN_START_END', 'box'),
                ('STAR_START_END', 'star'),
                )
        else:
            folder_names = (
                ('CBOX', 'cbox'),
                ('EMAN', 'box'),
                ('STAR', 'star'),
                )
        copied_log_files = []
        for folder_name, ext in folder_names:
            copied_log_files.extend(['{0}.{1}'.format(os.path.join(
                os.path.dirname(picking_root_path),
                folder_name,
                os.path.basename(picking_root_path)
                ),
                ext,
                )])
        log_files = copied_log_files
    elif tu.is_higher_version(picking_name, '1.2.2'):
        if settings[picking_name]['--filament'] == 'True':
            folder_names = (
                ('EMAN_HELIX_SEGMENTED', 'box'),
                ('EMAN_START_END', 'box'),
                ('STAR_START_END', 'star'),
                )
        else:
            folder_names = (
                ('EMAN', 'box'),
                ('STAR', 'star'),
                )
        copied_log_files = []
        for folder_name, ext in folder_names:
            copied_log_files.extend(['{0}.{1}'.format(os.path.join(
                os.path.dirname(picking_root_path),
                folder_name,
                os.path.basename(picking_root_path)
                ),
                ext,
                )])
        log_files = copied_log_files
    elif tu.is_higher_version(picking_name, '1.2.1'):
        copied_log_files = ['{0}.box'.format(picking_root_path)]
        log_files = copied_log_files

    elif tu.is_higher_version(picking_name, '1.1.0'):
        if settings[picking_name]['--filament'] == 'True':
            copied_log_files = ['{0}.txt'.format(picking_root_path)]
        else:
            copied_log_files = ['{0}.box'.format(picking_root_path)]
        log_files = copied_log_files

    elif tu.is_higher_version(picking_name, '1.0.4'):
        copied_log_files = ['{0}.box'.format(picking_root_path)]
        log_files = copied_log_files

    else:
        message = '\n'.join([
            '{0}: Not known!'.format(settings['Copy']['Picking']),
            'Please contact the TranSPHIRE authors!'
            ])
        queue_com['error'].put(
            message,
            name
            )
        raise IOError(message)

    assert log_files is not None
    assert copied_log_files is not None
    return log_files, copied_log_files


def create_filter_command(
        file_input, settings
        ):
    picking_name = settings['Copy']['Picking']
    command = []
    block_gpu = False
    gpu_list = []

    folder_name = 'picking_folder_feedback_{0}'.format(settings['do_feedback_loop'].value)

    file_output_tmp = file_input
    try:
        do_filter = bool(settings[picking_name]['Filter micrographs'] == 'True')
    except KeyError:
        do_filter = False
    if do_filter:

        filter_high = float(settings[picking_name]['Filter value high pass (A)'])
        filter_low = float(settings[picking_name]['Filter value low pass (A)'])
        pixel_size = float(settings[picking_name]['Pixel size (A/px)'])

        filter_high_abs = pixel_size / filter_high
        filter_low_abs = pixel_size / filter_low

        file_output_tmp = os.path.join(
                settings[folder_name],
                os.path.basename(file_input)
                )

        command.append("PATH=$(dirname $(which {0})):${{PATH}}".format(settings['Path']['e2proc2d.py']))
        command.append('{0}'.format(settings['Path']['e2proc2d.py']))
        command.append('{0}'.format(file_input))
        command.append('{0}'.format(file_output_tmp))
        command.append('--process=filter.lowpass.gauss:cutoff_freq={0}'.format(filter_low_abs))
        command.append('--process=filter.highpass.gauss:cutoff_freq={0}'.format(filter_high_abs))
        command.append(';')

    file_output_jpg = os.path.join(
            settings[folder_name],
            '{0}.png'.format(os.path.splitext(os.path.basename(file_input))[0])
            )
    command.append("PATH=$(dirname $(which {0})):${{PATH}}".format(settings['Path']['e2proc2d.py']))
    command.append('{0}'.format(settings['Path']['e2proc2d.py']))
    command.append('{0}'.format(file_output_tmp))
    command.append('{0}'.format(file_output_jpg))
    command.append('--meanshrink=4')
    command.append('--outmode=uint8')

    check_files = [file_output_tmp, file_output_jpg]
    return ' '.join(command), file_output_tmp, check_files, block_gpu, gpu_list


def create_cryolo_v1_4_1_command(
        picking_name, file_input, file_output, settings, name
        ):
    """Create the crYOLO v1.1.0 command"""
    command = []
    # Start the program
    ignore_list = []
    ignore_list.append('--filament')
    ignore_list.append('Filter micrographs')
    ignore_list.append('Filter value high pass (A)')
    ignore_list.append('Filter value low pass (A)')
    ignore_list.append('Pixel size (A/px)')
    ignore_list.append('Box size')
    ignore_list.append('Split Gpu?')
    ignore_list.append('--gpu')
    ignore_list.append('--threshold')
    ignore_list.append('--threshold_old')
    ignore_list.append('--weights_old')
    ignore_list.append('Lowest defocus percent')
    ignore_list.append('Minimum micrographs')
    ignore_list.append('Minimum particles')
    ignore_list.append('Mean percent')

    command.append('{0}'.format(settings['Path'][picking_name]))

    command.append('-i')
    command.append('{0}'.format(' '.join(file_input)))
    command.append('-o')
    command.append('{0}'.format(file_output))
    command.append('--write_empty')
    command.append('--threshold={0}'.format(
        settings[picking_name]['--threshold']
        if float(settings[picking_name]['--threshold']) != -1
        else 0.1
        ))

    ignore_list.append('--nomerging')
    ignore_list.append('--nosplit')
    if settings[picking_name]['--filament'] == 'True':
        command.append('--filament')
        if settings[picking_name]['--nomerging'] == 'True':
            command.append('--nomerging')
        if settings[picking_name]['--nosplit'] == 'True':
            command.append('--nosplit')
    else:
        ignore_list.append('--filament_width')
        ignore_list.append('--box_distance')
        ignore_list.append('--minimum_number_boxes')
        ignore_list.append('--mask_width')
        ignore_list.append('--search_range_factor')

    if settings[picking_name]['Split Gpu?'] == 'True':
        try:
            gpu_id = int(name.split('_')[-1])
        except ValueError:
            gpu_id = 0
        try:
            gpu_raw = settings[picking_name]['--gpu'].split()[gpu_id]
        except IndexError:
            raise UserWarning('There are less gpus provided than threads available! Please restart with the same number of pipeline processors as GPUs provided and restart! Stopping this thread!')
    else:
        gpu_raw = settings[picking_name]['--gpu']

    gpu = ' '.join(list(set([entry.split('_')[0] for entry in gpu_raw.split()])))
    if len(gpu.split()) != len(gpu_raw.split()) and settings[picking_name]['Split Gpu?'] == 'False':
        raise UserWarning('One cannot use multi GPU in combination with the disabled Split GPU option!')

    command.append('--gpu')
    command.append('{0}'.format(gpu))

    for key, value in settings[picking_name].items():
        if key in ignore_list:
            continue
        elif value:
            try:
                if '|||' in value:
                    external_log, local_key = value.split('|||')
                    with open(settings[external_log], 'r') as read:
                        log_data = json.load(read)
                    
                    try:
                        set_value = log_data[settings['current_set']][picking_name][local_key]['new_file']
                    except KeyError:
                        continue
                else:
                    set_value = value
            except TypeError:
                set_value = value
            command.append(key)
            command.append('{0}'.format(set_value))

    return ' '.join(command), gpu_raw


def create_cryolo_v1_1_0_command(
        picking_name, file_input, file_output, settings, name
        ):
    """Create the crYOLO v1.1.0 command"""

    command = []
    # Start the program
    ignore_list = []
    ignore_list.append('--filament')
    ignore_list.append('Filter micrographs')
    ignore_list.append('Filter value high pass (A)')
    ignore_list.append('Filter value low pass (A)')
    ignore_list.append('Pixel size (A/px)')
    ignore_list.append('Box size')
    ignore_list.append('Split Gpu?')
    ignore_list.append('--gpu')

    command.append('{0}'.format(settings['Path'][picking_name]))

    command.append('-i')
    command.append('{0}'.format(' '.join(file_input)))
    command.append('-o')
    command.append('{0}'.format(file_output))
    command.append('--write_empty')

    if settings[picking_name]['--filament'] == 'True':
        command.append('--filament')
    else:
        ignore_list.append('--filament_width')
        ignore_list.append('--box_distance')
        ignore_list.append('--minimum_number_boxes')

    if settings[picking_name]['Split Gpu?'] == 'True':
        try:
            gpu_id = int(name.split('_')[-1])-1
        except ValueError:
            gpu_id = 0
        try:
            gpu = settings[picking_name]['--gpu'].split()[gpu_id]
        except IndexError:
            raise UserWarning('There are less gpus provided than threads available! Please restart with the same number of pipeline processors as GPUs provided and restart! Stopping this thread!')
    else:
        gpu = settings[picking_name]['--gpu']

    command.append('--gpu')
    command.append('{0}'.format(gpu))

    for key, value in settings[picking_name].items():
        if key in ignore_list:
            continue
        elif value:
            try:
                if '|||' in value:
                    external_log, local_key = value.split('|||')
                    with open(settings[external_log], 'r') as read:
                        log_data = json.load(read)
                    try:
                        set_value = log_data[settings['current_set']][picking_name][local_key]['new_file']
                    except KeyError:
                        continue
                else:
                    set_value = value
            except TypeError:
                set_value = value
            command.append(key)
            command.append('{0}'.format(set_value))

    return ' '.join(command), gpu


def create_cryolo_v1_0_4_command(
        picking_name, file_input, file_output, settings, name
        ):
    """Create the crYOLO v1.0.4 command"""

    command = []
    # Start the program
    ignore_list = []
    ignore_list.append('Filter micrographs')
    ignore_list.append('Filter value high pass (A)')
    ignore_list.append('Filter value low pass (A)')
    ignore_list.append('Pixel size (A/px)')
    ignore_list.append('Box size')
    ignore_list.append('Split Gpu?')
    ignore_list.append('--gpu')

    command.append('{0}'.format(settings['Path'][picking_name]))

    command.append('-i')
    command.append('{0}'.format(' '.join(file_input)))
    command.append('-o')
    command.append('{0}'.format(file_output))
    command.append('--write_empty')

    if settings[picking_name]['Split Gpu?'] == 'True':
        try:
            gpu_id = int(name.split('_')[-1])-1
        except ValueError:
            gpu_id = 0
        try:
            gpu = settings[picking_name]['--gpu'].split()[gpu_id]
        except IndexError:
            raise UserWarning('There are less gpus provided than threads available! Please restart with the same number of pipeline processors as GPUs provided and restart! Stopping this thread!')
    else:
        gpu = settings[picking_name]['--gpu']

    command.append('--gpu')
    command.append('{0}'.format(gpu))

    for key, value in settings[picking_name].items():
        if key in ignore_list:
            continue
        elif value:
            try:
                if '|||' in value:
                    external_log, local_key = value.split('|||')
                    with open(settings[external_log], 'r') as read:
                        log_data = json.load(read)
                    try:
                        set_value = log_data[settings['current_set']][picking_name][local_key]['new_file']
                    except KeyError:
                        continue
                else:
                    set_value = value
            except TypeError:
                set_value = value
            command.append(key)
            command.append('{0}'.format(set_value))

    return ' '.join(command), gpu


@tu.rerun_function_in_case_of_error
def create_box_jpg(file_name, settings, queue_com, name):
    """
    Create jpg files that are overlayed with the box coordinate

    file_name - Name of the file to overlay.
    settings - Transphire settings.
    queue_com - Dictionary for communication.
    name - Thread name

    Return:
    It creates a file.
    """
    folder_name = 'picking_folder_feedback_{0}'.format(settings['do_feedback_loop'].value)
    picking_name = settings['Copy']['Picking']
    box_file = [entry for entry in find_logfiles(file_name, file_name, settings, queue_com, name)[0] if entry.endswith('.box') and '/EMAN_START_END/' not in entry][0]
    jpg_file = os.path.join(settings[folder_name], '{0}.png'.format(file_name))
    new_jpg_file = os.path.join(settings[folder_name], 'jpg', '{0}.jpg'.format(file_name))
    tu.mkdir_p(os.path.join(settings[folder_name], 'jpg'))

    box_data = np.atleast_2d(np.genfromtxt(box_file).astype(int))
    jpg_data = imageio.imread(jpg_file, as_gray=False, pilmode='RGB')

    bin_value = 4
    if box_data.size > 0:
        if box_file.endswith('.box'):
            try:
                box_data[:, 0] += box_data[:, 2]//2
                box_data[:, 1] += box_data[:, 3]//2
            except IndexError:
                pass
        elif box_file.endswith('.txt'):
            pass
        else:
            assert 'Box ending not known!', box_file
        box_data[:, 0] = box_data[:, 0]//bin_value
        box_data[:, 1] = box_data[:, 1]//bin_value

        jpg_data = np.rot90(jpg_data, 3)
        create_box(jpg_data=jpg_data, maskcenters=box_data[:,[0,1]], box_size=int(settings[picking_name]['Box size'])//bin_value)
        create_circle(jpg_data=jpg_data, maskcenters=box_data[:,[0,1]], radius=2)
        jpg_data = np.rot90(jpg_data, 1)
    else:
        pass

    imageio.imwrite(new_jpg_file, jpg_data)


def create_box(jpg_data, maskcenters, box_size):
    output_shape = (jpg_data.shape[0],jpg_data.shape[1])
    rect_mask = np.zeros((box_size, box_size))
    for i in range(2):
        rect_mask[:, i] = 1
        rect_mask[:, -i-1] = 1
        rect_mask[i, :] = 1
        rect_mask[-i-1, :] = 1

    idx_mask_x, idx_mask_y = np.where(rect_mask)
    out = np.zeros(output_shape, dtype=bool)

    idx_mask_x_abs = maskcenters[:, None, 0] + idx_mask_x - box_size//2
    idx_mask_y_abs = maskcenters[:, None, 1] + idx_mask_y - box_size//2

    valid_mask = (idx_mask_x_abs >= 0) & (idx_mask_x_abs < output_shape[0]) & \
             (idx_mask_y_abs >= 0) & (idx_mask_y_abs < output_shape[1])

    out[idx_mask_x_abs[valid_mask], idx_mask_y_abs[valid_mask]] = 1
    jpg_data[out, :] = np.array([255, 0, 0])


def create_circle(jpg_data, maskcenters, radius):
    """
    Create a circle in a numpy array

    Arguments:
    jpg_data - Data that needs to be changed
    maskcenters - center of mask
    radius - Radius of the circle

    Returns:
    None, jpg_data will be changed in-place
    """

    output_shape = (jpg_data.shape[0],jpg_data.shape[1])
    X,Y = [np.arange(-radius, radius+1)]*2
    disk_mask = X[:, None]**2 + Y**2 <= radius*radius
    idx_mask_x, idx_mask_y = np.where(disk_mask)

    out = np.zeros(output_shape, dtype=bool)

    idx_mask_x_abs = maskcenters[:, None, 0] + idx_mask_x - radius
    idx_mask_y_abs = maskcenters[:, None, 1] + idx_mask_y - radius

    valid_mask = (idx_mask_x_abs >= 0) & (idx_mask_x_abs < output_shape[0]) & \
             (idx_mask_y_abs >= 0) & (idx_mask_y_abs < output_shape[1])

    out[idx_mask_x_abs[valid_mask], idx_mask_y_abs[valid_mask]] = 1
    jpg_data[out, :] = np.array([255, 0, 0])
