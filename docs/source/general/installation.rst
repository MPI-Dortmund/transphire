.. include:: abbreviations.rst

.. _installation-page:

Installation
============

Welcome to the installation page of TranSPHIRE.
The installation can be divided into three parts.

    1. :ref:`Installation of TranSPHIRE`
    2. :ref:`Installation of the dependencies`
    3. :ref:`Basic TranSPHIRE setup`


Installation of TranSPHIRE
**************************

In order to install TranSPHIRE it is highly recommended to setup an |Anaconda| / |Miniconda| environment.
The same installation can be used to install crYOLO and other dependencies later.
In case you want to learn more about |conda| environments: `Manage environments <https://docs.conda.io/projects/conda/en/latest/user-guide/tasks/manage-environments.html>`__.

After successful installation, the |conda| command should be available.
To make things easier for copy and pasting, the proposed commands utilize bash variables.
The installation does usually not take longer than a few minutes.

0. Specify Necessary variables

>>> TRANSPHIRE_ENV_NAME=transphire

1. Create a |Conda| environment

>>> conda create -n ${TRANSPHIRE_ENV_NAME} python=3.6 pyqt=5

2. Activate the environment

>>> conda activate ${TRANSPHIRE_ENV_NAME}

.. note::

    For older versions of conda it might be:

    >>> source activate ${TRANSPHIRE_ENV_NAME}

3. Install TranSPHIRE

>>> pip install transphire


4. Test the installation

>>> transphire --version


Installation of the dependencies
********************************

TranSPHIRE is a wrapper for already existing software packages available.
Therefore, it is necessary to install the dependencies separately.
In the future, we will work on a dependency installer tool.


Utilities and packages
^^^^^^^^^^^^^^^^^^^^^^

- |SPHIRE| version >= 1.4
- |IMOD| version >= 4.9

.. note::
    The |SPHIRE| installation automatically installs all necessary tools for

    - Particle extraction
    - 3D initial model estimation
    - 3D refinement

    and installs utility programs from the EMAN2 package.

.. note::
    The |SPHIRE| installation needs one additional command to function properly:

    >>> bash ${SPHIRE_INSTALL_DIR}/utils/replace_shebang.sh

    This script will replace the `shebang <https://en.wikipedia.org/wiki/Shebang_(Unix)>`__ line of the |SPHIRE| executables to avoid collision with other python interpreters in your PATH.


Motion correction
^^^^^^^^^^^^^^^^^

- |MotionCor2| version >= 1.0.0 - |NOTFREE|
- |Unblur| cisTEM version >= 1.0.0-beta


CTF estimation
^^^^^^^^^^^^^^

- |SPHIRE| |CTER|
- |CTFFIND4| version >= 4.1.8
- |GCtf| version >= 1.06

.. note::
    GCtf version 1.18 is sometimes behaving different than expected.
    Use with caution.


Particle picking
^^^^^^^^^^^^^^^^

- |SPHIRE| |crYOLO| version >= 1.0.4 - |NOTFREE|


2D classification
^^^^^^^^^^^^^^^^^

- |SPHIRE| |GPUISAC| version >= 2.2


2D class selection
^^^^^^^^^^^^^^^^^^

- |SPHIRE| |Cinderella| version >= 0.3.1


.. include:: ../tutorial/introduction.rst
