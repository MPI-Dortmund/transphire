Basic TranSPHIRE setup
**********************

The following instructions are suppose to run only once at the very beginning after installation of TranSPHIRE.


Command line arguments
^^^^^^^^^^^^^^^^^^^^^^


The command line arguments of TranSPHIRE can additionally be controlled by environmental variables.
This is especially useful if TranSPHIRE should be used in some ``environmental module`` environment.


+------------------------+----------------------------------------+---------------------------+-------------------------------+
| Commmandline           | Description                            | Default value             | Environmental                 |
|                        |                                        |                           |                               |
| options                |                                        |                           | variable                      |
+------------------------+----------------------------------------+---------------------------+-------------------------------+
| \-\-root_directory     | TranSPHIRE root directory.             | The users home directory. | TRANSPHIRE_ROOT_DIRECTORY     |
|                        |                                        |                           |                               |
|                        | This is the directory where            |                           |                               |
|                        |                                        |                           |                               |
|                        | TranSPHIRE will be started.            |                           |                               |
|                        |                                        |                           |                               |
|                        | Every provided relative directory      |                           |                               |
|                        |                                        |                           |                               |
|                        | and file path will be respective       |                           |                               |
|                        |                                        |                           |                               |
|                        | to this directory.                     |                           |                               |
+------------------------+----------------------------------------+---------------------------+-------------------------------+
| \-\-settings_directory | TranSPHIRE settings directory.         | .transphire_settings in   | TRANSPHIRE_SETTINGS_DIRECTORY |
|                        |                                        |                           |                               |
|                        | This is the directory where            | the root_directory        |                               |
|                        |                                        |                           |                               |
|                        | the settings and templates             |                           |                               |
|                        |                                        |                           |                               |
|                        | are stored.                            |                           |                               |
+------------------------+----------------------------------------+---------------------------+-------------------------------+
| \-\-mount_directory    | TranSPHIRE mount directory.            | .transphire_mounts in     | TRANSPHIRE_MOUNT_DIRECTORY    |
|                        |                                        |                           |                               |
|                        | In case users need to mount            | the root_directory        |                               |
|                        |                                        |                           |                               |
|                        | pre-defined mount points               |                           |                               |
|                        |                                        |                           |                               |
|                        | themselves, those are located          |                           |                               |
|                        |                                        |                           |                               |
|                        | in this directory.                     |                           |                               |
+------------------------+----------------------------------------+---------------------------+-------------------------------+
| \-\-font               | Font size to use within the            | 5 or read from settings   | TRANSPHIRE_FONT_SIZE          |
|                        |                                        |                           |                               |
|                        | TranSPHIRE GUI. Most widgets           | if not provided.          |                               |
|                        |                                        |                           |                               |
|                        | are scaled accordingly.                |                           |                               |
+------------------------+----------------------------------------+---------------------------+-------------------------------+
| \-\-adjust_width       | Scaling factor for the widget          | 1 or read from settings   | TRANSPHIRE_ADJUST_WIDTH       |
|                        |                                        |                           |                               |
|                        | width. >1 will make the widgets        | if not provided.          |                               |
|                        |                                        |                           |                               |
|                        | larger; <1 will make the widgets       |                           |                               |
|                        |                                        |                           |                               |
|                        | smaller.                               |                           |                               |
+------------------------+----------------------------------------+---------------------------+-------------------------------+
| \-\-adjust_height      | Scaling factor for the widget          | 1 or read from settings   | TRANSPHIRE_ADJUST_HEIGTH      |
|                        |                                        |                           |                               |
|                        | width. >1 will make the widgets        | if not provided.          |                               |
|                        |                                        |                           |                               |
|                        | larger; <1 will make the widgets       |                           |                               |
|                        |                                        |                           |                               |
|                        | smaller.                               |                           |                               |
+------------------------+----------------------------------------+---------------------------+-------------------------------+
| \-\-n_feedbacks        | Maximum number of allowed feedbacks.   | 10                        | TRANSPHIRE_N_FEEDBACKS        |
+------------------------+----------------------------------------+---------------------------+-------------------------------+
| \-\-edit_settings      | Open the "Default settings" dialog.    | --                        | --                            |
+------------------------+----------------------------------------+---------------------------+-------------------------------+
| \-\-version            | Show version information.              | --                        | --                            |
+------------------------+----------------------------------------+---------------------------+-------------------------------+
| \-\-kill               | Kill open, dead or stalling TranSPHIRE | --                        | --                            |
|                        |                                        |                           |                               |
|                        | runs.                                  |                           |                               |
+------------------------+----------------------------------------+---------------------------+-------------------------------+
