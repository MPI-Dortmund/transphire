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

import re
import shutil
import os

from . import transphire_utils as tu


def create_substack_command(class_average_name, input_stack, isac_dir, output_dir, settings):
    command = []
    block_gpu = False
    gpu_list = []
    shell = True
    check_files = []
    gpu_list = []

    try:
        shutil.rmtree(output_dir)
    except IOError:
        pass

    command.append("PATH=$(dirname $(which {0})):${{PATH}}".format(settings['Path']['sp_pipe.py']))
    command.append(settings['Path']['sp_pipe.py'])
    command.append('isac_substack')
    command.append(input_stack)
    command.append(os.path.join(isac_dir, 'ISAC2'))
    command.append(os.path.join(output_dir, 'STACK'))
    command.append('--isac_class_avgs_path={0}'.format(class_average_name))

    #picking_name = settings['Copy']['Picking']
    #if settings[picking_name]['--filament'] == 'True':
    #    command.append('--min_nr_segments={0}'.format(settings[picking_name]['--minimum_number_boxes']))

    return ' '.join(command), check_files, block_gpu, gpu_list, shell, 'bdb:{0}/{1}'.format(os.path.join(output_dir, 'STACK'), 'isac_substack')


def create_restack_command(stack_name, output_dir, settings):
    prog_name = settings['Copy']['Train2d']
    command = []
    block_gpu = False
    gpu_list = []
    shell = True
    check_files = []
    gpu_list = []

    command.append("PATH=$(dirname $(which {0})):${{PATH}}".format(settings['Path']['sp_pipe.py']))
    command.append(settings['Path']['sp_pipe.py'])
    command.append('restacking')
    command.append(stack_name)
    command.append(os.path.join(output_dir, 'BOX'))
    command.append('--rb_box_size={0}'.format(settings[prog_name]['Box size']))
    command.append('--reboxing')

    return ' '.join(command), check_files, block_gpu, gpu_list, shell, os.path.join(output_dir, 'BOX')


def create_eval_command(config_file, weight_file, log_file, settings, name):
    prog_name = settings['Path']['cryolo_evaluation.py']
    command = []
    block_gpu = False
    gpu_list = []
    shell = False
    check_files = []
    gpu_list = []

    with open(log_file, 'r') as read:
        match = re.search('^.*Wrote runfile to: (.*)$', read.read(), re.M) # https://regex101.com/r/BY0m3B/1

    if match is None:
        return None, check_files, block_gpu, gpu_list, shell

    command.append(prog_name)
    command.append('--config={0}'.format(config_file))
    command.append('--weights={0}'.format(weight_file))
    command.append('--runfile={0}'.format(match.group(1).strip()))

    prog_name_train = settings['Copy']['Train2d']
    if settings[prog_name_train]['Split Gpu?'] == 'True':
        try:
            gpu_id = int(name.split('_')[-1])-1
        except ValueError:
            gpu_id = 0
        try:
            gpu = settings[prog_name_train]['--gpu'].split()[gpu_id]
        except IndexError:
            raise UserWarning('There are less gpus provided than threads available! Please restart with the same number of pipeline processors as GPUs provided and restart! Stopping this thread!')
    else:
        gpu = settings[prog_name_train]['--gpu']
    command.append('--gpu={0}'.format(gpu))

    return ' '.join(command), check_files, block_gpu, gpu.split(), shell


def create_train_command(sum_folder, box_folder, output_dir, name, settings):
    prog_name = settings['Copy']['Train2d']
    picking_name = settings['Copy']['Picking']
    command = []
    block_gpu = False
    shell = True
    check_files = []

    config_file = os.path.join(output_dir, 'config.json')
    weight_file = os.path.join(output_dir, 'weight.h5')

    command.append("PATH=$(dirname $(which {0})):${{PATH}}".format(settings['Path']['cryolo_gui.py']))
    command.append(settings['Path']['cryolo_gui.py'])
    command.append('config')
    command.append(config_file)
    command.append(settings[prog_name]['Box size'])
    command.append('--train_image_folder={0}'.format(sum_folder))
    command.append('--train_annot_folder={0}'.format(box_folder))
    command.append('--saved_weights_name={0}'.format(weight_file))
    command.append('--pretrained_weights={0}'.format(settings[picking_name]['--weights_old']))
    command.append('--filtered_output={0}'.format(os.path.join(
        settings['project_folder'],
        'XXX_Filtered_Images'
        )))
    command.append('--train_times={0}'.format(settings[prog_name]['--train_times']))

    command.append(';')
    command.append("PATH=$(dirname $(which {0})):${{PATH}}".format(settings['Path'][prog_name]))
    command.append(settings['Path'][prog_name])
    command.append('-c {0}'.format(config_file))

    ignore_list = []
    ignore_list.append('--fine_tune')
    ignore_list.append('--use_multithreading')
    for entry in ignore_list:
        try:
            if settings[prog_name][entry] == 'True':
                command.append(entry)
        except KeyError:
            pass

    if tu.is_higher_version(prog_name, '1.7.4'):
        try:
            command.remove('--use_multithreading')
        except ValueError:
            pass

    ignore_list.append('Split Gpu?')
    ignore_list.append('--gpu')
    ignore_list.append('Box size')
    ignore_list.append('--train_times')
    ignore_list.append('Maximum micrographs')
    ignore_list.append('Use centered')

    if settings[prog_name]['Split Gpu?'] == 'True':
        try:
            gpu_id = int(name.split('_')[-1])-1
        except ValueError:
            gpu_id = 0
        try:
            gpu = settings[prog_name]['--gpu'].split()[gpu_id]
        except IndexError:
            raise UserWarning('There are less gpus provided than threads available! Please restart with the same number of pipeline processors as GPUs provided and restart! Stopping this thread!')
    else:
        gpu = settings[prog_name]['--gpu']

    command.append('--gpu')
    command.append('{0}'.format(gpu))

    for key in settings[prog_name]:
        if key in ignore_list:
            continue
        else:
            command.append(key)
            command.append(
                '{0}'.format(settings[prog_name][key])
                )

    return ' '.join(command), check_files, block_gpu, gpu.split(), shell, weight_file, config_file
