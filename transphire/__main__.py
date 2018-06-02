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

    app = QApplication([])
    app.setStyle('cleanlooks')

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
    main(**parse_args())


if __name__ == '__main__':
    run_package()
