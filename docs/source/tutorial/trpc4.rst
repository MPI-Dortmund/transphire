.. include:: ../general/abbreviations.rst

TRPC4 tutorial data set
***********************

To demonstrate how TranSPHIRE works, a TRPC4 tutorial test data set can be downloaded here:
https://ftp.gwdg.de/pub/misc/sphire/TranSPHIRE/TranSPHIRE_1.5_trpc4_tutorial.zip

Unzip the downloaded file ``TranSPHIRE_1.5_trpc4_tutorial.zip``:

>>> tar -xf TranSPHIRE_nature_communications.zip

This extracts a folder called ``TranSPHIRE_1.5_trpc4_tutorial.zip``.

The following instructions can also be found in the included ``README.rst``.


Operating systems
*****************

The software has been tested on the following operating systems:

Ubuntu 18
Ubuntu 20
CentOS 7


Software dependencies
*********************

TranSPHIRE is dependent on different programs:


Included in this zip file
+++++++++++++++++++++++++

|TranSPHIRE| version 1.5.0
|SPHIRE| version 1.3_transphire
|SPHIRE| |GPUISAC| version 1.1


Not included in this zip file
+++++++++++++++++++++++++++++

|ANACONDA| / |MINICONDA| environment -- https://www.anaconda.com/
|IMOD| version 4.9 -- https://bio3d.colorado.edu/imod/ 
|CHIMERAX| version 1.0 -- https://www.cgl.ucsf.edu/chimerax/
|MotionCor2| version 1.3.2 -- https://emcore.ucsf.edu/ucsf-software
|Unblur| cisTEM version 1.0.0-beta -- https://cistem.org/
|CTFFIND4| version 4.1.14 -- https://grigoriefflab.umassmed.edu/ctf_estimation_ctffind_ctftilt
|GCtf| version 1.06 -- https://www2.mrc-lmb.cam.ac.uk/research/locally-developed-software/zhang-software/
|SPHIRE| |crYOLO| version 1.7.4 -- http://cryolo.readthedocs.io/
|SPHIRE| |Cinderella| version 0.7.0 -- http://sphire.mpg.de/wiki/doku.php?id=auto_2d_class_selection


Required non-standard hardware
*****************

- Nvidia GPU


Installation
************

The installation of TranSPHIRE takes about 5 to 20 minutes, depending on the download speed.


**Install SPHIRE_v1.3_transphire**

>>> bash ./install_sphire_v1.3_transphire.sh


**Install GPU ISAC**

Make sure that you have CUDA available then run:

>>> bash ./install_gpu_isac.sh


**Create a new conda environment for TranSPHIRE**

>>> bash ./install_transphire.sh

Put the TranSPHIRE installation in your PATH

>>> export PATH=$(realpath sphire_v1.3_transphire/envs/transphire/bin):${PATH}


**Install other dependencies**

Please install the other dependencies from the *Software dependencies* section.


Demo
****

A TRPC4 Demo data set containig 120 micrograph movies is coming within the ZIP file.

The expected output can be found in the *TRPC4_demo_results_expected* folder.

The expected runtime of the demo data is:

- 4.5 hours without 3D refinement on 6 cores.
- 5.5 hours with 3D refinement on 6 cores.

On a "normal" GPU machine:

- Intel(R) Xeon(R) CPU E5-2643 v4 @ 3.40Ghz
- 6 cores / hyperthreading 12 cores
- 128 GB RAM
- 2x GeForce RTX 2080 Ti

Instructions
++++++++++++

A more detailed version of the instructions is currently in preparation at `transphire.readthedocs.io`.


1. Open the TranSPHIRE GUI

>>> transphire --root_directory $(realpath .)

2. Click the **Settings** tab.

3. Click the **Input** tab.

  - *Input project path for frames*: click the folder icon and choose the *TRPC4_demo* folder
  - *Input project path for jpg*: click the folder icon and choose the *TRPC4_demo* folder
  - *Input frames extension*: tiff
  - *number of frames*: 50

4. Click the **Output** tab.

  - *Project name*: TRPC4_demo_results
  - *Rename prefix*: TRPC4_
  - *Rename suffix*: _demo

5. Click the **Global** tab.

  - *Pixel size*: 0.85
  - *Cs*: 0.001
  - *Gain*: click the folder icon and choose the *TRPC4_demo/gain_ref.mrc* file
  - *Protein radius*: 120

6. Click the **Copy** tab.

  - *Delete data after Import*: Symlink

7. Click the **Path** tab.


   Provide the file path values from your downloaded dependencies.

8. Click the **Motion** tab.

  - *-FmDose*: 1.77
  - *-Patch*: 5 5 20

9. Click the **CTF** tab.

  - *--f_start*: 40
  - *--f_stop*: 4

10. Click the **Picking** tab.

  - *--conf**: click the folder icon and choose the *TRPC4_demo/config_2020_07.json* file
  - *--weights**: click the folder icon and choose the *TRPC4_demo/gmodel_phosnet_202005_N63_c17.h5* file

11. Click the **Class2d** tab and go to the **Advanced** tab.

  - *Nr. Particles*: 5000
  - *--img_per_grp*: 50
  - *--minimum_grp_size*: 30
  - *MPI processes*: Choose the number of your physical cores available.

12. Click the **Select2d** tab.

  - *--weights*: click the folder icon and choose the *TRPC4_demo/config_2020_07.json* file

13. Click the **Auto3d** tab.

  - *--mpi_procs*: Choose the number of your physical cores available.
  - *--mpi_submission_command*: bash
  - *--mpi_submission_template*: click the folder icon and choose the *submission_bash_template.sh* file
  - *--memory_per_node*: Adjust depending on your system
  - *--mol_mass*: 900
  - *--symmetry*: c4
  - *input_volume*: click the folder icon and choose the *TRPC4_reference.hdf* file
  - *Use SSH*: False
  **Advanced** 
  - *Minimum classes*: 0
  - *Minimum particles*: 0

14. Click the **Start** button.
