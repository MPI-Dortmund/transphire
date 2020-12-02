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
import shutil
import glob
import os
import numpy as np
import matplotlib
matplotlib.use('qt5agg')
import matplotlib.pyplot as plt
import matplotlib.image as img

from . import transphire_utils as tu


def get_select2d_command(file_input, output_dir, settings, queue_com, name):
    """
    Create the picking command based on the picking software.

    file_input - Input name of the file for ctf estimation
    output_dir - Output file
    settings - TranSPHIRE settings
    queue_com - Queue for communication
    name - Name of process

    Returns:
    Picking command
    File to check vor validation if the process was successful
    """
    prog_name = settings['Copy']['Select2d']
    command = None
    block_gpu = None
    gpu_list = None
    shell = False
    if tu.is_higher_version(prog_name, '0.3.1'):
        command, gpu = create_cinderella_0_3_1_command(
            prog_name=prog_name,
            file_input=file_input,
            file_output=output_dir,
            settings=settings,
            name=name,
            )
        check_files = []
        block_gpu = True
        gpu_list = gpu.split()
        shell = True

    else:
        message = '\n'.join([
            '{0}: Not known!'.format(settings['Copy']['Select2d']),
            'Please contact the TranSPHIRE authors!'
            ])
        queue_com['error'].put(
            message,
            name
            )
        IOError(message)

    assert command is not None, 'command not specified: {0}'.format(prog_name)
    assert block_gpu is not None, 'block_gpu not specified: {0}'.format(prog_name)
    assert gpu_list is not None, 'gpu_list not specified: {0}'.format(prog_name)

    return command, check_files, block_gpu, gpu_list, shell


def create_cinderella_0_3_1_command(
        prog_name, file_input, file_output, settings, name
        ):
    """Create the Cinderella >=v0.3.1 command"""
    command = []
    # Start the program
    ignore_list = []
    ignore_list.append('Split Gpu?')
    ignore_list.append('--gpu')

    try:
        shutil.rmtree(file_output)
    except IOError:
        pass

    command.append('{0}'.format(settings['Path'][prog_name]))

    command.append('--input')
    command.append(os.path.join(file_input, 'ISAC2', 'ordered_class_averages.hdf'))
    command.append('--output')
    command.append(file_output)

    if settings[prog_name]['Split Gpu?'] == 'True':
        try:
            gpu_id = int(name.split('_')[-1])
        except ValueError:
            gpu_id = 0
        try:
            gpu_raw = settings[prog_name]['--gpu'].split()[gpu_id]
        except IndexError:
            raise UserWarning('There are less gpus provided than threads available! Please restart with the same number of pipeline processors as GPUs provided and restart! Stopping this thread!')
    else:
        gpu_raw = settings[prog_name]['--gpu']

    gpu = ' '.join(list(set([entry.split('_')[0] for entry in gpu_raw.split()])))
    if len(gpu.split()) != len(gpu_raw.split()) and settings[prog_name]['Split Gpu?'] == 'False':
        raise UserWarning('One cannot use multi GPU in combination with the disabled Split GPU option!')

    command.append('--gpu')
    command.append('{0}'.format(gpu))

    for key, value in settings[prog_name].items():
        if key in ignore_list:
            continue
        elif value:
            try:
                if '|||' in value:
                    external_log, local_key = value.split('|||')
                    with open(settings[external_log], 'r') as read:
                        log_data = json.load(read)
                    try:
                        set_value = log_data[settings['current_set']][prog_name][local_key]['new_file']
                    except KeyError:
                        continue
                else:
                    set_value = value
            except TypeError:
                set_value = value
            command.append(key)
            command.append('{0}'.format(set_value))
    command.append(';')

    command.append('echo Bad Particles')
    command.append(';')
    command.append("a=$(PATH=$(dirname $(which {0})):${{PATH}}".format(settings['Path']['sp_header.py']))
    command.append(settings['Path']['sp_header.py'])
    command.append(os.path.join(file_output, 'ordered_class_averages_bad.hdf'))
    command.append('--params n_objects')
    command.append('--print')
    command.append('|')
    command.append('paste -sd+ -')
    command.append('|')
    command.append('bc)')
    command.append(';')
    command.append('echo $(( a > 0 ? a : 0))')
    command.append(';')

    command.append('echo Good Particles')
    command.append(';')
    command.append("a=$(PATH=$(dirname $(which {0})):${{PATH}}".format(settings['Path']['sp_header.py']))
    command.append(settings['Path']['sp_header.py'])
    command.append(os.path.join(file_output, 'ordered_class_averages_good.hdf'))
    command.append('--params n_objects')
    command.append('--print')
    command.append('|')
    command.append('paste -sd+ -')
    command.append('|')
    command.append('bc)')
    command.append(';')
    command.append('echo $(( a > 0 ? a : 0))')
    command.append(';')

    command.append('mkdir -p {0}'.format(os.path.join(file_output, 'png_good')))
    command.append('mkdir -p {0}'.format(os.path.join(file_output, 'png_bad')))
    command.append(';')

    command.append("PATH=$(dirname $(which {0})):${{PATH}}".format(settings['Path']['e2proc2d.py']))
    command.append(settings['Path']['e2proc2d.py'])
    command.append(os.path.join(file_output, 'ordered_class_averages_good.hdf'))
    command.append(os.path.join(file_output, 'png_good', 'ordered_class_averages_good.hdf.png'))
    command.append('--unstacking')
    command.append('--outmode=uint16')
    command.append(';')

    command.append("PATH=$(dirname $(which {0})):${{PATH}}".format(settings['Path']['e2proc2d.py']))
    command.append(settings['Path']['e2proc2d.py'])
    command.append(os.path.join(file_output, 'ordered_class_averages_bad.hdf'))
    command.append(os.path.join(file_output, 'png_bad', 'ordered_class_averages_bad.hdf.png'))
    command.append('--unstacking')
    command.append('--outmode=uint16')

    return ' '.join(command), gpu_raw


def find_logfiles(root_path, settings, queue_com, name):
    log_files = None
    copied_log_files = None
    extract_name = settings['Copy']['Select2d']
    if 'Cinderella' in extract_name:
        if tu.is_higher_version(extract_name, '0.3.1'):
            copied_log_files = []
            copied_log_files.append(os.path.join(root_path, 'ordered_class_averages_good.hdf'))
            copied_log_files.append(os.path.join(root_path, 'ordered_class_averages_bad.hdf'))
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


@tu.rerun_function_in_case_of_error
def create_jpg_file(file_name, output_dir):
    for png_idx, folder_name in enumerate(sorted(glob.glob(os.path.join(output_dir, file_name, 'png*')))):
        files = sorted(glob.glob(os.path.join(folder_name, '*')))
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
        suffix = os.path.basename(folder_name).split('_')[1]
        tu.mkdir_p(os.path.join(output_dir, 'jpg_{0}'.format(png_idx)))
        plt.savefig(
            os.path.join(
                output_dir,
                'jpg_{0}'.format(png_idx),
                '{0}_{1}.jpg'.format(file_name, suffix)
                ),
            dpi=dpi,
            transparent=True,
            edgecolor=None
            ) 
        plt.close(fig)
