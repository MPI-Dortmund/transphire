.. include:: abbreviations.rst


Installation
============

Welcome to the installation page of TranSPHIRE.
The installation can be divided into three parts.

    1. :ref:`Installation of TranSPHIRE`
    2. :ref:`Installation of the dependencies`
    3. :ref:`Basic setup TranSPHIRE setup`


Installation of TranSPHIRE
**************************

In order to install TranSPHIRE it is highly recommended to setup an |Anaconda| / |Miniconda| environment. The same installation can be used to install crYOLO and other dependencies later. In case you want to learn more about conda environments: `Manage environments <https://docs.conda.io/projects/conda/en/latest/user-guide/tasks/manage-environments.html>`__.

After successful installation, the |Conda| command should be available.
To make things easier for copy and pasting, the proposed commands utilize bash variables.

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
