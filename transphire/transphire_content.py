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

import os
from transphire import transphire_utils as tu
from transphire import transphire_import as ti


def default_cryolo_v1_2_2():
    """
    Content of crYOLO version 1.2.2

    Arguments:
    None

    Return:
    Content items as list
    """
    items = default_cryolo_v1_2_1()
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
        ['WIDGETS MAIN', '5', int, '', 'PLAIN', '', ''],
        ['WIDGETS ADVANCED', '5', int, '', 'PLAIN', '', ''],
        ['WIDGETS RARE', '5', int, '', 'PLAIN', '', ''],
        ['--conf', '', str, '', 'FILE', 'Main', '', 'Path to configuration file.'],
        ['--weights', '', str, '', 'FILE', 'Main', 'Path to pretrained weights.'],
        ['--threshold', '0.3', float, '', 'PLAIN', 'Main', 'Confidence threshold. Have to be between 0 and 1. As higher, as more conservative.'],
        ['Pixel size (A/px)', '1', float, 'Filter micrographs:True', 'PLAIN', 'Main', 'NOT A CRYOLO OPTION. Pixel size value. Only used for visual representation.'],
        ['Box size', '200', int, '', 'PLAIN', 'Main', 'NOT A CRYOLO OPTION. Box size value. Only used for visual representation.'],
        ['--filament', ['False', 'True'], bool, '', 'COMBO', 'Main', 'Activate filament mode'],
        ['--filament_width', '0', float, '--filament:True', 'PLAIN', 'Main', '(FILAMENT MODE) Filament width (in pixel)'],
        ['--box_distance', '0', int, '--filament:True', 'PLAIN', 'Main', '(FILAMENT MODE) Distance between two boxes(in pixel)'],
        ['--minimum_number_boxes', '0', int, '--filament:True', 'PLAIN', 'Main', '(FILAMENT MODE) Distance between two boxes(in pixel)'],
        ['Filter micrographs', ['True', 'False'], bool, '', 'COMBO', 'Advanced', 'NOT A CRYOLO OPTION. Box size value. Only used for visual representation.'],
        ['Filter value high pass (A)', '9999', float, 'Filter micrographs:True', 'PLAIN', 'Advanced', 'NOT A CRYOLO OPTION. High-pass filter value in angstrom before running crYOLO.'],
        ['Filter value low pass (A)', '10', float, 'Filter micrographs:True', 'PLAIN', 'Advanced', 'NOT A CRYOLO OPTION. Low-pass filter value in angstrom before running crYOLO.'],
        ['--patch', '-1', int, '', 'PLAIN', 'Advanced', 'Number of patches. (-1 uses the patch size specified in the configuration file.)'],
        ['--gpu', '0', [int]*99, '', 'PLAIN', 'Advanced', 'Specifiy which gpu\'s should be used.'],
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
        ['WIDGETS MAIN', '5', int, '', 'PLAIN', '', ''],
        ['WIDGETS ADVANCED', '5', int, '', 'PLAIN', '', ''],
        ['WIDGETS RARE', '5', int, '', 'PLAIN', '', ''],
        ['--conf', '', str, '', 'FILE', 'Main', '', 'Path to configuration file.'],
        ['--weights', '', str, '', 'FILE', 'Main', 'Path to pretrained weights.'],
        ['--threshold', '0.3', float, '', 'PLAIN', 'Main', 'Confidence threshold. Have to be between 0 and 1. As higher, as more conservative.'],
        ['Pixel size (A/px)', '1', float, 'Filter micrographs:True', 'PLAIN', 'Main', 'NOT A CRYOLO OPTION. Pixel size value. Only used for visual representation.'],
        ['Box size', '200', int, '', 'PLAIN', 'Main', 'NOT A CRYOLO OPTION. Box size value. Only used for visual representation.'],
        ['--filament', ['False', 'True'], bool, '', 'COMBO', 'Main', 'Activate filament mode'],
        ['--filament_width', '0', float, '--filament:True', 'PLAIN', 'Main', '(FILAMENT MODE) Filament width (in pixel)'],
        ['--box_distance', '0', int, '--filament:True', 'PLAIN', 'Main', '(FILAMENT MODE) Distance between two boxes(in pixel)'],
        ['--minium_number_boxes', '0', int, '--filament:True', 'PLAIN', 'Main', '(FILAMENT MODE) Distance between two boxes(in pixel)'],
        ['Filter micrographs', ['True', 'False'], bool, '', 'COMBO', 'Advanced', 'NOT A CRYOLO OPTION. Box size value. Only used for visual representation.'],
        ['Filter value high pass (A)', '9999', float, 'Filter micrographs:True', 'PLAIN', 'Advanced', 'NOT A CRYOLO OPTION. High-pass filter value in angstrom before running crYOLO.'],
        ['Filter value low pass (A)', '10', float, 'Filter micrographs:True', 'PLAIN', 'Advanced', 'NOT A CRYOLO OPTION. Low-pass filter value in angstrom before running crYOLO.'],
        ['--patch', '-1', int, '', 'PLAIN', 'Advanced', 'Number of patches. (-1 uses the patch size specified in the configuration file.)'],
        ['--gpu', '0', [int]*99, '', 'PLAIN', 'Advanced', 'Specifiy which gpu\'s should be used.'],
        ['Split Gpu?', ['True', 'False'], bool, '', 'COMBO', 'Advanced', 'NOT A CRYOLO OPTION. Split the gpu values specified in --gpu to be able to run mutliple crYOLO jobs in parallel.'],
        ]
    return items


def default_cryolo_v1_0_5():
    """
    Content of crYOLO version 1.0.5

    Arguments:
    None

    Return:
    Content items as list
    """
    return default_cryolo_v1_0_4()


def default_cryolo_v1_0_4():
    """
    Content of crYOLO version 1.0.4

    Arguments:
    None

    Return:
    Content items as list
    """
    items = [
        ['WIDGETS MAIN', '5', int, '', 'PLAIN', '', ''],
        ['WIDGETS ADVANCED', '5', int, '', 'PLAIN', '', ''],
        ['WIDGETS RARE', '5', int, '', 'PLAIN', '', ''],
        ['--conf', '', str, '', 'FILE', 'Main', '', 'Path to configuration file.'],
        ['--weights', '', str, '', 'FILE', 'Main', 'Path to pretrained weights.'],
        ['--threshold', '0.3', float, '', 'PLAIN', 'Main', 'Confidence threshold. Have to be between 0 and 1. As higher, as more conservative.'],
        ['Pixel size (A/px)', '1', float, 'Filter micrographs:True', 'PLAIN', 'Main', 'NOT A CRYOLO OPTION. Pixel size value. Only used for visual representation.'],
        ['Box size', '200', int, '', 'PLAIN', 'Main', 'NOT A CRYOLO OPTION. Box size value. Only used for visual representation.'],
        ['Filter micrographs', ['True', 'False'], bool, '', 'COMBO', 'Advanced', 'NOT A CRYOLO OPTION. Box size value. Only used for visual representation.'],
        ['Filter value high pass (A)', '9999', float, 'Filter micrographs:True', 'PLAIN', 'Advanced', 'NOT A CRYOLO OPTION. High-pass filter value in angstrom before running crYOLO.'],
        ['Filter value low pass (A)', '10', float, 'Filter micrographs:True', 'PLAIN', 'Advanced', 'NOT A CRYOLO OPTION. Low-pass filter value in angstrom before running crYOLO.'],
        ['--patch', '-1', int, '', 'PLAIN', 'Advanced', 'Number of patches. (-1 uses the patch size specified in the configuration file.)'],
        ['--gpu', '0', [int]*99, '', 'PLAIN', 'Advanced', 'Specifiy which gpu\'s should be used.'],
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
        ['WIDGETS MAIN', '7', int, '', 'PLAIN', '', ''],
        ['WIDGETS ADVANCED', '7', int, '', 'PLAIN', '', ''],
        ['WIDGETS RARE', '7', int, '', 'PLAIN', '', ''],
        ['--apix', '-1', float, '', 'PLAIN', 'Main', 'Pixel size [A/Pixels]: The pixel size of input micrograph(s) or images in input particle stack.'],
        ['--Cs', '2.0', float, '', 'PLAIN', 'Main', 'Microscope spherical aberration (Cs) [mm]: The spherical aberration (Cs) of microscope used for imaging.'],
        ['--voltage', '300', float, '', 'PLAIN', 'Main', 'Microscope voltage [kV]: The acceleration voltage of microscope used for imaging.'],
        ['--ac', '10', float, '', 'PLAIN', 'Main', 'Amplitude contrast [%]: The typical amplitude contrast is in the range of 7% - 14%. The value mainly depends on the thickness of the ice embedding the particles.'],
        ['--f_start', '-1', float, '', 'PLAIN', 'Main', 'Lowest resolution [A]: Lowest resolution to be considered in the CTF estimation. Determined automatically by default.'],
        ['--f_stop', '-1', float, '', 'PLAIN', 'Main', 'Highest resolution [A]: Highest resolution to be considered in the CTF estimation. Determined automatically by default.'],
        ['Phase plate', ['False', 'True'], bool, '', 'COMBO', 'Main', 'Volta Phase Plate - fit smplitude contrast.'],
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
        ['WIDGETS MAIN', '7', int, '', 'PLAIN', '', ''],
        ['WIDGETS ADVANCED', '7', int, '', 'PLAIN', '', ''],
        ['WIDGETS RARE', '7', int, '', 'PLAIN', '', ''],
        ['--apix', '1.34', float, '', 'PLAIN', 'Main', 'Pixel size'],
        ['--dstep', '14.0', float, '', 'PLAIN', 'Main', 'Detector size in micrometer; don\'t worry if unknown; just use default.'],
        ['--kV', '300', float, '', 'PLAIN', 'Main', 'High tension in Kilovolt, typically 300, 200 or 120'],
        ['--cs', '2.7', float, '', 'PLAIN', 'Main', 'Spherical aberration, in  millimeter'],
        ['--ac', '0.1', float, '', 'PLAIN', 'Main', 'Amplitude contrast; normal range 0.04~0.1; pure ice 0.04, carbon 0.1; but doesn\'t matter too much if using wrong value'],
        ['Phase plate', ['False', 'True'], bool, '', 'COMBO', 'Main', 'Use phase plate options'],
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
        ['--gid', '0', [int]*99, '', 'PLAIN', 'Advanced', 'GPU id, normally it\'s 0, use gpu_info to get information of all available GPUs.'],
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
        ['WIDGETS MAIN', '7', int, '', 'PLAIN', '', ''],
        ['WIDGETS ADVANCED', '7', int, '', 'PLAIN', '', ''],
        ['WIDGETS RARE', '7', int, '', 'PLAIN', '', ''],
        ['--apix', '1.34', float, '', 'PLAIN', 'Main', 'Pixel size'],
        ['--dstep', '14.0', float, '', 'PLAIN', 'Main', 'Detector size in micrometer; don\'t worry if unknown; just use default.'],
        ['--kV', '300', float, '', 'PLAIN', 'Main', 'High tension in Kilovolt, typically 300, 200 or 120'],
        ['--cs', '2.7', float, '', 'PLAIN', 'Main', 'Spherical aberration, in  millimeter'],
        ['--ac', '0.1', float, '', 'PLAIN', 'Main', 'Amplitude contrast; normal range 0.04~0.1; pure ice 0.04, carbon 0.1; but doesn\'t matter too much if using wrong value'],
        ['Phase plate', ['False', 'True'], bool, '', 'COMBO', 'Main', 'Use phase plate options'],
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
        ['--gid', '0', [int]*99, '', 'PLAIN', 'Advanced', 'GPU id, normally it\'s 0, use gpu_info to get information of all available GPUs.'],
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
        ['WIDGETS MAIN', '8', int, '', 'PLAIN', 'Main', ''],
        ['WIDGETS ADVANCED', '8', int, '', 'PLAIN', 'Main', ''],
        ['WIDGETS RARE', '8', int, '', 'PLAIN', 'Main', ''],
        ['IMOD header', '', str, '', 'FILE', 'Main', ''],
        ['IMOD newstack', '', str, '', 'FILE', 'Main', ''],
        ['IMOD mrc2tif', '', str, '', 'FILE', 'Main', ''],
        ['IMOD dm2mrc', '', str, '', 'FILE', 'Main', ''],
        ['e2proc2d.py', '', str, '', 'FILE', 'Main', ''],
        ['SumMovie v1.0.2', '', str, '', 'FILE', 'Main', ''],
        ]
    function_dict = tu.get_function_dict()
    for key in sorted(function_dict.keys()):
        if function_dict[key]['executable']:
            items.append([key, '', str, '', 'FILE', 'Main', ''])
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
        ['Setting widget', '50', float, '', 'PLAIN', '', ''],
        ['Setting widget large', '50', float, '', 'PLAIN', '', ''],
        ['Status name', '12', float, '', 'PLAIN', '', ''],
        ['Status info', '12', float, '', 'PLAIN', '', ''],
        ['Status quota', '12', float, '', 'PLAIN', '', ''],
        ['Tab width', '50', float, '', 'PLAIN', '', ''],
        ['Widget height', '3', float, '', 'PLAIN', '', ''],
        ['Tab height', '5', float, '', 'PLAIN', '', ''],
        ]
    return items


def default_others():
    """
    Content of Status tab.

    Arguments:
    None

    Return:
    Content items as list
    """
    file_name = os.path.join(os.path.dirname(__file__), 'images', 'Transphire.png')
    items = [
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
    for name in ['ctf', 'motion', 'picking']:
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
        [
            'Meta',
            '1',
            int,
            'Meta;' +
            'Session to work:Copy to work:Copy_work,' +
            'Session to backup:Copy to backup:Copy_backup,' +
            'Session to HDD:Copy to HDD:Copy_hdd',
            'PLAIN',
            '',
            ''
            ],
        ['Find', '1', int, 'Find;Import', 'PLAIN', '', ''],
        [
            'Import',
            '1',
            int,
            'Find;' +
            'Motion:Motion,' +
            'CTF_frames:CTF,' +
            'Compress:Compress,' +
            'Meta to work:Copy to work:Copy_work,' +
            'Meta to backup:Copy to backup:Copy_backup,' +
            'Meta to HDD:Copy to HDD:Copy_hdd,' +
            '!Compress:Frames to work:Copy to work:Copy_work,' +
            '!Compress:Frames to HDD:Copy to HDD:Copy_hdd,' +
            '!Compress:Frames to backup:Copy to backup:Copy_backup',
            'PLAIN',
            '',
            ''
            ],
        [
            'Motion',
            '2',
            int,
            'Motion;' +
            'CTF_sum:CTF,' +
            'Picking:Picking,' +
            'Sum to work:Copy to work:Copy_work,' +
            'Sum to HDD:Copy to HDD:Copy_hdd,' +
            'Sum to backup:Copy to backup:Copy_backup',
            'PLAIN',
            '',
            ''
            ],
        [
            'CTF',
            '2',
            int,
            'CTF;' +
            'CTF to work:Copy to work:Copy_work,' +
            'CTF to HDD:Copy to HDD:Copy_hdd,' +
            'CTF to backup:Copy to backup:Copy_backup',
            'PLAIN',
            '',
            ''
            ],
        [
            'Picking',
            '2',
            int,
            'Picking;' +
            'Picking to work:Copy to work:Copy_work,' +
            'Picking to HDD:Copy to HDD:Copy_hdd,' +
            'Picking to backup:Copy to backup:Copy_backup',
            'PLAIN',
            '',
            ''
            ],
        [
            'Compress',
            '2',
            int,
            'Compress;' +
            'Frames to work:Copy to work:Copy_work,' +
            'Frames to HDD:Copy to HDD:Copy_hdd,' +
            'Frames to backup:Copy to backup:Copy_backup',
            'PLAIN',
            '',
            ''
            ],
        ['Copy_work', '1', int, 'Copy_work;', 'PLAIN', '', ''],
        ['Copy_hdd', '1', int, 'Copy_hdd;', 'PLAIN', '', ''],
        ['Copy_backup', '1', int, 'Copy_backup;', 'PLAIN', '', ''],
        ]
    return items


def default_ctffind_4_v4_1_10():
    """
    Content of CTFFind version 4.1.10.

    Arguments:
    None

    Return:
    Content items as list
    """
    return default_ctffind_4_v4_1_8()


def default_ctffind_4_v4_1_8():
    """
    Content of CTFFind version 4.1.8.

    Arguments:
    None

    Return:
    Content items as list
    """
    items = [
        ['WIDGETS MAIN', '7', int, '', 'PLAIN', '', ''],
        ['WIDGETS ADVANCED', '7', int, '', 'PLAIN', '', ''],
        ['WIDGETS RARE', '7', int, '', 'PLAIN', '', ''],
        ['Pixel size', '1.0', float, '', 'PLAIN', 'Main', ''],
        ['Acceleration voltage', '300.0', float, '', 'PLAIN', 'Main', ''],
        ['Spherical aberration', '2.7', float, '', 'PLAIN', 'Main', ''],
        ['Min resolution(A)', '30', float, '', 'PLAIN', 'Main', ''],
        ['Max resolution(A)', '5', float, '', 'PLAIN', 'Main', ''],
        ['Min defocus(A)', '5000', float, '', 'PLAIN', 'Main', ''],
        ['Max defocus(A)', '50000', float, '', 'PLAIN', 'Main', ''],
        ['Step defocus(A)', '500', float, '', 'PLAIN', 'Main', ''],
        ['Amplitude contrast', '0.07', float, '', 'PLAIN', 'Main', ''],
        ['Phase shift', ['False', 'True'], bool, '', 'COMBO', 'Main', ''],
        ['Min phase(rad)', '0', float, 'Phase shift:True', 'PLAIN', 'Main', ''],
        ['Max phase(rad)', '3.15', float, 'Phase shift:True', 'PLAIN', 'Main', ''],
        ['Step phase(rad)', '0.5', float, 'Phase shift:True', 'PLAIN', 'Main', ''],
        ['Amplitude spectrum', '512', float, '', 'PLAIN', 'Advanced', ''],
        ['High accuracy', ['True', 'False'], bool, '', 'COMBO', 'Advanced', ''],
        ['Know astigmatism', ['True', 'False'], bool, '', 'COMBO', 'Advanced', ''],
        ['Restrain astigmatism', ['True', 'False'], bool, 'Know astigmatism:False', 'COMBO', 'Advanced', ''],
        ['Expected astigmatism', '200', float, 'Restrain astigmatism:True', 'PLAIN', 'Advanced', ''],
        ['Astigmatism', '0', float, 'Know astigmatism:True', 'PLAIN', 'Advanced', ''],
        ['Astigmatism angle', '0', float, 'Know astigmatism:True', 'PLAIN', 'Advanced', ''],
        ['Resample micrographs', ['True', 'False'], bool, '', 'COMBO', 'Advanced', ''],
        ['Use movies', ['False', 'True'], bool, '', 'COMBO', 'Advanced', ''],
        ['Combine frames', '1', int, 'Use movies:True', 'PLAIN', 'Advanced', ''],
        ['Movie is gain-corrected?', ['True', 'False'], bool, 'Use movies:True', 'COMBO', 'Advanced', ''],
        ['Gain file', '', str, 'Movie is gain-corrected?:False', 'FILE', 'Advanced', ''],
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
        ['Need folder extension?', ['False', 'True'], bool, '', 'COMBO', '', ''],
        ['Default user', '', str, '', 'PLAIN', '', ''],
        ['Is df giving the right quota?', ['True', 'False'], bool, '', 'COMBO', '', ''],
        ['Target UID exists here and on target?', ['True', 'False'], bool, '', 'COMBO', '', ''],
        ['Need sudo for mount?', ['False', 'True'], bool, '', 'COMBO', '', ''],
        ['Need sudo for copy?', ['False', 'True'], bool, '', 'COMBO', '', ''],
        ['SSH address', '', str, '', 'PLAIN', '', ''],
        ['Quota command', '', str, '', 'PLAIN', '', ''],
        ['Quota / TB', '', float, '', 'PLAIN', '', ''],
        ['Typ', ['Import', 'Copy_work', 'Copy_backup'], str, '', 'COMBO', '', ''],
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
        ['WIDGETS MAIN', '5', int, '', 'PLAIN', '', ''],
        ['WIDGETS ADVANCED', '5', int, '', 'PLAIN', '', ''],
        ['WIDGETS RARE', '5', int, '', 'PLAIN', '', ''],
        ['-FmDose', '0', float, '', 'PLAIN', 'Main', 'Frame dose in e/A^2. If not specified, dose weighting will be skipped.'],
        ['-PixSize', '0', float, '', 'PLAIN', 'Main', 'Pixel size in A of input stack in angstrom. If not specified, dose weighting will be skipped.'],
        ['-kV', '300', float, '', 'PLAIN', 'Main', 'High tension in kV needed for dose weighting.  Default is 300.'],
        ['-Patch', '0 0', [int, int], '', 'PLAIN', 'Main', 'Number of patches to be used for patch based alignment, default 0 0 corresponding full frame alignment.'],
        ['-Bft', '100', float, '', 'PLAIN', 'Main', 'B-Factor for alignment, default 100.'],
        ['-Throw', '0', int, '', 'PLAIN', 'Main', 'Throw initial number of frames, default is 0'],
        ['-Trunc', '0', int, '', 'PLAIN', 'Main', 'Truncate last number of frames, default is 0'],
        ['-Gain', '', str, '', 'FILE', 'Main', 'MRC file that stores the gain reference. If not specified, MRC extended header will be visited to look for gain reference.'],
        ['-RotGain', '0', int, '', 'PLAIN', 'Main', 'Rotate gain reference counter-clockwise.  0 - no rotation, default, 1 - rotate 90 degree, 2 - rotate 180 degree, 3 - rotate 270 degree.'],
        ['-FlipGain', '0', int, '', 'PLAIN', 'Main', 'Flip gain reference after gain rotation.  0 - no flipping, default, 1 - flip upside down, 2 - flip left right.'],
        ['-MaskCent', '0 0', [float, float], '', 'PLAIN', 'Advanced', 'Center of subarea that will be used for alignement, default 0 0 corresponding to the frame center.'],
        ['-MaskSize', '1 1', [float, float], '', 'PLAIN', 'Advanced', 'The size of subarea that will be used for alignment, default 1.0 1.0 corresponding full size.'],
        ['-Iter', '7', int, '', 'PLAIN', 'Advanced', 'Maximum iterations for iterative alignment, default 5 iterations.'],
        ['-Tol', '0.5', float, '', 'PLAIN', 'Advanced', 'Tolerance for iterative alignment, default 0.5 pixel.'],
        ['-PhaseOnly', '0', int, '', 'PLAIN', 'Advanced', 'Only phase is used in cross correlation.  default is 0, i.e., false.'],
        ['-StackZ', '0', int, '', 'PLAIN', 'Advanced', 'Number of frames per stack. If not specified, it will be loaded from MRC header.'],
        ['-FtBin', '1', float, '', 'PLAIN', 'Advanced', 'Binning performed in Fourier space, default 1.0.'],
        ['-InitDose', '0', float, '', 'PLAIN', 'Advanced', 'Initial dose received before stack is acquired'],
        ['-Group', '1', int, '', 'PLAIN', 'Advanced', 'Group every specified number of frames by adding them together. The alignment is then performed on the summed frames. By default, no grouping is performed.'],
        ['-FmRef', '-1', int, '', 'PLAIN', 'Advanced', 'Specify which frame to be the reference to which all other frames are aligned. By default (-1) the the central frame is chosen. The central frame is at N/2 based upon zero indexing where N is the number of frames that will be summed, i.e., not including the frames thrown away.'],
        ['-DefectFile', '', str, '', 'FILE', 'Advanced', '1. Defect file that stores entries of defects on camera.  2. Each entry corresponds to a rectangular region in image.  The pixels in such a region are replaced by neighboring good pixel values.  3. Each entry contains 4 integers x, y, w, h representing the x, y coordinates, width, and heights, respectively.'],
        ['-Tilt', '0 0', [float, float], '', 'PLAIN', 'Advanced', 'Specify the starting angle and the step angle of tilt series. They are required for dose weighting. If not given, dose weighting will be disabled.'],
        ['-Mag', '1 1 0', [float, float, float], '', 'PLAIN', 'Advanced', '1. Correct anisotropic magnification by stretching image along the major axis, the axis where the lower magificantion is detected.  2. Three inputs are needed including magnifications along major and minor axes and the angle of the major axis relative to the image x-axis in degree.  3. By default no correction is performed.'],
        ['-InFmMotion', '0', int, '', 'PLAIN', 'Advanced', '1. 1 - Account for in-frame motion.  0 - Do not account for in-frame motion.'],
        ['-Crop', '0 0', [int, int], '', 'PLAIN', 'Advanced', '1. Crop the loaded frames to the given size.  2. By default the original size is loaded.'],
        ['-Gpu', '0', [int]*99, '', 'PLAIN', 'Advanced', ' GPU IDs. Default 0.  For multiple GPUs, separate IDs by space.  For example, -Gpu 0 1 2 3 specifies 4 GPUs.'],
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
        ['WIDGETS MAIN', '5', int, '', 'PLAIN', '', ''],
        ['WIDGETS ADVANCED', '5', int, '', 'PLAIN', '', ''],
        ['WIDGETS RARE', '5', int, '', 'PLAIN', '', ''],
        ['-FmDose', '0', float, '', 'PLAIN', 'Main', 'Frame dose in e/A^2. If not specified, dose weighting will be skipped.'],
        ['-PixSize', '0', float, '', 'PLAIN', 'Main', 'Pixel size in A of input stack in angstrom. If not specified, dose weighting will be skipped.'],
        ['-kV', '300', float, '', 'PLAIN', 'Main', 'High tension in kV needed for dose weighting.  Default is 300.'],
        ['-Patch', '0 0 0', [int, int, int], '', 'PLAIN', 'Main', '1. It follows by  number of patches in x and y dimensions, and overlapping in percentage of adjacent patches.  2. The default values are 0 0 0, meaning only full-frame based alignment is performed.'],
        ['-Bft', '100', float, '', 'PLAIN', 'Main', 'B-Factor for alignment, default 100.'],
        ['-Throw', '0', int, '', 'PLAIN', 'Main', 'Throw initial number of frames, default is 0'],
        ['-Trunc', '0', int, '', 'PLAIN', 'Main', 'Truncate last number of frames, default is 0'],
        ['-Gain', '', str, '', 'FILE', 'Main', 'MRC file that stores the gain reference. If not specified, MRC extended header will be visited to look for gain reference.'],
        ['-RotGain', '0', int, '', 'PLAIN', 'Main', 'Rotate gain reference counter-clockwise.  0 - no rotation, default, 1 - rotate 90 degree, 2 - rotate 180 degree, 3 - rotate 270 degree.'],
        ['-FlipGain', '0', int, '', 'PLAIN', 'Main', 'Flip gain reference after gain rotation.  0 - no flipping, default, 1 - flip upside down, 2 - flip left right.'],
        ['-MaskCent', '0 0', [float, float], '', 'PLAIN', 'Advanced', 'Center of subarea that will be used for alignement, default 0 0 corresponding to the frame center.'],
        ['-MaskSize', '1 1', [float, float], '', 'PLAIN', 'Advanced', 'The size of subarea that will be used for alignment, default 1.0 1.0 corresponding full size.'],
        ['-Iter', '7', int, '', 'PLAIN', 'Advanced', 'Maximum iterations for iterative alignment, default 5 iterations.'],
        ['-Tol', '0.5', float, '', 'PLAIN', 'Advanced', 'Tolerance for iterative alignment, default 0.5 pixel.'],
        ['-PhaseOnly', '0', int, '', 'PLAIN', 'Advanced', 'Only phase is used in cross correlation.  default is 0, i.e., false.'],
        ['-StackZ', '0', int, '', 'PLAIN', 'Advanced', 'Number of frames per stack. If not specified, it will be loaded from MRC header.'],
        ['-FtBin', '1', float, '', 'PLAIN', 'Advanced', 'Binning performed in Fourier space, default 1.0.'],
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
        ['WIDGETS MAIN', '5', int, '', 'PLAIN', '', ''],
        ['WIDGETS ADVANCED', '5', int, '', 'PLAIN', '', ''],
        ['WIDGETS RARE', '5', int, '', 'PLAIN', '', ''],
        ['-FmDose', '0', float, '', 'PLAIN', 'Main', 'Frame dose in e/A^2. If not specified, dose weighting will be skipped.'],
        ['-PixSize', '0', float, '', 'PLAIN', 'Main', 'Pixel size in A of input stack in angstrom. If not specified, dose weighting will be skipped.'],
        ['-kV', '300', float, '', 'PLAIN', 'Main', 'High tension in kV needed for dose weighting.  Default is 300.'],
        ['-Patch', '0 0 0', [int, int, int], '', 'PLAIN', 'Main', '1. It follows by  number of patches in x and y dimensions, and overlapping in percentage of adjacent patches.  2. The default values are 0 0 0, meaning only full-frame based alignment is performed.'],
        ['-Bft', '500 150', [float, float], '', 'PLAIN', 'Main', 'B-Factor for alignment, default 100.'],
        ['-Throw', '0', int, '', 'PLAIN', 'Main', 'Throw initial number of frames, default is 0'],
        ['-Trunc', '0', int, '', 'PLAIN', 'Main', 'Truncate last number of frames, default is 0'],
        ['-Gain', '', str, '', 'FILE', 'Main', 'MRC file that stores the gain reference. If not specified, MRC extended header will be visited to look for gain reference.'],
        ['-RotGain', '0', int, '', 'PLAIN', 'Main', 'Rotate gain reference counter-clockwise.  0 - no rotation, default, 1 - rotate 90 degree, 2 - rotate 180 degree, 3 - rotate 270 degree.'],
        ['-FlipGain', '0', int, '', 'PLAIN', 'Main', 'Flip gain reference after gain rotation.  0 - no flipping, default, 1 - flip upside down, 2 - flip left right.'],
        ['-MaskCent', '0 0', [float, float], '', 'PLAIN', 'Advanced', 'Center of subarea that will be used for alignement, default 0 0 corresponding to the frame center.'],
        ['-MaskSize', '1 1', [float, float], '', 'PLAIN', 'Advanced', 'The size of subarea that will be used for alignment, default 1.0 1.0 corresponding full size.'],
        ['-Iter', '7', int, '', 'PLAIN', 'Advanced', 'Maximum iterations for iterative alignment, default 5 iterations.'],
        ['-Tol', '0.5', float, '', 'PLAIN', 'Advanced', 'Tolerance for iterative alignment, default 0.5 pixel.'],
        ['-PhaseOnly', '0', int, '', 'PLAIN', 'Advanced', 'Only phase is used in cross correlation.  default is 0, i.e., false.'],
        ['-StackZ', '0', int, '', 'PLAIN', 'Advanced', 'Number of frames per stack. If not specified, it will be loaded from MRC header.'],
        ['-FtBin', '1', float, '', 'PLAIN', 'Advanced', 'Binning performed in Fourier space, default 1.0.'],
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
        ['-GpuMemUsage', '0.5', float, '', 'PLAIN', 'Advanced', '1. GPU memory usage, default 0.5, meaning 50% of GPU memory will be used to buffer movie frames.  2. The value should be between 0 and 0.5. When 0 is given, all movie frames are buffered on CPU memory.'],
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
        ['WIDGETS MAIN', '7', int, '', 'PLAIN', '', ''],
        ['WIDGETS ADVANCED', '7', int, '', 'PLAIN', '', ''],
        ['WIDGETS RARE', '7', int, '', 'PLAIN', '', ''],
        ['Software', ['EPU >1.9', 'EPU >1.8'], str, '', 'COMBO', 'Main', 'Software used for data collection.'],
        ['Type', ['Stack', 'Frames'], str, '', 'COMBO', 'Main', 'Stack type used for data collection.'],
        ['Camera', ['K2', 'Falcon3', 'Falcon2'], str, '', 'COMBO', 'Main', 'Camera used for data collection.'],
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
    programs_motion, programs_ctf, programs_picking = tu.reduce_programs()

    copy_work = sorted(mount_dict['Copy_work'])
    copy_backup = sorted(mount_dict['Copy_backup'])
    copy_hdd = sorted(mount_dict['Copy_hdd'])

    copy_work.extend(extend_list)
    copy_backup.extend(extend_list)
    copy_hdd.extend(extend_list)
    programs_motion.extend(extend_list)
    programs_ctf.extend(extend_list)
    programs_picking.extend(extend_list)

    items = [
        ['WIDGETS MAIN', '8', int, '', 'PLAIN', '', ''],
        ['WIDGETS ADVANCED', '8', int, '', 'PLAIN', '', ''],
        ['WIDGETS RARE', '8', int, '', 'PLAIN', '', '', ''],
        ['Copy to work', copy_work, bool, '', 'COMBO', 'Main', 'Copy data to the work drive.'],
        ['Copy to backup', copy_backup, bool, '', 'COMBO', 'Main', 'Copy data to the backup drive.'],
        ['Copy to HDD', copy_hdd, bool, '', 'COMBO', 'Main', 'Copy data to an external hard disc.'],
        ['Motion', programs_motion, bool, '', 'COMBO', 'Main', 'Software for motion correction.'],
        ['CTF', programs_ctf, bool, '', 'COMBO', 'Main', 'Software for CTF estimation.'],
        ['Picking', programs_picking, bool, '', 'COMBO', 'Main', 'Software for particle picking.'],
        ['Compress', ['True', 'Later', 'False'], bool, '', 'COMBO', 'Main', 'Compress the micrograph movie.'],
        ['Session to work', ['False', 'True'], bool, '', 'COMBO', 'Advanced', 'Copy the non-micrograph data (EPU session, ...) to the work drive if "Copy to work" is specified.'],
        ['Session to backup', ['False', 'True'], bool, '', 'COMBO', 'Advanced', 'Copy the non-micrograph data (EPU session, ...) to the backup drive if "Copy to backup" is specified.'],
        ['Session to HDD', ['False', 'True'], bool, '', 'COMBO', 'Advanced', 'Copy the non-micrograph data (EPU session, ...) to the HDD drive if "Copy to HDD" is specified.'],
        ['Frames to work', ['False', 'True'], bool, '', 'COMBO', 'Advanced', 'Copy the micograph movies to the work drive if "Copy to work" is specified.'],
        ['Frames to backup', ['False', 'True'], bool, '', 'COMBO', 'Advanced', 'Copy the micograph movies to the backup drive if "Copy to backup" is specified.'],
        ['Frames to HDD', ['False', 'True'], bool, '', 'COMBO', 'Advanced', 'Copy the micograph movies to the HDD drive if "Copy to HDD" is specified.'],
        ['Meta to work', ['False', 'True'], bool, '', 'COMBO', 'Advanced', 'Copy the micrograph meta data to the work drive if "Copy to work" is specified.'],
        ['Meta to backup', ['False', 'True'], bool, '', 'COMBO', 'Advanced', 'Copy the micrograph meta data to the backup drive if "Copy to backup" is specified.'],
        ['Meta to HDD', ['False', 'True'], bool, '', 'COMBO', 'Advanced', 'Copy the micrograph meta data to the HDD drive if "Copy to HDD" is specified.'],
        ['Sum to work', ['False', 'True'], bool, '', 'COMBO', 'Advanced', 'Copy the microgaph sum data to the work drive if "Copy to work" is specified.'],
        ['Sum to backup', ['False', 'True'], bool, '', 'COMBO', 'Advanced', 'Copy the microgaph sum data to the backup drive if "Copy to backup" is specified.'],
        ['Sum to HDD', ['False', 'True'], bool, '', 'COMBO', 'Advanced', 'Copy the microgaph sum data to the HDD drive if "Copy to HDD" is specified.'],
        ['CTF to work', ['False', 'True'], bool, '', 'COMBO', 'Advanced', 'Copy the microgaph ctf data to the work drive if "Copy to work" is specified.'],
        ['CTF to backup', ['False', 'True'], bool, '', 'COMBO', 'Advanced', 'Copy the microgaph ctf data to the backup drive if "Copy to backup" is specified.'],
        ['CTF to HDD', ['False', 'True'], bool, '', 'COMBO', 'Advanced', 'Copy the microgaph ctf data to the HDD drive if "Copy to HDD" is specified.'],
        ['Picking to work', ['False', 'True'], bool, '', 'COMBO', 'Advanced', 'Copy the microgaph picking data to the work drive if "Copy to work" is specified.'],
        ['Picking to backup', ['False', 'True'], bool, '', 'COMBO', 'Advanced', 'Copy the microgaph picking data to the backup drive if "Copy to backup" is specified.'],
        ['Picking to HDD', ['False', 'True'], bool, '', 'COMBO', 'Advanced', 'Copy the microgaph picking data to the HDD drive if "Copy to HDD" is specified.'],
        ['Tar to work', ['True', 'False'], bool, '', 'COMBO', 'Advanced', 'Copy the information to work drive in tar format if "Copy to work" is specified.'],
        ['Tar to backup', ['True', 'False'], bool, '', 'COMBO', 'Advanced', 'Copy the information to backup drive in tar format if "Copy to backup" is specified.'],
        ['Tar to HDD', ['True', 'False'], bool, '', 'COMBO', 'Advanced', 'Copy the information to HDD drive in tar format if "Copy to HDD" is specified.'],
        ['Delete data after import?', ['True', 'False'], bool, '', 'COMBO', 'Advanced', 'Delete the data from the camera computer after the import.'],
        ['Delete stack after compression?', ['True', 'False'], bool, '', 'COMBO', 'Advanced', 'Delete the mrc stack after compression.'],
        ]
    return items
