.. include:: abbreviations.rst

.. _changelog-page:

Changelog
=========

Version 1.5
+++++++++++

Version latest (Current master branch, might be unstable)
********************************************************

    - Fix an telegram issue when the messages do not contain proper key entries
    - Reduce the margin around the logfile box
    - Fixed a problem with with GPU SPLIT parameter when unchecked global flag in the GUI GPU parameter
    - Fixed a crash with connection refused SMTP error
    - Expose -\\-batch_size option in cryolo train
    - Do not do checksum calculations if the input file to copy is a directory
    - Proper restart of Motion with CTF Movie mode
    - Try to copy 5 times before deciding that a file is not able to copy

Version 1.5.13
**************

    - Set project pattern as default for the Project Name
    - Fix problem of mistyped e2proc2d.py option unstacking that lead to crashes

Version 1.5.11
**************

    - Improved filament mode for ISAC
    - Fixed retraining
    - Fix latency problems with arriving jpg files
    - Fix visualization problems with Sphire 1.4
    - Minor bug fixes

Version 1.5.0
**************

    - First public release
    - Automated data processing
    - TranSPHIRE feedback loop 
