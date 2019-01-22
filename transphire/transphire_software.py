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
import re
import numpy as np
import traceback as tb
import pexpect as pe
from transphire import transphire_import as ti


def extract_time_and_grid_information(root_name, settings, queue_com, name):
    """
    Extract the time and grid information from the micrograph names.

    Arguments:
    root_name - Name to extract information from.
    settings - TranSPHIRE settings.
    queue_com - Queue for communication.
    name - Name of the process.

    Returns:
    hole_number, spot1_number, spot2_number, date, time
    """
    message = None
    if settings['General']['Software'] == 'EPU >1.8':

        if settings['General']['Camera'] == 'Falcon2' \
                or settings['General']['Camera'] == 'Falcon3' \
                or settings['General']['Camera'] == 'K2':
            *skip, grid, skip, old_file = \
                os.path.realpath(root_name).split('/')
            grid_number = grid.split('_')[1]
            *skip, hole, skip, spot1, spot2, date, time = old_file.split('_')
            del skip

        else:
            message = '\n'.join([
                'Camera {0} for Software {1} not known!'.format(
                    settings['General']['Camera'],
                    settings['General']['Software']
                    ),
                'Please contact the TranSPHIRE authors!'
                ])

    elif settings['General']['Software'] == 'EPU >1.9':

        if settings['General']['Camera'] == 'Falcon2' \
                or settings['General']['Camera'] == 'Falcon3' \
                or settings['General']['Camera'] == 'K2':
            *skip, grid, skip, old_file = \
                os.path.realpath(root_name).split('/')
            grid_number = grid.split('_')[1]
            *skip, hole, skip, spot1, spot2, date, time = old_file.split('_')
            del skip

        elif settings['General']['Camera'] == 'K2':
            *skip, grid, skip, old_file = \
                os.path.realpath(root_name).split('/')
            grid_number = grid.split('_')[1]
            *skip, hole, skip, spot1, spot2, date, time = old_file.split('_')
            del skip

        else:
            message = '\n'.join([
                'Camera {0} for Software {1} not known!'.format(
                    settings['General']['Camera'],
                    settings['General']['Software']
                    ),
                'Please contact the TranSPHIRE authors!'
                ])

    else:
        message = '\n'.join([
            'Software {0} not known!'.format(settings['General']['Software']),
            'Please contact the TranSPHIRE authors!'
            ])

    if message is None:
        pass
    else:
        queue_com['error'].put(message, name)
        raise IOError(message)

    return hole, grid_number, spot1, spot2, date, time


def find_frames(frames_root, compare_name, settings, queue_com, name, write_error):
    """
    Find frames based on Software, Type and camera used.

    frames_root - Root name of the frames.
    compare_name - Name to compare jpg and frames as time might differ.
    settings - TranSPHIRE settings used.
    queue_com - Queue for communication
    name - Name of process
    write_error - Write error function

    Returns:
    None if the number of frames does not match user input.
    False if an error occured and the file needs to be skipped.
    True if the function was successful.
    """
    message = None
    if settings['General']['Software'] == 'EPU >1.8':

        ####
        #
        # FRAMES
        #
        ####

        if settings['General']['Type'] == 'Frames':

            if settings['General']['Camera'] == 'K2':
                frames = glob.glob(
                    '{0}-*.{1}'.format(
                        frames_root,
                        settings['General']['Input extension']
                        )
                    )
                if len(frames) != int(settings['General']['Number of frames']):
                    write_error(
                        msg='File {0} has {1} movie files instead of {2}\n'.format(
                            frames_root,
                            len(frames),
                            settings['General']['Number of frames']
                            ),
                        root_name=frames_root
                        )
                    return None
                else:
                    return True

            elif settings['General']['Camera'] == 'Falcon2' or \
                    settings['General']['Camera'] == 'Falcon3':
                message = '\n'.join([
                    'Frames and Falcon2/Falcon3 is not supported for Software {0}.'.format(
                        settings['General']['Software']
                        ),
                    'Please contact the TranSPHIRE authors!'
                    ])

            else:
                message = '\n'.join([
                    'Camera {0} not known for Software {1} with type {2}.'.format(
                        settings['General']['Camera'],
                        settings['General']['Software'],
                        settings['General']['Type']
                        ),
                    'Please contact the TranSPHIRE authors!'
                    ])

        ####
        #
        # Stack
        #
        ####

        elif settings['General']['Type'] == 'Stack':

            if settings['General']['Camera'] == 'K2':
                message = '\n'.join([
                    'Stack and K2 is not supported in EPU >1.8 version',
                    'Please contact the TranSPHIRE authors!'
                    ])

            elif settings['General']['Camera'] == 'Falcon2' or \
                    settings['General']['Camera'] == 'Falcon3':
                frames = glob.glob(
                    '{0}*_Fractions.{1}'.format(
                        compare_name,
                        settings['General']['Input extension']
                        )
                    )

                if len(frames) != 1:
                    message = 'File {0} has {1} movie files instead of 1\n'.format(
                        frames_root,
                        len(frames)
                        )
                    write_error(
                        msg=message,
                        root_name=frames_root
                        )
                    return None
                else:
                    try:
                        value, checked_nr_frames = check_nr_frames(
                            frames=frames,
                            settings=settings
                            )
                    except BlockingIOError:
                        write_error(
                            msg=tb.format_exc(),
                            root_name=frames_root
                            )
                        return False

                if not value:
                    message = 'File {0} has {1} frames instead of {2}\n'.format(
                        frames[0],
                        checked_nr_frames,
                        int(settings['General']['Number of frames'])
                        )
                    write_error(
                        msg=message,
                        root_name=frames_root
                        )
                    return None
                else:
                    return True

            else:
                message = '\n'.join([
                    'Camera {0} not known for Software {1} with type {2}.'.format(
                        settings['General']['Camera'],
                        settings['General']['Software'],
                        settings['General']['Type']
                        ),
                    'Please contact the TranSPHIRE authors!'
                    ])

        else:
            message = '\n'.join([
                '{0}: Unknown Type!'.format(settings['General']['Type']),
                'Please contact the TranSPHIRE authors!'
                ])

    elif settings['General']['Software'] == 'EPU >1.9':

        ####
        #
        # FRAMES
        #
        ####

        if settings['General']['Type'] == 'Frames':

            if settings['General']['Camera'] == 'K2':
                message = '\n'.join([
                    'Frames and K2 is not supported for Software {0}.'.format(
                        settings['General']['Software']
                        ),
                    'Please contact the TranSPHIRE authors!'
                    ])

            elif settings['General']['Camera'] == 'Falcon2' or \
                    settings['General']['Camera'] == 'Falcon3':
                message = '\n'.join([
                    'Frames and Falcon2/Falcon3 is not supported for Software {0}.'.format(
                        settings['General']['Software']
                        ),
                    'Please contact the TranSPHIRE authors!'
                    ])

            else:
                message = '\n'.join([
                    'Camera {0} not known for Software {1} with type {2}.'.format(
                        settings['General']['Camera'],
                        settings['General']['Software'],
                        settings['General']['Type']
                        ),
                    'Please contact the TranSPHIRE authors!'
                    ])

        ####
        #
        # Stack
        #
        ####

        elif settings['General']['Type'] == 'Stack':

            if settings['General']['Camera'] == 'K2':
                raw_frames = glob.glob(
                    '{0}*-*.{1}'.format(
                        compare_name,
                        settings['General']['Input extension']
                        )
                    )
                frames_re = re.compile('{0}.*-[0-9]+.{1}'.format(
                        compare_name,
                        settings['General']['Input extension']
                        ))
                frames = [frame for frame in raw_frames if frames_re.match(frame) is not None]

                if len(frames) != 1:
                    message = 'File {0} has {1} movie files instead of 1\n'.format(
                        frames_root,
                        len(frames)
                        )
                    write_error(
                        msg=message,
                        root_name=frames_root
                        )
                    return None
                else:
                    try:
                        value, checked_nr_frames = check_nr_frames(
                            frames=frames,
                            settings=settings
                            )
                    except BlockingIOError:
                        write_error(
                            msg=tb.format_exc(),
                            root_name=frames_root
                            )
                        return False

                if not value:
                    message = 'File {0} has {1} frames instead of {2}\n'.format(
                        frames[0],
                        checked_nr_frames,
                        int(settings['General']['Number of frames'])
                        )
                    write_error(
                        msg=message,
                        root_name=frames_root
                        )
                    return None
                else:
                    return True

            elif settings['General']['Camera'] == 'Falcon2' or \
                    settings['General']['Camera'] == 'Falcon3':
                frames = glob.glob(
                    '{0}*_Fractions.{1}'.format(
                        compare_name,
                        settings['General']['Input extension']
                        )
                    )

                if len(frames) != 1:
                    message = 'File {0} has {1} movie files instead of 1\n'.format(
                        frames_root,
                        len(frames)
                        )
                    write_error(
                        msg=message,
                        root_name=frames_root
                        )
                    return None
                else:
                    try:
                        value, checked_nr_frames = check_nr_frames(
                            frames=frames,
                            settings=settings
                            )
                    except BlockingIOError:
                        write_error(
                            msg=tb.format_exc(),
                            root_name=frames_root
                            )
                        return False

                if not value:
                    message = 'File {0} has {1} frames instead of {2}\n'.format(
                        frames[0],
                        checked_nr_frames,
                        int(settings['General']['Number of frames'])
                        )
                    write_error(
                        msg=message,
                        root_name=frames_root
                        )
                    return None
                else:
                    return True

            else:
                message = '\n'.join([
                    'Camera {0} not known for Softwaee {1} with type {2}.'.format(
                        settings['General']['Camera'],
                        settings['General']['Software'],
                        settings['General']['Type']
                        ),
                    'Please contact the TranSPHIRE authors!'
                    ])

        else:
            message = '\n'.join([
                '{0}: Unknown Type!'.format(settings['General']['Type']),
                'Please contact the TranSPHIRE authors!'
                ])

    else:
        message = '\n'.join([
            '{0}: Unknown Software!'.format(settings['General']['Software']),
            'Please contact the TranSPHIRE authors!'
            ])

    assert bool(message is not None)
    queue_com['error'].put(
        message,
        name
        )
    raise IOError(message)


def check_nr_frames(frames, settings):
    """
    Check if the nr of frames of the stack match the given nr of frames

    Arguments:
    frames - List of found frames
    settings - TranSPHIRE settings
    """
    command = '{0} {1}'.format(
        settings['Path']['IMOD header'],
        frames[0]
        )

    child = pe.spawnu(command)
    text = child.read()
    child.interact()

    nr_frames = 0
    for line in text.split('\n'):
        if line.startswith(' Number of columns, rows, sections .....'):
            nr_frames = int(line.split()[-1])

    return bool(nr_frames == int(settings['General']['Number of frames'])), nr_frames


def find_related_frames_to_jpg(frames_root, root_name, settings, queue_com, name):
    """
    Find related frames to the jpg file based on the used software.

    Arguments:
    frames_root - Root name to search for related files
    root_name - Root name of the jpg file
    settings - TranSPHIRE settings
    queue_com - Queue for communication
    name - Name of the process
    """
    message = None
    if settings['General']['Software'] == 'EPU >1.8':

        ####
        #
        # Stack
        #
        ####

        if settings['General']['Type'] == 'Stack':

            if settings['General']['Camera'] == 'K2':
                message = '\n'.join([
                    'Stack and K2 is not supported in EPU >1.8 version',
                    'Please contact the TranSPHIRE authors!'
                    ])

            elif settings['General']['Camera'] == 'Falcon2' or \
                    settings['General']['Camera'] == 'Falcon3':
                compare_name_frames = frames_root[:-len('_19911213_2019')]
                compare_name_meta = root_name[:-len('_19911213_2019')]
                frames = glob.glob('{0}*_Fractions.{1}'.format(
                    compare_name_frames,
                    settings['General']['Input extension']
                    ))
                return frames, compare_name_frames, compare_name_meta

            else:
                message = '\n'.join([
                    'Camera {0} not known for Software {1} with type {2}.'.format(
                        settings['General']['Camera'],
                        settings['General']['Software'],
                        settings['General']['Type']
                        ),
                    'Please contact the TranSPHIRE authors!'
                    ])

        ####
        #
        # Frames
        #
        ####

        elif settings['General']['Type'] == 'Frames':

            if settings['General']['Camera'] == 'K2':
                frames = sorted(glob.glob(
                    '{0}-*.{1}'.format(
                        frames_root,
                        settings['General']['Input extension']
                        )
                    ))
                return frames, frames_root, root_name

            elif settings['General']['Camera'] == 'Falcon2' or \
                    settings['General']['Camera'] == 'Falcon3':
                message = '\n'.join([
                    'Frames and Falcon2/Falcon3 is not supported',
                    'Please contact the TranSPHIRE authors!'
                    ])

            else:
                message = '\n'.join([
                    'Camera {0} not known for Software {1} with type {2}.'.format(
                        settings['General']['Camera'],
                        settings['General']['Software'],
                        settings['General']['Type']
                        ),
                    'Please contact the TranSPHIRE authors!'
                    ])

        else:
            message = '\n'.join([
                '{0}: Unknown Type!'.format(settings['General']['Type']),
                'Please contact the TranSPHIRE authors!'
                ])

    elif settings['General']['Software'] == 'EPU >1.9':

        ####
        #
        # Stack
        #
        ####

        if settings['General']['Type'] == 'Stack':

            if settings['General']['Camera'] == 'K2':
                compare_name_frames = frames_root[:-len('_19911213_2019')]
                compare_name_meta = root_name[:-len('_19911213_2019')]
                raw_frames = glob.glob('{0}*-*.{1}'.format(
                    compare_name_frames,
                    settings['General']['Input extension']
                    ))
                frames_re = re.compile('{0}.*-[0-9]+.{1}'.format(
                        compare_name_frames,
                        settings['General']['Input extension']
                        ))
                frames = [frame for frame in raw_frames if frames_re.match(frame) is not None]
                return frames, compare_name_frames, compare_name_meta

            elif settings['General']['Camera'] == 'Falcon2' or \
                    settings['General']['Camera'] == 'Falcon3':
                compare_name_frames = frames_root[:-len('_19911213_2019')]
                compare_name_meta = root_name[:-len('_19911213_2019')]
                frames = glob.glob('{0}*_Fractions.{1}'.format(
                    compare_name_frames,
                    settings['General']['Input extension']
                    ))
                return frames, compare_name_frames, compare_name_meta

            else:
                message = '\n'.join([
                    'Camera {0} not known for Software {1} with type {2}.'.format(
                        settings['General']['Camera'],
                        settings['General']['Software'],
                        settings['General']['Type']
                        ),
                    'Please contact the TranSPHIRE authors!'
                    ])

        ####
        #
        # Frames
        #
        ####

        elif settings['General']['Type'] == 'Frames':

            if settings['General']['Camera'] == 'K2':
                message = '\n'.join([
                    'Frames and K2 is not supported',
                    'Please contact the TranSPHIRE authors!'
                    ])

            elif settings['General']['Camera'] == 'Falcon2' or \
                    settings['General']['Camera'] == 'Falcon3':
                message = '\n'.join([
                    'Frames and Falcon2/Falcon3 is not supported',
                    'Please contact the TranSPHIRE authors!'
                    ])

            else:
                message = '\n'.join([
                    'Camera {0} not known for Software {1} with type {2}.'.format(
                        settings['General']['Camera'],
                        settings['General']['Software'],
                        settings['General']['Type']
                        ),
                    'Please contact the TranSPHIRE authors!'
                    ])

        else:
            message = '\n'.join([
                '{0}: Unknown Type!'.format(settings['General']['Type']),
                'Please contact the TranSPHIRE authors!'
                ])

    else:
        message = '\n'.join([
            '{0}: Unknown Software!'.format(settings['General']['Software']),
            'Please contact the TranSPHIRE authors!'
            ])

    assert bool(message is not None)
    queue_com['error'].put(
        message,
        name
        )
    raise IOError(message)


def get_copy_command_for_frames(settings, queue_com, name):
    """
    Copy the frames based on stack or frames type.

    settings - TranSPHIRE settings.
    queue_com - Queue for communication.
    name - Name of the process.

    Returns:
    Command to use for copy.
    """
    message = None
    if settings['General']['Software'] == 'EPU >1.8':

        ####
        #
        # Stack
        #
        ####

        if settings['General']['Type'] == 'Stack':

            if settings['General']['Camera'] == 'K2':
                message = '\n'.join([
                    'Stack and K2 is not supported in EPU >1.8 version',
                    'Please contact the TranSPHIRE authors!'
                    ])

            elif settings['General']['Camera'] == 'Falcon2' or \
                    settings['General']['Camera'] == 'Falcon3':
                return 'rsync'

            else:
                message = '\n'.join([
                    'Camera {0} not known for Software {1} with type {2}.'.format(
                        settings['General']['Camera'],
                        settings['General']['Software'],
                        settings['General']['Type']
                        ),
                    'Please contact the TranSPHIRE authors!'
                    ])

        ####
        #
        # Frames
        #
        ####

        elif settings['General']['Type'] == 'Frames':

            if settings['General']['Camera'] == 'K2':
                return settings['Path']['IMOD newstack']

            elif settings['General']['Camera'] == 'Falcon2' or \
                    settings['General']['Camera'] == 'Falcon3':
                message = '\n'.join([
                    'Frames and Falcon2/Falcon3 is not supported, yet.',
                    'Please contact the TranSPHIRE authors!'
                    ])

            else:
                message = '\n'.join([
                    'Camera {0} not known for Software {1} with type {2}.'.format(
                        settings['General']['Camera'],
                        settings['General']['Software'],
                        settings['General']['Type']
                        ),
                    'Please contact the TranSPHIRE authors!'
                    ])

        else:
            message = '\n'.join([
                '{0}: Unknown Type!'.format(settings['General']['Type']),
                'Please contact the TranSPHIRE authors!'
                ])

    elif settings['General']['Software'] == 'EPU >1.9':

        ####
        #
        # Stack
        #
        ####

        if settings['General']['Type'] == 'Stack':

            if settings['General']['Camera'] == 'K2':
                return 'rsync'

            elif settings['General']['Camera'] == 'Falcon2' or \
                    settings['General']['Camera'] == 'Falcon3':
                return 'rsync'

            else:
                message = '\n'.join([
                    'Camera {0} not known for Software {1} with type {2}.'.format(
                        settings['General']['Camera'],
                        settings['General']['Software'],
                        settings['General']['Type']
                        ),
                    'Please contact the TranSPHIRE authors!'
                    ])

        ####
        #
        # Frames
        #
        ####

        elif settings['General']['Type'] == 'Frames':

            if settings['General']['Camera'] == 'K2':
                message = '\n'.join([
                    'Frames and K22 is not supported in EPU >1.9',
                    'Please contact the TranSPHIRE authors!'
                    ])

            elif settings['General']['Camera'] == 'Falcon2' or \
                    settings['General']['Camera'] == 'Falcon3':
                message = '\n'.join([
                    'Frames and Falcon2/Falcon3 is not supported n EPU >1.9',
                    'Please contact the TranSPHIRE authors!'
                    ])

            else:
                message = '\n'.join([
                    'Camera {0} not known for Software {1} with type {2}.'.format(
                        settings['General']['Camera'],
                        settings['General']['Software'],
                        settings['General']['Type']
                        ),
                    'Please contact the TranSPHIRE authors!'
                    ])

        else:
            message = '\n'.join([
                '{0}: Unknown Type!'.format(settings['General']['Type']),
                'Please contact the TranSPHIRE authors!'
                ])

    else:
        message = '\n'.join([
            '{0}: Unknown Software!'.format(settings['General']['Software']),
            'Please contact the TranSPHIRE authors!'
            ])

    assert bool(message is not None)
    queue_com['error'].put(
        message,
        name
        )
    raise IOError(message)


def find_all_files(root_name, compare_name_frames, compare_name_meta, settings, queue_com, name):
    """
    Find other files that relate to root_name.

    root_name - Root name of files to find.
    compare_name_meta - Name of the meta data to find.
    queue_com - Queue for communication.
    name - Name of the process

    Returns:
    list of files related to root_name.
    """
    message = None
    if settings['General']['Software'] == 'EPU >1.8':

        if settings['General']['Camera'] == 'K2':
            meta_files = glob.glob('{0}.*'.format(root_name))
            frame_files = glob.glob('{0}*'.format(compare_name_frames))
            return set(meta_files), set(frame_files)

        elif settings['General']['Camera'] == 'Falcon2' or \
                settings['General']['Camera'] == 'Falcon3':
            meta_files = [
                name for name in glob.glob('{0}*'.format(compare_name_meta))
                if 'Fractions' not in name
                ]
            frame_files = glob.glob('{0}*'.format(compare_name_frames))
            return set(meta_files), set(frame_files)

        else:
            message = '\n'.join([
                '{0}: Unknown Camera!'.format(settings['General']['Camera']),
                'Please contact the TranSPHIRE authors!'
                ])

    elif settings['General']['Software'] == 'EPU >1.9':

        if settings['General']['Camera'] == 'K2':
            meta_files = glob.glob('{0}*'.format(compare_name_meta))
            frame_files = glob.glob('{0}*'.format(compare_name_frames))
            return set(meta_files), set(frame_files)

        elif settings['General']['Camera'] == 'Falcon2' or \
                settings['General']['Camera'] == 'Falcon3':
            meta_files = [
                name for name in glob.glob('{0}*'.format(compare_name_meta))
                if 'Fractions' not in name
                ]
            frame_files = glob.glob('{0}*'.format(compare_name_frames))
            return set(meta_files), set(frame_files)

        else:
            message = '\n'.join([
                '{0}: Unknown Camera!'.format(settings['General']['Camera']),
                'Please contact the TranSPHIRE authors!'
                ])

    else:
        message = '\n'.join([
            '{0}: Unknown Software!'.format(settings['General']['Software']),
            'Please contact the TranSPHIRE authors!'
            ])

    assert bool(message is not None)
    queue_com['error'].put(
        message,
        name
        )
    raise IOError(message)


def check_outputs(zero_list, non_zero_list, exists_list, folder, command):
    """
    Check, if the output files are present and have the proper size.

    zero_list - List of files that should be zero
    non_zero_list - List of files that should not be zero

    Returns:
    None
    """
    for file_path in non_zero_list:
        try:
            size = os.path.getsize(file_path)
        except OSError:
            raise Exception(
                'Command failed: {0} for {1}. Please check the logfiles in {2}!'.format(
                    command,
                    file_path,
                    folder
                    )
                )
        else:
            if size == 0:
                raise Exception(
                    'Command failed: {0} for {1}. Please check the logfiles in {2}!'.format(
                        command,
                        file_path,
                        folder
                        )
                    )
            else:
                continue

    for file_path in zero_list:
        try:
            size = os.path.getsize(file_path)
        except OSError:
            raise Exception(
                'Command failed: {0} for {1}. Please check the logfiles in {2}!'.format(
                    command,
                    file_path,
                    folder
                    )
                )
        else:
            if size > 0:
                raise Exception(
                    'Command failed: {0} for {1}. Please check the logfiles in {2}!'.format(
                        command,
                        file_path,
                        folder
                        )
                    )
            else:
                continue

    for file_path in exists_list:
        if not os.path.exists(file_path):
            raise Exception(
                'Command failed: {0} for {1}. Please check the logfiles in {2}!'.format(
                    command,
                    file_path,
                    folder
                    )
                )
        else:
            continue


def check_for_outlier(dict_name, data, file_name, settings):
    dtype_dict = ti.get_dtype_dict()
    lower_median = int(settings['Notification']['Nr. of values used for median'])
    warning_list = []
    skip_list = []

    file_name_match = os.path.basename(os.path.splitext(file_name)[0])
    match_file = re.compile(file_name_match)
    vmatch = np.vectorize(lambda x:bool(match_file.search(x)))
    try:
        mask = vmatch(data['file_name'])
    except ValueError:
        print('ERROR with file!')
        print('dict_name', data)
        print('dict_name', dict_name)
        print('file_name', file_name)
        raise

    for key in dtype_dict[dict_name]:
        key = key[0]

        try:
            last_values_median = np.median(data[key][-lower_median:])
            warning_low, warning_high = settings['Notification']['{0} warning'.format(key)].split()
            skip_low, skip_high = settings['Notification']['{0} skip'.format(key)].split()
        except Exception:
            continue

        if float(warning_low) <= last_values_median and last_values_median <= float(warning_high):
            pass
        else:
            warning_list.append([
                key,
                last_values_median,
                warning_low,
                warning_high
                ])

        assert data[mask].shape[0] == 1, [data[mask], file_name, file_name_match, data['file_name']]

        if float(skip_low) <= data[key][mask][0] and data[key][mask][0] <= float(skip_high):
            pass
        else:
            skip_list.append([
                key,
                data[key][mask][0],
                skip_low,
                skip_high
                ])

    return warning_list, skip_list


def get_logfiles(log_prefix):
    """
    Return the names of the log_file and error file.

    Arguments:
    log_prefix - Prefix to use.

    Returns:
    Name of log file, Name of error file
    """
    template = '{0}_transphire.{{0}}'.format(log_prefix)
    return template.format('log'), template.format('err')
