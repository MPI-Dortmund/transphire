.. include:: abbreviations.rst

Welcome to TranSPHIRE's documentation!
======================================

TranSPHIRE is an automated pre-processing tool designed for on-the-fly processing during data aquisition.
It is an open source project published under the `GPLv3 license <https://github.com/MPI-Dortmund/transphire/blob/master/LICENSE>`__ and the code is available on `GitHub <https://github.com/MPI-Dortmund/transphire>`__.

TranSPHIRE coveres the inital steps of the |SPA| pipeline.


Pre-processing
**************


    - Motion correction (Outputs can be used to run particle polishing in Relion)
        - |MotionCor2| - |NOTFREE|
        - |Unblur|

    - CTF estimation
        - |SPHIRE| |CTER|
        - |CTFFIND4|
        - |GCtf|

    - Particle picking
        - |SPHIRE| |crYOLO| - |NOTFREE|

    - Particle extraction
        - |SPHIRE| |WINDOW|


Processing
**********


    - 2D classification
        - |SPHIRE| |GPUISAC|

    - 2D class selection
        - |SPHIRE| |Cinderella|

    - 3D initial model estimation
        - |SPHIRE| |RVIPER|

    - 3D refinement
        - |SPHIRE| |MERIDIEN|


Feedback loop
*************


Additionally, TranSPHIRE implements a new ``Feedback loop`` that automatically re-trains and therefore adapts the model used for particle picking to the data set at hand.

    1. Particle picking
    2. Particle extraction
    3. Wait for a number of extracted particles to accumulate
    4. 2D classification
    5. 2D class selection
    6. Class member extraction
    7. Re-training of the picking model
    8. ``1.`` with the re-trained model


Hardware recommendations
************************


Hardware recommendations can be found at the :ref:`hardware-recommendations-page` page.


Installation
************


The installation instructions can be found at the :ref:`installation-page` page.


Tutorial
********


The tutorial can be found at the :ref:`tutorial-page` page.


Contribute
**********


If you want to contribute to the TranSPHIRE project, please checkout the :ref:`how-to-contribute-page` page.


License
*******


TranSPHIRE is an open source project published under the `GPLv3 license <https://github.com/MPI-Dortmund/transphire/blob/master/LICENSE>`__.


Code availability
*****************


The source code is available on `GitHub <https://github.com/MPI-Dortmund/transphire>`__.
