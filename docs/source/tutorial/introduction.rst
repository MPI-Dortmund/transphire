.. include:: ../general/abbreviations.rst

Presentations
*************

2020 10 29 - SBGrid Consortium
`YouTube <https://www.youtube.com/watch?v=RlAxtrRrnlQ>`_

Basic TranSPHIRE setup
**********************

The following instructions are suppose to run only once at the very beginning after installation of TranSPHIRE.


Command line arguments
^^^^^^^^^^^^^^^^^^^^^^


TranSPHIRE offers some command line arguments that control its basic behaviour.
Most of the command line arguments can additionally be controlled by environmental variables.
This is especially useful if TranSPHIRE is used in an ``environmental module`` environment.

+-------------------------------+----------------------------------------+---------------------------+
| Commmandline options /        | Description                            | Default value             |
|                               |                                        |                           |
| Environmental variable        |                                        |                           |
+===============================+========================================+===========================+
| -\\-root_directory            | TranSPHIRE root directory.             | The users home directory. |
|                               |                                        |                           |
| TRANSPHIRE_ROOT_DIRECTORY     | This is the directory where            |                           |
|                               |                                        |                           |
|                               | TranSPHIRE will be started.            |                           |
|                               |                                        |                           |
|                               | Every provided relative directory      |                           |
|                               |                                        |                           |
|                               | and file path will be respective       |                           |
|                               |                                        |                           |
|                               | to this directory.                     |                           |
+-------------------------------+----------------------------------------+---------------------------+
| -\\-settings_directory        | TranSPHIRE settings directory.         | transphire_settings in    |
|                               |                                        |                           |
| TRANSPHIRE_SETTINGS_DIRECTORY | This is the directory where            | the root_directory        |
|                               |                                        |                           |
|                               | the settings and templates             |                           |
|                               |                                        |                           |
|                               | are stored.                            |                           |
+-------------------------------+----------------------------------------+---------------------------+
| -\\-mount_directory           | TranSPHIRE mount directory.            | transphire_mounts in      |
|                               |                                        |                           |
| TRANSPHIRE_MOUNT_DIRECTORY    | In case users need to mount            | the root_directory        |
|                               |                                        |                           |
|                               | pre-defined mount points               |                           |
|                               |                                        |                           |
|                               | themselves, those are located          |                           |
|                               |                                        |                           |
|                               | in this directory.                     |                           |
+-------------------------------+----------------------------------------+---------------------------+
| -\\-font                      | Font size to use within the            | 5 or read from settings   |
|                               |                                        |                           |
| TRANSPHIRE_FONT_SIZE          | TranSPHIRE GUI. Most widgets           | if not provided.          |
|                               |                                        |                           |
|                               | are scaled accordingly.                |                           |
+-------------------------------+----------------------------------------+---------------------------+
| -\\-adjust_width              | Scaling factor for the widget          | 1 or read from settings   |
|                               |                                        |                           |
| TRANSPHIRE_ADJUST_WIDTH       | width. >1 will make the widgets        | if not provided.          |
|                               |                                        |                           |
|                               | larger; <1 will make the widgets       |                           |
|                               |                                        |                           |
|                               | smaller.                               |                           |
+-------------------------------+----------------------------------------+---------------------------+
| -\\-adjust_height             | Scaling factor for the widget          | 1 or read from settings   |
|                               |                                        |                           |
| TRANSPHIRE_ADJUST_HEIGHT      | width. >1 will make the widgets        | if not provided.          |
|                               |                                        |                           |
|                               | larger; <1 will make the widgets       |                           |
|                               |                                        |                           |
|                               | smaller.                               |                           |
+-------------------------------+----------------------------------------+---------------------------+
| -\\-n_feedbacks               | Maximum number of allowed feedbacks.   | 10                        |
|                               |                                        |                           |
| TRANSPHIRE_N_FEEDBACKS        |                                        |                           |
+-------------------------------+----------------------------------------+---------------------------+
| -\\-edit_settings             | Open the "Default settings" dialog.    | --                        |
+-------------------------------+----------------------------------------+---------------------------+
| -\\-version                   | Show version information.              | --                        |
+-------------------------------+----------------------------------------+---------------------------+
| -\\-kill                      | Kill open, dead or stalling TranSPHIRE | --                        |
|                               |                                        |                           |
|                               | runs.                                  |                           |
+-------------------------------+----------------------------------------+---------------------------+



Basic setup and templates
^^^^^^^^^^^^^^^^^^^^^^^^^


It is possible to setup default settings and templates for the TranSPHIRE pipeline.
To enter the setup area type:

>>> transphire --edit_settings


And the GUI will open:


.. image:: ../img/Screenshot\ 2020-09-03\ at\ 10.34.03.png
    :align: center
    :width: 350

The first level Tab bar groups the different settings.

- Settings affected by templates

    - External software:
      Contains all settings related for the software packages used for processing.
    - Internal settings:
      Settings related to the TranSPHIRE pipeline itself.

- Settings shared throughout templates

    - TranSPHIRE settings:
      Settings that should be available to every template.


Program paths
-------------

Click on **TranSPHIRE settings -> Path -> Current**.


.. image:: ../img/Screenshot\ 2020-09-03\ at\ 11.01.54.png
    :align: center
    :width: 350


Provide the full PATH to the executables.
You can press **Ctrl + Return** while editing to open a *File Open Dialog*.
If you are not sure where the files are located, but you can execute them in the terminal type:

>>> which desired_command

Otherwise contact your system administrator.


.. image:: ../img/Screenshot\ 2020-09-03\ at\ 11.57.13.png
    :align: center
    :width: 350


.. note::
    Please provide the mpirun command that is shipped with the |SPHIRE| installation.


After the information has been provided, click the **Save settings** button.


.. image:: ../img/Screenshot\ 2020-09-03\ at\ 12.14.36.png
    :align: center
    :width: 350


Mount points
------------


Next provide the mount point information to tell TranSPHIRE where possible data is located or where to copy created data to.
Click on **TranSPHIRE settings -> Mount**.
By default there is a mount point for external hard drives present, but additional mount points need to be added in order to function properly.
To mount external Machines, Linux `mount <https://linux.die.net/man/8/mount>`__.mount_protocol executables are used.


.. image:: ../img/Screenshot\ 2020-09-03\ at\ 12.47.46.png
    :align: center
    :width: 350


There are two possible ways to deal with mount points: *Fixed folder mount points* and *On demand mount points*.

Fixed folder mount points
+++++++++++++++++++++++++

Click on the **Add mount point** button and a new mount point entry ``Mount 2`` appears.
You need to provide the following entries:

- Mount name
    - Name of the mount point within the TranSPHIRE GUI.

- IP
    - IP adress of the remote device.
      This is necessary to assure the correct execution of the Auto3D command via SSH.

- Folder
    - Mount entry folder name of the remote device.

- Typ
    - Choose if the mount point is used to import the data or if it is a destination for either processing or backup.

- Fixed folder
    - Folder of the fixed mount point on the local device.


.. note::

    Our cluster is called ``CLEM`` and is mounted on the local device at the location ``/home/shared/mounted/CLEM``.
    The IP is ``clem.mpi-dortmund.mpg.de`` and the mounted folder is ``/home/stabrin``.
    Because it is a cluster for data processing, the Typ is ``Copy_to_work``.
    The Fixed folder location is ``/home/shared/mounted/CLEM``.

    Therefore our configuration is:

    - **Mount name**: CLEM
    - **IP**: clem.mpi-dortmund.mpg.de
    - **Folder**: /home/stabrin
    - **Typ**: Copy_to_work
    - **Fixed folder**: /home/shared/mounted/CLEM

    .. image:: ../img/Screenshot\ 2020-09-03\ at\ 15.20.49.png
        :align: center
        :width: 350


On demand mount points
++++++++++++++++++++++

Click on the **Add mount point** button and a new mount point entry ``Mount 2`` appears.
To fill out the respective entries, you should talk to your system administrator.
You need to provide the following entries:

- Mount name
    - Name of the mount point within the TranSPHIRE GUI.

- Protocol
    - Mount protocol.

- Protocol version
    - The version of the protocol.

- sec
    - The security protocol used for the mount point. If your ``sec`` value is ``krb5``, the cruid option is automatically set to the user.
      If you need a different behaviour, please contact markus.stabrin@mpi-dortmund.mpg.de.

- gid
    - The mount group.

- Domain
    - Domain of the mount point.

- IP
    - IP adress of the remote device.
      This is necessary to assure the correct execution of the Auto3D command via SSH.

- Folder
    - Mount entry folder name of the remote device.

- Folder from root
    - Path to the folder specified in ``Folder`` from the root directory of the remote device.

- Need folder extension?
    - Set to True, to allow dynamic point entries.
      See the note for an example.

- Default user
    - Default user to fill in for mounting.
      This way only the password needs to be provided.
      Useful for computers where the mount user does not change.

- Is df giving the right quota?
    - The Linux command ``df`` provides information about the disc occupancy of mount points.
      However, for file systems that use a quota management this value is usually not correct.
      If in doubt, leave the settings to ``True``.

- Target UID exists here and on target?
    - For domain user managed computers.
      If set to ``True``, the provided user/password combination will be used to run an ``ls`` command on the local machine to provide a sanity check.

- Need sudo for mount?
    - **WARNING**: Providing root passwords is not ideal.
      We would recommended to use ``cifs`` mount points and allow for password-less sudo rights for ``mount.cifs``.


- Need sudo for copy?
    - **WARNING**: Use this with caution, a shared account for the TranSPHIRE runs is not recommended.
      If you use a shared "Transfer" account for the dedicated TranSPHIRE machine, the root password needs to be provided at the beginning of the session to allow for copy of the data to the mount points.

- SSH address
    - SSH address used to calculate the quota if ``Is df giving the right quota`` is set to False.

- Quota command
    - Command to calculate the quota on the remote device.

- Quota / TB
    - **Deprecated** will be removed in the next versions.

- Typ
    - Choose if the mount point is used to import the data or if it is a destination for either processing or backup.

- Fixed folder
    - Folder of the fixed mount point on the local device.


.. note::

    The current user is ``stabrin`` and the authentification mechanism works with a ``kerberos ticket``.
    Our cluster is called ``CLEM``.
    The mount protocol is ``cifs`` and the version is ``3.0``.
    The sec protocol is ``krb5``.
    ``stabrin`` is a member of the group ``32000`` ad the domain is ``mpi-dortmund.mpg.de``.
    The mount IP entry point is ``//clem.mpi-dortmund.mpg.de/beegfs`` and the mount folder is ``/home/``.
    The path from root to the mount folder is ``/beegfs`` resulting in ``/beegfs/home/`` on the remote device.
    Since every user has its own separate home directory on ``CLEM`` and we want to allow for dynamic mounting, we have ``Need folder extension?`` set to ``True``.
    This way we can provide ``stabrin`` as the folder extension during mounting to mount ``/beegfs/home/stabrin``.
    Additionally, the ``Target UID exists here and on target`` and we change the setting to ``False`` as well as the ``Typ`` to ``Copy_to_work``.

    Therefore our configuration is:

    .. image:: ../img/Screenshot\ 2020-09-03\ at\ 16.15.17.png
        :align: center
        :width: 350


Create templates
++++++++++++++++


In order to create setting templates you need to click the **Load template** button.

.. image:: ../img/Screenshot\ 2020-09-03\ at\ 16.39.59.png
    :align: center
    :width: 350


- Drop-down widget:
  You can choose the template here.

- New template:
  You can create a new and empty template entry.

- Copy current template:
  Create a new template, but the settings are identical to the template chosen in the drop-down widget.

- Remove current template:
  Remove the currently selected template.

- Choose current template:
  Choose the current template in order to change its settings.


Click on **New template** and provide a name like ``Tutorial_template`` for your new template and set **Choose current template**.
The text next to the **Load template** button indicates that the correct template is active.

.. image:: ../img/Screenshot\ 2020-09-03\ at\ 16.53.52.png
    :align: center
    :width: 350

Now adjust the settings to match the needs for your facility.
This helps especially beginner users to avoid making errors during setup.
