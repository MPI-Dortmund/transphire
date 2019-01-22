[![DOI](https://zenodo.org/badge/DOI/10.5281/zenodo.2546030.svg)](https://doi.org/10.5281/zenodo.2546030)


A tutorial is available in the wiki.

[Wiki](https://github.com/MPI-Dortmund/transphire/wiki)


# Transphire

Cryo-EM on the fly processing pipeline.

If you have any questions contact:  
markus.stabrin@mpi-dortmund.mpg.de

## External programs

To enjoy the full functionaly of TranSPHIRE, install the following programs:

IMOD 4.9: http://bio3d.colorado.edu/imod  
MotionCor2 1.0.0/1.0.5/1.1.0: http://msg.ucsf.edu/em/software/motioncor2.html  
SumMovie 1.0.2: http://grigoriefflab.janelia.org/unblur  
CTER 1.0: http://sphire.mpg.de  
CTFFIND 4.1.8/4.1.10: http://grigoriefflab.janelia.org/ctf  
Gctf 1.06,1.18: https://www.mrc-lmb.cam.ac.uk/kzhang  
crYOLO 1.0.4/1.0.5/1.1.0: http://sphire.mpg.de  

## Installation

TranSPHIRE needs an environment that includes Python version 3.6, QT version 5 and PyQt version 5.

### Installation using Anaconda

https://www.anaconda.com/download/#linux

Create a new virtual environment

> conda create -n transphire python=3.6 pyqt=5

Activate the environment

> source activate transphire

or

> conda activate transphire

Depending on your installation of anaconda.

Install transphire

> pip install transphire


### Installation inside your own environment that matches the requirements

Install transphire

> pip install transphire


## Run TranSPHIRE

Make sure, that you have your transphire environment active.
If you start TranSPHIRE for the first time:

> transphire --edit\_settings

In case the appearing window is too large for your screen, adjust the font size (default 20).  
For example:

> transphire --edit\_settings --font 8

First got to the **TranSPHIRE settings** tab and after that the **Font** tab.
Adjust the *Font* value.
If necessary, the other options can be adjusted at a later point, after the GUI is opened.

Open the other tabs and adjust the settings according to your system.

Close the dialog and the GUI will open.

In the future, you only need to run:

> transphire

If you want to run TranSPHIRE, fill in the tabs from left to right (General to CTF) and press the Start button.

A more detailed tutorial will be available soon.

## FAQ

Please refere to this link: [https://github.com/MPI-Dortmund/transphire/wiki/FAQ](https://github.com/MPI-Dortmund/transphire/wiki/FAQ)
