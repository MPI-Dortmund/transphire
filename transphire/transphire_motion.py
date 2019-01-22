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
import re
import collections as co
import numpy as np
import mrcfile as mrc
import matplotlib.image as mi
from transphire import transphire_utils as tu


def get_motion_default(settings, motion_frames, queue_com, name):
    """
    Set the default values for the motion correction software.

    settings - TranSPHIRE settings.
    motion_frames - Sub frame settings.
    queue_com - Queue for communication.
    name - Name of the process.

    Returns:
    True, if dose weighting will be applied.
    """

    motion_name = settings['Copy']['Motion']
    if motion_name == 'MotionCor2 v1.0.0' or \
            motion_name == 'MotionCor2 v1.0.5' or \
            motion_name == 'MotionCor2 v1.1.0':
        motion_frames['last'] = \
            int(settings['General']['Number of frames']) - \
            int(settings[motion_name]['-Trunc'])
        motion_frames['first'] = \
            int(settings[motion_name]['-Throw']) + 1

        return bool(
                settings[motion_name]['-FmDose'] != '0' and
                settings[motion_name]['-PixSize'] != '0' and
                settings[motion_name]['-kV'] != '0'
                )

    else:
        message = '\n'.join([
            '{0}: Motion version not known.'.format(motion_name),
            'Please contact the TranSPHIRE authors!'
            ])
        queue_com['error'].put(
            message,
            name
            )
        raise IOError(message)


def get_dw_file_name(output_transfer_scratch, file_name, settings, queue_com, name):
    """
    Get the name of the dose weighted file directly after the program finished.

    output_transfer - Name of the folder in the scratch directory.
    file_name - File name of the root_name path.
    settings - TranSPHIRE settings.
    queue_com - Queue for communication.
    name - Name of the process.

    Returns:
    File path of the DW file.
    """
    motion_name = settings['Copy']['Motion']
    if motion_name == 'MotionCor2 v1.0.0' or \
            motion_name == 'MotionCor2 v1.0.5' or \
            motion_name == 'MotionCor2 v1.1.0':
        return os.path.join(
            output_transfer_scratch,
            '{0}_DW.mrc'.format(file_name)
            )

    else:
        message = '\n'.join([
            '{0}: Motion version not known.'.format(motion_name),
            'Please contact the TranSPHIRE authors!'
            ])
        queue_com['error'].put(
            message,
            name
            )
        raise IOError(message)


def get_motion_command(file_input, file_output_scratch, file_log_scratch, settings, queue_com, name, do_subsum):
    """
    Get the command for the selected motion software.

    file_input - Input file for motion correction.
    file_output_scratch - Output file name
    file_log_scratch - Logfile path on the scratch disc
    settings - TranSPHIRE settings.
    queue_com - Queue for communication.
    name - Name of the process.

    Returns:
    Motion command
    """
    motion_name = settings['Copy']['Motion']
    command = None
    block_gpu = None
    gpu_list = None
    if motion_name == 'MotionCor2 v1.0.0' or \
            motion_name == 'MotionCor2 v1.0.5' or \
            motion_name == 'MotionCor2 v1.1.0':
        command, gpu = create_motion_cor_2_v1_0_0_command(
            motion_name=motion_name,
            file_input=file_input,
            file_output=file_output_scratch,
            file_log=file_log_scratch,
            settings=settings,
            queue_com=queue_com,
            name=name,
            do_subsum=do_subsum,
            )
        gpu_list = gpu.split()

        if motion_name == 'MotionCor2 v1.0.0':
            block_gpu = False
        elif motion_name == 'MotionCor2 v1.0.5':
            block_gpu = True
        elif motion_name == 'MotionCor2 v1.1.0':
            if settings[motion_name]['-GpuMemUsage'] == '0':
                block_gpu = False
            else:
                block_gpu = True

    else:
        message = '\n'.join([
            '{0}: Motion version not known.'.format(settings['Copy']['Motion']),
            'Please contact the TranSPHIRE authors!'
            ])
        queue_com['error'].put(
            message,
            name
            )
        raise IOError(message)

    assert command is not None, 'command not specified: {0}'.format(motion_name)
    assert block_gpu is not None, 'block_gpu not specified: {0}'.format(motion_name)
    assert gpu_list is not None, 'gpu_list not specified: {0}'.format(motion_name)

    return command, block_gpu, gpu_list


def create_motion_cor_2_v1_0_0_command(motion_name, file_input, file_output, file_log, settings, queue_com, name, do_subsum):
    """
    Create the MotionCor2 v1.0.0 command

    file_input - Input file for motion correction.
    file_output - Output filename
    file_log - Logfile name
    settings - TranSPHIRE settings.
    queue_com - Queue for communication.
    name - Name of the process.

    Returns:
    Command for MotionCor2 v1.0.0
    """

    ignore_list = []
    ignore_list.append('Split Gpu?')
    ignore_list.append('-Gpu')
    ignore_list.append('dose cutoff')
    command = []
    # Start the program
    command.append('{0}'.format(settings['Path'][motion_name]))
    # Input Micrograph
    _, extension = os.path.splitext(file_input)
    if extension == '.tiff' or \
            extension == '.tif':
        command.append('-InTiff')
        command.append('{0}'.format(file_input))

    elif extension == '.mrc':
        command.append('-InMrc')
        command.append('{0}'.format(file_input))

    else:
        message = '{0}: Not known!'.format(extension)
        queue_com['error'].put(message, name)
        raise IOError(message)

    # Output micrograph
    command.append('-OutMrc')
    command.append('{0}'.format(file_output))
    if do_subsum:
        # Write the output stack
        command.append('-OutStack')
        command.append('1')
    else:
        pass
    # Log file
    command.append('-LogFile')
    command.append('{0}'.format(file_log))

    if settings[motion_name]['Split Gpu?'] == 'True':
        try:
            gpu_id = int(name.split('_')[-1])-1
        except ValueError:
            gpu_id = 0
        try:
            gpu = settings[motion_name]['-Gpu'].split()[gpu_id]
        except IndexError:
            raise UserWarning('There are less gpus provided than threads available! Please restart with the same number of pipeline processors as GPUs provided and restart! Stopping this thread!')
    else:
        gpu = settings[motion_name]['-Gpu']

    command.append('-Gpu')
    command.append('{0}'.format(gpu))

    for key in settings[motion_name]:
        if key in ignore_list:
            continue
        elif settings[motion_name][key]:
            command.append(key)
            command.append(
                '{0}'.format(settings[motion_name][key])
                )
        else:
            continue

    return ' '.join(command), gpu


def create_sum_movie_command(
        motion_frames, file_input, file_output, file_shift, file_frc,
        settings, queue_com, name
        ):
    """
    Create the SumMovie command.

    motion_frames - Sub frames settings dictionary
    file_input - File to sum.
    file_output - Output file name
    file_shift - Output shift file name
    file_frc - Output frc file name
    settings - TranSPHIRE settings
    queue_com - Queue for communication
    name - Name of the process

    Returns:
    Command for SumMovie
    """
    command = create_sum_movie_v1_0_2_command(
        motion_frames=motion_frames,
        file_input=file_input,
        file_output=file_output,
        file_shift=file_shift,
        file_frc=file_frc,
        settings=settings,
        queue_com=queue_com,
        name=name
        )
    block_gpu = False
    gpu_list = []
    return command, block_gpu, gpu_list


def create_sum_movie_v1_0_2_command(
        motion_frames, file_input, file_output, file_shift, file_frc,
        settings, queue_com, name
        ):
    """
    Create the SumMovie v1.0.2 command.

    motion_frames - Sub frames settings dictionary
    file_input - File to sum.
    file_output - Output file name
    file_shift - Output shift file name
    file_frc - Output frc file name
    settings - TranSPHIRE settings
    queue_com - Queue for communication
    name - Name of the process

    Returns:
    Command for Summovie v1.0.2
    """
    sum_movie_command = []
    # Input file
    sum_movie_command.append('{0}'.format(file_input))
    # Number of frames

    motion_name = settings['Copy']['Motion']
    if motion_name == 'MotionCor2 v1.0.0' or \
            motion_name == 'MotionCor2 v1.0.5' or \
            motion_name == 'MotionCor2 v1.1.0':
        sum_movie_command.append('{0}'.format(
            int(settings['General']['Number of frames']) -
            int(settings[motion_name]['-Trunc']) -
            int(settings[motion_name]['-Throw'])
            ))

    else:
        message = '\n'.join([
            '{0}: Motion version not known.'.format(motion_name),
            'Please contact the TranSPHIRE authors!'
            ])
        queue_com['error'].put(
            message,
            name
            )
        raise IOError(message)

    # Output sum file
    sum_movie_command.append('{0}'.format(file_output))
    # Shift file
    sum_movie_command.append('{0}'.format(file_shift))
    # FRC file
    sum_movie_command.append('{0}'.format(file_frc))
    # First frame
    sum_movie_command.append('{0}'.format(motion_frames['first']))
    # Last frame
    sum_movie_command.append('{0}'.format(motion_frames['last']))
    # Pixel size

    if motion_name == 'MotionCor2 v1.0.0' or \
            motion_name == 'MotionCor2 v1.0.5' or \
            motion_name == 'MotionCor2 v1.1.0':
        sum_movie_command.append(
            '{0}'.format(settings[motion_name]['-PixSize'])
            )

    else:
        message = '\n'.join([
            '{0}: Motion version not known.'.format(motion_name),
            'Please contact the TranSPHIRE authors!'
            ])
        queue_com['error'].put(
            message,
            name
            )
        raise IOError(message)

    # Dose correction
    sum_movie_command.append('No')

    command = 'echo "{0}" | {1}'.format(
        '\n'.join(sum_movie_command),
        '{0}'.format(settings['Path']['SumMovie v1.0.2'])
        )

    return command


def combine_motion_outputs(
        data,
        data_original,
        settings,
        queue_com,
        shared_dict,
        name,
        log_file,
        sum_file,
        dw_file,
        ):
    """
    Combine the motion outputs to one micrograph and one relion star file.

    root_path - Root path of the file
    file_name - File name of the ctf file.
    settings - TranSPHIRE settings
    queue_com - Queue for communication
    name - Name of process
    sum_file - Name of the dose uncorrected sum file

    Returns:
    None
    """
    motion_name = settings['Copy']['Motion']
    motion_settings = settings[motion_name]
    log_folder = os.path.dirname(log_file)
    stack_folder = settings['stack_folder']
    project_folder = '{0}/'.format(settings['project_folder'])
    sum_file = sum_file.replace(project_folder, '')
    if dw_file:
        dw_file = dw_file.replace(project_folder, '')
    else:
        pass

    output_name_mic = os.path.join(
        log_folder,
        '{0}_transphire_motion.txt'.format(os.path.basename(sum_file))
        )
    output_name_star = os.path.join(
        log_folder,
        '{0}_transphire_motion.star'.format(os.path.basename(sum_file))
        )
    output_name_star_relion3 = os.path.join(
        log_folder,
        '{0}_transphire_motion_relion3.star'.format(os.path.basename(sum_file))
        )

    output_name_mic_combined = os.path.join(
        project_folder,
        '{0}_transphire_motion.txt'.format(motion_name.replace(' ', '_'))
        )
    output_name_star_combined = os.path.join(
        project_folder,
        '{0}_transphire_motion.star'.format(motion_name.replace(' ', '_'))
        )
    output_name_star_relion3_combined = os.path.join(
        project_folder,
        '{0}_transphire_motion_relion3.star'.format(motion_name.replace(' ', '_'))
        )

    # SPHIRE
    with open(output_name_mic, 'w') as write:
        write.write('{0}\n'.format(os.path.basename(sum_file)))

    # RELION 2
    header_star = co.OrderedDict()
    if dw_file:
        header_star['_rlnMicrographNameNoDW'] = sum_file
        header_star['_rlnMicrographName'] = dw_file
    else:
        header_star['_rlnMicrographName'] = sum_file

    export_lines_star = [get_relion_header(header_star.keys())]
    create_export_data(header_star.values(), export_lines_star)
    with open(output_name_star, 'w') as write:
        write.write('\n'.join(export_lines_star))

    # RELION 3
    with open(log_file, 'r') as read:
        data_read = read.read()

    stack_size = re.search(
        r'^Stack[ ]+size:[ ]+([0-9]+)[ ]+([0-9]+)[ ]+([0-9]+)$',
        data_read,
        re.MULTILINE
        )
    movie_name = re.search( r'^-(?:InTiff|InMrc)[ ]+([^ ]+)$', data_read, re.MULTILINE).group(1)

    if settings['Copy']['Compress'] == 'True':
        movie_name = movie_name.replace(stack_folder, 'Compress')
        movie_name = movie_name.replace('.mrc', '.tiff')
    else:
        pass

    data_meta = [
        '',
        'data_general',
        '',
        '_rlnImageSizeX {0}'.format(stack_size.group(1)),
        '_rlnImageSizeY {0}'.format(stack_size.group(2)),
        '_rlnImageSizeZ {0}'.format(stack_size.group(3)),
        '_rlnMicrographMovieName {0}'.format(movie_name.replace(project_folder, '')),
        ]
    if motion_settings['-Gain']:
        new_gain = os.path.join(
            project_folder,
            '{0}_gain.mrc'.format(os.path.basename(motion_settings['-Gain']))
            )
        if not os.path.exists(new_gain):
            tu.copy(motion_settings['-Gain'], new_gain)
            data_meta.extend([
                '_rlnMicrographGainName {0}'.format(new_gain.replace(project_folder, '')),
                ])
        else:
            data_meta.extend([
                '_rlnMicrographGainName {0}'.format(new_gain.replace(project_folder, '')),
                ])
            new_gain = None
    else:
        new_gain = None

    if motion_settings['-DefectFile']:
        new_defect = os.path.join(
            project_folder,
            '{0}_defect.mrc'.format(os.path.basename(motion_settings['-DefectFile']))
            )
        if not os.path.exists(new_defect):
            tu.copy(motion_settings['-DefectFile'], new_defect)
            data_meta.extend([
                '_rlnMicrographDefectFile {0}'.format(new_defect.replace(project_folder, '')),
                ])
        else:
            data_meta.extend([
                '_rlnMicrographDefectFile {0}'.format(new_defect.replace(project_folder, '')),
                ])
            new_defect = None
    else:
        new_defect = None

    data_meta.extend([
        '_rlnMicrographBinning {0}'.format(motion_settings['-FtBin']),
        ])
    data_meta.extend([
        '_rlnMicrographOriginalPixelSize {0}'.format(motion_settings['-PixSize']),
        ])
    data_meta.extend([
        '_rlnMicrographDoseRate {0}'.format(motion_settings['-FmDose']),
        ])
    data_meta.extend([
        '_rlnMicrographPreExposure {0}'.format(motion_settings['-InitDose']),
        ])
    data_meta.extend([
        '_rlnVoltage {0}'.format(motion_settings['-kV']),
        ])

    data_meta.extend([
        '_rlnMicrographStartFrame {0}'.format(int(motion_settings['-Throw']) + 1),
        '_rlnMotionModelVersion 0',
        '',
        'data_global_shift',
        '',
        'loop_',
        '_rlnMicrographFrameNumber #1',
        '_rlnMicrographShiftX #2',
        '_rlnMicrographShiftY #3',
        ])

    assert data_original.shape[0] == 1, data_original
    data_original = data_original[0]
    idx_x = 0
    idx_y = 1
    offset_x = data_original[idx_x][0]
    offset_y = data_original[idx_y][0]

    sum_total = 0
    sum_early = 0
    sum_late = 0
    frame_cutoff = float(motion_settings['dose cutoff']) - float(motion_settings['-InitDose'])
    frame_cutoff /= float(motion_settings['-FmDose'])
    for idx in range(1, data_original.shape[1]):
        drift = np.sqrt(
            (data_original[idx_x][idx-1] - data_original[idx_x][idx])**2 +
            (data_original[idx_y][idx-1] - data_original[idx_y][idx])**2
            )
        sum_total += drift
        if idx <= frame_cutoff:
            sum_early += drift
        else:
            sum_late += drift

    for idx in range(data_original.shape[1]):
        data_meta.extend(['{0}\t{1}\t{2}'.format(
            idx+1,
            data_original[idx_x][idx]-offset_x,
            data_original[idx_y][idx]-offset_y
            )])

    relion3_meta = os.path.join(
        log_folder,
        '{0}_transphire_motion_relion3_meta.star'.format(os.path.basename(sum_file))
        )
    with open(relion3_meta, 'w') as write:
        write.write('\n'.join(data_meta))

    header_star_relion3 = co.OrderedDict()
    if dw_file:
        header_star_relion3['_rlnMicrographNameNoDW'] = sum_file.replace(project_folder, '')
        header_star_relion3['_rlnMicrographName'] = dw_file.replace(project_folder, '')
    else:
        header_star_relion3['_rlnMicrographName'] = sum_file.replace(project_folder, '')
    header_star_relion3['_rlnMicrographMetadata'] = relion3_meta.replace(project_folder, '')
    if sum_total:
        header_star_relion3['_rlnAccumMotionTotal'] = sum_total
        header_star_relion3['_rlnAccumMotionEarly'] = sum_early
        header_star_relion3['_rlnAccumMotionLate'] = sum_late
    else:
        pass

    export_lines_star_relion3 = [get_relion_header(header_star_relion3.keys())]
    create_export_data(header_star_relion3.values(), export_lines_star_relion3)

    with open(output_name_star_relion3, 'w') as write:
        write.write('\n'.join(export_lines_star_relion3))

    return output_name_mic_combined, output_name_star_combined, output_name_star_relion3_combined, new_gain, new_defect


def get_relion_header(names):
    """
    Create a relion star file header.

    names - Header names as list

    Returns:
    header string
    """
    header = []
    header.append('')
    header.append('data_')
    header.append('')
    header.append('loop_')
    for index, name in enumerate(names):
        header.append('{0} #{1}'.format(name, index+1))
    return '\n'.join(header)


def create_export_data(export_data, lines):
    """
    Write export data to file.

    export_data - Data to export.
    file_name - Name of the file to write to.

    Returns:
    In place modificaion of lines
    """
    row_string = []
    for value in export_data:
        if isinstance(value, int):
            row_string.append('{0: 7d}'.format(value))
        elif isinstance(value, float):
            row_string.append('{0: 14f}'.format(value))
        else:
            row_string.append('{0:s}'.format(value))
    lines.append('{0}\n'.format('\t'.join(row_string)))


def create_jpg_file(input_file, settings):
    file_name = tu.get_name(input_file)

    tu.mkdir_p(os.path.join(settings['motion_folder'], 'jpg'))
    tu.mkdir_p(os.path.join(settings['motion_folder'], 'jpg_2'))

    jpg_file_1 = os.path.join(settings['motion_folder'], 'jpg', '{0}.jpg'.format(file_name))
    jpg_file_2 = os.path.join(settings['motion_folder'], 'jpg_2', '{0}.jpg'.format(file_name))

    arr_1 = None
    arr_2 = None

    try:
        with mrc.open(input_file) as mrc_file:
            input_data = mrc_file.data
    except ValueError:
        with mrc.open(input_file, 'r+', permissive=True) as mrc_file:
            mrc_file.header.map = mrc.constants.MAP_ID
        with mrc.open(input_file) as mrc_file:
            input_data = mrc_file.data
    if len(input_data.shape) == 3:
            input_data = np.sum(input_data, axis=0) / input_data.shape[0]
    input_data = input_data - np.mean(input_data)
    input_data = tu.normalize_image(input_data)

    original_shape = 4096
    bin_shape = 512
    ratio = original_shape / bin_shape
    assert ratio.is_integer()
    ratio = int(ratio)
    pad_x = original_shape - input_data.shape[0]
    pad_y = original_shape - input_data.shape[1]

    input_data = np.pad(input_data, ((0, pad_x), (0, pad_y)), mode='median')
    shape = (bin_shape, bin_shape)
    output_data = tu.rebin(input_data, shape)[:-int(1+pad_x//ratio), :-int(1+pad_y//ratio)]
    arr_1 = output_data

    tile_overlap = 512 / 2
    tile_shape = 512
    tile_ratio = original_shape / tile_overlap
    assert tile_ratio.is_integer()
    tile_ratio = int(tile_ratio)
    tile_images = []
    for x_val in range(tile_ratio):
        if (x_val+1)*tile_shape > original_shape:
            continue
        for y_val in range(tile_ratio):
            if (y_val+1)*tile_shape > original_shape:
                continue
            slices = (
                slice(x_val*tile_shape, (x_val+1)*tile_shape, 1),
                slice(y_val*tile_shape, (y_val+1)*tile_shape, 1),
                )
            pw = np.abs(np.fft.fftshift(np.fft.fft2(input_data[slices])))**2
            tile_images.append(pw)
    if tile_images:
        arr_2 = np.sum(np.array(tile_images) / len(tile_images), axis=0)
        arr_2 = tu.rebin(arr_2, shape)
        arr_2 = tu.normalize_image(arr_2, apix=float(settings[settings['Copy']['Motion']]['-PixSize']), real=False)
    if arr_1 is not None:
        mi.imsave(jpg_file_1, arr_1, cmap='gist_gray')
    if arr_2 is not None:
        mi.imsave(jpg_file_2, arr_2, cmap='gist_gray')
