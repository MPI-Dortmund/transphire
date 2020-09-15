.. _outputs-page:

TranSPHIRE outputs
==================


TranSPHIRE output folder structure
**********************************

The TranSPHIRE output directory looks like this

| Projects
|  \|
|  \|\-Project directory 1
|    \|
|    \|\-TranSPHIRE_results
|      \|
|      \|\-000_Feedback_results
|        \|
|        \|\-004_{PICKING_NAME}_feedback_XX
|        \|\-005_{EXTRACT_NAME}_feedback_XX
|        \|\-006_{2D_CLASSIFICATION_NAME}_feedback_XX
|        \|\-007_{2D_CLASS_SELECTION_NAME}_feedback_XX
|        \|\-008_{RETRAIN_NAME}_feedback_XX
|        \|\-009_{3D_NAME}_feedback_XX
|      \|\-000_Import
|      \|\-000_Import_meta
|      \|\-000_Session_meta
|      \|\-001_{COMPRESS_NAME}
|      \|\-002_{MOTION_NAME}
|      \|\-003_{CTF_NAME}
|      \|\-004_{PICKING_NAME}
|      \|\-005_{EXTRACT_NAME}
|      \|\-006_{2D_CLASSIFICATION_NAME}
|      \|\-007_{2D_CLASS_SELECTION_NAME}
|      \|\-009_{3D_NAME}
|      \|\-XXX_Error_files
|      \|\-XXX_Log_files
|      \|\-XXX_Filtered_Images
|      \|\-XXX_Queue_files
|      \|\-XXX_Restart_Backup
|      \|\-XXX_Settings
|      \|\-XXX_Tar_file_folder
|      \|\-Valid_micrograph_info.txt
|      \|\-Discarded_micrograph_info.txt
|      \|\-{CTF_NAME}_transphire_ctf_partres.txt
|      \|\-{CTF_NAME}_transphire_ctf.star
|      \|\-{MOTION_NAME}_transphire_motion.txt
|      \|\-{MOTION_NAME}_transphire_motion.star
|      \|\-{MOTION_NAME}_transphire_motion_relion3.star
|  ...
|  \|\-Project directory N

+----------------------------------------------+-------------------------------------------------------+
| Output folder                                | Content                                               |
+==============================================+=======================================================+
| Projects                                     | Folder that contains all TranSPHIRE projects.         |
|                                              |                                                       |
|                                              | This folder is provided within the TranSPHIRE GUI.    |
+----------------------------------------------+-------------------------------------------------------+
| Project directory X                          | TranSPHIRE project directory. Every project is        |
|                                              |                                                       |
|                                              | created with the provided *Project name*.             |
|                                              |                                                       |
|                                              | ---                                                   |
|                                              |                                                       |
|                                              | Every path of the major output files is stored        |
|                                              |                                                       |
|                                              | relative to this directory. **Therefore it is**       |
|                                              |                                                       |
|                                              | **recommended to use this folder as a project**       |
|                                              |                                                       |
|                                              | **directory for further processing so that**          |
|                                              |                                                       |
|                                              | **problems with for example particle polishing**      |
|                                              |                                                       |
|                                              | **can be avoided.**                                   |
+----------------------------------------------+-------------------------------------------------------+
| TranSPHIRE_results                           | Folder containing the actual TranSPHIRE results.      |
+----------------------------------------------+-------------------------------------------------------+
| 000_Import                                   | Folder containing the incoming movies.                |
|                                              |                                                       |
|                                              | If the incoming movies are already tiff files         |
|                                              |                                                       |
|                                              | the files will remain in this folder.                 |
|                                              |                                                       |
+----------------------------------------------+-------------------------------------------------------+
| 000_Import_meta                              | Folder containing the meta data that comes with       |
|                                              |                                                       |
|                                              | the data. This includes xml, jpg, and                 |
|                                              |                                                       |
|                                              | spot overview mrc files.                              |
|                                              |                                                       |
+----------------------------------------------+-------------------------------------------------------+
| 000_Session_meta                             | Folder containing the meta data that is created       |
|                                              |                                                       |
|                                              | by the data aquisition software, but is not           |
|                                              |                                                       |
|                                              | the meta data for an acquired image but present.      |
|                                              |                                                       |
|                                              | in the specified directory.                           |
|                                              |                                                       |
+----------------------------------------------+-------------------------------------------------------+
| 001_{COMPRESS_NAME}                          | Folder containing the compressed movies.              |
|                                              |                                                       |
|                                              | ---                                                   |
|                                              |                                                       |
|                                              | If the incoming movies are already tiff files         |
|                                              |                                                       |
|                                              | or no compression is specified, the movies            |
|                                              |                                                       |
|                                              | remain in the 000_Import folder.                      |
|                                              |                                                       |
|                                              | The COMPRESS_NAME depends on the specified            |
|                                              |                                                       |
|                                              | compression method.                                   |
|                                              |                                                       |
+----------------------------------------------+-------------------------------------------------------+
| 002_{MOTION_NAME}                            | Folder containing the results of motion               |
|                                              |                                                       |
|                                              | correction.                                           |
|                                              |                                                       |
|                                              | ---                                                   |
|                                              |                                                       |
|                                              | **In addition to the outputs produced**               |
|                                              |                                                       |
|                                              | **by the chosen program, TranSPHIRE also creates**    |
|                                              |                                                       |
|                                              | **_meta.star files that can be used to run**          |
|                                              |                                                       |
|                                              | **particle polishing in RELION.**                     |
|                                              |                                                       |
|                                              | The MOTION_NAME depends on the specified              |
|                                              |                                                       |
|                                              | motion correction program and version.                |
|                                              |                                                       |
+----------------------------------------------+-------------------------------------------------------+
| 003_{CTF_NAME}                               | Folder containing the results of the CTF estimation.  |
|                                              |                                                       |
|                                              | The CTF_NAME depends on the specified ctf             |
|                                              |                                                       |
|                                              | estimaion program and version.                        |
+----------------------------------------------+-------------------------------------------------------+
| 004_{PICKING_NAME}                           | Folder containing the results of the particle         |
|                                              |                                                       |
|                                              | picking job.                                          |
|                                              |                                                       |
|                                              | The PICKING_NAME depends on the specified             |
|                                              |                                                       |
|                                              | particle picking program and version.                 |
+----------------------------------------------+-------------------------------------------------------+
| 005_{EXTRACT_NAME}                           | Folder containing the results of particle             |
|                                              |                                                       |
|                                              | extraction.                                           |
|                                              |                                                       |
|                                              | The EXTRACT_NAME depends on the specified             |
|                                              |                                                       |
|                                              | particle extraction program and version.              |
+----------------------------------------------+-------------------------------------------------------+
| 006_{2D_CLASSIFICATION_NAME}                 | Folder containing the results of 2D                   |
|                                              |                                                       |
|                                              | classification.                                       |
|                                              |                                                       |
|                                              | The 2D_CLASSIFICATION_NAME depends on the             |
|                                              |                                                       |
|                                              | specified 2d classification program and version.      |
+----------------------------------------------+-------------------------------------------------------+
| 007_{2D_CLASS_SELECTION_NAME}                | Folder containing the results of 2D                   |
|                                              |                                                       |
|                                              | class selection.                                      |
|                                              |                                                       |
|                                              | The 2D_CLASS_SELECTION_NAME depends on the            |
|                                              |                                                       |
|                                              | specified 2d class selection program and version.     |
+----------------------------------------------+-------------------------------------------------------+
| 009_{3D_NAME}                                | Folder containing the results of 3D ab-initio         |
|                                              |                                                       |
|                                              | reconstructon and 3D refinement.                      |
|                                              |                                                       |
|                                              | The 3D_NAME depends on the                            |
|                                              |                                                       |
|                                              | specified 3D program and version.                     |
+----------------------------------------------+-------------------------------------------------------+
| 000_Feedback_results                         | Folder containing the results of the feedback loop.   |
|                                              |                                                       |
|                                              | ---                                                   |
|                                              |                                                       |
|                                              | Every feedback round has its own output folder        |
|                                              |                                                       |
|                                              | indicated by a *_feedback_XX* suffix. The *XX*        |
|                                              |                                                       |
|                                              | stands for the respective feedback iteration.         |
|                                              |                                                       |
|                                              | Results produced outside the feedback loop will be    |
|                                              |                                                       |
|                                              | stored in its respective folders outside the          |
|                                              |                                                       |
|                                              | 000_Feedback_results folder.                          |
|                                              |                                                       |
+----------------------------------------------+-------------------------------------------------------+
| 008_{RETRAIN_NAME}_feedback_XX               | Folder containing the results of the training of      |
|                                              |                                                       |
|                                              | the used picking model.                               |
|                                              |                                                       |
|                                              | This folder is only present in the                    |
|                                              |                                                       |
|                                              | 000_Feedback_results folder.                          |
|                                              |                                                       |
|                                              | The RETRAIN_NAME depends on the                       |
|                                              |                                                       |
|                                              | specified retrain program and version.                |
+----------------------------------------------+-------------------------------------------------------+
| XXX_Error_files                              | Folder containing the error files of the              |
|                                              |                                                       |
|                                              | TranSPHIRE run.                                       |
+----------------------------------------------+-------------------------------------------------------+
| XXX_Log_files                                | Folder containing the log files of the                |
|                                              |                                                       |
|                                              | ---                                                   |
|                                              |                                                       |
|                                              | TranSPHIRE run. Log information like the current      |
|                                              |                                                       |
|                                              | feedback loop iteration, the current picking          |
|                                              |                                                       |
|                                              | threshold and last used file numbers are stored.      |
|                                              |                                                       |
+----------------------------------------------+-------------------------------------------------------+
| XXX_Filtered_Images                          | Folder containing the filtered images from crYOLO     |
|                                              |                                                       |
|                                              | before and after the feedback loop.                   |
+----------------------------------------------+-------------------------------------------------------+
| XXX_Queue_files                              | Folder containing the queue status of the             |
|                                              |                                                       |
|                                              | ---                                                   |
|                                              |                                                       |
|                                              | TranSPHIRE run. There are 3 queue files per job:      |
|                                              |                                                       |
|                                              | *NAME*, *NAME_done*, *NAME_list*.                     |
|                                              |                                                       |
|                                              | The *NAME* file contains the information about        |
|                                              |                                                       |
|                                              | the to-be-processed files. The *NAME_done* file       |
|                                              |                                                       |
|                                              | contains the information of the already processed     |
|                                              |                                                       |
|                                              | files. The *NAME_list* file is only filled for        |
|                                              |                                                       |
|                                              | jobs that have an additional internal queue like      |
|                                              |                                                       |
|                                              | particle picking, particle extraction, and            |
|                                              |                                                       |
|                                              | 2d classification. The content indicates that files   |
|                                              |                                                       |
|                                              | are ready to be processed but still wait for a        |
|                                              |                                                       |
|                                              | certain condition to be met. In case of particle      |
|                                              |                                                       |
|                                              | picking, the program waits for 30 seconds before      |
|                                              |                                                       |
|                                              | starting the actual picking run to reduce the         |
|                                              |                                                       |
|                                              | overhead of program initialisation. For particle      |
|                                              |                                                       |
|                                              | extraction, the program waits until all the results   |
|                                              |                                                       |
|                                              | of motion correction, particle picking, and ctf       |
|                                              |                                                       |
|                                              | estimation arrived. 2D classification and 3D          |
|                                              |                                                       |
|                                              | waits until a certain number of particles is          |
|                                              |                                                       |
|                                              | accumulated. Because multiple files depend on         |
|                                              |                                                       |
|                                              | a different number of input files, the provided       |
|                                              |                                                       |
|                                              | queue status can be larger than the number of         |
|                                              |                                                       |
|                                              | imported movies for the respective jobs.              |
+----------------------------------------------+-------------------------------------------------------+
| XXX_Restart_Backup                           | Folder containing the obsolete files due to a         |
|                                              |                                                       |
|                                              | restart.                                              |
|                                              |                                                       |
+----------------------------------------------+-------------------------------------------------------+
| XXX_Settings                                 | Folder containing the settings and files for the      |
|                                              |                                                       |
|                                              | current session.                                      |
|                                              |                                                       |
|                                              | ---                                                   |
|                                              |                                                       |
|                                              | Everytime the *Start* button is pressed, the provided |
|                                              |                                                       |
|                                              | external files and the current setup of TranSPHIRE    |
|                                              |                                                       |
|                                              | is saved in a new session folder indicated by the     |
|                                              |                                                       |
|                                              | current date and time. Internally, the copied files   |
|                                              |                                                       |
|                                              | are used instead of the original ones.                |
|                                              |                                                       |
+----------------------------------------------+-------------------------------------------------------+
| XXX_Tar_file_folder                          | Folder containing the tar files that are created      |
|                                              |                                                       |
|                                              | prior to copying when the *Tar to work* or            |
|                                              |                                                       |
|                                              | *Tar to backup* option is activated.                  |
|                                              |                                                       |
+----------------------------------------------+-------------------------------------------------------+
| Valid_micrograph_info.txt                    | File containing the extracted meta data for each      |
|                                              |                                                       |
|                                              | movie in a star file format. Only the movies          |
|                                              |                                                       |
|                                              | that do not violate the range provided by the user    |
|                                              |                                                       |
|                                              | are stored in the Valid version.                      |
+----------------------------------------------+-------------------------------------------------------+
| Discarded_micrograph_info.txt                | File containing the extracted meta data for each      |
|                                              |                                                       |
|                                              | movie in a star file format. Only the movies          |
|                                              |                                                       |
|                                              | that do violate the range provided by the user        |
|                                              |                                                       |
|                                              | are stored in the Discarded version.                  |
+----------------------------------------------+-------------------------------------------------------+
| {CTF_NAME}_transphire_ctf_partres.txt        | File containing the CTF estimation information in     |
|                                              |                                                       |
|                                              | the SPHIRE partres format. This file can be used to   |
|                                              |                                                       |
|                                              | skip CTF estimation in a real processing scenario.    |
|                                              |                                                       |
+----------------------------------------------+-------------------------------------------------------+
| {CTF_NAME}_transphire_ctf.star               | File containing the CTF estimation information in     |
|                                              |                                                       |
|                                              | the RELION star file format. This file can be used to |
|                                              |                                                       |
|                                              | skip CTF estimation in a real processing scenario.    |
|                                              |                                                       |
+----------------------------------------------+-------------------------------------------------------+
| {MOTION_NAME}_transphire_motion.txt          | File containing a list of valid micrograph entries.   |
+----------------------------------------------+-------------------------------------------------------+
| {MOTION_NAME}_transphire_motion.star         | File containing micrograph information like the name  |
|                                              |                                                       |
|                                              | and path of the DW and non DW summed image.           |
+----------------------------------------------+-------------------------------------------------------+
| {MOTION_NAME}_transphire_motion_relion3.star | File containing micrograph information like the name  |
|                                              |                                                       |
|                                              | and path of the DW and non DW summed image.           |
|                                              |                                                       |
|                                              | Additionally, information to run particle polishing   |
|                                              |                                                       |
|                                              | is available. Provide this file to run as input for   |
|                                              |                                                       |
|                                              | particle polishing.                                   |
+----------------------------------------------+-------------------------------------------------------+



