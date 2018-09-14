#! /usr/bin/env python
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
import sys
import os
import json
import argparse
import re
try:
    from PyQt4.QtGui import QApplication
except ImportError:
    from PyQt5.QtWidgets import QApplication

import transphire
from transphire import transphire_utils as tu
from transphire.mainwindow import MainWindow
from transphire.loadwindow import DefaultSettings


def main(font, root_directory, settings_directory, mount_directory, adjust_width, adjust_height, edit_settings):
    """
    Run the GUI.

    Arguments:
    font - Default value for the font size
    adjust_width - Value to adjust the width of buttons
    adjust_height - Value to adjust the height of buttons
    edit_settings - If True, open the default settings dialog

    Return:
    None
    """
    # Start the GUI from the users home directory.
    os.chdir(root_directory)

    QApplication.setStyle('fusion')
    app = QApplication([])

    # Create default folders
    tu.mkdir_p(settings_directory)
    tu.mkdir_p(mount_directory)

    # Load default font settings for the default settings dialog
    if font is None:
        try:
            with open('{0}/content_Font.txt'.format(settings_directory), 'r') as file_r:
                settings = json.load(file_r)
            app.setStyleSheet(
                tu.look_and_feel_small(
                    app=app,
                    font=settings[0][0]['Font'][0]
                    )
                )
        except FileNotFoundError:
            pass
    else:
        app.setStyleSheet(tu.look_and_feel_small(app=app, font=font))

    # Get default settings 0: content 
    IDX_CONTENT = 0
    content = DefaultSettings.get_content_default(
        edit_settings=edit_settings,
        apply=False,
        settings_folder=settings_directory
        )[IDX_CONTENT]

    # Apply font settings to application
    app.setStyleSheet(
        tu.look_and_feel(
            app=app,
            font=font,
            adjust_width=adjust_width,
            adjust_height=adjust_height,
            default=content['Font']
            )
        )

    # Load content for the GUI
    content_gui = tu.get_content_gui(content=content)

    # Initilise and show GUI
    gui = MainWindow(
        content_gui=content_gui,
        content_pipeline=content['Pipeline'],
        settings_folder=settings_directory,
        mount_directory=mount_directory,
        version=transphire.__version__
        )
    gui.show()

    sys.exit(app.exec_())


def parse_args():
    """
    Handle command line arguments.

    Arguments:
    None

    Return:
    Dictionary of command line arguments
    """

    parser = argparse.ArgumentParser(description='Cryo-EM post-datacollection pipeline')
    parser.add_argument(
        '--root_directory',
        default=os.environ['HOME'],
        type=str,
        nargs='?',
        help='Directory where transphire is started'
        )
    parser.add_argument(
        '--settings_directory',
        default='.transphire_settings',
        type=str,
        nargs='?',
        help='Folder containing the settings'
        )
    parser.add_argument(
        '--mount_directory',
        default='mounted',
        type=str,
        nargs='?',
        help='Folder containing the mount points'
        )
    parser.add_argument(
        '--font',
        default=None,
        type=float,
        nargs='?',
        help='Font size in px (default 20)'
        )
    parser.add_argument(
        '--adjust_width',
        default=None,
        type=float,
        nargs='?',
        help='Width adjustment value (default 1)'
        )
    parser.add_argument(
        '--adjust_height',
        default=None,
        type=float,
        nargs='?',
        help='Height adjustment value (default 1)'
        )
    parser.add_argument(
        '--edit_settings',
        const='edit_settings',
        default=False,
        action='store_const',
        help='Show settings dialog (default False)'
        )

    return vars(parser.parse_args())


def run_package():
    """
    Entry point for the transphire package
    """
    check_running()
    check_update()
    main(**parse_args())


def check_update():
    """
    Check for TranSHPIRE updates on PyPi
    """
    pip_path = '{0}/pip'.format([path for path in sys.path if '/bin' in path][0])
    current_version = transphire.__version__
    version_string = os.popen("{0} install transphire== 2>&1".format(pip_path)).read()
    message_insert = None
    message_template = '{{0}}\nUse:\n"{0} install transphire --upgrade"\nto update!\nTo check the changes visit:\n{1}!'.format(
        pip_path,
        "http://sphire.mpg.de/wiki/doku.php?id=downloads:transphire_1"
        )
    try:
        latest_version = re.search('.* ([0-9]+\.[0-9]+\.[0-9]+)\).*', version_string).group(1)
    except AttributeError:
        print('Could not check for updates! Please check your internet connection or for erros in the command:  {0}'.format(version_string))
        print('If you have questions, please contact the TranSPHIRE authors.')
    else:
        if current_version == 'XX.XX.XX':
            print('Available version: {0}'.format(latest_version))
            return None
        print('Current version: {0} -- Available version: {1}'.format(current_version, latest_version))
        vers_1, vers_2, vers_3 = current_version.split('.')
        latest_vers_1, latest_vers_2, latest_vers_3 = latest_version.split('.')
        if int(latest_vers_1) > int(vers_1):
            message_insert = 'Major TranSPHIRE update available!\nYou might need to do more than just the pip update procedure!'
        elif int(latest_vers_1) == int(vers_1) and \
                int(latest_vers_2) > int(vers_2):
            message_insert = 'TranSPHIRE update available!\nTranSPHIRE got additional functionalities!'
        elif int(latest_vers_1) == int(vers_1) and \
                int(latest_vers_2) == int(vers_2) and \
                int(latest_vers_3) > int(vers_3):
            message_insert = 'TranSPHIRE bugfix update available!'
        else:
            print('No updates available')

    if message_insert is None:
        pass
    else:
        message = message_template.format(message_insert)
        print(message)
        while True:
            answer = input('Do you want to quit here to do the update? [y/n]\n')
            if answer not in ['y', 'n']:
                print('Answer needs to be y or n')
                continue
            else:
                break
        if answer == 'y':
            sys.exit()
        else:
            pass


def check_running():
    """
    Check if a TranSPHIRE run is already running

    Arguments:
    None

    Returns:
    None
    """
    pids = [pid for pid in os.listdir('/proc') if pid.isdigit()]
    running_instances = 0

    for pid in pids:
        try:
            with open(os.path.join('/proc', pid, 'cmdline'), 'rb') as read:
                file_read = read.read()
        except IOError: # proc has already terminated
            continue
        else:
            if b'/bin/transphire' in file_read:
                running_instances += 1
            else:
                pass

    if running_instances > 1:
        while True:
            answer = input(
                '\n'.join([
                    'Another TranSPHIRE instance is already opened!',
                    'Please double check if another job is running, as running multiple instances will crash the jobs',
                    'Do you want to continue? [y/n]\n'
                    ])
                )
            if answer not in ['y', 'n']:
                print('Answer needs to be y or n')
                continue
            elif answer == 'n':
                sys.exit()
            elif answer == 'y':
                break
            else:
                raise IOError('Answer not known {0}'.format(answer))
    else:
        pass


if __name__ == '__main__':
    check_running()
    run_package()
