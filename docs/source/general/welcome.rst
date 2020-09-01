.. include:: abbreviations.rst

Welcome to TranSPHIRE's documentation!
======================================

TranSPHIRE is an automated pre-processing tool designed for on-the-fly processing during data aquisition and coveres the inital steps of the |SPA| pipeline:

**Pre-processing**

    - Motion correction (Outputs can be used to run particle polishing in Relion)
        - MotionCor2 (Not free for commercial use)
        - Unblur

    - CTF estimation
        - SPHIRE CTER
        - CTFFIND
        - GCtf

    - Particle picking
        - SPHIRE crYOLO (Not free for commercial use)

    - Particle extraction
        - SPHIRE sp_window.py

**Processing**

    - 2D classification
        - SPHIRE GPU ISAC

    - 2D class selection
        - SPHIRE Cinderella

    - 3D initial model estimation
        - SPHIRE RVIPER

    - 3D refinement
        - SPHIRE MERIDIEN

Additionally, TranSPHIRE implements a new ``Feedback loop`` that automatically re-trains and therefore adapts the model used for particle picking to the data set at hand.

**Feedback loop**

    1. Particle picking
    2. Particle extraction
    3. Wait for a number of extracted particles to accumulate
    4. 2D classification
    5. 2D class selection
    6. Class member extraction
    7. Re-training of the picking model
    8. ``1.`` with the re-trained model

