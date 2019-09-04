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
import glob
import shutil
import numpy as np
import matplotlib
matplotlib.use('qt5agg')
import matplotlib.pyplot as plt
import matplotlib.image as img
from transphire import transphire_utils as tu
from transphire import transphire_plot as tp

def get_extract_command(file_sum, file_box, file_ctf, output_dir, settings, queue_com, name):
    """
    Create the ctf command based on the ctf software.

    file_input - Input name of the file for ctf estimation
    new_name - Output file
    settings - TranSPHIRE settings
    queue_com - Queue for communication
    name - Name of process

    Returns:
    CTF command
    File to check vor validation if the process was successful
    """
    extract_name = settings['Copy']['Extract']
    command = None
    block_gpu = None
    gpu_list = None
    shell = None
    if 'WINDOW' in extract_name:
        if tu.is_higher_version(extract_name, '1.2'):
            command = create_window_1_2_command(
                extract_name=extract_name,
                file_sum=file_sum,
                file_box=file_box,
                file_ctf=file_ctf,
                output_dir=output_dir,
                settings=settings
                )
            check_files = []
            block_gpu = False
            gpu_list = []
            shell = True

    else:
        message = '\n'.join([
            '{0}: Not known!'.format(settings['Copy']['CTF']),
            'Please contact the TranSPHIRE authors!'
            ])
        queue_com['error'].put(
            message,
            name
            )
        IOError(message)

    assert command is not None, 'command not specified: {0}'.format(extract_name)
    assert block_gpu is not None, 'block_gpu not specified: {0}'.format(extract_name)
    assert gpu_list is not None, 'gpu_list not specified: {0}'.format(extract_name)
    assert shell is not None, 'shell not specified: {0}'.format(extract_name)

    return command, check_files, block_gpu, gpu_list, shell


def create_window_1_2_command(extract_name, file_sum, file_box, file_ctf, output_dir, settings):
    """Create the WINDOW v1.2 command"""

    try:
        shutil.rmtree(output_dir)
    except FileNotFoundError:
        pass

    command = []
    # Add SPHIRE to the PATH
    command.append("PATH=$(dirname $(head $(which {0}) -n 1 | cut -c 3-) | sed 's/ //g'):${{PATH}}".format(settings['Path'][extract_name]))
    # Start the program
    if settings['General']['Rename micrographs'] == 'True':
        mic_number = tp.get_mic_number([file_sum], settings, as_int=False)
    else:
        mic_number = [tu.get_name(file_sum)]
    command.append(settings['Path'][extract_name])
    command.append("'{0}'".format(file_sum.replace(mic_number[0], '*')))
    command.append("'{0}'".format(file_box.replace(mic_number[0], '*')))
    command.append(file_ctf)
    command.append(output_dir)
    command.append('--selection_list={0}'.format(file_sum))
    ignore_list = []
    ignore_list.append('--skip_invert')
    ignore_list.append('--limit_ctf')
    ignore_list.append('--check_consistency')
    for entry in ignore_list:
        if settings[extract_name][entry] == 'True':
            command.append(entry)

    for key in settings[extract_name]:
        if key in ignore_list:
            continue
        elif settings[extract_name][key]:
            command.append('{0}={1}'.format(key, settings[extract_name][key]))
        else:
            continue

    command.append(';')
    command.append('mkdir -p {0}'.format(os.path.join(output_dir, 'png')))
    command.append(';')
    command.append(settings['Path']['e2proc2d.py'])
    file_name = os.path.basename(output_dir)
    command.append(os.path.join(output_dir, '{0}_ptcls.mrcs'.format(file_name)))
    command.append(os.path.join(output_dir, 'png', '{0}.png').format(file_name))
    command.append('--unstack')
    return ' '.join(command)


def find_logfiles(root_path, settings, queue_com, name):
    """
    Find logfiles related to the produced Extract files.

    root_path - Root path of the file
    settings - TranSPHIRE settings
    queue_com - Queue for communication
    name - Name of process

    Returns:
    list of log files
    """
    log_files = None
    copied_log_files = None
    extract_name = settings['Copy']['Extract']
    if 'WINDOW' in extract_name:
        if tu.is_higher_version(extract_name, '1.2'):
            copied_log_files = []
            recursive_file_search(directory=root_path, files=copied_log_files)
            log_files = copied_log_files
    else:
        message = '\n'.join([
            '{0}: Not known!'.format(settings['Copy']['Extract']),
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


def recursive_file_search(directory, files):
    """
    Recursive file search function.
    """
    file_names = glob.glob('{0}*'.format(directory))
    for name in file_names:
        if os.path.isdir(name):
            recursive_file_search('{0}/'.format(name), files)
        else:
            files.append(name)


def create_jpg_file(file_name, output_dir):
    files = sorted(glob.glob(os.path.join(output_dir, file_name, 'png', '*')))
    if len(files) == 0:
        return None
    columns = np.sqrt(2*len(files))
    columns = int(columns+bool(columns % 2))
    columns += bool(columns % 2)
    rows = int(len(files) / columns + 0.5)

    if columns * rows < len(files):
        rows += 1
    image = img.imread(files[0])
    dpi = 600
    width = image.shape[0] * columns / dpi
    height = image.shape[1] * rows / dpi

    for idx, img_file in enumerate(files):
        ax = plt.subplot(rows, columns, idx+1, aspect='equal', frameon=False, adjustable='box')
        ax.imshow(img.imread(img_file), cmap='Greys_r')
        ax.axis('off')

    fig = plt.gcf()
    fig.set_size_inches(width, height)
    aspect = width / height
    plt.subplots_adjust(wspace=0.05, hspace=0.05/aspect, top=1, bottom=0, left=0, right=1)
    tu.mkdir_p(os.path.join(output_dir, 'jpg'))
    plt.savefig(os.path.join(output_dir, 'jpg', '{0}.jpg'.format(file_name)), dpi=dpi, transparent=True, edgecolor=None) 
    plt.clf()
