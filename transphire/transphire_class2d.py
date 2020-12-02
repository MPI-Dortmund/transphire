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
import glob
import shutil
import matplotlib
matplotlib.use('qt5agg')
import matplotlib.pyplot as plt
import matplotlib.image as img

from . import transphire_utils as tu

def create_stack_combine_command(class2d_name, file_names, file_name, output_dir, settings, queue_com, name):
    """
    Create the command to combine BDB stacks.
    """

    command = None
    block_gpu = None
    gpu_list = None
    shell = None
    stack = None
    if 'ISAC2' in class2d_name:
        if tu.is_higher_version(class2d_name, '1.2'):
            command, stack = create_isac2_1_2_combine_command(
                class2d_name=class2d_name,
                file_names=file_names,
                file_name=file_name,
                output_dir=output_dir,
                settings=settings,
                )
            check_files = []
            block_gpu = True
            gpu_list = []
            shell = False
    else:
        message = '\n'.join([
            '{0}: Not known!'.format(settings['Copy']['Class2d']),
            'Please contact the TranSPHIRE authors!'
            ])
        queue_com['error'].put(
            message,
            name
            )
        IOError(message)

    assert command is not None, 'command not specified: {0}'.format(class2d_name)
    assert block_gpu is not None, 'block_gpu not specified: {0}'.format(class2d_name)
    assert gpu_list is not None, 'gpu_list not specified: {0}'.format(class2d_name)
    assert shell is not None, 'shell not specified: {0}'.format(class2d_name)
    assert stack is not None, 'stack not specified: {0}'.format(class2d_name)

    return command, check_files, block_gpu, gpu_list, shell, stack


def create_isac2_1_2_combine_command(class2d_name, file_names, file_name, output_dir, settings):
    """
    Create e2bdb.py combine command
    """
    try:
        shutil.rmtree(os.path.join(output_dir, file_name))
    except FileNotFoundError:
        pass
    file_names = [
        entry
        if not entry.endswith('.bdb')
        else
        'bdb:{0}'.format(entry.replace('EMAN2DB/', '').replace('.bdb', ''))
        for entry in file_names
        ]
    output_name = os.path.join(output_dir, file_name, file_name)
    command = []
    command.append(settings['Path']['e2bdb.py'])
    command.append(' '.join(file_names))
    command.append('--makevstack=bdb:{0}'.format(output_name))
    return ' '.join(command), 'bdb:{0}'.format(output_name)


def create_class2d_command(class2d_name, stack_name, file_name, output_dir, settings, queue_com, name):
    """
    Create the command to combine BDB stacks.
    """

    command = None
    block_gpu = None
    gpu_list = None
    shell = None
    if 'ISAC2' in class2d_name:
        if tu.is_higher_version(class2d_name, '1.2'):
            command, gpu, check_file = create_isac2_1_2_command(
                class2d_name=class2d_name,
                stack_name=stack_name,
                file_name=file_name,
                output_dir=output_dir,
                settings=settings,
                name=name,
                )
            check_files = [check_file]
            block_gpu = True
            gpu_list = gpu.split()
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

    assert command is not None, 'command not specified: {0}'.format(class2d_name)
    assert block_gpu is not None, 'block_gpu not specified: {0}'.format(class2d_name)
    assert gpu_list is not None, 'gpu_list not specified: {0}'.format(class2d_name)
    assert shell is not None, 'shell not specified: {0}'.format(class2d_name)

    return command, check_files, block_gpu, gpu_list, shell


def create_isac2_1_2_command(class2d_name, stack_name, file_name, output_dir, settings, name):
    """
    Create e2bdb.py combine command
    """
    isac_output_dir = os.path.join(output_dir, file_name, 'ISAC2')
    try:
        shutil.rmtree(isac_output_dir)
    except FileNotFoundError:
        pass

    ignore_list = []
    if settings[class2d_name]['Split Gpu?'] == 'True':
        try:
            gpu_id = int(name.split('_')[-1])
        except ValueError:
            gpu_id = 0
        try:
            gpu_raw = settings[class2d_name]['--gpu_devices'].split()[gpu_id]
        except IndexError:
            raise UserWarning('There are less gpus provided than threads available! Please restart with the same number of pipeline processors as GPUs provided and restart! Stopping this thread!')
    else:
        gpu_raw = settings[class2d_name]['--gpu_devices']

    gpu = ' '.join(list(set([entry.split('_')[0] for entry in gpu_raw.split()])))
    if len(gpu.split()) != len(gpu_raw.split()) and settings[class2d_name]['Split Gpu?'] == 'False':
        raise UserWarning('One cannot use multi GPU in combination with the disabled Split GPU option!')

    command = []

    command.append("PATH=$(dirname $(which {0})):${{PATH}}".format(settings['Path'][class2d_name]))
    command.append('CUDA_VISIBLE_DEVICES={0}'.format(','.join(gpu.split())))
    command.append(settings['Path']['mpirun'])
    command.append('-np {0}'.format(settings[class2d_name]['MPI processes']))
    command.append(settings['Path'][class2d_name])
    command.append(stack_name)
    command.append(isac_output_dir)

    ignore_list.append('--CTF')
    ignore_list.append('--VPP')
    if settings[class2d_name]['--CTF'] == 'True' and settings[class2d_name]['--VPP'] == 'True':
        command.append('--VPP')
    else:
        for entry in ignore_list:
            if settings[class2d_name][entry] == 'True':
                command.append(entry)

    ignore_list.append('Nr. Particles')
    ignore_list.append('MPI processes')
    ignore_list.append('Split Gpu?')
    ignore_list.append('--gpu_devices')
    command.append('--gpu_devices={0}'.format(','.join(gpu.split())))

    for key in settings[class2d_name]:
        if key in ignore_list:
            continue
        else:
            command.append(key)
            command.append(
                '{0}'.format(settings[class2d_name][key])
                )

    command.append(';')
    command.append('mkdir -p {0}'.format(os.path.join(output_dir, file_name, 'png')))
    command.append(';')
    command.append("PATH=$(dirname $(which {0})):${{PATH}}".format(settings['Path']['e2proc2d.py']))
    command.append(settings['Path']['e2proc2d.py'])
    command.append(os.path.join(isac_output_dir, 'ordered_class_averages.hdf'))
    command.append(os.path.join(output_dir, file_name, 'png', 'ordered_class_averages.hdf.png'))
    command.append('--unstacking')
    command.append('--outmode=uint16')
    check_file = os.path.join(isac_output_dir, 'ordered_class_averages.hdf')
    return ' '.join(command), gpu, check_file


@tu.rerun_function_in_case_of_error
def create_jpg_file(file_name, output_dir):
    files = sorted(glob.glob(os.path.join(output_dir, file_name, 'png', '*')))
    dpi = 300
    if len(files) == 0:
        columns = 1
        rows = 1
        width = 1
        height = 1
    else:
        columns = np.sqrt(2*len(files))
        columns = int(columns+bool(columns % 2))
        columns += bool(columns % 2)
        rows = int(len(files) / columns + 1)

        if columns * rows < len(files):
            rows += 1
        image = img.imread(files[0])
        width = image.shape[0] * columns / dpi
        height = image.shape[1] * rows / dpi

    fig, ax = plt.subplots(rows, columns, subplot_kw={'frameon':False, 'adjustable': 'box', 'aspect': 'equal'})
    ax = np.atleast_1d(ax).ravel()
    for idx, ax_instance in enumerate(ax):
        try:
            ax_instance.imshow(img.imread(files[idx]), cmap='Greys_r')
        except IndexError:
            pass
        ax_instance.axis('off')

    fig.set_size_inches(width, height)
    aspect = width / height
    plt.subplots_adjust(wspace=0.05, hspace=0.05/aspect, top=1, bottom=0, left=0, right=1)
    tu.mkdir_p(os.path.join(output_dir, 'jpg'))
    plt.savefig(os.path.join(output_dir, 'jpg', '{0}.jpg'.format(file_name)), dpi=dpi, transparent=True, edgecolor=None) 
    plt.close(fig)


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
    extract_name = settings['Copy']['Class2d']
    if 'ISAC2' in extract_name:
        if tu.is_higher_version(extract_name, '1.2'):
            copied_log_files = []
            recursive_file_search(directory=root_path, files=copied_log_files)
            log_files = copied_log_files
    else:
        message = '\n'.join([
            '{0}: Not known!'.format(settings['Copy']['Class2d']),
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
