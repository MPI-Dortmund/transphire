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
    if picking_name == 'crYOLO v1.0.0':
        command = create_cryolo_v1_0_0_command(
            picking_name=picking_name,
            file_input=file_input,
            file_output=new_name,
            settings=settings
            )
        check_files = []
        block_gpu = True
        gpu_list = settings[picking_name]['--gpu'].split()

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
    log_files = None
    copied_log_files = None
    picking_root_path = os.path.join(settings['picking_folder'], file_name)
    if settings['Copy']['Picking'] == 'crYOLO v1.0.0':
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


def create_cryolo_v1_0_0_command(
        picking_name, file_input, file_output, settings
        ):
    """Create the Gctf v1.06 command"""

    command = []
    # Start the program
    ignore_list = []
    ignore_list.append('Filter micrographs')
    ignore_list.append('Filter value high pass (A)')
    ignore_list.append('Filter value low pass (A)')
    ignore_list.append('Pixel size (A/px)')
    if settings[picking_name]['Filter micrographs'] == 'True':

        filter_high = float(settings[picking_name]['Filter value high pass (A)'])
        filter_low = float(settings[picking_name]['Filter value low pass (A)'])
        pixel_size = float(settings[picking_name]['Pixel size (A/px)'])

        filter_high_abs = pixel_size / filter_high
        filter_low_abs = pixel_size / filter_low

        file_output_tmp = os.path.join(
                settings['picking_folder'],
                os.path.basename(file_input)
                )

        command.append('{0}'.format(settings['Path']['e2proc2d.py']))
        command.append('{0}'.format(file_input))
        command.append('{0}'.format(file_output_tmp))
        command.append('--process=filter.lowpass.gauss:cutoff_freq={0}'.format(filter_low_abs))
        command.append('--process=filter.highpass.gauss:cutoff_freq={0}'.format(filter_high_abs))
        command.append(';')
        file_input = file_output_tmp

    command.append('{0}'.format(settings['Path'][picking_name]))

    command.append('-i')
    command.append('{0}'.format(file_input))
    command.append('-o')
    command.append('{0}'.format(file_output))

    for key in settings[picking_name]:
        if key in ignore_list:
            continue
        else:
            command.append(key)
            command.append(
                '{0}'.format(settings[picking_name][key])
                )

    if settings[picking_name]['Filter micrographs'] == 'True':
        command.append(';')
        command.append('rm')
        command.append('{0}'.format(file_output_tmp))

    return ' '.join(command)

