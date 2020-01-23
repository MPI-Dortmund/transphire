"""
    TranSPHIRE is supposed to help with the cryo-EM data collection
    Copyright (C) 2017 Markus Stabrin

    This program is free software: you can redistribute it and/or modify
    it under the terms of the GNU General Public License as published by
    the Free Software Foundation, either version 3 of the License, or
    (at your option) any later version.

    This program is distributed in the hope that it will be useful,
    but WITHOUT ANY WARRANTY; without even the implied warranty of
    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
    GNU General Public License for more details.

    You should have received a copy of the GNU General Public License
    along with this program.  If not, see <http://www.gnu.org/licenses/>.
"""

import glob
import os
from transphire import transphire_utils as tu
from transphire import transphire_import as ti


def default_auto_sphire_v1_3():
    """
    Content for auto sphire

    Arguments:
    None

    Return:
    Content items as list
    """
    items = [
        ['WIDGETS MAIN', '10', int, '', 'PLAIN', '', ''],
        ['WIDGETS ADVANCED', '10', int, '', 'PLAIN', '', ''],
        ['WIDGETS RARE', '10', int, '', 'PLAIN', '', ''],

        ['--mpi_procs', '24', int, '', 'PLAIN', 'Main', '', 'Number of processors to use.'],
        ['--mpi_submission_command', 'sbatch', str, '', 'PLAIN', 'Main', '', 'Submission command, e.g. sbatch, qsub, ...'],
        ['--mpi_submission_template', '', str, '', 'FILE', 'Main', '', 'Submission template.'],

        ['--apix:Pixel size', '1.0', float, '', 'PLAIN', 'Main', '', 'Pixel size in A/pixel.'],
        ['--mol_mass', '250.0', float, '', 'PLAIN', 'Main', '', 'Molecular mass of the protein in kDa. Used to calculate the masking density threshold.'],
        ['--symmetry', 'c1', str, '', 'PLAIN', 'Main', '', 'Symmetry of the particle.'],
        ['--mtf', '', str, '', 'FILE', 'Main', '', 'MTF file for the sharpening step'],
        ['--phase_plate:Phase Plate', ['False', 'True'], bool, '', 'COMBO', 'Main', '', 'Input is phase_plate.'],
        ['--memory_per_node', '100', int,  '', 'PLAIN', 'Main', '', 'Available memory per node.'],

        ['--skip_meridien', ['False', 'True'], bool,  '', 'COMBO', 'Main', '', 'Skip meridien and just do initial model estimation.'],
        ['--rviper_use_final', ['True', 'False'], bool,  '', 'COMBO', 'Main', '', 'Available memory per node.'],
        ['--sharpening_meridien_ndilation', '2', int,  '', 'PLAIN', 'Main', '', 'Available memory per node.'],
        ['--sharpening_meridien_soft_edge', '1', str,  '', 'PLAIN', 'Main', '', 'Available memory per node.'],

        ['--rviper_addition', '', str,  '', 'PLAIN', 'Main', '', 'Available memory per node.'],
        ['--adjust_rviper_addition', '', str,  '', 'PLAIN', 'Main', '', 'Available memory per node.'],
        ['--meridien_addition', '', str,  '', 'PLAIN', 'Main', '', 'Available memory per node.'],
        ['--sharpening_meridien_addition', '', str,  '', 'PLAIN', 'Main', '', 'Available memory per node.'],

        ['input_volume', '', str,  '', 'FILE', 'Main', '', 'Available memory per node.'],
        ['input_mask', '', str,  '', 'FILE', 'Main', '', 'Available memory per node.'],

        ['Use SSH', ['True', 'False'], bool,  '', 'COMBO', 'Main', '', 'Use SSH to submit a job.'],
        ['SSH username', '', str,  'Use SSH:True', 'PLAIN', 'Main', '', 'Username on the work directory'],
        ['SSH password', '', str,  'Use SSH:True', 'PASSWORD', 'Main', '', 'Password of the user (Will not be saved anywhere)'],
        ['Minimum classes', '100', int, '', 'PLAIN', 'Advanced', 'NOT AN AutoSPHIRE OPTION. Minimum number of classes to start AutoSPHIRE (Only used the first time.).'],
        ['Minimum particles', '40000', int, '', 'PLAIN', 'Advanced', 'NOT AN AutoSPHIRE OPTION. Minimum number of particles to start AutoSPHIRE.'],
        ]
    return items


def default_compress_command_line():
    """
    Content for compression

    Arguments:
    None

    Return:
    Content items as list
    """
    items = [
        ['WIDGETS MAIN', '10', int, '', 'PLAIN', '', ''],
        ['WIDGETS ADVANCED', '10', int, '', 'PLAIN', '', ''],
        ['WIDGETS RARE', '10', int, '', 'PLAIN', '', ''],
        ['--command_compress_path', 'mrc2tif', str, '', 'FILE', 'Main', '', 'Program used to execute compression.'],
        ['--command_compress_option', '-s -c lzw ##INPUT## ##OUTPUT##', str, '', 'PLAIN', 'Main', '', 'Command options used to compress the data. Use ##INPUT## and ##OUTPUT## as variables for the respective files.'],
        ['--command_compress_extension', 'tiff', str, '', 'PLAIN', 'Main', '', 'Output extension for the compressed files.'],
        ['--command_uncompress_path', 'tif2mrc', str, '', 'FILE', 'Advanced', '', 'Program used to execute uncompression.'],
        ['--command_uncompress_option', '##INPUT## ##OUTPUT##', str, '', 'PLAIN', 'Advanced', '', 'Command options used to uncompress the data. Use ##INPUT## and ##OUTPUT## as variables for the respective files.'],
        ['--command_uncompress_extension', 'mrc', str, '', 'PLAIN', 'Advanced', '', 'Output extension for the uncompressed files.'],
        ]
    return items


def default_isac2_1_2():
    """
    Content of sp_isac2(gpu) version 1.2

    Arguments:
    None

    Return:
    Content items as list
    """
    items = [
        ['WIDGETS MAIN', '10', int, '', 'PLAIN', '', ''],
        ['WIDGETS ADVANCED', '10', int, '', 'PLAIN', '', ''],
        ['WIDGETS RARE', '10', int, '', 'PLAIN', '', ''],
        ['Nr. Particles', '10000', int, '', 'PLAIN', 'Main', 'NOT AN ISAC OPTION: Wait to accumulate this number of particles to process.'],
        ['MPI processes', '6', int, '', 'PLAIN', 'Main', 'NOT AN ISAC OPTION: Number of MPI processes to use with ISAC.'],
        ['--radius', '-1', int, '', 'PLAIN', 'Main', 'particle radius: there is no default, a sensible number has to be provided, units - pixels (default required int)'],
        ['--target_radius', '29', int, '', 'PLAIN', 'Advanced', 'target particle radius: actual particle radius on which isac will process data. Images will be shrinked/enlarged to achieve this radius (default 29)'],
        ['--target_nx', '76', int, '', 'PLAIN', 'Advanced', 'target particle image size: actual image size on which isac will process data. Images will be shrinked/enlarged according to target particle radius and then cut/padded to achieve target_nx size. When xr > 0, the final image size for isac processing is target_nx + xr - 1  (default 76)'],
        ['--img_per_grp', '200', int, '', 'PLAIN', 'Advanced', 'number of images per class (maximum group size, also defines number of classes K=(total number of images)/img_per_grp (default 200)'],
        ['--minimum_grp_size', '60', float, '', 'PLAIN', 'Advanced', 'minimum size of class (default 60)'],
        ['--thld_err', '0.7', float, '', 'PLAIN', 'Advanced', 'threshold of pixel error when checking stability: equals root mean square of distances between corresponding pixels from set of found transformations and theirs average transformation, depends linearly on square of radius (parameter target_radius). units - pixels. (default 0.7)'],
        ['--center_method', '-1', int, '', 'PLAIN', 'Advanced', ' method for centering: of global 2D average during initial prealignment of data (0 : no centering; -1 : average shift method; please see center_2D in utilities.py for methods 1-7) (default -1)'],

        ['--CTF', ['False', 'True'], bool, '', 'COMBO', 'Main', 'apply phase-flip for CTF correction: if set the data will be phase-flipped using CTF information included in image headers (default False)'],
        ['--VPP:Phase Plate', ['False', 'True'], bool, '--CTF:False', 'COMBO', 'Main', 'Phase Plate data (default False)'],
        ['--gpu_devices:GPU', '0', str, '', 'PLAIN', 'Advanced', 'Print detailed information about the selected GPUs, including the class limit which is relevant when using the --gpu_class_limit parameter. Use --gpu_devices to specify what GPUs you want to know about. NOTE: ISAC will stop after printing this information, so don\'t use this parameter if you intend to actually process any data. [Default: False]'],
        ['--gpu_class_limit', '-1', int, '', 'PLAIN', 'Advanced', 'By default ISAC will check how much data can fit on the available GPUs. This can take more than a minute, which is annoying for testing. To skip this check, use --gpu_info to get a class limit value to use for this parameter. [Default: -1]'],
        ['--gpu_memory_use:Memory usage', '-1', float, '', 'PLAIN', 'Advanced', 'Specify how much memory on the chosen GPUs ISAC is allowed to use. A value of 0.9 means 90% of the available memory (this is the default; higher percentages should be used with caution). [Default: -1.0]'],
        ['GPU SPLIT:GPU SPLIT', '1', int, '', 'PLAIN', 'Advanced', 'NOT AN ISAC2 OPTION. Specify how many jobs per GPU.'],
        ['Split Gpu?', ['True', 'False'], bool, '', 'COMBO', 'Advanced', 'NOT AN ISAC2 OPTION. Split the gpu values specified in --gpu to be able to run mutliple crYOLO jobs in parallel.'],
        ]
    return items


def default_window_1_2():
    """
    Content of sp_window version 1.2

    Arguments:
    None

    Return:
    Content items as list
    """
    items = [
        ['WIDGETS MAIN', '10', int, '', 'PLAIN', '', ''],
        ['WIDGETS ADVANCED', '10', int, '', 'PLAIN', '', ''],
        ['WIDGETS RARE', '10', int, '', 'PLAIN', '', ''],
        ['--box_size', '256', int, '', 'PLAIN', 'Main', 'Particle box size [Pixels]: The x and y dimensions of square area to be windowed. The box size after resampling is assumed when resample_ratio < 1.0. (default 256)'],
        ['--skip_invert', ['False', 'True'], bool, '', 'COMBO', 'Advanced', 'Skip invert image contrast: Use this option for negative staining data. By default, the image contrast is inverted for cryo data. (default False)'],
        ['--limit_ctf', ['False', 'True'], bool, '', 'COMBO', 'Advanced', 'Use CTF limit filter: Frequencies where CTF oscillations can not be properly modeled with the resampled pixel size will be discarded in the images with the appropriate low-pass filter. This has no effects when the CTER partres file is not specified by the CTF paramters source argument. (default False)'],
        ['--astigmatism_error', '360.0', float, '', 'PLAIN', 'Advanced', 'Astigmatism error limit [Degrees]: Set astigmatism to zero for all micrographs where the angular error computed by sxcter is larger than the desired value. This has no effects when the CTER partres file is not specified by the CTF paramters source argument. (default 360.0)'],
        ['--resample_ratio', '1.0', float, '', 'PLAIN', 'Advanced', 'Ratio between new and original pixel size: Use a value between 0.0 and 1.0 (excluding 0.0). The new pixel size will be automatically recalculated and stored in CTF paramers when resample_ratio < 1.0 is used. (default 1.0)'],
        ['--check_consistency', ['False', 'True'], bool, '', 'COMBO', 'Advanced', 'Check consistency of dataset: Create a text file containing the list of Micrograph ID entries might have inconsistency among the provided dataset. (i.e. mic_consistency_check_info_TIMESTAMP.txt). (default False)'],
        ['--filament_width', '-1', int, '', 'PLAIN', 'Advanced', 'Filament width [Pixels]: Filament width for the creation of the rectangular mask. Default is one third of the box size. (default -1)'],
        ]
    return items


def default_cinderella_v0_3_1():
    """
    Content of cinderella v0.3.1

    Arguments:
    None

    Return:
    Content items as list
    """
    items = [
        ['WIDGETS MAIN', '10', int, '', 'PLAIN', '', ''],
        ['WIDGETS ADVANCED', '10', int, '', 'PLAIN', '', ''],
        ['WIDGETS RARE', '10', int, '', 'PLAIN', '', ''],
        ['--weights', '', str, '', 'FILE', 'Main', 'Path network weights.'],
        ['--confidence_threshold', '0.5', float, '', 'PLAIN', 'Main', 'Classes with a confidence higher as that threshold are classified as good.'],
        ['--batch_size', '32', int, '', 'PLAIN', 'Main', 'Classes with a confidence higher as that threshold are classified as good.'],
        ['--gpu:GPU', '0', [int]*99, '', 'PLAIN', 'Advanced', 'Specifiy which gpu\'s should be used.'],
        ['GPU SPLIT:GPU SPLIT', '1', int, '', 'PLAIN', 'Advanced', 'NOT AN ISAC2 OPTION. Specify how many jobs per GPU.'],
        ['Split Gpu?', ['True', 'False'], bool, '', 'COMBO', 'Advanced', 'NOT A CRYOLO OPTION. Split the gpu values specified in --gpu to be able to run mutliple crYOLO jobs in parallel.'],
        ]
    return items


def default_cryolo_train_v1_5_4():
    """
    Content of crYOLO_train version 1.5.4

    Arguments:
    None

    Return:
    Content items as list
    """
    items = [
        ['WIDGETS MAIN', '10', int, '', 'PLAIN', '', ''],
        ['WIDGETS ADVANCED', '10', int, '', 'PLAIN', '', ''],
        ['WIDGETS RARE', '10', int, '', 'PLAIN', '', ''],
        ['Box size', '205', int, '', 'PLAIN', 'Main', 'Box size used for retraining. Should be quite narrow.'],
        ['--warmup', '5', int, '', 'PLAIN', 'Main', 'Number of warmup epochs. Set it to zero if you fine tune a model.'],
        ['--num_cpu', '-1', int, '', 'PLAIN', 'Main', 'Number of CPUs used during training. By default it will use half of the available CPUs.'],
        ['--early', '10', int, '', 'PLAIN', 'Main', 'Number of CPUs used during training. By default it will use half of the available CPUs.'],
        ['--fine_tune', ['False', 'True'], bool, '', 'COMBO', 'Main', 'Set it to true if you only want to use the fine tune mode. When using the fine tune mode, only the last layers of your network are trained and youhave to specify pretrained_weights (see action "config"->"Training options") You typically use a general model as pretrained weights.'],
        ['--layers_fine_tune', '2', int, '--fine_tune:True', 'PLAIN', 'Main', 'Layers to be trained when using fine tuning.'],
        ['--gpu:GPU', '0', [int]*99, '', 'PLAIN', 'Advanced', 'Specifiy which gpu\'s should be used.'],
        ['--gpu_fraction:Memory usage', '1.0', float, '', 'PLAIN', 'Advanced', 'Specify the fraction of memory per GPU used by crYOLO during prediction. Only values between 0.0 and 1.0 are allowed.'],
        ['--train_times', '1', int, '', 'PLAIN', 'Main', 'How often each image is presented to the network during one epoch. The default should be kept until you have many training images.'],
        ['Maximum micrographs', '50', int, '', 'PLAIN', 'Advanced', 'NOT A CRYOLO TRAIN OPTION. Maximum number of randomly selected micrographs to consider for training.'],
        ['GPU SPLIT:GPU SPLIT', '1', int, '', 'PLAIN', 'Advanced', 'NOT AN ISAC2 OPTION. Specify how many jobs per GPU.'],
        ['Split Gpu?', ['True', 'False'], bool, '', 'COMBO', 'Advanced', 'NOT A CRYOLO TRAIN OPTION. Split the gpu values specified in --gpu to be able to run mutliple crYOLO jobs in parallel.'],
        ]
    return items


def default_cryolo_v1_4_1():
    """
    Content of crYOLO version 1.4.1

    Arguments:
    None

    Return:
    Content items as list
    """
    items = [
        ['WIDGETS MAIN', '10', int, '', 'PLAIN', '', ''],
        ['WIDGETS ADVANCED', '10', int, '', 'PLAIN', '', ''],
        ['WIDGETS RARE', '10', int, '', 'PLAIN', '', ''],
        ['--conf', '', str, '', 'FILE', 'Main', '', 'Path to configuration file.'],
        ['--weights', '', str, '', 'FILE', 'Main', 'Path to pretrained weights.'],
        ['--threshold', '0.3', float, '', 'PLAIN', 'Main', 'Confidence threshold. Have to be between 0 and 1. The higher, the more conservative.'],
        ['Pixel size (A/px):Pixel size', '1', float, 'Filter micrographs:True', 'PLAIN', 'Main', 'NOT A CRYOLO OPTION. Pixel size value. Only used for visual representation.'],
        ['Box size', '200', int, '', 'PLAIN', 'Main', 'NOT A CRYOLO OPTION. Box size value. Only used for visual representation.'],
        ['--filament', ['False', 'True'], bool, '', 'COMBO', 'Main', 'Activate filament mode'],
        ['--filament_width', '0', float, '--filament:True', 'PLAIN', 'Main', '(FILAMENT MODE) Filament width (in pixel)'],
        ['--nomerging', ['False', 'True'], bool, '', 'COMBO', 'Main', '(FILAMENT MODE) The filament mode does not merge filaments'],
        ['--nosplit', ['False', 'True'], bool, '', 'COMBO', 'Main', '(FILAMENT MODE) The filament mode does not split to curved filaments'],
        ['--box_distance', '0', int, '--filament:True', 'PLAIN', 'Main', '(FILAMENT MODE) Distance between two boxes(in pixel)'],
        ['--mask_width', '100', int, '--filament:True', 'PLAIN', 'Main', '(FILAMENT MODE) Mask width (in pixel)'],
        ['--search_range_factor', '1.41', float, '--filament:True', 'PLAIN', 'Main', '(FILAMENT MODE) The search range for connecting boxes is the box size times this factor.'],
        ['--minimum_number_boxes', '0', int, '--filament:True', 'PLAIN', 'Main', '(FILAMENT MODE) Distance between two boxes(in pixel)'],
        ['Filter micrographs', ['False', 'True'], bool, '', 'COMBO', 'Advanced', 'NOT A CRYOLO OPTION. Filter option in case one does not want to use the internal filter of crYOLO.'],
        ['Filter value high pass (A)', '9999', float, 'Filter micrographs:True', 'PLAIN', 'Advanced', 'NOT A CRYOLO OPTION. High-pass filter value in angstrom before running crYOLO.'],
        ['Filter value low pass (A)', '10', float, 'Filter micrographs:True', 'PLAIN', 'Advanced', 'NOT A CRYOLO OPTION. Low-pass filter value in angstrom before running crYOLO.'],
        ['--patch', '-1', int, '', 'PLAIN', 'Advanced', 'Number of patches. (-1 uses the patch size specified in the configuration file.)'],
        ['--distance', '0', int, '', 'PLAIN', 'Advanced', 'Particles with a distance less than this value (in pixel) will be removed'],
        ['--norm_margin', '0', int, '', 'PLAIN', 'Advanced', 'Relative margin size for normalization.'],
        ['--prediction_batch_size', '3', int, '', 'PLAIN', 'Advanced', 'How many images should be predicted in one batch.  Smaller values might resolve memory issues.'],
        ['--num_cpu', '-1', int, '', 'PLAIN', 'Advanced', '(FILAMENT MODE) Number of CPUs used during filament tracing. By default it will use all of the available CPUs.'],
        ['--otf', ['False', 'True'], bool, '', 'COMBO', 'Advanced', 'On the fly filtering.'],
        ['--gpu:GPU', '0', [int]*99, '', 'PLAIN', 'Advanced', 'Specifiy which gpu\'s should be used.'],
        ['--gpu_fraction:Memory usage', '1.0', float, '', 'PLAIN', 'Advanced', 'Specify the fraction of memory per GPU used by crYOLO during prediction. Only values between 0.0 and 1.0 are allowed.'],
        ['Lowest defocus percent', '0.5', float, '', 'PLAIN', 'Advanced', 'NOT A CRYOLO OPTION. Calculate the picking threshold on the lower "Lowest defocus percent" percent of the dataset'],
        ['Minimum micrographs', '50', int, '', 'PLAIN', 'Advanced', 'NOT A CRYOLO OPTION. Minimum number of micrographs to check the picking threshold on.'],
        ['Minimum particles', '20000', int, '', 'PLAIN', 'Advanced', 'NOT A CRYOLO OPTION. Minimum number of particles to check the picking threshold on.'],
        ['Mean percent', '0.75', float, '', 'PLAIN', 'Advanced', 'NOT A CRYOLO OPTION. Percentage of the mean to use for particle picking.'],
        ['GPU SPLIT:GPU SPLIT', '1', int, '', 'PLAIN', 'Advanced', 'NOT AN ISAC2 OPTION. Specify how many jobs per GPU.'],
        ['Split Gpu?', ['True', 'False'], bool, '', 'COMBO', 'Advanced', 'NOT A CRYOLO OPTION. Split the gpu values specified in --gpu to be able to run mutliple crYOLO jobs in parallel.'],
        ]
    return items


def default_cryolo_v1_2_1():
    """
    Content of crYOLO version 1.2.1

    Arguments:
    None

    Return:
    Content items as list
    """
    items = [
        ['WIDGETS MAIN', '10', int, '', 'PLAIN', '', ''],
        ['WIDGETS ADVANCED', '10', int, '', 'PLAIN', '', ''],
        ['WIDGETS RARE', '10', int, '', 'PLAIN', '', ''],
        ['--conf', '', str, '', 'FILE', 'Main', '', 'Path to configuration file.'],
        ['--weights', '', str, '', 'FILE', 'Main', 'Path to pretrained weights.'],
        ['--threshold', '0.3', float, '', 'PLAIN', 'Main', 'Confidence threshold. Have to be between 0 and 1. As higher, as more conservative.'],
        ['Pixel size (A/px):Pixel size', '1', float, 'Filter micrographs:True', 'PLAIN', 'Main', 'NOT A CRYOLO OPTION. Pixel size value. Only used for visual representation.'],
        ['Box size', '200', int, '', 'PLAIN', 'Main', 'NOT A CRYOLO OPTION. Box size value. Only used for visual representation.'],
        ['--filament', ['False', 'True'], bool, '', 'COMBO', 'Main', 'Activate filament mode'],
        ['--filament_width', '0', float, '--filament:True', 'PLAIN', 'Main', '(FILAMENT MODE) Filament width (in pixel)'],
        ['--box_distance', '0', int, '--filament:True', 'PLAIN', 'Main', '(FILAMENT MODE) Distance between two boxes(in pixel)'],
        ['--minimum_number_boxes', '0', int, '--filament:True', 'PLAIN', 'Main', '(FILAMENT MODE) Distance between two boxes(in pixel)'],
        ['Filter micrographs', ['False', 'True'], bool, '', 'COMBO', 'Advanced', 'NOT A CRYOLO OPTION. Filter option in case one does not want to use the internal filter of crYOLO.'],
        ['Filter value high pass (A)', '9999', float, 'Filter micrographs:True', 'PLAIN', 'Advanced', 'NOT A CRYOLO OPTION. High-pass filter value in angstrom before running crYOLO.'],
        ['Filter value low pass (A)', '10', float, 'Filter micrographs:True', 'PLAIN', 'Advanced', 'NOT A CRYOLO OPTION. Low-pass filter value in angstrom before running crYOLO.'],
        ['--patch', '-1', int, '', 'PLAIN', 'Advanced', 'Number of patches. (-1 uses the patch size specified in the configuration file.)'],
        ['--gpu:GPU', '0', [int]*99, '', 'PLAIN', 'Advanced', 'Specifiy which gpu\'s should be used.'],
        ['GPU SPLIT:GPU SPLIT', '1', int, '', 'PLAIN', 'Advanced', 'NOT AN ISAC2 OPTION. Specify how many jobs per GPU.'],
        ['Split Gpu?', ['True', 'False'], bool, '', 'COMBO', 'Advanced', 'NOT A CRYOLO OPTION. Split the gpu values specified in --gpu to be able to run mutliple crYOLO jobs in parallel.'],
        ]
    return items


def default_cryolo_v1_1_0():
    """
    Content of crYOLO version 1.1.0

    Arguments:
    None

    Return:
    Content items as list
    """
    items = [
        ['WIDGETS MAIN', '10', int, '', 'PLAIN', '', ''],
        ['WIDGETS ADVANCED', '10', int, '', 'PLAIN', '', ''],
        ['WIDGETS RARE', '10', int, '', 'PLAIN', '', ''],
        ['--conf', '', str, '', 'FILE', 'Main', '', 'Path to configuration file.'],
        ['--weights', '', str, '', 'FILE', 'Main', 'Path to pretrained weights.'],
        ['--threshold', '0.3', float, '', 'PLAIN', 'Main', 'Confidence threshold. Have to be between 0 and 1. As higher, as more conservative.'],
        ['Pixel size (A/px):Pixel size', '1', float, 'Filter micrographs:True', 'PLAIN', 'Main', 'NOT A CRYOLO OPTION. Pixel size value. Only used for visual representation.'],
        ['Box size', '200', int, '', 'PLAIN', 'Main', 'NOT A CRYOLO OPTION. Box size value. Only used for visual representation.'],
        ['--filament', ['False', 'True'], bool, '', 'COMBO', 'Main', 'Activate filament mode'],
        ['--filament_width', '0', float, '--filament:True', 'PLAIN', 'Main', '(FILAMENT MODE) Filament width (in pixel)'],
        ['--box_distance', '0', int, '--filament:True', 'PLAIN', 'Main', '(FILAMENT MODE) Distance between two boxes(in pixel)'],
        ['--minium_number_boxes', '0', int, '--filament:True', 'PLAIN', 'Main', '(FILAMENT MODE) Distance between two boxes(in pixel)'],
        ['Filter micrographs', ['False', 'True'], bool, '', 'COMBO', 'Advanced', 'NOT A CRYOLO OPTION. Filter option in case one does not want to use the internal filter of crYOLO.'],
        ['Filter value high pass (A)', '9999', float, 'Filter micrographs:True', 'PLAIN', 'Advanced', 'NOT A CRYOLO OPTION. High-pass filter value in angstrom before running crYOLO.'],
        ['Filter value low pass (A)', '10', float, 'Filter micrographs:True', 'PLAIN', 'Advanced', 'NOT A CRYOLO OPTION. Low-pass filter value in angstrom before running crYOLO.'],
        ['--patch', '-1', int, '', 'PLAIN', 'Advanced', 'Number of patches. (-1 uses the patch size specified in the configuration file.)'],
        ['--gpu:GPU', '0', [int]*99, '', 'PLAIN', 'Advanced', 'Specifiy which gpu\'s should be used.'],
        ['GPU SPLIT:GPU SPLIT', '1', int, '', 'PLAIN', 'Advanced', 'NOT AN ISAC2 OPTION. Specify how many jobs per GPU.'],
        ['Split Gpu?', ['True', 'False'], bool, '', 'COMBO', 'Advanced', 'NOT A CRYOLO OPTION. Split the gpu values specified in --gpu to be able to run mutliple crYOLO jobs in parallel.'],
        ]
    return items


def default_cryolo_v1_0_4():
    """
    Content of crYOLO version 1.0.4

    Arguments:
    None

    Return:
    Content items as list
    """
    items = [
        ['WIDGETS MAIN', '10', int, '', 'PLAIN', '', ''],
        ['WIDGETS ADVANCED', '10', int, '', 'PLAIN', '', ''],
        ['WIDGETS RARE', '10', int, '', 'PLAIN', '', ''],
        ['--conf', '', str, '', 'FILE', 'Main', '', 'Path to configuration file.'],
        ['--weights', '', str, '', 'FILE', 'Main', 'Path to pretrained weights.'],
        ['--threshold', '0.3', float, '', 'PLAIN', 'Main', 'Confidence threshold. Have to be between 0 and 1. As higher, as more conservative.'],
        ['Pixel size (A/px):Pixel size', '1', float, 'Filter micrographs:True', 'PLAIN', 'Main', 'NOT A CRYOLO OPTION. Pixel size value. Only used for visual representation.'],
        ['Box size', '200', int, '', 'PLAIN', 'Main', 'NOT A CRYOLO OPTION. Box size value. Only used for visual representation.'],
        ['Filter micrographs', ['False', 'True'], bool, '', 'COMBO', 'Advanced', 'NOT A CRYOLO OPTION. Filter option in case one does not want to use the internal filter of crYOLO.'],
        ['Filter value high pass (A)', '9999', float, 'Filter micrographs:True', 'PLAIN', 'Advanced', 'NOT A CRYOLO OPTION. High-pass filter value in angstrom before running crYOLO.'],
        ['Filter value low pass (A)', '10', float, 'Filter micrographs:True', 'PLAIN', 'Advanced', 'NOT A CRYOLO OPTION. Low-pass filter value in angstrom before running crYOLO.'],
        ['--patch', '-1', int, '', 'PLAIN', 'Advanced', 'Number of patches. (-1 uses the patch size specified in the configuration file.)'],
        ['--gpu:GPU', '0', [int]*99, '', 'PLAIN', 'Advanced', 'Specifiy which gpu\'s should be used.'],
        ['GPU SPLIT:GPU SPLIT', '1', int, '', 'PLAIN', 'Advanced', 'NOT AN ISAC2 OPTION. Specify how many jobs per GPU.'],
        ['Split Gpu?', ['True', 'False'], bool, '', 'COMBO', 'Advanced', 'NOT A CRYOLO OPTION. Split the gpu values specified in --gpu to be able to run mutliple crYOLO jobs in parallel.'],
        ]
    return items


def default_cter_v1_0():
    """
    Content of CTER SPHIRE version 1.0.

    Arguments:
    None

    Return:
    Content items as list
    """
    items = [
        ['WIDGETS MAIN', '10', int, '', 'PLAIN', '', ''],
        ['WIDGETS ADVANCED', '10', int, '', 'PLAIN', '', ''],
        ['WIDGETS RARE', '10', int, '', 'PLAIN', '', ''],
        ['--apix:Pixel size', '1.0', float, '', 'PLAIN', 'Main', 'Pixel size [A/Pixels]: The pixel size of input micrograph(s) or images in input particle stack.'],
        ['--Cs', '2.0', float, '', 'PLAIN', 'Main', 'Microscope spherical aberration (Cs) [mm]: The spherical aberration (Cs) of microscope used for imaging.'],
        ['--voltage:voltage', '300', float, '', 'PLAIN', 'Main', 'Microscope voltage [kV]: The acceleration voltage of microscope used for imaging.'],
        ['--ac', '10', float, '', 'PLAIN', 'Main', 'Amplitude contrast [%]: The typical amplitude contrast is in the range of 7% - 14%. The value mainly depends on the thickness of the ice embedding the particles.'],
        ['--f_start', '-1', float, '', 'PLAIN', 'Main', 'Lowest resolution [A]: Lowest resolution to be considered in the CTF estimation. Determined automatically by default.'],
        ['--f_stop', '-1', float, '', 'PLAIN', 'Main', 'Highest resolution [A]: Highest resolution to be considered in the CTF estimation. Determined automatically by default.'],
        ['Phase plate:Phase Plate', ['False', 'True'], bool, '', 'COMBO', 'Main', 'Volta Phase Plate - fit smplitude contrast.'],
        ['--defocus_min', '0.3', float, 'Phase plate:True', 'PLAIN', 'Main', 'Minimum defocus search [um]'],
        ['--defocus_max', '9.0', float, 'Phase plate:True', 'PLAIN', 'Main', 'Maximum defocus search [um]'],
        ['--defocus_step', '0.1', float, 'Phase plate:True', 'PLAIN', 'Main', 'Step defocus search [um]'],
        ['--phase_min', '5', float, 'Phase plate:True', 'PLAIN', 'Main', 'Minimum phase search [degrees]'],
        ['--phase_max', '175', float, 'Phase plate:True', 'PLAIN', 'Main', 'Maximum phase search [degrees]'],
        ['--phase_step', '5', float, 'Phase plate:True', 'PLAIN', 'Main', 'Step phase search [degrees]'],
        ['--wn', '512', float, '', 'PLAIN', 'Advanced', 'CTF window size [pixels]: The size should be slightly larger than particle box size. This will be ignored in Stack Mode.'],
        ['--kboot', '16', float, '', 'PLAIN', 'Advanced', 'Number of CTF estimates per micrograph: Used for error assessment.'],
        ['--overlap_x', '50', float, '', 'PLAIN', 'Advanced', 'X overlap [%]: Overlap between the windows in the x direction. This will be ignored in Stack Mode.'],
        ['--overlap_y', '50', float, '', 'PLAIN', 'Advanced', 'Y overlap [%]: Overlap between the windows in the y direction. This will be ignored in Stack Mode.'],
        ['--edge_x', '0', float, '', 'PLAIN', 'Advanced', 'Edge x [pixels]: Defines the edge of the tiling area in the x direction. Normally it does not need to be modified. This will be ignored in Stack Mode.'],
        ['--edge_y', '0', float, '', 'PLAIN', 'Advanced', 'Edge x [pixels]: Defines the edge of the tiling area in the x direction. Normally it does not need to be modified. This will be ignored in Stack Mode.'],
        ['--pap', ['False', 'True'], bool, '', 'COMBO', 'Advanced', 'Use power spectrum for fitting.'],
        ]
    return items


def default_gctf_v1_06():
    """
    Content of GCtf version 1.06.

    Arguments:
    None

    Return:
    Content items as list
    """
    items = [
        ['WIDGETS MAIN', '10', int, '', 'PLAIN', '', ''],
        ['WIDGETS ADVANCED', '10', int, '', 'PLAIN', '', ''],
        ['WIDGETS RARE', '10', int, '', 'PLAIN', '', ''],
        ['--apix:Pixel size', '1.34', float, '', 'PLAIN', 'Main', 'Pixel size'],
        ['--dstep', '14.0', float, '', 'PLAIN', 'Main', 'Detector size in micrometer; don\'t worry if unknown; just use default.'],
        ['--kV:voltage', '300', float, '', 'PLAIN', 'Main', 'High tension in Kilovolt, typically 300, 200 or 120'],
        ['--cs', '2.7', float, '', 'PLAIN', 'Main', 'Spherical aberration, in  millimeter'],
        ['--ac', '0.1', float, '', 'PLAIN', 'Main', 'Amplitude contrast; normal range 0.04~0.1; pure ice 0.04, carbon 0.1; but doesn\'t matter too much if using wrong value'],
        ['Phase plate:Phase Plate', ['False', 'True'], bool, '', 'COMBO', 'Main', 'Use phase plate options'],
        ['--phase_shift_L', '0.0', float, 'Phase plate:True', 'PLAIN', 'Main', 'User defined phase shift, lowest phase shift,  in degree; typically, ~90.0 for micrographs using phase plate '],
        ['--phase_shift_H', '180.0', float, 'Phase plate:True', 'PLAIN', 'Main', 'User defined phase shift, highest phase shift, final range will be (phase_shift_L, phase_shift_H)'],
        ['--phase_shift_S', '5.0', float, 'Phase plate:True', 'PLAIN', 'Main', 'User defined phase shift search step; don\'t worry about the accuracy; this is just the search step, Gctf will refine the phase shift anyway.'],
        ['--phase_shift_T', '1', int, 'Phase plate:True', 'PLAIN', 'Main', 'Phase shift target in the search; 1: CCC; 2: resolution limit;'],
        ['--defL', '5000', float, '', 'PLAIN', 'Main', 'Lowest defocus value to search, in angstrom'],
        ['--defH', '90000', float, '', 'PLAIN', 'Main', 'Highest defocus value to search, in angstrom'],
        ['--defS', '500', float, '', 'PLAIN', 'Main', 'Step of defocus value used to search, in angstrom'],
        ['--astm', '1000', float, '', 'PLAIN', 'Main', 'Estimated astigmation in angstrom, don\'t need to be accurate, within 0.1~10 times is OK'],
        ['--bfac', '150', float, '', 'PLAIN', 'Advanced', 'Bfactor used to decrease high resolution amplitude,A^2; NOT the estimated micrograph Bfactor! suggested range 50~300 except using "REBS method".'],
        ['--resL', '50', float, '', 'PLAIN', 'Advanced', 'Lowest Resolution to be used for search, in angstrom'],
        ['--resH', '4', float, '', 'PLAIN', 'Advanced', 'Highest Resolution to be used for search, in angstrom'],
        ['--boxsize', '1024', int, '', 'PLAIN', 'Advanced', 'Boxsize in pixel to be used for FFT, 512 or 1024 highly recommended'],
        ['--overlap', '0.5', float, '', 'PLAIN', 'Advanced', 'Overlapping factor for grid boxes sampling, for boxsize=512, 0.5 means 256 pixeles overlapping'],
        ['--convsize', '85', float, '', 'PLAIN', 'Advanced', 'Boxsize to be used for smoothing, suggested 1/10 ~ 1/20 of boxsize in pixel, e.g. 40 for 512 boxsize'],
        ['--do_EPA', '0', int, '', 'PLAIN', 'Advanced', '1: Do Equiphase average; 0: Don\'t do;  only for nice output, will NOT be used for CTF determination.'],
        ['--do_Hres_ref', '0', int, '', 'PLAIN', 'Advanced', 'Whether to do High-resolution refinement or not, very useful for selecting high quality micrographs'],
        ['--Href_resL', '15.0', float, '', 'PLAIN', 'Advanced', 'Lowest Resolution  to be used for High-resolution refinement, in angstrom'],
        ['--Href_resH', '4.0', float, '', 'PLAIN', 'Advanced', 'Highest Resolution  to be used for High-resolution refinement, in angstrom'],
        ['--Href_bfac', '50', float, '', 'PLAIN', 'Advanced', 'Bfactor to be used for High-resolution refinement,A^2 NOT the estimated micrograph Bfactor!'],
        ['--refine_after_EPA', '0', int, '', 'PLAIN', 'Advanced', 'Refinement after EPA'],
        ['--estimate_B', '1', int, '', 'PLAIN', 'Advanced', 'Estimate B-Factor'],
        ['--B_resL', '15', float, '', 'PLAIN', 'Advanced', 'Lowest resolution for Bfactor estimation; This output Bfactor is the real estimation of the micrograph'],
        ['--B_resH', '6', float, '', 'PLAIN', 'Advanced', 'Highest resolution for Bfactor estimation'],
        ['Use movies', ['False', 'True'], bool, '', 'COMBO', 'Advanced', 'Enable Gctf movie mode'],
        ['--do_mdef_refine', '0', int, 'Use movies:True', 'PLAIN', 'Advanced', 'Whether to do CTF refinement of each frames, by default it will do averaged frames. Not quite useful at the moment, but maybe in future.'],
        ['--mdef_ave_type', '0', int, 'Use movies:True', 'PLAIN', 'Advanced', '0: coherent average, average FFT with phase information(suggested for movies); 1:incoherent average, only average amplitude(suggested for particle stack);'],
        ['--mdef_aveN', '7', int, 'Use movies:True', 'PLAIN', 'Advanced', 'Average number of movie frames for movie or particle stack CTF refinement'],
        ['--mdef_fit', '0', int, 'Use movies:True', 'PLAIN', 'Advanced', '0: no fitting; 1: linear fitting defocus changes in Z-direction'],
        ['--do_local_refine', '0', int, '', 'PLAIN', 'Advanced', '0: do not refine local defocus(default); 1: refine local defocus, need .box or .star coordinate files ("--boxsuffix" option).'],
        ['--local_radius', '1024', float, '', 'PLAIN', 'Advanced', 'Radius for local refinement, no weighting if the distance is larger than that'],
        ['--local_boxsize', '512', float, '', 'PLAIN', 'Advanced', 'Boxsize for local refinement'],
        ['--local_overlap', '0.5', float, '', 'PLAIN', 'Advanced', 'Overlapping factor for grid boxes sampling'],
        ['--local_avetype', '0', float, '', 'PLAIN', 'Advanced', '0: equal weights for all local areas, neither distance nor frequency is weighted; 1: single weight for each local area, only distance is weighted;'],
        ['--do_phase_flip', '0', int, '', 'PLAIN', 'Advanced', 'Whether to do phase flip and write a new micrograph'],
        ['--do_validation', '0', int, '', 'PLAIN', 'Advanced', 'Whether to validate the CTF determination.'],
        ['--ctfout_resL', '100.0', float, '', 'PLAIN', 'Advanced', 'Lowest resolution for CTF diagnosis file. NOTE this only affects the final output of .ctf file, nothing related to CTF determination.'],
        ['--ctfout_resH', '2.8', float, '', 'PLAIN', 'Advanced', 'Highest resolution for CTF diagnosis file, ~Nyqiust by default.'],
        ['--ctfout_bfac', '50', float, '', 'PLAIN', 'Advanced', 'Bfactor for CTF diagnosis file. NOTE this only affects the final output of .ctf file, nothing related to CTF determination.'],
        ['--gid:GPU', '0', [int]*99, '', 'PLAIN', 'Advanced', 'GPU id, normally it\'s 0, use gpu_info to get information of all available GPUs.'],
        ['GPU SPLIT:GPU SPLIT', '1', int, '', 'PLAIN', 'Advanced', 'NOT AN ISAC2 OPTION. Specify how many jobs per GPU.'],
        ['Split Gpu?', ['True', 'False'], bool, '', 'COMBO', 'Advanced', 'NOT A CRYOLO OPTION. Split the gpu values specified in --gpu to be able to run mutliple crYOLO jobs in parallel.'],
        ]
    return items


def default_gctf_v1_18():
    """
    Content of GCtf version 1.18.

    Arguments:
    None

    Return:
    Content items as list
    """
    items = [
        ['WIDGETS MAIN', '10', int, '', 'PLAIN', '', ''],
        ['WIDGETS ADVANCED', '10', int, '', 'PLAIN', '', ''],
        ['WIDGETS RARE', '10', int, '', 'PLAIN', '', ''],
        ['--apix:Pixel size', '1.34', float, '', 'PLAIN', 'Main', 'Pixel size'],
        ['--dstep', '14.0', float, '', 'PLAIN', 'Main', 'Detector size in micrometer; don\'t worry if unknown; just use default.'],
        ['--kV:voltage', '300', float, '', 'PLAIN', 'Main', 'High tension in Kilovolt, typically 300, 200 or 120'],
        ['--cs', '2.7', float, '', 'PLAIN', 'Main', 'Spherical aberration, in  millimeter'],
        ['--ac', '0.1', float, '', 'PLAIN', 'Main', 'Amplitude contrast; normal range 0.04~0.1; pure ice 0.04, carbon 0.1; but doesn\'t matter too much if using wrong value'],
        ['Phase plate:Phase Plate', ['False', 'True'], bool, '', 'COMBO', 'Main', 'Use phase plate options'],
        ['--phase_shift_L', '0.0', float, 'Phase plate:True', 'PLAIN', 'Main', 'User defined phase shift, lowest phase shift,  in degree; typically, ~90.0 for micrographs using phase plate '],
        ['--phase_shift_H', '180.0', float, 'Phase plate:True', 'PLAIN', 'Main', 'User defined phase shift, highest phase shift, final range will be (phase_shift_L, phase_shift_H)'],
        ['--phase_shift_S', '5.0', float, 'Phase plate:True', 'PLAIN', 'Main', 'User defined phase shift search step; don\'t worry about the accuracy; this is just the search step, Gctf will refine the phase shift anyway.'],
        ['--phase_shift_T', '1', int, 'Phase plate:True', 'PLAIN', 'Main', 'Phase shift target in the search; 1: CCC; 2: resolution limit;'],
        ['--only_search_ps', '0', int, 'Phase plate:True', 'PLAIN', 'Advanced', 'Only search phase shift'],
        ['--cosearch_refine_ps', '0', int, 'Phase plate:True', 'PLAIN', 'Advanced', 'Specify this option to do refinement during phase shift search. Default approach is to do refinement after search'],
        ['--refine_2d_T', '1', int, '', 'PLAIN', 'Advanced', 'Refinement type: 1, 2, 3 allowed; NOTE:  --phase_shift_T is the overall target, but refine_2d_T is the concrete refinement approaches.'],
        ['--defL', '5000', float, '', 'PLAIN', 'Main', 'Lowest defocus value to search, in angstrom'],
        ['--defH', '90000', float, '', 'PLAIN', 'Main', 'Highest defocus value to search, in angstrom'],
        ['--defS', '500', float, '', 'PLAIN', 'Main', 'Step of defocus value used to search, in angstrom'],
        ['--bfac', '150', float, '', 'PLAIN', 'Advanced', 'Bfactor used to decrease high resolution amplitude,A^2; NOT the estimated micrograph Bfactor! suggested range 50~300 except using "REBS method".'],
        ['--astm', '1000', float, '', 'PLAIN', 'Main', 'Estimated astigmation in angstrom, don\'t need to be accurate, within 0.1~10 times is OK'],
        ['--resL', '50', float, '', 'PLAIN', 'Advanced', 'Lowest Resolution to be used for search, in angstrom'],
        ['--resH', '4', float, '', 'PLAIN', 'Advanced', 'Highest Resolution to be used for search, in angstrom'],
        ['--boxsize', '1024', int, '', 'PLAIN', 'Advanced', 'Boxsize in pixel to be used for FFT, 512 or 1024 highly recommended'],
        ['--overlap', '0.5', float, '', 'PLAIN', 'Advanced', 'Overlapping factor for grid boxes sampling, for boxsize=512, 0.5 means 256 pixeles overlapping'],
        ['--convsize', '85', float, '', 'PLAIN', 'Advanced', 'Boxsize to be used for smoothing, suggested 1/10 ~ 1/20 of boxsize in pixel, e.g. 40 for 512 boxsize'],
        ['--smooth_resL', '1000.00', float, '', 'PLAIN', 'Advanced', 'Provide a reasonable resolution for low frequency background smoothing; 20 angstrom suggested, 10-50 is proper range'],
        ['--do_EPA', '0', int, '', 'PLAIN', 'Advanced', '1: Do Equiphase average; 0: Don\'t do;  only for nice output, will NOT be used for CTF determination.'],
        ['--refine_after_EPA', '0', int, '', 'PLAIN', 'Advanced', 'Refinement after EPA'],
        ['--do_Hres_ref', '0', int, '', 'PLAIN', 'Advanced', 'Whether to do High-resolution refinement or not, very useful for selecting high quality micrographs'],
        ['--Href_resL', '15.0', float, '', 'PLAIN', 'Advanced', 'Lowest Resolution  to be used for High-resolution refinement, in angstrom'],
        ['--Href_resH', '4.0', float, '', 'PLAIN', 'Advanced', 'Highest Resolution  to be used for High-resolution refinement, in angstrom'],
        ['--Href_bfac', '50', float, '', 'PLAIN', 'Advanced', 'Bfactor to be used for High-resolution refinement,A^2 NOT the estimated micrograph Bfactor!'],
        ['--Href_PS_err', '2', float, '', 'PLAIN', 'Advanced', ''],
        ['--Href_U_err', '100', float, '', 'PLAIN', 'Advanced', ''],
        ['--Href_V_err', '100', float, '', 'PLAIN', 'Advanced', ''],
        ['--Href_A_err', '5', float, '', 'PLAIN', 'Advanced', ''],
        ['--estimate_B', '1', int, '', 'PLAIN', 'Advanced', 'Estimate B-Factor'],
        ['--B_resL', '15', float, '', 'PLAIN', 'Advanced', 'Lowest resolution for Bfactor estimation; This output Bfactor is the real estimation of the micrograph'],
        ['--B_resH', '6', float, '', 'PLAIN', 'Advanced', 'Highest resolution for Bfactor estimation'],
        ['Use movies', ['False', 'True'], bool, '', 'COMBO', 'Advanced', 'Enable Gctf movie mode'],
        ['--do_mdef_refine', '0', int, 'Use movies:True', 'PLAIN', 'Advanced', 'Whether to do CTF refinement of each frames, by default it will do averaged frames. Not quite useful at the moment, but maybe in future.'],
        ['--mdef_ave_type', '0', int, 'Use movies:True', 'PLAIN', 'Advanced', '0: coherent average, average FFT with phase information(suggested for movies); 1:incoherent average, only average amplitude(suggested for particle stack);'],
        ['--mdef_aveN', '7', int, 'Use movies:True', 'PLAIN', 'Advanced', 'Average number of movie frames for movie or particle stack CTF refinement'],
        ['--mdef_fit', '0', int, 'Use movies:True', 'PLAIN', 'Advanced', '0: no fitting; 1: linear fitting defocus changes in Z-direction'],
        ['--do_local_refine', '0', int, '', 'PLAIN', 'Advanced', '0: do not refine local defocus(default); 1: refine local defocus, need .box or .star coordinate files ("--boxsuffix" option).'],
        ['--local_radius', '1024', float, '', 'PLAIN', 'Advanced', 'Radius for local refinement, no weighting if the distance is larger than that'],
        ['--local_boxsize', '512', float, '', 'PLAIN', 'Advanced', 'Boxsize for local refinement'],
        ['--local_overlap', '0.5', float, '', 'PLAIN', 'Advanced', 'Overlapping factor for grid boxes sampling'],
        ['--local_avetype', '0', float, '', 'PLAIN', 'Advanced', '0: equal weights for all local areas, neither distance nor frequency is weighted; 1: single weight for each local area, only distance is weighted;'],
        ['--do_phase_flip', '0', int, '', 'PLAIN', 'Advanced', 'Whether to do phase flip and write a new micrograph'],
        ['--do_validation', '0', int, '', 'PLAIN', 'Advanced', 'Whether to validate the CTF determination.'],
        ['--ctfout_resL', '100.0', float, '', 'PLAIN', 'Advanced', 'Lowest resolution for CTF diagnosis file. NOTE this only affects the final output of .ctf file, nothing related to CTF determination.'],
        ['--ctfout_resH', '2.8', float, '', 'PLAIN', 'Advanced', 'Highest resolution for CTF diagnosis file, ~Nyqiust by default.'],
        ['--ctfout_bfac', '50', float, '', 'PLAIN', 'Advanced', 'Bfactor for CTF diagnosis file. NOTE this only affects the final output of .ctf file, nothing related to CTF determination.'],
        ['--gid:GPU', '0', [int]*99, '', 'PLAIN', 'Advanced', 'GPU id, normally it\'s 0, use gpu_info to get information of all available GPUs.'],
        ['Split Gpu?', ['True', 'False'], bool, '', 'COMBO', 'Advanced', 'NOT A CRYOLO OPTION. Split the gpu values specified in --gid to be able to run mutliple crYOLO jobs in parallel.'],
        ]
    return items


def default_path():
    """
    Content of Path tab.

    Arguments:
    None

    Return:
    Content items as list
    """
    items = [
        ['WIDGETS MAIN', '10', int, '', 'PLAIN', 'Main', ''],
        ['WIDGETS ADVANCED', '10', int, '', 'PLAIN', 'Main', ''],
        ['WIDGETS RARE', '10', int, '', 'PLAIN', 'Main', ''],
        ['IMOD header', 'header', str, '', 'FILE', 'Main', ''],
        ['IMOD newstack', 'newstack', str, '', 'FILE', 'Main', ''],
        ['IMOD dm2mrc', 'dm2mrc', str, '', 'FILE', 'Main', ''],
        ['e2proc2d.py', 'e2proc2d.py', str, '', 'FILE', 'Main', ''],
        ['sp_header.py', 'sp_header.py', str, '', 'FILE', 'Main', ''],
        ['sp_pipe.py', 'sp_pipe.py', str, '', 'FILE', 'Main', ''],
        ['e2bdb.py', 'e2bdb.py', str, '', 'FILE', 'Main', ''],
        ['mpirun', 'mpirun', str, '', 'FILE', 'Main', ''],
        ['SumMovie v1.0.2', 'summovie', str, '', 'FILE', 'Main', ''],
        ['cryolo_gui.py', 'cryolo_gui.py', str, '', 'FILE', 'Main', ''],
        ]
    function_dict = tu.get_function_dict()
    for key in sorted(function_dict.keys()):
        if function_dict[key]['executable']:
            if function_dict[key]['has_path']:
                items.append([key, function_dict[key]['has_path'], str, '', 'FILE', 'Advanced', ''])
        else:
            pass

    return items


def default_font():
    """
    Content of Font tab.

    Arguments:
    None

    Return:
    Content items as list
    """
    items = [
        ['Font', '5', float, '', 'PLAIN', '', ''],
        ['Width adjustment', '1', float, '', 'PLAIN', '', ''],
        ['Height adjustment', '1', float, '', 'PLAIN', '', ''],
        ['Start button', '25', float, '', 'PLAIN', '', ''],
        ['Notification edit', '40', float, '', 'PLAIN', '', ''],
        ['Notification check', '25', float, '', 'PLAIN', '', ''],
        ['Notification button', '30', float, '', 'PLAIN', '', ''],
        ['Mount button', '80', float, '', 'PLAIN', '', ''],
        ['Frame entry', '5', float, '', 'PLAIN', '', ''],
        ['Frame button', '8', float, '', 'PLAIN', '', ''],
        ['Frame label', '8', float, '', 'PLAIN', '', ''],
        ['Setting widget', '15', float, '', 'PLAIN', '', ''],
        ['Setting widget large', '25', float, '', 'PLAIN', '', ''],
        ['Setting widget xlarge', '100', float, '', 'PLAIN', '', ''],
        ['Status name', '12', float, '', 'PLAIN', '', ''],
        ['Status info', '12', float, '', 'PLAIN', '', ''],
        ['Status quota', '12', float, '', 'PLAIN', '', ''],
        ['Tab width', '50', float, '', 'PLAIN', '', ''],
        ['Widget height', '3', float, '', 'PLAIN', '', ''],
        ['Tab height', '5', float, '', 'PLAIN', '', ''],
        ]
    return items


def default_others(settings_folder):
    """
    Content of Status tab.

    Arguments:
    None

    Return:
    Content items as list
    """
    file_name = os.path.join(os.path.dirname(__file__), 'images', 'Transphire.png')
    templates = ['DEFAULT']
    templates.extend(sorted([os.path.basename(entry) for entry in glob.glob(os.path.join(settings_folder, '*')) if os.path.isdir(entry)]))
    items = [
        ['Default template', templates, str, '', 'COMBO', '', 'Image used in the lower right corner of TranSPHIRE.'],
        ['Image', file_name, str, '', 'FILE', '', 'Image used in the lower right corner of TranSPHIRE.'],
        ['Project name pattern', '', str, '', 'PLAIN', '', 'Regex pattern for the project name.'],
        ['Project name pattern example', '', str, '', 'PLAIN', '', 'Example of the specified pattern.'],
        ]
    return items


def default_notification():
    """
    Content of notification tab.

    Arguments:
    None

    Return:
    Content items as list
    """
    items = [
        ['WIDGETS MAIN', '10', int, '', 'PLAIN', '', ''],
        ['WIDGETS ADVANCED', '10', int, '', 'PLAIN', '', ''],
        ['WIDGETS RARE', '10', int, '', 'PLAIN', '', ''],
        ['Project quota warning (%)', '80', float, '', 'PLAIN', 'Main', ''],
        ['Project quota stop (%)', '90', float, '', 'PLAIN', 'Main', ''],
        ['Scratch quota warning (%)', '80', float, '', 'PLAIN', 'Main', ''],
        ['Scratch quota stop (%)', '90', float, '', 'PLAIN', 'Main', ''],
        ['Time until notification', '25', float, '', 'PLAIN', 'Main', ''],
        ['Nr. of values used for median', '5', int, '', 'PLAIN', 'Main', ''],
        ]
    dtype_dict = ti.get_dtype_dict()
    skip_set = set([
        'file_name',
        'mic_number',
        'image',
        'object'
        ])
    for name in tu.get_unique_types():
        try:
            for key in dtype_dict[name]:
                key = key[0]
                if key in skip_set:
                    continue
                else:
                    items.append(
                        ['{0} warning'.format(key), '-1000000 1000000', [float, float], '', 'PLAIN', 'Main', ''],
                        )
                    items.append(
                        ['{0} skip'.format(key), '-1000000 1000000', [float, float], '', 'PLAIN', 'Main', ''],
                        )
        except KeyError:
            pass
    return items


def default_notification_widget():
    """
    Content of notification widget.

    Arguments:
    None

    Return:
    Content items as list
    """
    items = [
        ['Bot token', '', str, '', 'PLAIN', '', 'Telegram Bot token.'],
        [
            'Default names telegram',
            'name1:telegram_name1;name2:telegram_name2',
            str,
            '',
            'PLAIN',
            '',
            'Default names for the Notification area.',
            ],
        ['SMTP server', '', str, '', 'PLAIN', '', 'SMTP Mail server'],
        ['E-Mail adress', '', str, '', 'PLAIN', '', 'E-Mail address used to send e-mails'],
        [
            'Default names email',
            'name1:telegram_name1;name2:telegram_name2',
            str,
            '',
            'PLAIN',
            '',
            'Default names for the Notification area.',
            ],
        ['Number of users', '3', int, '', 'PLAIN', '', 'Number of freely choosable users in addition to the default users.'],
        ]
    return items


def default_pipeline():
    """
    Content of pipeline tab.

    Arguments:
    None

    Return:
    Content items as list
    """
    items = [
        ['WIDGETS MAIN', '10', int, '', 'PLAIN', '', ''],
        ['WIDGETS ADVANCED', '10', int, '', 'PLAIN', '', ''],
        ['WIDGETS RARE', '10', int, '', 'PLAIN', '', ''],
        [
            'Meta',
            '1',
            int,
            'Meta;' +
            'Session to work:Copy to work:Copy_to_work,' +
            'Session to backup:Copy to backup:Copy_to_backup,' +
            'Session to HDD:Copy to HDD:Copy_to_hdd',
            'PLAIN',
            'Main',
            ''
            ],
        ['Find', '1', int, 'Find;Import', 'PLAIN', 'Main', ''],
        [
            'Import',
            '1',
            int,
            'Find;' +
            'Motion:Motion,' +
            'CTF_frames:CTF,' +
            'Compress:Compress,' +
            'Meta to work:Copy to work:Copy_to_work,' +
            'Meta to backup:Copy to backup:Copy_to_backup,' +
            'Meta to HDD:Copy to HDD:Copy_to_hdd,' +
            'Frames to work:Copy to work:Copy_to_work,' +
            'Frames to HDD:Copy to HDD:Copy_to_hdd,' +
            'Frames to backup:Copy to backup:Copy_to_backup',
            'PLAIN',
            'Main',
            ''
            ],
        [
            'Motion',
            '1',
            int,
            'Motion;' +
            'CTF_sum:CTF,' +
            'Picking:Picking,' +
            'Extract:Extract,' +
            'Train2d:Train2d,' +
            'Motion to work:Copy to work:Copy_to_work,' +
            'Motion to HDD:Copy to HDD:Copy_to_hdd,' +
            'Motion to backup:Copy to backup:Copy_to_backup',
            'PLAIN',
            'Main',
            ''
            ],
        [
            'CTF',
            '1',
            int,
            'CTF;' +
            'Extract:Extract,' +
            'CTF to work:Copy to work:Copy_to_work,' +
            'CTF to HDD:Copy to HDD:Copy_to_hdd,' +
            'CTF to backup:Copy to backup:Copy_to_backup',
            'PLAIN',
            'Main',
            ''
            ],
        [
            'Picking',
            '1',
            int,
            'Picking;' +
            'Extract:Extract,' +
            'Picking to work:Copy to work:Copy_to_work,' +
            'Picking to HDD:Copy to HDD:Copy_to_hdd,' +
            'Picking to backup:Copy to backup:Copy_to_backup',
            'PLAIN',
            'Main',
            ''
            ],
        [
            'Extract',
            '1',
            int,
            'Extract;' +
            'Class2d:Class2d,' +
            'Extract to work:Copy to work:Copy_to_work,' +
            'Extract to HDD:Copy to HDD:Copy_to_hdd,' +
            'Extract to backup:Copy to backup:Copy_to_backup',
            'PLAIN',
            'Main',
            ''
            ],
        [
            'Class2d',
            '1',
            int,
            'Class2d;' +
            'Select2d:Select2d,' +
            'Class2d to work:Copy to work:Copy_to_work,' +
            'Class2d to HDD:Copy to HDD:Copy_to_hdd,' +
            'Class2d to backup:Copy to backup:Copy_to_backup',
            'PLAIN',
            'Main',
            ''
            ],
        [
            'Select2d',
            '1',
            int,
            'Select2d;' +
            'Train2d:Train2d,' +
            'Auto3d:Auto3d,' +
            'Select2d to work:Copy to work:Copy_to_work,' +
            'Select2d to HDD:Copy to HDD:Copy_to_hdd,' +
            'Select2d to backup:Copy to backup:Copy_to_backup',
            'PLAIN',
            'Main',
            ''
            ],
        [
            'Train2d',
            '1',
            int,
            'Train2d;' +
            'Train2d to work:Copy to work:Copy_to_work,' +
            'Train2d to HDD:Copy to HDD:Copy_to_hdd,' +
            'Train2d to backup:Copy to backup:Copy_to_backup',
            'PLAIN',
            'Main',
            ''
            ],
        [
            'Auto3d',
            '1',
            int,
            'Auto3d;' +
            'Auto3d to work:Copy to work:Copy_to_work,' +
            'Auto3d to HDD:Copy to HDD:Copy_to_hdd,' +
            'Auto3d to backup:Copy to backup:Copy_to_backup',
            'PLAIN',
            'Main',
            ''
            ],
        [
            'Compress',
            '1',
            int,
            'Compress;' +
            'Compress to work:Copy to work:Copy_to_work,' +
            'Compress to HDD:Copy to HDD:Copy_to_hdd,' +
            'Compress to backup:Copy to backup:Copy_to_backup',
            'PLAIN',
            'Main',
            ''
            ],
        ['Copy_to_work', '1', int, 'Copy_to_work;', 'PLAIN', 'Main', ''],
        ['Copy_to_hdd', '1', int, 'Copy_to_hdd;', 'PLAIN', 'Main', ''],
        ['Copy_to_backup', '1', int, 'Copy_to_backup;', 'PLAIN', 'Main', ''],
        ]
    return items


def default_ctffind_4_v4_1_8():
    """
    Content of CTFFind version 4.1.8.

    Arguments:
    None

    Return:
    Content items as list
    """
    items = [
        ['WIDGETS MAIN', '10', int, '', 'PLAIN', '', ''],
        ['WIDGETS ADVANCED', '10', int, '', 'PLAIN', '', ''],
        ['WIDGETS RARE', '10', int, '', 'PLAIN', '', ''],
        ['Pixel size:Pixel size', '1.0', float, '', 'PLAIN', 'Main', ''],
        ['Acceleration voltage', '300.0', float, '', 'PLAIN', 'Main', ''],
        ['Spherical aberration', '2.7', float, '', 'PLAIN', 'Main', ''],
        ['Min resolution(A)', '30', float, '', 'PLAIN', 'Main', ''],
        ['Max resolution(A)', '5', float, '', 'PLAIN', 'Main', ''],
        ['Min defocus(A)', '5000', float, '', 'PLAIN', 'Main', ''],
        ['Max defocus(A)', '50000', float, '', 'PLAIN', 'Main', ''],
        ['Step defocus(A)', '500', float, '', 'PLAIN', 'Main', ''],
        ['Amplitude contrast', '0.07', float, '', 'PLAIN', 'Main', ''],
        ['Phase shift:Phase Plate', ['False', 'True'], bool, '', 'COMBO', 'Main', ''],
        ['Min phase(rad)', '0', float, 'Phase shift:True', 'PLAIN', 'Main', ''],
        ['Max phase(rad)', '3.15', float, 'Phase shift:True', 'PLAIN', 'Main', ''],
        ['Step phase(rad)', '0.5', float, 'Phase shift:True', 'PLAIN', 'Main', ''],
        ['Amplitude spectrum', '512', float, '', 'PLAIN', 'Advanced', ''],
        ['High accuracy', ['True', 'False'], bool, '', 'COMBO', 'Advanced', ''],
        ['Know astigmatism', ['False', 'True'], bool, '', 'COMBO', 'Advanced', ''],
        ['Restrain astigmatism', ['True', 'False'], bool, 'Know astigmatism:False', 'COMBO', 'Advanced', ''],
        ['Expected astigmatism', '200', float, 'Restrain astigmatism:True', 'PLAIN', 'Advanced', ''],
        ['Astigmatism', '0', float, 'Know astigmatism:True', 'PLAIN', 'Advanced', ''],
        ['Astigmatism angle', '0', float, 'Know astigmatism:True', 'PLAIN', 'Advanced', ''],
        ['Resample micrographs', ['True', 'False'], bool, '', 'COMBO', 'Advanced', ''],
        ['Use movies', ['False', 'True'], bool, '', 'COMBO', 'Advanced', ''],
        ['Combine frames', '1', int, 'Use movies:True', 'PLAIN', 'Advanced', ''],
        ['Movie is gain-corrected?', ['True', 'False'], bool, 'Use movies:True', 'COMBO', 'Advanced', ''],
        ['Gain file:Gain', '', str, 'Movie is gain-corrected?:False', 'FILE', 'Advanced', ''],
        ['Correct mag. distort.', ['False', 'True'], bool, 'Use movies:True', 'COMBO', 'Advanced', ''],
        ['Mag. dist. angle', '0.0', float, 'Correct mag. distort.:True', 'PLAIN', 'Advanced', ''],
        ['Mag. dist. major scale', '1.0', float, 'Correct mag. distort.:True', 'PLAIN', 'Advanced', ''],
        ['Mag. dist. minor scale', '1.0', float, 'Correct mag. distort.:True', 'PLAIN', 'Advanced', ''],
        ]
    return items


def default_mount(hdd=None):
    """
    Content of Mount tab.

    Arguments:
    hdd - Content is related to HDD

    Return:
    Content items as list
    """
    if hdd is not None:
        name = 'HDD'
    else:
        name = ''
    items = [
        ['Mount name', name, str, '', 'PLAIN', '', ''],
        ['Protocol', ['smbfs', 'cifs', 'nfs'], str, '', 'COMBO', '', ''],
        ['Protocol version', '2.0', float, '', 'PLAIN', '', ''],
        ['sec', ['ntlmssp', 'krb5', 'krb5i', 'ntlm', 'ntlmi', 'ntlmv2', 'ntlmv2i', 'ntlmsspi', 'none'], str, '', 'COMBO', '', ''],
        ['gid', '', str, '', 'PLAIN', '', ''],
        ['Domain', '', str, '', 'PLAIN', '', ''],
        ['IP', '', str, '', 'PLAIN', '', ''],
        ['Folder', '', str, '', 'PLAIN', '', ''],
        ['Folder from root', '', str, '', 'PLAIN', '', ''],
        ['Need folder extension?', ['False', 'True'], bool, '', 'COMBO', '', ''],
        ['Default user', '', str, '', 'PLAIN', '', ''],
        ['Is df giving the right quota?', ['True', 'False'], bool, '', 'COMBO', '', ''],
        ['Target UID exists here and on target?', ['True', 'False'], bool, '', 'COMBO', '', ''],
        ['Need sudo for mount?', ['False', 'True'], bool, '', 'COMBO', '', ''],
        ['Need sudo for copy?', ['False', 'True'], bool, '', 'COMBO', '', ''],
        ['SSH address', '', str, '', 'PLAIN', '', ''],
        ['Quota command', '', str, '', 'PLAIN', '', ''],
        ['Quota / TB', '', float, '', 'PLAIN', '', ''],
        ['Typ', ['Import', 'Copy_to_work', 'Copy_to_backup'], str, '', 'COMBO', '', ''],
        ]
    return items


def default_motion_cor_2_v1_0_0():
    """
    Content of MotionCor2 version 1.0.0.

    Arguments:
    None

    Return:
    Content items as list
    """
    items = [
        ['WIDGETS MAIN', '10', int, '', 'PLAIN', '', ''],
        ['WIDGETS ADVANCED', '10', int, '', 'PLAIN', '', ''],
        ['WIDGETS RARE', '10', int, '', 'PLAIN', '', ''],
        ['-FmDose', '0', float, '', 'PLAIN', 'Main', 'Frame dose in e/A^2. If not specified, dose weighting will be skipped.'],
        ['-PixSize:Pixel size', '0', float, '', 'PLAIN', 'Main', 'Pixel size in A of input stack in angstrom. If not specified, dose weighting will be skipped.'],
        ['-kV:voltage', '300', float, '', 'PLAIN', 'Main', 'High tension in kV needed for dose weighting.  Default is 300.'],
        ['-Patch', '0 0', [int, int], '', 'PLAIN', 'Main', 'Number of patches to be used for patch based alignment, default 0 0 corresponding full frame alignment.'],
        ['-Bft', '100', float, '', 'PLAIN', 'Main', 'B-Factor for alignment, default 100.'],
        ['-Throw', '0', int, '', 'PLAIN', 'Main', 'Throw initial number of frames, default is 0'],
        ['-Trunc', '0', int, '', 'PLAIN', 'Main', 'Truncate last number of frames, default is 0'],
        ['-Gain:Gain', '', str, '', 'FILE', 'Main', 'MRC file that stores the gain reference. If not specified, MRC extended header will be visited to look for gain reference.'],
        ['-RotGain', '0', int, '', 'PLAIN', 'Main', 'Rotate gain reference counter-clockwise.  0 - no rotation, default, 1 - rotate 90 degree, 2 - rotate 180 degree, 3 - rotate 270 degree.'],
        ['-FlipGain', '0', int, '', 'PLAIN', 'Main', 'Flip gain reference after gain rotation.  0 - no flipping, default, 1 - flip upside down, 2 - flip left right.'],
        ['-MaskCent', '0 0', [float, float], '', 'PLAIN', 'Advanced', 'Center of subarea that will be used for alignement, default 0 0 corresponding to the frame center.'],
        ['-MaskSize', '1 1', [float, float], '', 'PLAIN', 'Advanced', 'The size of subarea that will be used for alignment, default 1.0 1.0 corresponding full size.'],
        ['-Iter', '7', int, '', 'PLAIN', 'Advanced', 'Maximum iterations for iterative alignment, default 5 iterations.'],
        ['-Tol', '0.5', float, '', 'PLAIN', 'Advanced', 'Tolerance for iterative alignment, default 0.5 pixel.'],
        ['-PhaseOnly', '0', int, '', 'PLAIN', 'Advanced', 'Only phase is used in cross correlation.  default is 0, i.e., false.'],
        ['-StackZ', '0', int, '', 'PLAIN', 'Advanced', 'Number of frames per stack. If not specified, it will be loaded from MRC header.'],
        ['-FtBin:Bin superres', '1', float, '', 'PLAIN', 'Advanced', 'Binning performed in Fourier space, default 1.0.'],
        ['-InitDose', '0', float, '', 'PLAIN', 'Advanced', 'Initial dose received before stack is acquired'],
        ['-Group', '1', int, '', 'PLAIN', 'Advanced', 'Group every specified number of frames by adding them together. The alignment is then performed on the summed frames. By default, no grouping is performed.'],
        ['-FmRef', '-1', int, '', 'PLAIN', 'Advanced', 'Specify which frame to be the reference to which all other frames are aligned. By default (-1) the the central frame is chosen. The central frame is at N/2 based upon zero indexing where N is the number of frames that will be summed, i.e., not including the frames thrown away.'],
        ['-DefectFile', '', str, '', 'FILE', 'Advanced', '1. Defect file that stores entries of defects on camera.  2. Each entry corresponds to a rectangular region in image.  The pixels in such a region are replaced by neighboring good pixel values.  3. Each entry contains 4 integers x, y, w, h representing the x, y coordinates, width, and heights, respectively.'],
        ['-Tilt', '0 0', [float, float], '', 'PLAIN', 'Advanced', 'Specify the starting angle and the step angle of tilt series. They are required for dose weighting. If not given, dose weighting will be disabled.'],
        ['-Mag', '1 1 0', [float, float, float], '', 'PLAIN', 'Advanced', '1. Correct anisotropic magnification by stretching image along the major axis, the axis where the lower magificantion is detected.  2. Three inputs are needed including magnifications along major and minor axes and the angle of the major axis relative to the image x-axis in degree.  3. By default no correction is performed.'],
        ['-InFmMotion', '0', int, '', 'PLAIN', 'Advanced', '1. 1 - Account for in-frame motion.  0 - Do not account for in-frame motion.'],
        ['-Crop', '0 0', [int, int], '', 'PLAIN', 'Advanced', '1. Crop the loaded frames to the given size.  2. By default the original size is loaded.'],
        ['-Gpu:GPU', '0', [int]*99, '', 'PLAIN', 'Advanced', ' GPU IDs. Default 0.  For multiple GPUs, separate IDs by space.  For example, -Gpu 0 1 2 3 specifies 4 GPUs.'],
        ['Split Gpu?', ['True', 'False'], bool, '', 'COMBO', 'Advanced', 'NOT A CRYOLO OPTION. Split the gpu values specified in --Gpu to be able to run mutliple crYOLO jobs in parallel.'],
        ['dose cutoff', '4', float, '', 'PLAIN', 'Advanced', 'NOT A MOTIONCOR OPTION. Used to create the Relion3 bayesian polishing files.'],
        ]
    return items


def default_motion_cor_2_v1_0_5():
    """
    Content of MotionCor2 version 1.0.5.

    Arguments:
    None

    Return:
    Content items as list
    """
    items = [
        ['WIDGETS MAIN', '10', int, '', 'PLAIN', '', ''],
        ['WIDGETS ADVANCED', '10', int, '', 'PLAIN', '', ''],
        ['WIDGETS RARE', '10', int, '', 'PLAIN', '', ''],
        ['-FmDose', '0', float, '', 'PLAIN', 'Main', 'Frame dose in e/A^2. If not specified, dose weighting will be skipped.'],
        ['-PixSize:Pixel size', '0', float, '', 'PLAIN', 'Main', 'Pixel size in A of input stack in angstrom. If not specified, dose weighting will be skipped.'],
        ['-kV:voltage', '300', float, '', 'PLAIN', 'Main', 'High tension in kV needed for dose weighting.  Default is 300.'],
        ['-Patch', '0 0 0', [int, int, int], '', 'PLAIN', 'Main', '1. It follows by  number of patches in x and y dimensions, and overlapping in percentage of adjacent patches.  2. The default values are 0 0 0, meaning only full-frame based alignment is performed.'],
        ['-Bft', '100', float, '', 'PLAIN', 'Main', 'B-Factor for alignment, default 100.'],
        ['-Throw', '0', int, '', 'PLAIN', 'Main', 'Throw initial number of frames, default is 0'],
        ['-Trunc', '0', int, '', 'PLAIN', 'Main', 'Truncate last number of frames, default is 0'],
        ['-Gain:Gain', '', str, '', 'FILE', 'Main', 'MRC file that stores the gain reference. If not specified, MRC extended header will be visited to look for gain reference.'],
        ['-RotGain', '0', int, '', 'PLAIN', 'Main', 'Rotate gain reference counter-clockwise.  0 - no rotation, default, 1 - rotate 90 degree, 2 - rotate 180 degree, 3 - rotate 270 degree.'],
        ['-FlipGain', '0', int, '', 'PLAIN', 'Main', 'Flip gain reference after gain rotation.  0 - no flipping, default, 1 - flip upside down, 2 - flip left right.'],
        ['-MaskCent', '0 0', [float, float], '', 'PLAIN', 'Advanced', 'Center of subarea that will be used for alignement, default 0 0 corresponding to the frame center.'],
        ['-MaskSize', '1 1', [float, float], '', 'PLAIN', 'Advanced', 'The size of subarea that will be used for alignment, default 1.0 1.0 corresponding full size.'],
        ['-Iter', '7', int, '', 'PLAIN', 'Advanced', 'Maximum iterations for iterative alignment, default 5 iterations.'],
        ['-Tol', '0.5', float, '', 'PLAIN', 'Advanced', 'Tolerance for iterative alignment, default 0.5 pixel.'],
        ['-PhaseOnly', '0', int, '', 'PLAIN', 'Advanced', 'Only phase is used in cross correlation.  default is 0, i.e., false.'],
        ['-StackZ', '0', int, '', 'PLAIN', 'Advanced', 'Number of frames per stack. If not specified, it will be loaded from MRC header.'],
        ['-FtBin:Bin superres', '1', float, '', 'PLAIN', 'Advanced', 'Binning performed in Fourier space, default 1.0.'],
        ['-InitDose', '0', float, '', 'PLAIN', 'Advanced', 'Initial dose received before stack is acquired'],
        ['-Group', '1', int, '', 'PLAIN', 'Advanced', 'Group every specified number of frames by adding them together. The alignment is then performed on the summed frames. By default, no grouping is performed.'],
        ['-FmRef', '-1', int, '', 'PLAIN', 'Advanced', 'Specify which frame to be the reference to which all other frames are aligned. By default (-1) the the central frame is chosen. The central frame is at N/2 based upon zero indexing where N is the number of frames that will be summed, i.e., not including the frames thrown away.'],
        ['-DefectFile', '', str, '', 'FILE', 'Advanced', '1. Defect file that stores entries of defects on camera.  2. Each entry corresponds to a rectangular region in image.  The pixels in such a region are replaced by neighboring good pixel values.  3. Each entry contains 4 integers x, y, w, h representing the x, y coordinates, width, and heights, respectively.'],
        ['-Dark', '', str, '', 'FILE', 'Advanced', '1. MRC file that stores the dark reference. If not specified, dark subtraction will be skipped.  2. If -RotGain and/or -FlipGain is specified, the dark reference will also be rotated and/or flipped.'],
        ['-Tilt', '0 0', [float, float], '', 'PLAIN', 'Advanced', 'Specify the starting angle and the step angle of tilt series. They are required for dose weighting. If not given, dose weighting will be disabled.'],
        ['-Mag', '1 1 0', [float, float, float], '', 'PLAIN', 'Advanced', '1. Correct anisotropic magnification by stretching image along the major axis, the axis where the lower magificantion is detected.  2. Three inputs are needed including magnifications along major and minor axes and the angle of the major axis relative to the image x-axis in degree.  3. By default no correction is performed.'],
        ['-InFmMotion', '0', int, '', 'PLAIN', 'Advanced', '1. 1 - Account for in-frame motion.  0 - Do not account for in-frame motion.'],
        ['-Crop', '0 0', [int, int], '', 'PLAIN', 'Advanced', '1. Crop the loaded frames to the given size.  2. By default the original size is loaded.'],
        ['-Gpu', '0', [int]*99, '', 'PLAIN', 'Advanced', ' GPU IDs. Default 0.  For multiple GPUs, separate IDs by space.  For example, -Gpu 0 1 2 3 specifies 4 GPUs.'],
        ['GPU SPLIT:GPU SPLIT', '1', int, '', 'PLAIN', 'Advanced', 'NOT AN ISAC2 OPTION. Specify how many jobs per GPU.'],
        ['Split Gpu?', ['True', 'False'], bool, '', 'COMBO', 'Advanced', 'NOT A CRYOLO OPTION. Split the gpu values specified in --Gpu to be able to run mutliple crYOLO jobs in parallel.'],
        ['dose cutoff', '4', float, '', 'PLAIN', 'Advanced', 'NOT A MOTIONCOR OPTION. Used to create the Relion3 bayesian polishing files.'],
        ]
    return items


def default_motion_cor_2_v1_1_0():
    """
    Content of MotionCor2 version 1.1.0.

    Arguments:
    None

    Return:
    Content items as list
    """
    items = [
        ['WIDGETS MAIN', '10', int, '', 'PLAIN', '', ''],
        ['WIDGETS ADVANCED', '10', int, '', 'PLAIN', '', ''],
        ['WIDGETS RARE', '10', int, '', 'PLAIN', '', ''],
        ['-FmDose', '0', float, '', 'PLAIN', 'Main', 'Frame dose in e/A^2. If not specified, dose weighting will be skipped.'],
        ['-PixSize:Pixel size', '0', float, '', 'PLAIN', 'Main', 'Pixel size in A of input stack in angstrom. If not specified, dose weighting will be skipped.'],
        ['-kV:voltage', '300', float, '', 'PLAIN', 'Main', 'High tension in kV needed for dose weighting.  Default is 300.'],
        ['-Patch', '0 0 0', [int, int, int], '', 'PLAIN', 'Main', '1. It follows by  number of patches in x and y dimensions, and overlapping in percentage of adjacent patches.  2. The default values are 0 0 0, meaning only full-frame based alignment is performed.'],
        ['-Bft', '500 150', [float, float], '', 'PLAIN', 'Main', 'B-Factor for alignment, default 100.'],
        ['-Throw', '0', int, '', 'PLAIN', 'Main', 'Throw initial number of frames, default is 0'],
        ['-Trunc', '0', int, '', 'PLAIN', 'Main', 'Truncate last number of frames, default is 0'],
        ['-Gain:Gain', '', str, '', 'FILE', 'Main', 'MRC file that stores the gain reference. If not specified, MRC extended header will be visited to look for gain reference.'],
        ['-RotGain', '0', int, '', 'PLAIN', 'Main', 'Rotate gain reference counter-clockwise.  0 - no rotation, default, 1 - rotate 90 degree, 2 - rotate 180 degree, 3 - rotate 270 degree.'],
        ['-FlipGain', '0', int, '', 'PLAIN', 'Main', 'Flip gain reference after gain rotation.  0 - no flipping, default, 1 - flip upside down, 2 - flip left right.'],
        ['-MaskCent', '0 0', [float, float], '', 'PLAIN', 'Advanced', 'Center of subarea that will be used for alignement, default 0 0 corresponding to the frame center.'],
        ['-MaskSize', '1 1', [float, float], '', 'PLAIN', 'Advanced', 'The size of subarea that will be used for alignment, default 1.0 1.0 corresponding full size.'],
        ['-Iter', '7', int, '', 'PLAIN', 'Advanced', 'Maximum iterations for iterative alignment, default 5 iterations.'],
        ['-Tol', '0.5', float, '', 'PLAIN', 'Advanced', 'Tolerance for iterative alignment, default 0.5 pixel.'],
        ['-PhaseOnly', '0', int, '', 'PLAIN', 'Advanced', 'Only phase is used in cross correlation.  default is 0, i.e., false.'],
        ['-StackZ', '0', int, '', 'PLAIN', 'Advanced', 'Number of frames per stack. If not specified, it will be loaded from MRC header.'],
        ['-FtBin:Bin superres', '1', float, '', 'PLAIN', 'Advanced', 'Binning performed in Fourier space, default 1.0.'],
        ['-InitDose', '0', float, '', 'PLAIN', 'Advanced', 'Initial dose received before stack is acquired'],
        ['-Group', '1', int, '', 'PLAIN', 'Advanced', 'Group every specified number of frames by adding them together. The alignment is then performed on the summed frames. By default, no grouping is performed.'],
        ['-FmRef', '-1', int, '', 'PLAIN', 'Advanced', 'Specify which frame to be the reference to which all other frames are aligned. By default (-1) the the central frame is chosen. The central frame is at N/2 based upon zero indexing where N is the number of frames that will be summed, i.e., not including the frames thrown away.'],
        ['-DefectFile', '', str, '', 'FILE', 'Advanced', '1. Defect file that stores entries of defects on camera.  2. Each entry corresponds to a rectangular region in image.  The pixels in such a region are replaced by neighboring good pixel values.  3. Each entry contains 4 integers x, y, w, h representing the x, y coordinates, width, and heights, respectively.'],
        ['-Dark', '', str, '', 'FILE', 'Advanced', '1. MRC file that stores the dark reference. If not specified, dark subtraction will be skipped.  2. If -RotGain and/or -FlipGain is specified, the dark reference will also be rotated and/or flipped.'],
        ['-Tilt', '0 0', [float, float], '', 'PLAIN', 'Advanced', 'Specify the starting angle and the step angle of tilt series. They are required for dose weighting. If not given, dose weighting will be disabled.'],
        ['-Mag', '1 1 0', [float, float, float], '', 'PLAIN', 'Advanced', '1. Correct anisotropic magnification by stretching image along the major axis, the axis where the lower magificantion is detected.  2. Three inputs are needed including magnifications along major and minor axes and the angle of the major axis relative to the image x-axis in degree.  3. By default no correction is performed.'],
        ['-InFmMotion', '0', int, '', 'PLAIN', 'Advanced', '1. 1 - Account for in-frame motion.  0 - Do not account for in-frame motion.'],
        ['-Crop', '0 0', [int, int], '', 'PLAIN', 'Advanced', '1. Crop the loaded frames to the given size.  2. By default the original size is loaded.'],
        ['-Gpu:GPU', '0', [int]*99, '', 'PLAIN', 'Advanced', ' GPU IDs. Default 0.  For multiple GPUs, separate IDs by space.  For example, -Gpu 0 1 2 3 specifies 4 GPUs.'],
        ['-GpuMemUsage:Memory usage', '0.5', float, '', 'PLAIN', 'Advanced', '1. GPU memory usage, default 0.5, meaning 50% of GPU memory will be used to buffer movie frames.  2. The value should be between 0 and 0.5. When 0 is given, all movie frames are buffered on CPU memory.'],
        ['GPU SPLIT:GPU SPLIT', '1', int, '', 'PLAIN', 'Advanced', 'NOT AN ISAC2 OPTION. Specify how many jobs per GPU.'],
        ['Split Gpu?', ['True', 'False'], bool, '', 'COMBO', 'Advanced', 'NOT A CRYOLO OPTION. Split the gpu values specified in --Gpu to be able to run mutliple crYOLO jobs in parallel.'],
        ['dose cutoff', '4', float, '', 'PLAIN', 'Advanced', 'NOT A MOTIONCOR OPTION. Used to create the Relion3 bayesian polishing files.'],
        ]
    return items


def default_general():
    """
    Content of General tab.

    Arguments:
    None

    Return:
    Content items as list
    """
    items = [
        ['WIDGETS MAIN', '10', int, '', 'PLAIN', '', ''],
        ['WIDGETS ADVANCED', '10', int, '', 'PLAIN', '', ''],
        ['WIDGETS RARE', '10', int, '', 'PLAIN', '', ''],
        ['Software', ['EPU >=1.9', 'EPU >=1.8', 'Latitude S', 'Just Stack'], str, '', 'COMBO', 'Main', 'Software used for data collection.'],
        ['Type', ['Stack', 'Frames'], str, '', 'COMBO', 'Main', 'Stack type used for data collection.'],
        ['Camera', ['K2', 'K3', 'Falcon3', 'Falcon2'], str, '', 'COMBO', 'Main', 'Camera used for data collection.'],
        ['Search path frames', '', str, '', 'DIR', 'Main', 'Directory path containing the micrograph movie files of the data collection (mrc, tif, tiff, ...)'],
        ['Search path meta', '', str, '', 'DIR', 'Main', 'Directory path containing the Meta files of the data collection (jpg, xml, ... files). Can be the same as Serach path frames.'],
        ['Input extension', ['mrc', 'dm4', 'tif', 'tiff'], str, '', 'COMBO', 'Main', 'Extension of the original micrograph movies.'],
        ['Project name', '', str, '', 'PLAIN', 'Main', 'Project name.'],
        ['Number of frames', '0', int, '', 'PLAIN', 'Main', 'Expected number of frames of the input micrograph movies. This is used to verify that the micrograph movie is not corrupted.'],
        ['Rename micrographs', ['True', 'False'], bool, '', 'COMBO', 'Main', 'Rename the micrographs.'],
        ['Rename prefix', '', str, 'Rename micrographs:True', 'PLAIN', 'Main', 'prefix for the renamed micrographs prefix_number_suffix.extension; The separator between prefix and number needs to be specified, too.'],
        ['Rename suffix', '', str, 'Rename micrographs:True', 'PLAIN', 'Main', 'Suffix for the renamed micrographs prefix_number_suffix.extension; The separator between number and suffix needs to be specified, too.'],
        ['Increment number', ['True', 'False'], bool, 'Rename micrographs:True', 'COMBO', 'Main', 'Increment the number automatically in continue mode instead of manually.'],
        ['Start number', '0', int, 'Rename micrographs:True', 'PLAIN', 'Main', 'First number to use for the renaming process.'],
        ['Estimated mic number', '10000', int, 'Rename micrographs:True', 'PLAIN', 'Main', 'Estimated number of micrographs. This is used for the leading number of zeros in the renamed start number.'],
        ['Project directory', '', str, '', 'DIR', 'Advanced', 'TranSPHIRE project directory used to store all the project folders.'],
        ['Scratch directory', '', str, '', 'DIR', 'Advanced', 'TranSPHIRE scratch directory used for faster IO during the TranSPHIRE run.'],
        ['Number of feedbacks', '1', int, '', 'PLAIN', 'Advanced', 'Number of iterations to re-train crYOLO in an ISAC feedback loop. The feedback loop will use the ISAC output and do a crYOLO retrain with sparse picking.'],
        ]
    return items


def default_copy(settings_folder):
    """
    Content of Copy tab.

    Arguments:
    None

    Return:
    Content items as list
    """
    extend_list = ['Later', 'False']
    mount_dict = tu.get_key_names(
        settings_folder=settings_folder,
        name='Mount'
        )
    programs_extern = tu.reduce_programs()

    copy_to_work = sorted(mount_dict['Copy_to_work'])
    copy_to_backup = sorted(mount_dict['Copy_to_backup'])
    copy_to_hdd = sorted(mount_dict['Copy_to_hdd'])

    copy_to_work.extend(extend_list)
    copy_to_backup.extend(extend_list)
    copy_to_hdd.extend(extend_list)

    for value in programs_extern.values():
        value.extend(extend_list)

    #valid_sub_items = [entry['typ'] for entry in value for value in tu.get_function_dict().values() in entry['typ'] is not None]
    valid_sub_items = tu.get_unique_types()

    items = [
        ['WIDGETS MAIN', '10', int, '', 'PLAIN', '', ''],
        ['WIDGETS ADVANCED', '10', int, '', 'PLAIN', '', ''],
        ['WIDGETS RARE', '10', int, '', 'PLAIN', '', '', ''],
        ['Copy to work', copy_to_work, bool, '', 'COMBO', 'Main', 'Copy data to the work drive.'],
        ['Copy to backup', copy_to_backup, bool, '', 'COMBO', 'Main', 'Copy data to the backup drive.'],
        ['Copy to HDD', copy_to_hdd, bool, '', 'COMBO', 'Main', 'Copy data to an external hard disc.'],
        ]

    for entry in valid_sub_items:
        items.append([entry, programs_extern[entry], bool, '', 'COMBO', 'Main', 'Software for {0}.'.format(entry)])

    items.extend([
        ['Session to work', ['False', 'True'], bool, '', 'COMBO', 'Advanced', 'Copy the non-micrograph data (EPU session, ...) to the work drive if "Copy to work" is specified.'],
        ['Session to backup', ['True', 'False'], bool, '', 'COMBO', 'Advanced', 'Copy the non-micrograph data (EPU session, ...) to the backup drive if "Copy to backup" is specified.'],
        ['Session to HDD', ['True', 'False'], bool, '', 'COMBO', 'Advanced', 'Copy the non-micrograph data (EPU session, ...) to the HDD drive if "Copy to HDD" is specified.'],
        ['Frames to work', ['False', 'True'], bool, '', 'COMBO', 'Advanced', 'Copy the micograph movies to the work drive if "Copy to work" is specified.'],
        ['Frames to backup', ['False', 'True'], bool, '', 'COMBO', 'Advanced', 'Copy the micograph movies to the backup drive if "Copy to backup" is specified.'],
        ['Frames to HDD', ['False', 'True'], bool, '', 'COMBO', 'Advanced', 'Copy the micograph movies to the HDD drive if "Copy to HDD" is specified.'],
        ['Meta to work', ['True', 'False'], bool, '', 'COMBO', 'Advanced', 'Copy the micrograph meta data to the work drive if "Copy to work" is specified.'],
        ['Meta to backup', ['True', 'False'], bool, '', 'COMBO', 'Advanced', 'Copy the micrograph meta data to the backup drive if "Copy to backup" is specified.'],
        ['Meta to HDD', ['True', 'False'], bool, '', 'COMBO', 'Advanced', 'Copy the micrograph meta data to the HDD drive if "Copy to HDD" is specified.'],
        ])

    for entry in valid_sub_items:
        items.append(['{0} to work'.format(entry), ['True', 'False'], bool, '', 'COMBO', 'Advanced', 'Copy the {0} data to the work drive if "Copy to work" is specified.'.format(entry)])
        items.append(['{0} to backup'.format(entry), ['True', 'False'], bool, '', 'COMBO', 'Advanced', 'Copy the {0} data to the backup drive if "Copy to backup" is specified.'.format(entry)])
        items.append(['{0} to HDD'.format(entry), ['True', 'False'], bool, '', 'COMBO', 'Advanced', 'Copy the {0} data the HDD drive if "Copy to HDD" is specified.'.format(entry)])

    items.extend([
        ['Tar to work', ['False', 'True'], bool, '', 'COMBO', 'Advanced', 'Copy the information to work drive in tar format if "Copy to work" is specified.'],
        ['Tar to backup', ['False', 'True'], bool, '', 'COMBO', 'Advanced', 'Copy the information to backup drive in tar format if "Copy to backup" is specified.'],
        ['Tar to HDD', ['False', 'True'], bool, '', 'COMBO', 'Advanced', 'Copy the information to HDD drive in tar format if "Copy to HDD" is specified.'],
        ['Tar size (Gb)', '2', float, '', 'PLAIN', 'Advanced', 'Size of the tar files before copying.'],
        ['Delete data after import?', ['True', 'False'], bool, '', 'COMBO', 'Advanced', 'Delete the data from the camera computer after the import.'],
        ['Delete stack after compression?', ['True', 'False'], bool, '', 'COMBO', 'Advanced', 'Delete the mrc stack after compression.'],
        ['Delete compressed stack after copy?', ['False', 'True'], bool, '', 'COMBO', 'Advanced', 'Delete the compressed stack after copying to another location.'],
        ])
    return items


def default_global():
    items = [
        ['WIDGETS MAIN', '10', int, '', 'PLAIN', '', ''],
        ['WIDGETS ADVANCED', '10', int, '', 'PLAIN', '', ''],
        ['WIDGETS RARE', '10', int, '', 'PLAIN', '', ''],
        ['Bin superres', ['ON-THE-FLY', 'False'], bool, '', 'COMBO', 'Main', 'Bin superresolution datasets by a factor of 2 automatically.'],
        ['Pixel size:Pixel size', '1.0', float, '', 'PLAIN', 'Main', '', 'Pixel size in A/pixel.'],
        ['Phase Plate:Phase Plate', ['False', 'True'], bool, '', 'COMBO', 'Main', 'Use phase plate options'],
        ['Gain:Gain', '', str, '', 'FILE', 'Main', '', 'MRC file that stores the gain reference. If not specified, MRC extended header will be visited to look for gain reference.'],
        ['voltage:voltage', '300.0', float, '', 'PLAIN', 'Main', 'High tension in kV needed for dose weighting.  Default is 300.'],
        ['GPU:GPU', '0', [int]*99, '', 'PLAIN', 'Main', 'Specifiy which gpu\'s should be used.'],
        ['Memory usage:Memory usage', '0.9', float, '', 'PLAIN', 'Main', 'Specifiy how much GPU memory should be used.'],
        ['GPU SPLIT:GPU SPLIT', '0', int, '', 'PLAIN', 'Main', 'Define the number of GPU splits.'],
        ]
    return items
