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
import datetime
import numpy as np
import traceback as tb
import subprocess
from hyperspy.io_plugins.digital_micrograph import DigitalMicrographReader

from . import transphire_import as ti
from . import transphire_utils as tu


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
    if settings['Input']['Software'] == 'Just Stack':
        hole = 0
        grid_number = 0
        spot1 = 0
        spot2 = 0
        date = 0
        time = 0

    elif settings['Input']['Software'] == 'Latitude S':
        if settings['Input']['Camera'] in ('Falcon2', 'Falcon3'):
            message = '\n'.join([
                'Falcon2/Falcon3 is not supported for Software {0}.'.format(
                    settings['Input']['Software']
                    ),
                'Please contact the TranSPHIRE authors!'
                ])

        elif settings['Input']['Camera'] in ('K2', 'K3'):
            search_results = re.search(
                r'(?P<date>\d{8})_(?P<project>.*)_A(?P<atlas>\d{3,})_G(?P<grid>\d{3,})_H(?P<hole>\d{3,})_D(?P<spot>\d{3,})',
                root_name
                )
            grid_number = '{0}_{1}'.format(
                search_results.group('atlas'),
                search_results.group('grid')
                )
            hole = search_results.group('hole')
            spot1 = search_results.group('spot')
            spot2 = ''
            date = search_results.group('date')
            with open('{0}.gtg'.format(root_name), 'rb') as read:
                reader = DigitalMicrographReader(read)
                reader.parse_file()
            time = datetime.datetime.strptime(
                reader.tags_dict['DataBar']['Acquisition Time'],
                '%I:%M:%S %p'
                ).strftime('%H%M%S')

        else:
            message = '\n'.join([
                'Camera {0} for Software {1} not known!'.format(
                    settings['Input']['Camera'],
                    settings['Input']['Software']
                    ),
                'Please contact the TranSPHIRE authors!'
                ])

    elif settings['Input']['Software'] == 'EPU >=1.8':

        if settings['Input']['Camera'] == 'Falcon2' \
                or settings['Input']['Camera'] == 'Falcon3' \
                or settings['Input']['Camera'] in ('K2', 'K3'):
            *skip, grid, skip, old_file = \
                os.path.realpath(root_name).split('/')
            grid_number = grid.split('_')[1]
            *skip, hole, skip, spot1, spot2, date, time = old_file.split('_')
            del skip

        else:
            message = '\n'.join([
                'Camera {0} for Software {1} not known!'.format(
                    settings['Input']['Camera'],
                    settings['Input']['Software']
                    ),
                'Please contact the TranSPHIRE authors!'
                ])

    elif settings['Input']['Software'] == 'EPU >=1.9':

        if settings['Input']['Camera'] == 'Falcon2' \
                or settings['Input']['Camera'] == 'Falcon3' \
                or settings['Input']['Camera'] in ('K2', 'K3'):
            *skip, grid, skip, old_file = \
                os.path.realpath(root_name).split('/')
            grid_number = grid.split('_')[1]
            *skip, hole, skip, spot1, spot2, date, time = old_file.split('_')
            del skip

        elif settings['Input']['Camera'] in ('K2', 'K3'):
            *skip, grid, skip, old_file = \
                os.path.realpath(root_name).split('/')
            grid_number = grid.split('_')[1]
            *skip, hole, skip, spot1, spot2, date, time = old_file.split('_')
            del skip

        else:
            message = '\n'.join([
                'Camera {0} for Software {1} not known!'.format(
                    settings['Input']['Camera'],
                    settings['Input']['Software']
                    ),
                'Please contact the TranSPHIRE authors!'
                ])

    else:
        message = '\n'.join([
            'Software {0} not known!'.format(settings['Input']['Software']),
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
    if settings['Input']['Software'] == 'Just Stack':
        frames = glob.glob(
            '{0}.{1}'.format(
                compare_name,
                settings['Input']['Input frames extension']
                )
            )
        if not frames:
            return False

        try:
            value, _, _, checked_nr_frames = check_nr_frames(
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
                int(settings['Input']['Number of frames'])
                )
            write_error(
                msg=message,
                root_name=frames_root
                )
            return None
        else:
            return True
    elif settings['Input']['Software'] == 'Latitude S':
        if settings['Input']['Type'] == 'Frames':
            message = '\n'.join([
                'Frames and Falcon2/Falcon3 is not supported for Software {0}.'.format(
                    settings['Input']['Software']
                    ),
                'Please contact the TranSPHIRE authors!'
                ])

        elif settings['Input']['Type'] == 'Stack':

            if settings['Input']['Camera'] in ('Falcon2', 'Falcon3'):
                message = '\n'.join([
                    'Falcon2/Falcon3 is not supported for Software {0}.'.format(
                        settings['Input']['Software']
                        ),
                    'Please contact the TranSPHIRE authors!'
                    ])

            elif settings['Input']['Camera'] in ('K2', 'K3'):
                frames = glob.glob(
                    '{0}.{1}'.format(
                        os.path.join(os.path.dirname(compare_name), 'Stack', os.path.basename(compare_name)),
                        settings['Input']['Input frames extension']
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
                    if len(frames) == 0:
                        return False
                    else:
                        return None
                else:
                    try:
                        value, _, _, checked_nr_frames = check_nr_frames(
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
                        int(settings['Input']['Number of frames'])
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
                    'Camera {0} for Software {1} not known!'.format(
                        settings['Input']['Camera'],
                        settings['Input']['Software']
                        ),
                    'Please contact the TranSPHIRE authors!'
                    ])

        else:
            message = '\n'.join([
                '{0}: Unknown Type!'.format(settings['Input']['Type']),
                'Please contact the TranSPHIRE authors!'
                ])

    elif settings['Input']['Software'] == 'EPU >=1.8':

        ####
        #
        # FRAMES
        #
        ####

        if settings['Input']['Type'] == 'Frames':

            if settings['Input']['Camera'] in ('K2', 'K3'):
                frames = glob.glob(
                    '{0}-*.{1}'.format(
                        frames_root,
                        settings['Input']['Input frames extension']
                        )
                    )
                if len(frames) != int(settings['Input']['Number of frames']):
                    write_error(
                        msg='File {0} has {1} movie files instead of {2}\n'.format(
                            frames_root,
                            len(frames),
                            settings['Input']['Number of frames']
                            ),
                        root_name=frames_root
                        )
                    if len(frames) == 0:
                        return False
                    else:
                        return None
                else:
                    return True

            elif settings['Input']['Camera'] == 'Falcon2' or \
                    settings['Input']['Camera'] == 'Falcon3':
                message = '\n'.join([
                    'Frames and Falcon2/Falcon3 is not supported for Software {0}.'.format(
                        settings['Input']['Software']
                        ),
                    'Please contact the TranSPHIRE authors!'
                    ])

            else:
                message = '\n'.join([
                    'Camera {0} not known for Software {1} with type {2}.'.format(
                        settings['Input']['Camera'],
                        settings['Input']['Software'],
                        settings['Input']['Type']
                        ),
                    'Please contact the TranSPHIRE authors!'
                    ])

        ####
        #
        # Stack
        #
        ####

        elif settings['Input']['Type'] == 'Stack':

            if settings['Input']['Camera'] in ('K2', 'K3'):
                message = '\n'.join([
                    'Stack and K2, K3 is not supported in EPU >=1.8 version',
                    'Please contact the TranSPHIRE authors!'
                    ])

            elif settings['Input']['Camera'] == 'Falcon2' or \
                    settings['Input']['Camera'] == 'Falcon3':
                frames = glob.glob(
                    '{0}*_Fractions.{1}'.format(
                        compare_name,
                        settings['Input']['Input frames extension']
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
                    if len(frames) == 0:
                        return False
                    else:
                        return None
                else:
                    try:
                        value, _, _, checked_nr_frames = check_nr_frames(
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
                        int(settings['Input']['Number of frames'])
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
                        settings['Input']['Camera'],
                        settings['Input']['Software'],
                        settings['Input']['Type']
                        ),
                    'Please contact the TranSPHIRE authors!'
                    ])

        else:
            message = '\n'.join([
                '{0}: Unknown Type!'.format(settings['Input']['Type']),
                'Please contact the TranSPHIRE authors!'
                ])

    elif settings['Input']['Software'] == 'EPU >=1.9':

        ####
        #
        # FRAMES
        #
        ####

        if settings['Input']['Type'] == 'Frames':

            if settings['Input']['Camera'] in ('K2', 'K3'):
                message = '\n'.join([
                    'Frames and K2, K3 is not supported for Software {0}.'.format(
                        settings['Input']['Software']
                        ),
                    'Please contact the TranSPHIRE authors!'
                    ])

            elif settings['Input']['Camera'] == 'Falcon2' or \
                    settings['Input']['Camera'] == 'Falcon3':
                message = '\n'.join([
                    'Frames and Falcon2/Falcon3 is not supported for Software {0}.'.format(
                        settings['Input']['Software']
                        ),
                    'Please contact the TranSPHIRE authors!'
                    ])

            else:
                message = '\n'.join([
                    'Camera {0} not known for Software {1} with type {2}.'.format(
                        settings['Input']['Camera'],
                        settings['Input']['Software'],
                        settings['Input']['Type']
                        ),
                    'Please contact the TranSPHIRE authors!'
                    ])

        ####
        #
        # Stack
        #
        ####

        elif settings['Input']['Type'] == 'Stack':

            if settings['Input']['Camera'] in ('K2'):
                raw_frames = glob.glob(
                    '{0}*-*.{1}'.format(
                        compare_name,
                        settings['Input']['Input frames extension']
                        )
                    )
                frames_re = re.compile('{0}.*-[0-9]+.{1}'.format(
                        compare_name,
                        settings['Input']['Input frames extension']
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
                    if len(frames) == 0:
                        return False
                    else:
                        return None
                else:
                    try:
                        value, _, _, checked_nr_frames = check_nr_frames(
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
                        int(settings['Input']['Number of frames'])
                        )
                    write_error(
                        msg=message,
                        root_name=frames_root
                        )
                    return None
                else:
                    return True

            elif settings['Input']['Camera'] == 'K3':
                frames = glob.glob(
                    '{0}*_fractions.{1}'.format(
                        compare_name,
                        settings['Input']['Input frames extension']
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
                    if len(frames) == 0:
                        return False
                    else:
                        return None
                else:
                    try:
                        value, _, _, checked_nr_frames = check_nr_frames(
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
                        int(settings['Input']['Number of frames'])
                        )
                    write_error(
                        msg=message,
                        root_name=frames_root
                        )
                    return None
                else:
                    return True

            elif settings['Input']['Camera'] == 'Falcon2' or \
                    settings['Input']['Camera'] == 'Falcon3':
                frames = glob.glob(
                    '{0}*_Fractions.{1}'.format(
                        compare_name,
                        settings['Input']['Input frames extension']
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
                    if len(frames) == 0:
                        return False
                    else:
                        return None
                else:
                    try:
                        value, _, _, checked_nr_frames = check_nr_frames(
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
                        int(settings['Input']['Number of frames'])
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
                        settings['Input']['Camera'],
                        settings['Input']['Software'],
                        settings['Input']['Type']
                        ),
                    'Please contact the TranSPHIRE authors!'
                    ])

        else:
            message = '\n'.join([
                '{0}: Unknown Type!'.format(settings['Input']['Type']),
                'Please contact the TranSPHIRE authors!'
                ])

    else:
        message = '\n'.join([
            '{0}: Unknown Software!'.format(settings['Input']['Software']),
            'Please contact the TranSPHIRE authors!'
            ])

    assert bool(message is not None)
    queue_com['error'].put(
        message,
        name
        )
    raise IOError(message)


def get_x_dim(frames, settings):
    command = "{0} '{1}'".format(
        settings['Path']['IMOD header'],
        frames[0]
        )

    text = subprocess.check_output(command, shell=True, encoding='utf-8')

    x_dim = 0
    for line in text.split('\n'):
        if line.startswith(' Number of columns, rows, sections .....'):
            x_dim = int(line.split()[-3])

    return int(x_dim)


def check_nr_frames(frames, settings, force=False):
    """
    Check if the nr of frames of the stack match the given nr of frames

    Arguments:
    frames - List of found frames
    settings - TranSPHIRE settings
    """
    if int(settings['Input']['Number of frames']) == -1 and not force:
        return True, 0, 0, 0

#    if settings['is_superres'].value == 2:
#        settings['is_superres'].value = bool(get_x_dim(frames, settings) > 7000)
#
    if not frames:
        frames.append(None)
        return False, 0, 0, 0
    else:
        command = "{0} '{1}'".format(
            settings['Path']['IMOD header'],
            frames[0]
            )

        text = subprocess.check_output(command, shell=True, encoding='utf-8')

        z_dim = 0
        x_dim = 0
        y_dim = 0
        for line in text.split('\n'):
            if line.startswith(' Number of columns, rows, sections .....'):
                x_dim, y_dim, z_dim = list(map(int, line.split()[-3:]))

        return bool(z_dim == int(settings['Input']['Number of frames'])), x_dim, y_dim, z_dim


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
    if settings['Input']['Software'] == 'Just Stack':
        compare_name_frames = root_name
        compare_name_meta = root_name
        frames = glob.glob('{0}*.{1}'.format(
            compare_name_frames,
            settings['Input']['Input frames extension']
            ))
        return frames, compare_name_frames, compare_name_meta

    elif settings['Input']['Software'] == 'Latitude S':
        if settings['Input']['Type'] == 'Frames':
            message = '\n'.join([
                'Frames and Falcon2/Falcon3 is not supported for Software {0}.'.format(
                    settings['Input']['Software']
                    ),
                'Please contact the TranSPHIRE authors!'
                ])

        elif settings['Input']['Type'] == 'Stack':

            if settings['Input']['Camera'] in ('Falcon2', 'Falcon3'):
                message = '\n'.join([
                    'Falcon2/Falcon3 is not supported for Software {0}.'.format(
                        settings['Input']['Software']
                        ),
                    'Please contact the TranSPHIRE authors!'
                    ])

            elif settings['Input']['Camera'] in ('K2', 'K3'):
                compare_name_frames = os.path.join(os.path.dirname(root_name), 'Stack', os.path.basename(root_name))
                compare_name_meta = root_name
                frames = glob.glob('{0}.{1}'.format(
                    compare_name_frames,
                    settings['Input']['Input frames extension']
                    ))
                return frames, compare_name_frames, compare_name_meta

            else:
                message = '\n'.join([
                    'Camera {0} for Software {1} not known!'.format(
                        settings['Input']['Camera'],
                        settings['Input']['Software']
                        ),
                    'Please contact the TranSPHIRE authors!'
                    ])

        else:
            message = '\n'.join([
                '{0}: Unknown Type!'.format(settings['Input']['Type']),
                'Please contact the TranSPHIRE authors!'
                ])

    elif settings['Input']['Software'] == 'EPU >=1.8':

        ####
        #
        # Stack
        #
        ####

        if settings['Input']['Type'] == 'Stack':

            if settings['Input']['Camera'] in ('K2', 'K3'):
                message = '\n'.join([
                    'Stack and K2, K3 is not supported in EPU >=1.8 version',
                    'Please contact the TranSPHIRE authors!'
                    ])

            elif settings['Input']['Camera'] == 'Falcon2' or \
                    settings['Input']['Camera'] == 'Falcon3':
                compare_name_frames = frames_root[:-len('_19911213_2019')]
                compare_name_meta = root_name[:-len('_19911213_2019')]
                frames = glob.glob('{0}*_Fractions.{1}'.format(
                    compare_name_frames,
                    settings['Input']['Input frames extension']
                    ))
                return frames, compare_name_frames, compare_name_meta

            else:
                message = '\n'.join([
                    'Camera {0} not known for Software {1} with type {2}.'.format(
                        settings['Input']['Camera'],
                        settings['Input']['Software'],
                        settings['Input']['Type']
                        ),
                    'Please contact the TranSPHIRE authors!'
                    ])

        ####
        #
        # Frames
        #
        ####

        elif settings['Input']['Type'] == 'Frames':

            if settings['Input']['Camera'] in ('K2', 'K3'):
                frames = sorted(glob.glob(
                    '{0}-*.{1}'.format(
                        frames_root,
                        settings['Input']['Input frames extension']
                        )
                    ))
                return frames, frames_root, root_name

            elif settings['Input']['Camera'] == 'Falcon2' or \
                    settings['Input']['Camera'] == 'Falcon3':
                message = '\n'.join([
                    'Frames and Falcon2/Falcon3 is not supported',
                    'Please contact the TranSPHIRE authors!'
                    ])

            else:
                message = '\n'.join([
                    'Camera {0} not known for Software {1} with type {2}.'.format(
                        settings['Input']['Camera'],
                        settings['Input']['Software'],
                        settings['Input']['Type']
                        ),
                    'Please contact the TranSPHIRE authors!'
                    ])

        else:
            message = '\n'.join([
                '{0}: Unknown Type!'.format(settings['Input']['Type']),
                'Please contact the TranSPHIRE authors!'
                ])

    elif settings['Input']['Software'] == 'EPU >=1.9':

        ####
        #
        # Stack
        #
        ####

        if settings['Input']['Type'] == 'Stack':

            if settings['Input']['Camera'] in ('K2'):
                compare_name_frames = frames_root[:-len('_19911213_2019')]
                compare_name_meta = root_name[:-len('_19911213_2019')]
                raw_frames = glob.glob('{0}*-*.{1}'.format(
                    compare_name_frames,
                    settings['Input']['Input frames extension']
                    ))
                frames_re = re.compile('{0}.*-[0-9]+.{1}'.format(
                        compare_name_frames,
                        settings['Input']['Input frames extension']
                        ))
                frames = [frame for frame in raw_frames if frames_re.match(frame) is not None]
                return frames, compare_name_frames, compare_name_meta

            elif settings['Input']['Camera'] == 'K3':
                compare_name_frames = frames_root[:-len('_19911213_2019')]
                compare_name_meta = root_name[:-len('_19911213_2019')]
                frames = glob.glob('{0}*_fractions.{1}'.format(
                    compare_name_frames,
                    settings['Input']['Input frames extension']
                    ))
                return frames, compare_name_frames, compare_name_meta

            elif settings['Input']['Camera'] == 'Falcon2' or \
                    settings['Input']['Camera'] == 'Falcon3':
                compare_name_frames = frames_root[:-len('_19911213_2019')]
                compare_name_meta = root_name[:-len('_19911213_2019')]
                frames = glob.glob('{0}*_Fractions.{1}'.format(
                    compare_name_frames,
                    settings['Input']['Input frames extension']
                    ))
                return frames, compare_name_frames, compare_name_meta

            else:
                message = '\n'.join([
                    'Camera {0} not known for Software {1} with type {2}.'.format(
                        settings['Input']['Camera'],
                        settings['Input']['Software'],
                        settings['Input']['Type']
                        ),
                    'Please contact the TranSPHIRE authors!'
                    ])

        ####
        #
        # Frames
        #
        ####

        elif settings['Input']['Type'] == 'Frames':

            if settings['Input']['Camera'] in ('K2', 'K3'):
                message = '\n'.join([
                    'Frames and K2, K3 is not supported',
                    'Please contact the TranSPHIRE authors!'
                    ])

            elif settings['Input']['Camera'] == 'Falcon2' or \
                    settings['Input']['Camera'] == 'Falcon3':
                message = '\n'.join([
                    'Frames and Falcon2/Falcon3 is not supported',
                    'Please contact the TranSPHIRE authors!'
                    ])

            else:
                message = '\n'.join([
                    'Camera {0} not known for Software {1} with type {2}.'.format(
                        settings['Input']['Camera'],
                        settings['Input']['Software'],
                        settings['Input']['Type']
                        ),
                    'Please contact the TranSPHIRE authors!'
                    ])

        else:
            message = '\n'.join([
                '{0}: Unknown Type!'.format(settings['Input']['Type']),
                'Please contact the TranSPHIRE authors!'
                ])

    else:
        message = '\n'.join([
            '{0}: Unknown Software!'.format(settings['Input']['Software']),
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
    if settings['Copy']['Delete data after import?'] == 'Symlink':
        return "ln -rsf"
    elif settings['Input']['Software'] == 'Just Stack':
        return "rsync --copy-links"
    elif settings['Input']['Software'] == 'Latitude S':
        if settings['Input']['Type'] == 'Frames':
            message = '\n'.join([
                'Frames and Falcon2/Falcon3 is not supported for Software {0}.'.format(
                    settings['Input']['Software']
                    ),
                'Please contact the TranSPHIRE authors!'
                ])

        elif settings['Input']['Type'] == 'Stack':

            if settings['Input']['Camera'] in ('Falcon2', 'Falcon3'):
                message = '\n'.join([
                    'Falcon2/Falcon3 is not supported for Software {0}.'.format(
                        settings['Input']['Software']
                        ),
                    'Please contact the TranSPHIRE authors!'
                    ])

            elif settings['Input']['Camera'] in ('K2', 'K3'):
                return 'rsync --copy-links'

            else:
                message = '\n'.join([
                    'Camera {0} for Software {1} not known!'.format(
                        settings['Input']['Camera'],
                        settings['Input']['Software']
                        ),
                    'Please contact the TranSPHIRE authors!'
                    ])

        else:
            message = '\n'.join([
                '{0}: Unknown Type!'.format(settings['Input']['Type']),
                'Please contact the TranSPHIRE authors!'
                ])

    elif settings['Input']['Software'] == 'EPU >=1.8':

        ####
        #
        # Stack
        #
        ####

        if settings['Input']['Type'] == 'Stack':

            if settings['Input']['Camera'] in ('K2', 'K3'):
                message = '\n'.join([
                    'Stack and K2, K3 is not supported in EPU >=1.8 version',
                    'Please contact the TranSPHIRE authors!'
                    ])

            elif settings['Input']['Camera'] == 'Falcon2' or \
                    settings['Input']['Camera'] == 'Falcon3':
                return 'rsync --copy-links'

            else:
                message = '\n'.join([
                    'Camera {0} not known for Software {1} with type {2}.'.format(
                        settings['Input']['Camera'],
                        settings['Input']['Software'],
                        settings['Input']['Type']
                        ),
                    'Please contact the TranSPHIRE authors!'
                    ])

        ####
        #
        # Frames
        #
        ####

        elif settings['Input']['Type'] == 'Frames':

            if settings['Input']['Camera'] in ('K2', 'K3'):
                return settings['Path']['IMOD newstack']

            elif settings['Input']['Camera'] == 'Falcon2' or \
                    settings['Input']['Camera'] == 'Falcon3':
                message = '\n'.join([
                    'Frames and Falcon2/Falcon3 is not supported, yet.',
                    'Please contact the TranSPHIRE authors!'
                    ])

            else:
                message = '\n'.join([
                    'Camera {0} not known for Software {1} with type {2}.'.format(
                        settings['Input']['Camera'],
                        settings['Input']['Software'],
                        settings['Input']['Type']
                        ),
                    'Please contact the TranSPHIRE authors!'
                    ])

        else:
            message = '\n'.join([
                '{0}: Unknown Type!'.format(settings['Input']['Type']),
                'Please contact the TranSPHIRE authors!'
                ])

    elif settings['Input']['Software'] == 'EPU >=1.9':

        ####
        #
        # Stack
        #
        ####

        if settings['Input']['Type'] == 'Stack':

            if settings['Input']['Camera'] in ('K2', 'K3'):
                return 'rsync --copy-links'

            elif settings['Input']['Camera'] == 'Falcon2' or \
                    settings['Input']['Camera'] == 'Falcon3':
                return 'rsync --copy-links'

            else:
                message = '\n'.join([
                    'Camera {0} not known for Software {1} with type {2}.'.format(
                        settings['Input']['Camera'],
                        settings['Input']['Software'],
                        settings['Input']['Type']
                        ),
                    'Please contact the TranSPHIRE authors!'
                    ])

        ####
        #
        # Frames
        #
        ####

        elif settings['Input']['Type'] == 'Frames':

            if settings['Input']['Camera'] in ('K2', 'K3'):
                message = '\n'.join([
                    'Frames and K2, K3 is not supported in EPU >=1.9',
                    'Please contact the TranSPHIRE authors!'
                    ])

            elif settings['Input']['Camera'] == 'Falcon2' or \
                    settings['Input']['Camera'] == 'Falcon3':
                message = '\n'.join([
                    'Frames and Falcon2/Falcon3 is not supported n EPU >=1.9',
                    'Please contact the TranSPHIRE authors!'
                    ])

            else:
                message = '\n'.join([
                    'Camera {0} not known for Software {1} with type {2}.'.format(
                        settings['Input']['Camera'],
                        settings['Input']['Software'],
                        settings['Input']['Type']
                        ),
                    'Please contact the TranSPHIRE authors!'
                    ])

        else:
            message = '\n'.join([
                '{0}: Unknown Type!'.format(settings['Input']['Type']),
                'Please contact the TranSPHIRE authors!'
                ])

    else:
        message = '\n'.join([
            '{0}: Unknown Software!'.format(settings['Input']['Software']),
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
    if settings['Input']['Software'] == 'Just Stack':
        meta_files = glob.glob('{0}.*'.format(root_name))
        frame_files = glob.glob('{0}*'.format(compare_name_frames))
        return set(meta_files), set(frame_files)
    elif settings['Input']['Software'] == 'Latitude S':

        if settings['Input']['Camera'] in ('Falcon2', 'Falcon3'):
            message = '\n'.join([
                'Falcon2/Falcon3 is not supported for Software {0}.'.format(
                    settings['Input']['Software']
                    ),
                'Please contact the TranSPHIRE authors!'
                ])

        elif settings['Input']['Camera'] in ('K2', 'K3'):
            meta_files = glob.glob('{0}.*'.format(root_name))
            frame_files = glob.glob('{0}*'.format(compare_name_frames))
            return set(meta_files), set(frame_files)

        else:
            message = '\n'.join([
                'Camera {0} for Software {1} not known!'.format(
                    settings['Input']['Camera'],
                    settings['Input']['Software']
                    ),
                'Please contact the TranSPHIRE authors!'
                ])

    elif settings['Input']['Software'] == 'EPU >=1.8':

        if settings['Input']['Camera'] in ('K2', 'K3'):
            meta_files = glob.glob('{0}.*'.format(root_name))
            frame_files = glob.glob('{0}*'.format(compare_name_frames))
            return set(meta_files), set(frame_files)

        elif settings['Input']['Camera'] == 'Falcon2' or \
                settings['Input']['Camera'] == 'Falcon3':
            meta_files = [
                name for name in glob.glob('{0}*'.format(compare_name_meta))
                if 'Fractions' not in name
                ]
            frame_files = glob.glob('{0}*'.format(compare_name_frames))
            return set(meta_files), set(frame_files)

        else:
            message = '\n'.join([
                '{0}: Unknown Camera!'.format(settings['Input']['Camera']),
                'Please contact the TranSPHIRE authors!'
                ])

    elif settings['Input']['Software'] == 'EPU >=1.9':

        if settings['Input']['Camera'] in ('K2'):
            meta_files = glob.glob('{0}*'.format(compare_name_meta))
            frame_files = glob.glob('{0}*'.format(compare_name_frames))
            return set(meta_files), set(frame_files)

        elif settings['Input']['Camera'] == 'K3':
            meta_files = [
                name for name in glob.glob('{0}*'.format(compare_name_meta))
                if 'fractions' not in name
                ]
            frame_files = glob.glob('{0}*'.format(compare_name_frames))
            return set(meta_files), set(frame_files)

        elif settings['Input']['Camera'] == 'Falcon2' or \
                settings['Input']['Camera'] == 'Falcon3':
            meta_files = [
                name for name in glob.glob('{0}*'.format(compare_name_meta))
                if 'Fractions' not in name
                ]
            frame_files = glob.glob('{0}*'.format(compare_name_frames))
            return set(meta_files), set(frame_files)

        else:
            message = '\n'.join([
                '{0}: Unknown Camera!'.format(settings['Input']['Camera']),
                'Please contact the TranSPHIRE authors!'
                ])

    else:
        message = '\n'.join([
            '{0}: Unknown Software!'.format(settings['Input']['Software']),
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
    template = '{0} - Command failed:\n{1}\nfor\n{2}.\nPlease check the logfiles in\n{3}!'
    for file_path in non_zero_list:
        try:
            size = os.path.getsize(file_path)
        except OSError as e:
            raise Exception(
                template.format(
                    str(e),
                    command,
                    file_path,
                    folder
                    )
                )
        else:
            if size == 0:
                raise Exception(
                    template.format(
                        'SIZE ERROR 1',
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
        except OSError as e:
            raise Exception(
                template.format(
                    str(e),
                    command,
                    file_path,
                    folder
                    )
                )
        else:
            if size > 0:
                raise Exception(
                    template.format(
                        'SIZE ERROR 2',
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
                template.format(
                    'Exist error',
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
        print('data', data)
        print('dict_name', dict_name)
        print('file_name', file_name)
        raise

    for (key, dtype) in dtype_dict[dict_name]:
        if dtype not in ('<f8', '<i8'):
            continue

        try:
            last_values_median = np.median(data[key][-lower_median:])
            warning_low, warning_high = settings['Notification']['{0} {1} warning'.format(dict_name, key)].split()
            skip_low, skip_high = settings['Notification']['{0} {1} skip'.format(dict_name, key)].split()
        except KeyError:
            continue
        except Exception as e:
            print('Exception')
            print('lower_median', lower_median)
            print('dict_name', dict_name)
            print('key', key)
            print('data', data)
            print(e)
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
    tu.mkdir_p(os.path.dirname(log_prefix))
    template = '{0}_transphire.{{0}}'.format(log_prefix)

    if os.path.exists(template.format('log')):
        log_prefix_faulty = os.path.join(os.path.dirname(log_prefix), 'FAULTY', os.path.basename(log_prefix))
        tu.mkdir_p(os.path.dirname(log_prefix_faulty))
        template_faulty = '{0}_transphire_{{1}}.{{0}}'.format(log_prefix_faulty)
        idx = 0
        while os.path.exists(template_faulty.format('log', idx)):
            idx += 1
        tu.copy(template.format('log'), template_faulty.format('log', idx))
        tu.copy(template.format('err'), template_faulty.format('err', idx))

    return template.format('log'), template.format('err')
