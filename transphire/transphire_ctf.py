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

import glob
import os
import shutil
import numpy as np
import mrcfile as mrc
import matplotlib.image as mi
import matplotlib.pyplot as plt
from transphire import transphire_import as ti
from transphire import transphire_utils as tu


def get_ctf_command(file_sum, file_input, new_name, settings, queue_com, name):
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
    ctf_name = settings['Copy']['CTF']
    command = None
    block_gpu = None
    gpu_list = None
    shell = None
    if ctf_name == 'CTFFIND4 v4.1.8' or \
            ctf_name == 'CTFFIND4 v4.1.10':
        command = create_ctffind_4_v4_1_8_command(
            ctf_name = ctf_name,
            file_sum=file_sum,
            file_input=file_input,
            file_output=new_name,
            settings=settings
            )
        check_files = []
        block_gpu = False
        gpu_list = []
        shell = True

    elif ctf_name == 'Gctf v1.06' or \
            ctf_name == 'Gctf v1.18':
        command, gpu = create_gctf_v1_06_command(
            ctf_name=ctf_name,
            file_sum=file_sum,
            file_input=file_input,
            file_output=new_name,
            settings=settings,
            name=name
            )
        check_files = ['{0}_gctf.star'.format(new_name)]
        if ctf_name == 'Gctf v1.06':
            block_gpu = False
        elif ctf_name == 'Gctf v1.18':
            block_gpu = True
        else:
            assert False
        gpu_list = gpu.split()
        shell = False

    elif ctf_name == 'CTER v1.0':
        output_dir, _ = os.path.splitext(new_name)
        command = create_cter_1_0_command(
            ctf_name=ctf_name,
            file_sum=file_sum,
            file_input=file_input,
            output_dir=output_dir,
            settings=settings
            )
        check_files = ['{0}/partres.txt'.format(output_dir)]
        block_gpu = False
        gpu_list = []
        shell = False

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

    assert command is not None, 'command not specified: {0}'.format(ctf_name)
    assert block_gpu is not None, 'block_gpu not specified: {0}'.format(ctf_name)
    assert gpu_list is not None, 'gpu_list not specified: {0}'.format(ctf_name)
    assert shell is not None, 'shell not specified: {0}'.format(ctf_name)

    return command, check_files, block_gpu, gpu_list, shell


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
    ctf_root_path = os.path.join(settings['ctf_folder'], file_name)
    if settings['Copy']['CTF'] == 'CTFFIND4 v4.1.8' or \
            settings['Copy']['CTF'] == 'CTFFIND4 v4.1.10' or \
            settings['Copy']['CTF'] == 'CTER v1.0':
        copied_log_files = []
        recursive_file_search(directory=ctf_root_path, files=copied_log_files)
        log_files = copied_log_files

    elif settings['Copy']['CTF'] == 'Gctf v1.18' or \
            settings['Copy']['CTF'] == 'Gctf v1.06':
        log_files = []
        copied_log_files = []
        exclude_list = [
            '{0}.mrc'.format(root_path),
            '{0}_DW.mrc'.format(root_path),
            '{0}.log'.format(root_path),
            '{0}.err'.format(root_path),
            ]
        for log_file in glob.glob('{0}*'.format(root_path)):
            if log_file in exclude_list:
                continue
            else:
                pass

            new_file = os.path.join(
                settings['ctf_folder'],
                os.path.basename(log_file)
                )
            log_files.append(log_file)
            copied_log_files.append(new_file)

    else:
        message = '\n'.join([
            '{0}: Not known!'.format(settings['Copy']['CTF']),
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


def create_gctf_v1_06_command(
        ctf_name, file_sum, file_input, file_output, settings, name
        ):
    """Create the Gctf v1.06 command"""

    ignore_list = []
    ignore_list.append('Use movies')
    ignore_list.append('Phase plate')
    command = []
    # Start the program
    command.append('{0}'.format(settings['Path'][ctf_name]))
    if settings[ctf_name]['Phase plate'] == 'False':
        ignore_list.append('--phase_shift_L')
        ignore_list.append('--phase_shift_H')
        ignore_list.append('--phase_shift_S')
        ignore_list.append('--phase_shift_T')
        ignore_list.append('--only_search_ps')
        ignore_list.append('--cosearch_refine_ps')
    else:
        pass
    if settings[ctf_name]['Use movies'] == 'False':
        ignore_list.append('--do_mdef_refine')
        ignore_list.append('--mdef_ave_type')
        ignore_list.append('--mdef_aveN')
        ignore_list.append('--mdef_fit')
        file_input = file_sum
    else:
        pass

    ignore_list.append('Split Gpu?')
    ignore_list.append('--gid')
    if settings[ctf_name]['Split Gpu?'] == 'True':
        try:
            gpu_id = int(name.split('_')[-1])-1
        except ValueError:
            gpu_id = 0
        try:
            gpu = settings[ctf_name]['--gid'].split()[gpu_id]
        except IndexError:
            raise UserWarning('There are less gpus provided than threads available! Please restart with the same number of pipeline processors as GPUs provided and restart! Stopping this thread!')
    else:
        gpu = settings[ctf_name]['--gid']

    command.append('--gid')
    command.append('{0}'.format(gpu))

    command.append('--ctfstar')
    command.append('{0}_gctf.star'.format(file_output))

    for key in settings[ctf_name]:
        if key in ignore_list:
            continue
        elif settings[ctf_name][key]:
            command.append(key)
            command.append(
                '{0}'.format(settings[ctf_name][key])
                )
        else:
            continue

    command.append('{0}'.format(file_input))

    return ' '.join(command), gpu


def create_cter_1_0_command(
        ctf_name, file_sum, file_input, output_dir, settings
        ):
    """Create the CTER v1.0 command"""

    try:
        shutil.rmtree(output_dir)
    except FileNotFoundError:
        pass

    command = []
    # Start the program
    command.append('{0}'.format(settings['Path'][ctf_name]))
    command.append("{0}*".format(file_sum[:-1]))
    command.append(output_dir)
    command.append('--selection_list={0}'.format(file_sum))
    ignore_list = []
    ignore_list.append('Phase plate')
    if settings[ctf_name]['Phase plate'] == 'False':
        ignore_list.append('--defocus_min')
        ignore_list.append('--defocus_max')
        ignore_list.append('--defocus_step')
        ignore_list.append('--phase_min')
        ignore_list.append('--phase_max')
        ignore_list.append('--phase_step')
    else:
        command.append('--vpp')

    ignore_list.append('--pap')
    if settings[ctf_name]['--pap'] == 'True':
        command.append('--pap')
    else:
        pass

    for key in settings[ctf_name]:
        if key in ignore_list:
            continue
        elif settings[ctf_name][key]:
            command.append('{0}={1}'.format(key, settings[ctf_name][key]))
        else:
            continue

    return ' '.join(command)

def create_ctffind_4_v4_1_8_command(ctf_name, file_sum, file_input, file_output, settings):
    """Create the ctffind command"""
    ctf_settings = settings[ctf_name]
    ctffind_command = []
    if ctf_settings['Use movies'] == 'True':
        pass
    else:
        file_input = file_sum
    # Input file
    ctffind_command.append('{0}'.format(file_input))
    # Is movie
    if ctf_settings['Use movies'] == 'True':
        ctffind_command.append('{0}'.format('yes'))
        ctffind_command.append('{0}'.format(ctf_settings['Combine frames']))
    else:
        pass
    # Output file
    ctffind_command.append('{0}'.format(file_output))
    # Pixel size
    ctffind_command.append('{0}'.format(ctf_settings['Pixel size']))
    # Acceleration voltage
    ctffind_command.append('{0}'.format(ctf_settings['Acceleration voltage']))
    # Spherical abberation
    ctffind_command.append('{0}'.format(ctf_settings['Spherical aberration']))
    # Amplitude contrast
    ctffind_command.append('{0}'.format(ctf_settings['Amplitude contrast']))
    # Amplitude spectrum
    ctffind_command.append('{0}'.format(ctf_settings['Amplitude spectrum']))
    # Minimum resolution
    ctffind_command.append('{0}'.format(ctf_settings['Min resolution(A)']))
    # Maximum resolution
    ctffind_command.append('{0}'.format(ctf_settings['Max resolution(A)']))
    # Minimum defocus
    ctffind_command.append('{0}'.format(ctf_settings['Min defocus(A)']))
    # Maximum defocus
    ctffind_command.append('{0}'.format(ctf_settings['Max defocus(A)']))
    # Defocus step
    ctffind_command.append('{0}'.format(ctf_settings['Step defocus(A)']))
    # Do you know astigmatism
    if ctf_settings['Know astigmatism'] == 'True':
        ctffind_command.append('{0}'.format('yes'))
    else:
        ctffind_command.append('{0}'.format('no'))
    # Slow or fast
    if ctf_settings['High accuracy'] == 'True':
        ctffind_command.append('{0}'.format('yes'))
    else:
        ctffind_command.append('{0}'.format('no'))
    # Astigmatism ctf_settings
    if ctf_settings['Know astigmatism'] == 'True':
        ctffind_command.append('{0}'.format(ctf_settings['Astigmatism']))
        ctffind_command.append('{0}'.format(ctf_settings['Astigmatism angle']))
    else:
        if ctf_settings['Restrain astigmatism'] == 'True':
            ctffind_command.append('{0}'.format('yes'))
            ctffind_command.append(
                '{0}'.format(ctf_settings['Expected astigmatism'])
                )
        else:
            ctffind_command.append('{0}'.format('no'))
    # Phase shift
    if ctf_settings['Phase shift'] == 'True':
        ctffind_command.append('{0}'.format('yes'))
        ctffind_command.append('{0}'.format(ctf_settings['Min phase(rad)']))
        ctffind_command.append('{0}'.format(ctf_settings['Max phase(rad)']))
        ctffind_command.append('{0}'.format(ctf_settings['Step phase(rad)']))
    else:
        ctffind_command.append('{0}'.format('no'))
    # Expert ctf_settings
    ctffind_command.append('{0}'.format('yes'))
    # Resmaple micrograph
    if ctf_settings['Resample micrographs'] == 'True':
        ctffind_command.append('{0}'.format('yes'))
    else:
        ctffind_command.append('{0}'.format('no'))
    # Movie input ctf_settings
    if ctf_settings['Use movies'] == 'True':
        # Gain correction
        if ctf_settings['Movie is gain-corrected?'] == 'True':
            ctffind_command.append('{0}'.format('yes'))
        else:
            ctffind_command.append('{0}'.format('no'))
            ctffind_command.append('{0}'.format(ctf_settings['Gain file']))
        # Correct for magnifying distortions
        if ctf_settings['Correct mag. distort.'] == 'True':
            ctffind_command.append('{0}'.format('yes'))
            ctffind_command.append(
                '{0}'.format(ctf_settings['Mag. dist. angle'])
                )
            ctffind_command.append(
                '{0}'.format(ctf_settings['Mag. dist. major scale'])
                )
            ctffind_command.append(
                '{0}'.format(ctf_settings['Mag. dist. minor scale'])
                )
        else:
            ctffind_command.append('{0}'.format('no'))

    else:
        pass

    command = 'echo "{0}" | {1}'.format(
        '\n'.join(ctffind_command),
        settings['Path'][ctf_name]
        )
    return command


def combine_ctf_outputs(
        data,
        data_orig,
        root_path,
        file_name,
        settings,
        queue_com,
        shared_dict,
        name,
        sum_file,
        dw_file,
        ):
    """
    Combine the ctf outputs to one SPHIRE partres and one RELION star file.

    root_path - Root path of the file
    file_name - File name of the ctf file.
    settings - TranSPHIRE settings
    queue_com - Queue for communication
    name - Name of process
    sum_file - Name of the dose uncorrected sum file

    Returns:
    None
    """

    ctf_name = settings['Copy']['CTF']
    ctf_settings = settings[ctf_name]
    ctf_folder = settings['ctf_folder']
    project_folder = '{0}/'.format(settings['project_folder'])

    if ctf_name.lower().startswith('cter'):
        data_star = data
    else:
        data_star = data_orig

    lines = to_star_file(
        data=np.copy(data_star),
        ctf_name=ctf_name,
        ctf_settings=ctf_settings,
        project_folder=project_folder,
        ctf_folder=ctf_folder,
        sum_file=sum_file,
        dw_file=dw_file,
        )
    output_name_star = os.path.join(
        ctf_folder,
        '{0}_transphire_ctf.star'.format(os.path.basename(sum_file))
        )

    with open(output_name_star, 'w') as write:
        write.write(lines)

    lines = to_partres_file(
        data=np.copy(data_orig),
        ctf_name=ctf_name,
        ctf_settings=ctf_settings,
        project_folder=project_folder,
        ctf_folder=ctf_folder,
        sum_file=sum_file,
        )
    output_name_partres = os.path.join(
        ctf_folder,
        '{0}_transphire_ctf_partres.txt'.format(os.path.basename(sum_file))
        )

    with open(output_name_partres, 'w') as write:
        write.write(lines)

    output_name_partres_combined = os.path.join(
        project_folder,
        '{0}_transphire_ctf_partres.txt'.format(ctf_name.replace(' ', '_'))
        )
    output_name_star_combined = os.path.join(
        project_folder,
        '{0}_transphire_ctf.star'.format(ctf_name.replace(' ', '_'))
        )
    return output_name_partres_combined, output_name_star_combined


def to_star_file(data, ctf_name, ctf_settings, project_folder, ctf_folder, sum_file, dw_file):
    """
    Create a CTF star file from data

    data - Array containing ctf information.
    ctf_name - Name of the ctf program.
    ctf_settings - Settings for this ctf estimation run.
    project_folder - Name of the project folder.
    ctf_folder - Name of the ctf output folder.
    sum_file - Name of the sum file

    Returns:
    None
    """
    export_dtype = data.dtype.descr
    extension_dtype = [
        ('_rlnCtfImage', '|U1200'),
        ('_rlnVoltage', '<f8'),
        ('_rlnSphericalAberration', '<f8'),
        ('_rlnAmplitudeContrast', '<f8'),
        ('_rlnMagnification', '<f8'),
        ('_rlnDetectorPixelSize', '<f8'),
        ]

    export_dtype.extend(extension_dtype)
    if dw_file == 'None':
        pass
    else:
        export_dtype.extend([('_rlnMicrographNameNoDW', '|U1200')])
    export_data = np.atleast_1d(np.empty(data.shape[0], dtype=export_dtype))
    header = get_relion_header(names=export_data.dtype.names)

    for idx, row in enumerate(data):

        for name in row.dtype.names:

            if name == 'file_name':
                if dw_file == 'None':
                    export_data[idx]['file_name'] = sum_file.replace(project_folder, '')
                else:
                    export_data[idx]['_rlnMicrographNameNoDW'] = sum_file.replace(project_folder, '')
                    export_data[idx]['file_name'] = dw_file.replace(project_folder, '')
                continue

            elif name == 'defocus':
                value = (-1 * row['defocus_diff'] + 2 * row['defocus']) / 2
            elif name == 'defocus_diff':
                value = 2 * row['defocus'] - export_data[idx]['defocus']
            else:
                value = row[name]
            export_data[idx][name] = value

        for key, _ in extension_dtype:
            value = get_constant_value(key, ctf_settings, row, project_folder, ctf_name, ctf_folder)
            export_data[idx][key] = value

    lines = [header]
    maximum_string = {
        '_rlnCtfImage': len(max(export_data['_rlnCtfImage'], key=len)),
        'file_name': len(max(export_data['file_name'], key=len))
        }
    if dw_file == 'None':
        pass
    else:
        maximum_string['_rlnMicrographNameNoDW'] = len(max(export_data['_rlnMicrographNameNoDW'], key=len))
    create_export_data(
        export_data=export_data,
        lines=lines,
        maximum_string=maximum_string
        )
    return ''.join(lines)


def create_export_data(export_data, lines, maximum_string):
    """
    Write export data to file.

    export_data - Data to export.
    file_name - Name of the file to write to.

    Returns:
    In place modificaion of lines
    """
    for row in export_data:
        row_string = []
        for name in export_data.dtype.names:
            if name == 'mic_number':
                continue
            elif name == 'image':
                continue
            else:
                pass
            value = row[name]
            if isinstance(value, int):
                row_string.append('{0: 7d}'.format(value))
            elif isinstance(value, float):
                row_string.append('{0: 14f}'.format(value))
            else:
                length = maximum_string[name]
                row_string.append('{0:{1}s}'.format(value, length))
        lines.append('{0}\n'.format('\t'.join(row_string)))


def to_partres_file(data, ctf_name, ctf_settings, project_folder, ctf_folder, sum_file):
    """
    Create a CTF partres file from data

    data - Array containing ctf information.
    ctf_name - Name of the ctf program.
    ctf_settings - Settings for this ctf estimation run.
    project_folder - Name of the project folder.
    ctf_folder - Name of the ctf output folder.
    sum_file - Name of the summed micrograph image

    Returns:
    None
    """

    export_dtype = ti.get_dtype_import_dict()['CTER v1.0']
    export_data = np.atleast_1d(np.empty(data.shape[0], dtype=export_dtype))
    constant_settings = set([
        'cs',
        'volt',
        'apix',
        'const_amplitude_contrast',
        ])

    for idx, row in enumerate(data):

        for name in export_data.dtype.names:

            try:
                value = row[name] 
            except ValueError:
                # Is not a CTER partres name
                assert name != 'phase_shift'
                assert name != 'file_name'
                if name in constant_settings:
                    value = get_constant_value(name, ctf_settings, row, project_folder, ctf_name, ctf_folder)
                    if name == 'const_amplitude_contrast':
                        value *= 100
                    else:
                        pass
                elif name == 'reserved_spot':
                    value = row['cross_corr']
                elif name == 'defocus':
                    value = (row['defocus_1'] + row['defocus_2']) / 20000
                elif name == 'astigmatism_amplitude':
                    value = (-row['defocus_1'] + row['defocus_2']) / 10000
                elif name == 'astigmatism_angle':
                    value = 45 - row['astigmatism']
                elif name == 'limit_defocus_and_astigmatism':
                    if row['limit'] == 0:
                        value = -1
                    else:
                        value = 1 / row['limit']
                elif name == 'limit_pixel_error':
                    value = 1 / (get_constant_value('apix', ctf_settings, row, project_folder, ctf_name, ctf_folder) * 2)
                elif name == 'amplitude_contrast':
                    contrast = get_constant_value('const_amplitude_contrast', ctf_settings, row, project_folder, ctf_name, ctf_folder) * 100
                    contrast = contrast_to_shift(contrast)
                    phase_shift = row['phase_shift']
                    value = shift_to_contrast(contrast + phase_shift)
                else:
                    value = 0
            else:
                # Is a CTER partres name
                if name == 'file_name':
                    value = sum_file.replace(project_folder, '')
                else:
                    pass

            export_data[idx][name] = value

    lines = []
    maximum_string = {
        'file_name': len(max(export_data['file_name'], key=len))
        }
    create_export_data(
        export_data=export_data,
        lines=lines,
        maximum_string=maximum_string
        )
    return ''.join(lines)


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
    transphire_dict = ti.get_transphire_dict()
    index = 0
    for name in names:
        try:
            new_name = transphire_dict[name]
        except KeyError:
            if name == 'mic_number':
                continue
            elif name == 'image':
                continue
            else:
                new_name = name
        header.append('{0} #{1}'.format(new_name, index+1))
        index += 1
    return '{0}\n'.format('\n'.join(header))


def get_constant_value(key, ctf_settings, row, project_folder, ctf_name, ctf_folder):
    if key == '_rlnCtfImage':
        _, extension = os.path.splitext(row['file_name'])
        if ctf_name.lower().startswith('gctf'):
            file_name = row['file_name'].replace(
                extension,
                '.ctf:mrc'
                )
            file_name = os.path.join(ctf_folder, os.path.basename(file_name))
        elif ctf_name.lower().startswith('ctffind'):
            file_name = row['file_name'].replace(
                extension,
                '.mrc:mrc'
                )
            file_name = os.path.join(ctf_folder, os.path.basename(file_name))
        elif ctf_name.lower().startswith('cter'):
            file_name = 'not_available_with_cter_option'
        else:
            raise IOError('Cannot find ctf_name! {0}'.format(
                ctf_name
                ))
        value = file_name.replace(project_folder, '')
    elif key == '_rlnVoltage' or key == 'volt':
        if '--kV' in ctf_settings:
            value = ctf_settings['--kV']
        elif 'Acceleration voltage' in ctf_settings:
            value = ctf_settings['Acceleration voltage']
        elif '--voltage' in ctf_settings:
            value = ctf_settings['--voltage']
        else:
            raise IOError('Cannot find voltage key! {0}'.format(
                ctf_name
                ))
        value = float(value)
    elif key == '_rlnSphericalAberration' or key == 'cs':
        if 'Spherical aberration' in ctf_settings:
            value = ctf_settings['Spherical aberration']
        elif '--cs' in ctf_settings:
            value = ctf_settings['--cs']
        elif '--Cs' in ctf_settings:
            value = ctf_settings['--Cs']
        else:
            raise IOError('Cannot find cs key! {0}'.format(
                ctf_name
                ))
        value = float(value)
    elif key == '_rlnAmplitudeContrast' or key == 'const_amplitude_contrast':
        if '--ac' in ctf_settings:
            value = ctf_settings['--ac']
            value = float(value)
            if value > 1:
                value /= 100
            else:
                pass
        elif 'Amplitude contrast' in ctf_settings:
            value = ctf_settings['Amplitude contrast']
        else:
            raise IOError('Cannot find ac key! {0}'.format(
                ctf_name
                ))
        value = float(value)
    elif key == '_rlnMagnification':
        value = 10000.0
        value = float(value)
    elif key == '_rlnDetectorPixelSize' or key == 'apix':
        if 'Pixel size' in ctf_settings:
            value = ctf_settings['Pixel size']
        elif '--apix' in ctf_settings:
            value = ctf_settings['--apix']
        else:
            raise IOError('Cannot find apix key! {0}'.format(
                ctf_name
                ))
        value = float(value)
    else:
        raise IOError('Dont know {0}'.format(
            key
            ))
    return value


def contrast_to_shift(a_cont):
    """
    Transform amplitude contrast to phase shift.

    a_cont - Amplitude contrast value in percent

    Returns:
    Phase shift in degrees.
    """
    a_cont = float(a_cont)
    if a_cont == 100.0:
        value = 90.0
    elif a_cont == -100.0:
        value = 90.0
    elif a_cont < 0.0:
        value =  np.degrees(np.arctan(a_cont / np.sqrt(1.0e4 - a_cont**2))) + 180.0
    else:
        value = np.degrees(np.arctan(a_cont / np.sqrt(1.0e4 - a_cont**2)))
    return value


def shift_to_contrast(phase_shift):
    """
    Convert phase shift to amplitud contrast.

    phase_shift - Phase shift in degrees.

    Returns:
    Amplitude contrast in percent.
    """
    return np.tan(np.radians(phase_shift)) / \
        np.sqrt(1.0 + np.tan(np.radians(phase_shift))**2) * 100.0


def create_jpg_file(input_mrc_file, settings, ctf_name):
    file_name = tu.get_name(input_mrc_file)
    input_ctf_file = None
    input_1d_file = None
    if 'CTFFIND' in ctf_name:
        input_ctf_file = os.path.join(settings['ctf_folder'], '{0}.mrc'.format(file_name))
        input_1d_file = os.path.join(settings['ctf_folder'], '{0}_avrot.txt'.format(file_name))
    elif 'Gctf' in ctf_name:
        input_ctf_file = os.path.join(settings['ctf_folder'], '{0}.ctf'.format(file_name))
        input_1d_file = os.path.join(settings['ctf_folder'], '{0}_EPA.log'.format(file_name))
    elif 'CTER' in ctf_name:
        input_1d_file = os.path.join(settings['ctf_folder'], file_name, 'pwrot', '{0}_rotinf.txt'.format(file_name))

    try:
        if not os.path.exists(input_ctf_file):
            input_ctf_file = None
    except TypeError:
            input_ctf_file = None
    try:
        if not os.path.exists(input_1d_file):
            input_1d_file = None
    except TypeError:
        input_1d_file = None

    tu.mkdir_p(os.path.join(settings['ctf_folder'], 'jpg'))
    tu.mkdir_p(os.path.join(settings['ctf_folder'], 'jpg_2'))
    tu.mkdir_p(os.path.join(settings['ctf_folder'], 'jpg_3'))

    jpg_file_1 = os.path.join(settings['ctf_folder'], 'jpg', '{0}.jpg'.format(file_name))
    jpg_file_2 = os.path.join(settings['ctf_folder'], 'jpg_2', '{0}.jpg'.format(file_name))
    jpg_file_3 = os.path.join(settings['ctf_folder'], 'jpg_3', '{0}.jpg'.format(file_name))

    arr_1 = None
    arr_2 = None
    arr_3 = None

    if input_mrc_file:
        try:
            with mrc.open(input_mrc_file) as mrc_file:
                input_data = mrc_file.data
        except ValueError:
            with mrc.open(input_mrc_file, 'r+', permissive=True) as mrc_file:
                mrc_file.header.map = mrc.constants.MAP_ID
            with mrc.open(input_mrc_file) as mrc_file:
                input_data = mrc_file.data
        if len(input_data.shape) == 3:
            input_data = np.sum(input_data, axis=0) / input_data.shape[0]
        input_data = input_data - np.mean(input_data)
        input_data = tu.normalize_image(input_data)

        if input_data.shape[0] > 512:
            if input_data.shape[0] > 4096:
                original_shape = 4096*2
            else:
                original_shape = 4096
            bin_shape = 512
            ratio = original_shape / bin_shape
            pad_x = original_shape - input_data.shape[0]
            pad_y = original_shape - input_data.shape[1]
            shape = (bin_shape, bin_shape)
            input_data = np.pad(input_data, ((0, pad_x), (0, pad_y)), mode='median')
            shape = (bin_shape, bin_shape)
            output_data = tu.rebin(input_data, shape)[:-int(1+pad_x//ratio), :-int(1+pad_y//ratio)]
        else:
            output_data = input_data

        arr_1 = output_data

    if input_ctf_file:
        try:
            with mrc.open(input_ctf_file) as mrc_file:
                input_data = mrc_file.data
        except ValueError:
            with mrc.open(input_ctf_file, 'r+', permissive=True) as mrc_file:
                mrc_file.header.map = mrc.constants.MAP_ID
            with mrc.open(input_ctf_file) as mrc_file:
                input_data = mrc_file.data
        if len(input_data.shape) == 3:
            input_data = np.sum(input_data, axis=0) / input_data.shape[0]
        input_data = input_data - np.mean(input_data)

        if input_data.shape[0] > 512*2:
            shape = (512*2, 512*2)
            output_data = tu.rebin(input_data, shape)
        else:
            output_data = input_data
        arr_2 = output_data

    if input_1d_file:
        plot_data = []
        if 'CTFFIND' in ctf_name:
            data = np.genfromtxt(input_1d_file)
            x_data = data[0]
            plot_data.append([data[1], 'CTF_no_astig'])
            plot_data.append([data[2], 'CTF'])
            plot_data.append([data[3], 'CTF_fit'])
            plot_data.append([data[4], 'CCC'])
            plot_data.append([data[5], '2sigma'])
        elif 'Gctf' in ctf_name:
            data = np.genfromtxt(input_1d_file, skip_header=1)
            x_data = 1/data[:,0]
            plot_data.append([data[:,1], 'CTF'])
            plot_data.append([data[:,3], 'EPA_BG'])
            plot_data.append([data[:,4], 'CCC'])
        elif 'CTER' in ctf_name:
            data = np.genfromtxt(input_1d_file)
            x_data = data[:,1]
            plot_data.append([data[:,2], 'CTF_no_astig'])
            plot_data.append([data[:,3], 'CTF_no_astig_fit'])
            plot_data.append([data[:,4], 'CTF'])
            plot_data.append([data[:,5], 'CTF_fit'])

        arr_3 = plot_data

    if arr_1 is not None:
        mi.imsave(jpg_file_1, arr_1, cmap='gist_gray')
    if arr_2 is not None:
        mi.imsave(jpg_file_2, arr_2, cmap='gist_gray')
    if arr_3 is not None:
        fig, ax = plt.subplots()
        for y_values, label in arr_3:
            ax.plot(x_data, y_values, label=label)
        plt.legend(loc='upper right')
        plt.grid()
        plt.ylim([-0.5, 2.5])
        plt.savefig(jpg_file_3, dpi=300)
        plt.close(fig)
