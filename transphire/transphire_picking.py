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
    if picking_name == 'crYOLO v1.0.0':
        command = create_cryolo_v1_0_0_command(
            picking_name = picking_name,
            file_input=file_input,
            file_output=new_name,
            settings=settings
            )
        check_files = []

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

    return command, check_files


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
    if picking_name == 'crYOLO v1.0.0':
        copied_log_files = []
        recursive_file_search(directory=picking_root_path, files=copied_log_files)
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


def create_cryolo_v1_0_0_command(
        picking_name, file_input, file_output, settings
        ):
    """Create the Gctf v1.06 command"""

    command = []
    # Start the program
    command.append('{0}'.format(settings['Path'][picking_name]))

    command.append('-i')
    command.append('{0}'.format(file_input))
    command.append('-o')
    command.append('{0}'.format(file_output))

    for key in settings[ctf_name]:
        command.append(key)
        command.append(
            '{0}'.format(settings[ctf_name][key])
            )

    return ' '.join(command)

