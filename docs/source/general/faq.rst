.. include:: abbreviations.rst

.. toctree::
    :maxdepth: 3
    :caption: Contents:

    faq

FAQ
===


In addition to the TranSPHIRE related questions, we provide an in-depth |SPHIRE| tutorial on our |SPHIRE| website: `Tutorial <http://sphire.mpg.de/wiki/doku.php?id=howto:download_latest>`__.
There, not only |SPHIRE| related topics are discussed, but also general tips and tricks for |SPA|.


How to create a template for faster setup?
******************************************

You can find more information here: :ref:`Basic TranSPHIRE setup`.


What kind of computer should I use?
***********************************

TranSPHIRE is designed to run on a Linux system.
The better the hardware is, the faster the processing will be.
This also allows to stay on-the-fly for faster data acquisition schemes.

You can find more information here: :ref:`hardware-recommendations-page`.


How do I measure my particle radius in pixels?
**********************************************

There are mutliple ways of doing this, but we recommend to use `e2display.py` from the |EMAN2| package.

>>> e2display.py example_image.mrc

Press the **Middle mouse button** and the **Meas** tab.
Keep the ``A/Pix`` value to ``1.0`` and click+drag a line on the micrograph.
The ``Len`` value shows the distance in pixels.

If the particles do not have a globular shape you should choose a radius that is a wider than the measured one to allow for a more liberal centering.


What box size should I use?
***************************

A list of good box sizes can be found `on the EMAN2 box size recommendation website <https://blake.bcm.edu/emanwiki/EMAN2/BoxSize>`__.

The recommendation is to use a box size of 1.5x to 2x of the longest particle axis (3x to 4x of the radius).

By default, TranSPHIRE will use the next bigger value of a "good" box size from the list after multiplying the provided protein radius by 3.

.. note::
    Example 1:

    | particle_radius = 100
    | box_size = 300   # particle_radius * 3.
    | final_box_size = 300   # 300 is in the list of good values.

    Example 2:

    | particle_radius = 101
    | box_size = 303   # parrticle_radius * 3.
    | final_box_size = 320   # 303 is not in the list of good values, the next larger good value is 320.
