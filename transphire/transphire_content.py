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

from transphire import transphire_utils as tu


def default_cter_v1_0():
    """
    Content of CTER SPHIRE version 1.0.

    Arguments:
    None

    Return:
    Content items as list
    """
    items = [
        ['--wn', '512', float, '', 'PLAIN'],
        ['--apix', '-1', float, '', 'PLAIN'],
        ['--Cs', '2.0', float, '', 'PLAIN'],
        ['--voltage', '300', float, '', 'PLAIN'],
        ['--ac', '10', float, '', 'PLAIN'],
        ['--f_start', '-1', float, '', 'PLAIN'],
        ['--f_stop', '-1', float, '', 'PLAIN'],
        ['--kboot', '16', float, '', 'PLAIN'],
        ['--overlap_x', '50', float, '', 'PLAIN'],
        ['--overlap_y', '50', float, '', 'PLAIN'],
        ['--edge_x', '0', float, '', 'PLAIN'],
        ['--pap', ['False', 'True'], bool, '', 'COMBO'],
        ['Phase plate', ['False', 'True'], bool, '', 'COMBO'],
        ['--defocus_min', '0.3', float, 'Phase plate:True', 'PLAIN'],
        ['--defocus_max', '9.0', float, 'Phase plate:True', 'PLAIN'],
        ['--defocus_step', '0.1', float, 'Phase plate:True', 'PLAIN'],
        ['--phase_min', '5', float, 'Phase plate:True', 'PLAIN'],
        ['--phase_max', '175', float, 'Phase plate:True', 'PLAIN'],
        ['--phase_step', '5', float, 'Phase plate:True', 'PLAIN'],
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
        ['--apix', '1.34', float, '', 'PLAIN'],
        ['--dstep', '14.0', float, '', 'PLAIN'],
        ['--kV', '300', float, '', 'PLAIN'],
        ['--cs', '2.7', float, '', 'PLAIN'],
        ['--ac', '0.1', float, '', 'PLAIN'],
        ['Phase plate', ['False', 'True'], bool, '', 'COMBO'],
        ['--phase_shift_L', '0.0', float, 'Phase plate:True', 'PLAIN'],
        ['--phase_shift_H', '180.0', float, 'Phase plate:True', 'PLAIN'],
        ['--phase_shift_S', '5.0', float, 'Phase plate:True', 'PLAIN'],
        ['--phase_shift_T', '1', int, 'Phase plate:True', 'PLAIN'],
        ['--bfac', '150', float, '', 'PLAIN'],
        ['--defL', '5000', float, '', 'PLAIN'],
        ['--defH', '90000', float, '', 'PLAIN'],
        ['--defS', '500', float, '', 'PLAIN'],
        ['--astm', '1000', float, '', 'PLAIN'],
        ['--resL', '50', float, '', 'PLAIN'],
        ['--resH', '4', float, '', 'PLAIN'],
        ['--boxsize', '1024', int, '', 'PLAIN'],
        ['--overlap', '0.5', float, '', 'PLAIN'],
        ['--convsize', '85', float, '', 'PLAIN'],
        ['--do_EPA', '0', int, '', 'PLAIN'],
        ['--do_Hres_ref', '0', int, '', 'PLAIN'],
        ['--Href_resL', '15.0', float, '', 'PLAIN'],
        ['--Href_resH', '4.0', float, '', 'PLAIN'],
        ['--Href_bfac', '50', float, '', 'PLAIN'],
        ['--refine_after_EPA', '0', int, '', 'PLAIN'],
        ['--estimate_B', '1', int, '', 'PLAIN'],
        ['--B_resL', '15', float, '', 'PLAIN'],
        ['--B_resH', '6', float, '', 'PLAIN'],
        ['Use movies', ['False', 'True'], bool, '', 'COMBO'],
        ['--do_mdef_refine', '0', int, 'Use movies:True', 'PLAIN'],
        ['--mdef_ave_type', '0', int, 'Use movies:True', 'PLAIN'],
        ['--mdef_aveN', '7', int, 'Use movies:True', 'PLAIN'],
        ['--mdef_fit', '0', int, 'Use movies:True', 'PLAIN'],
        ['--do_local_refine', '0', int, '', 'PLAIN'],
        ['--local_radius', '1024', float, '', 'PLAIN'],
        ['--local_boxsize', '512', float, '', 'PLAIN'],
        ['--local_overlap', '0.5', float, '', 'PLAIN'],
        ['--local_avetype', '0', float, '', 'PLAIN'],
        ['--do_phase_flip', '0', int, '', 'PLAIN'],
        ['--do_validation', '0', int, '', 'PLAIN'],
        ['--ctfout_resL', '100.0', float, '', 'PLAIN'],
        ['--ctfout_resH', '2.8', float, '', 'PLAIN'],
        ['--ctfout_bfac', '50', float, '', 'PLAIN'],
        ['--gid', '0', [int]*9, '', 'PLAIN']
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
        ['--apix', '1.34', float, '', 'PLAIN'],
        ['--dstep', '14.0', float, '', 'PLAIN'],
        ['--kV', '300', float, '', 'PLAIN'],
        ['--cs', '2.7', float, '', 'PLAIN'],
        ['--ac', '0.1', float, '', 'PLAIN'],
        ['Phase plate', ['False', 'True'], bool, '', 'COMBO'],
        ['--phase_shift_L', '0.0', float, 'Phase plate:True', 'PLAIN'],
        ['--phase_shift_H', '180.0', float, 'Phase plate:True', 'PLAIN'],
        ['--phase_shift_S', '0.0', float, 'Phase plate:True', 'PLAIN'],
        ['--phase_shift_T', '1', int, 'Phase plate:True', 'PLAIN'],
        ['--only_search_ps', '0', int, 'Phase plate:True', 'PLAIN'],
        ['--cosearch_refine_ps', '0', int, 'Phase plate:True', 'PLAIN'],
        ['--bfac', '150', float, '', 'PLAIN'],
        ['--defL', '5000', float, '', 'PLAIN'],
        ['--defH', '90000', float, '', 'PLAIN'],
        ['--defS', '500', float, '', 'PLAIN'],
        ['--astm', '1000', float, '', 'PLAIN'],
        ['--resL', '50', float, '', 'PLAIN'],
        ['--resH', '4', float, '', 'PLAIN'],
        ['--boxsize', '1024', int, '', 'PLAIN'],
        ['--overlap', '0.5', float, '', 'PLAIN'],
        ['--convsize', '85', float, '', 'PLAIN'],
        ['--refine_2d_T', '1', int, '', 'PLAIN'],
        ['--smooth_resL', '0', float, '', 'PLAIN'],
        ['--do_basic_rotave', '0', int, '', 'PLAIN'],
        ['--do_EPA', '0', int, '', 'PLAIN'],
        ['--refine_after_EPA', '0', int, '', 'PLAIN'],
        ['--do_Hres_ref', '0', int, '', 'PLAIN'],
        ['--Href_resL', '15.0', float, '', 'PLAIN'],
        ['--Href_resH', '4.0', float, '', 'PLAIN'],
        ['--Href_bfac', '50', float, '', 'PLAIN'],
        ['--Href_PS_err', '2', float, '', 'PLAIN'],
        ['--Href_U_err', '100', float, '', 'PLAIN'],
        ['--Href_V_err', '100', float, '', 'PLAIN'],
        ['--Href_A_err', '5', float, '', 'PLAIN'],
        ['--estimate_B', '1', int, '', 'PLAIN'],
        ['--B_resL', '15', float, '', 'PLAIN'],
        ['--B_resH', '6', float, '', 'PLAIN'],
        ['Use movies', ['False', 'True'], bool, '', 'COMBO'],
        ['--do_mdef_refine', '0', int, 'Use movies:True', 'PLAIN'],
        ['--mdef_ave_type', '0', int, 'Use movies:True', 'PLAIN'],
        ['--mdef_aveN', '7', int, 'Use movies:True', 'PLAIN'],
        ['--mdef_fit', '0', int, 'Use movies:True', 'PLAIN'],
        ['--do_local_refine', '0', int, '', 'PLAIN'],
        ['--local_radius', '1024', float, '', 'PLAIN'],
        ['--local_boxsize', '512', float, '', 'PLAIN'],
        ['--local_overlap', '0.5', float, '', 'PLAIN'],
        ['--local_avetype', '0', float, '', 'PLAIN'],
        ['--do_phase_flip', '0', int, '', 'PLAIN'],
        ['--do_validation', '0', int, '', 'PLAIN'],
        ['--ctfout_resL', '100.0', float, '', 'PLAIN'],
        ['--ctfout_resH', '2.78', float, '', 'PLAIN'],
        ['--ctfout_bfac', '50', float, '', 'PLAIN'],
        ['--gid', '0', [int]*9, '', 'PLAIN']
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
    items = [['IMOD header', '', str, '', 'FILE/CHOICE']]
    items.append(['IMOD newstack', '', str, '', 'FILE/CHOICE'])
    items.append(['IMOD mrc2tif', '', str, '', 'FILE/CHOICE'])
    items.append(['IMOD dm2mrc', '', str, '', 'FILE/CHOICE'])
    items.append(['SumMovie v1.0.2', '', str, '', 'FILE/CHOICE'])
    function_dict = tu.get_function_dict()
    for key in sorted(function_dict.keys()):
        if function_dict[key]['executable']:
            items.append([key, '', str, '', 'FILE/CHOICE'])
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
        ['Font', '15', float, '', 'PLAIN'],
        ['Width adjustment', '1', float, '', 'PLAIN'],
        ['Height adjustment', '1', float, '', 'PLAIN'],
        ['Start button', '10', float, '', 'PLAIN'],
        ['Notification edit', '16', float, '', 'PLAIN'],
        ['Notification check', '8', float, '', 'PLAIN'],
        ['Notification button', '25', float, '', 'PLAIN'],
        ['Mount button', '16', float, '', 'PLAIN'],
        ['Frame entry', '5', float, '', 'PLAIN'],
        ['Frame button', '8', float, '', 'PLAIN'],
        ['Frame label', '8', float, '', 'PLAIN'],
        ['Setting widget', '22', float, '', 'PLAIN'],
        ['Status name', '12', float, '', 'PLAIN'],
        ['Status info', '12', float, '', 'PLAIN'],
        ['Status quota', '12', float, '', 'PLAIN'],
        ['Widget height', '1.5', float, '', 'PLAIN']
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
    items = [
        ['Image', '', str, '', 'FILE'],
        ['Mount/umount needs sudo password?', ['True', 'False'], bool, '', 'COMBO'],
        ['Project name pattern', '', str, '', 'PLAIN'],
        ['Project name pattern example', '', str, '', 'PLAIN'],
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
        ['Bot token', '', str, '', 'PLAIN'],
        [
            'Default names telegram',
            'name1:telegram_name1;name2:telegram_name2',
            str,
            '',
            'PLAIN'
            ],
        ['SMTP server', '', str, '', 'PLAIN'],
        ['E-Mail adress', '', str, '', 'PLAIN'],
        [
            'Default names email',
            'name1:telegram_name1;name2:telegram_name2',
            str,
            '',
            'PLAIN'
            ],
        ['Number of users', '3', int, '', 'PLAIN']
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
            'PLAIN'
            ],
        ['Find', '1', int, 'Find;Copy', 'PLAIN'],
        [
            'Copy',
            '1',
            int,
            'Find;' +
            'Motion:Motion,' +
            'Meta to work:Copy to work:Copy_work,' +
            'Meta to backup:Copy to backup:Copy_backup,' +
            'Meta to HDD:Copy to HDD:Copy_hdd,' +
            '!Motion:CTF_frames:CTF,' +
            '!Motion:!CTF_frames:Compress data:Compress,' +
            '!Motion:!CTF_frames:!Compress data:Frames to work:Copy to work:Copy_work,' +
            '!Motion:!CTF_frames:!Compress data:Frames to HDD:Copy to HDD:Copy_hdd,' +
            '!Motion:!CTF_frames:!Compress data:Frames to backup:Copy to backup:Copy_backup',
            'PLAIN'
            ],
        [
            'Motion',
            '2',
            int,
            'Motion;' +
            'Sum to work:Copy to work:Copy_work,' +
            'Sum to HDD:Copy to HDD:Copy_hdd,' +
            'Sum to backup:Copy to backup:Copy_backup,' +
            'CTF_frames:CTF,' +
            'CTF_sum:CTF,' +
            '!CTF_frames:Compress data:Compress,' +
            '!CTF_frames:!Compress data:Frames to work:Copy to work:Copy_work,' +
            '!CTF_frames:!Compress data:Frames to HDD:Copy to HDD:Copy_hdd,' +
            '!CTF_frames:!Compress data:Frames to backup:Copy to backup:Copy_backup',
            'PLAIN'
            ],
        [
            'CTF',
            '2',
            int,
            'CTF;' +
            'CTF to work:Copy to work:Copy_work,' +
            'CTF to HDD:Copy to HDD:Copy_hdd,' +
            'CTF to backup:Copy to backup:Copy_backup,' +
            'CTF_frames:Compress data:Compress,' +
            'CTF_frames:!Compress data:Frames to work:Copy to work:Copy_work,' +
            'CTF_frames:!Compress data:Frames to HDD:Copy to HDD:Copy_hdd,' +
            'CTF_frames:!Compress data:Frames to backup:Copy to backup:Copy_backup',
            'PLAIN'
            ],
        [
            'Compress',
            '2',
            int,
            'Compress;'
            'Frames to backup:Copy to backup:Copy_backup,'
            'Frames to HDD:Copy to HDD:Copy_hdd,'
            'Frames to work:Copy to work:Copy_work',
            'PLAIN'
            ],
        ['Copy_work', '1', int, 'Copy_work;', 'PLAIN'],
        ['Copy_hdd', '1', int, 'Copy_hdd;', 'PLAIN'],
        ['Copy_backup', '1', int, 'Copy_backup;', 'PLAIN'],
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
        ['Pixel size', '1.0', float, '', 'PLAIN'],
        ['Acceleration voltage', '300.0', float, '', 'PLAIN'],
        ['Spherical aberration', '2.7', float, '', 'PLAIN'],
        ['Amplitude contrast', '0.07', float, '', 'PLAIN'],
        ['Amplitude spectrum', '512', float, '', 'PLAIN'],
        ['Min resolution(A)', '30', float, '', 'PLAIN'],
        ['Max resolution(A)', '5', float, '', 'PLAIN'],
        ['Min defocus(A)', '5000', float, '', 'PLAIN'],
        ['Max defocus(A)', '50000', float, '', 'PLAIN'],
        ['Step defocus(A)', '500', float, '', 'PLAIN'],
        ['High accuracy', ['True', 'False'], bool, '', 'COMBO'],
        ['Know astigmatism', ['True', 'False'], bool, '', 'COMBO'],
        ['Restrain astigmatism', ['True', 'False'], bool, 'Know astigmatism:False', 'COMBO'],
        ['Expected astigmatism', '200', float, 'Restrain astigmatism:True', 'PLAIN'],
        ['Astigmatism', '0', float, 'Know astigmatism:True', 'PLAIN'],
        ['Astigmatism angle', '0', float, 'Know astigmatism:True', 'PLAIN'],
        ['Phase shift', ['False', 'True'], bool, '', 'COMBO'],
        ['Min phase(rad)', '0', float, 'Phase shift:True', 'PLAIN'],
        ['Max phase(rad)', '3.15', float, 'Phase shift:True', 'PLAIN'],
        ['Step phase(rad)', '0.5', float, 'Phase shift:True', 'PLAIN'],
        ['Resample micrographs', ['True', 'False'], bool, '', 'COMBO'],
        ['Use movies', ['False', 'True'], bool, '', 'COMBO'],
        ['Combine frames', '1', int, 'Use movies:True', 'PLAIN'],
        ['Movie is gain-corrected?', ['True', 'False'], bool, 'Use movies:True', 'COMBO'],
        ['Gain file', '', str, 'Movie is gain-corrected?:False', 'FILE'],
        ['Correct mag. distort.', ['False', 'True'], bool, 'Use movies:True', 'COMBO'],
        ['Mag. dist. angle', '0.0', float, 'Correct mag. distort.:True', 'PLAIN'],
        ['Mag. dist. major scale', '1.0', float, 'Correct mag. distort.:True', 'PLAIN'],
        ['Mag. dist. minor scale', '1.0', float, 'Correct mag. distort.:True', 'PLAIN'],
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
        ['Mount name', name, str, '', 'PLAIN'],
        ['Protocol', ['smbfs', 'cifs', 'nfs'], str, '', 'COMBO'],
        ['Protocol version', '2.0', float, '', 'PLAIN'],
        ['sec', ['ntlmssp', 'krb5', 'krb5i', 'ntlm', 'ntlmi', 'ntlmv2', 'ntlmv2i', 'ntlmsspi', 'none'], str, '', 'COMBO'],
        ['gid', '', str, '', 'PLAIN'],
        ['Domain', '', str, '', 'PLAIN'],
        ['IP', '', str, '', 'PLAIN'],
        ['Folder', '', str, '', 'PLAIN'],
        ['Need folder extension?', ['False', 'True'], bool, '', 'COMBO'],
        ['Default user', '', str, '', 'PLAIN'],
        ['Is df giving the right quota?', ['True', 'False'], bool, '', 'COMBO'],
        ['Target UID exists here and on target?', ['True', 'False'], bool, '', 'COMBO'],
        ['Need sudo for copy?', ['False', 'True'], bool, '', 'COMBO'],
        ['SSH address', '', str, '', 'PLAIN'],
        ['Quota command', '', str, '', 'PLAIN'],
        ['Quota / TB', '', float, '', 'PLAIN'],
        ['Typ', ['Copy', 'Copy_work', 'Copy_backup'], str, '', 'COMBO'],
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
        ['-FmDose', '0', float, '', 'PLAIN'],
        ['-PixSize', '0', float, '', 'PLAIN'],
        ['-kV', '300', float, '', 'PLAIN'],
        ['-MaskCent', '0 0', [float, float], '', 'PLAIN'],
        ['-MaskSize', '1 1', [float, float], '', 'PLAIN'],
        ['-Patch', '0 0', [int, int], '', 'PLAIN'],
        ['-Iter', '7', int, '', 'PLAIN'],
        ['-Tol', '0.5', float, '', 'PLAIN'],
        ['-Bft', '100', float, '', 'PLAIN'],
        ['-PhaseOnly', '0', int, '', 'PLAIN'],
        ['-StackZ', '0', int, '', 'PLAIN'],
        ['-FtBin', '1', float, '', 'PLAIN'],
        ['-InitDose', '0', float, '', 'PLAIN'],
        ['-Throw', '0', int, '', 'PLAIN'],
        ['-Trunc', '0', int, '', 'PLAIN'],
        ['-Group', '1', int, '', 'PLAIN'],
        ['-FmRef', '-1', int, '', 'PLAIN'],
        ['-DefectFile', '', str, '', 'FILE'],
        ['-Gain', '', str, '', 'FILE'],
        ['-RotGain', '0', int, '', 'PLAIN'],
        ['-FlipGain', '0', int, '', 'PLAIN'],
        ['-Tilt', '0 0', [float, float], '', 'PLAIN'],
        ['-Mag', '1 1 0', [float, float, float], '', 'PLAIN'],
        ['-InFmMotion', '0', int, '', 'PLAIN'],
        ['-Crop', '0 0', [int, int], '', 'PLAIN'],
        ['-Gpu', '0', [int]*9, '', 'PLAIN'],
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
        ['-FmDose', '0', float, '', 'PLAIN'],
        ['-PixSize', '0', float, '', 'PLAIN'],
        ['-kV', '300', float, '', 'PLAIN'],
        ['-MaskCent', '0 0', [float, float], '', 'PLAIN'],
        ['-MaskSize', '1 1', [float, float], '', 'PLAIN'],
        ['-Patch', '0 0 0', [int, int, int], '', 'PLAIN'],
        ['-Iter', '7', int, '', 'PLAIN'],
        ['-Tol', '0.5', float, '', 'PLAIN'],
        ['-Bft', '100', float, '', 'PLAIN'],
        ['-PhaseOnly', '0', int, '', 'PLAIN'],
        ['-StackZ', '0', int, '', 'PLAIN'],
        ['-FtBin', '1', float, '', 'PLAIN'],
        ['-InitDose', '0', float, '', 'PLAIN'],
        ['-Throw', '0', int, '', 'PLAIN'],
        ['-Trunc', '0', int, '', 'PLAIN'],
        ['-Group', '1', int, '', 'PLAIN'],
        ['-FmRef', '-1', int, '', 'PLAIN'],
        ['-DefectFile', '', str, '', 'FILE'],
        ['-Dark', '', str, '', 'FILE'],
        ['-Gain', '', str, '', 'FILE'],
        ['-RotGain', '0', int, '', 'PLAIN'],
        ['-FlipGain', '0', int, '', 'PLAIN'],
        ['-Tilt', '0 0', [float, float], '', 'PLAIN'],
        ['-Mag', '1 1 0', [float, float, float], '', 'PLAIN'],
        ['-InFmMotion', '0', int, '', 'PLAIN'],
        ['-Crop', '0 0', [int, int], '', 'PLAIN'],
        ['-Gpu', '0', [int]*9, '', 'PLAIN'],
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
        ['-FmDose', '0', float, '', 'PLAIN'],
        ['-PixSize', '0', float, '', 'PLAIN'],
        ['-kV', '300', float, '', 'PLAIN'],
        ['-MaskCent', '0 0', [float, float], '', 'PLAIN'],
        ['-MaskSize', '1 1', [float, float], '', 'PLAIN'],
        ['-Patch', '0 0 0', [int, int, int], '', 'PLAIN'],
        ['-Iter', '7', int, '', 'PLAIN'],
        ['-Tol', '0.5', float, '', 'PLAIN'],
        ['-Bft', '500 150', [float, float], '', 'PLAIN'],
        ['-PhaseOnly', '0', int, '', 'PLAIN'],
        ['-StackZ', '0', int, '', 'PLAIN'],
        ['-FtBin', '1', float, '', 'PLAIN'],
        ['-InitDose', '0', float, '', 'PLAIN'],
        ['-Throw', '0', int, '', 'PLAIN'],
        ['-Trunc', '0', int, '', 'PLAIN'],
        ['-Group', '1', int, '', 'PLAIN'],
        ['-FmRef', '-1', int, '', 'PLAIN'],
        ['-DefectFile', '', str, '', 'FILE'],
        ['-Dark', '', str, '', 'FILE'],
        ['-Gain', '', str, '', 'FILE'],
        ['-RotGain', '0', int, '', 'PLAIN'],
        ['-FlipGain', '0', int, '', 'PLAIN'],
        ['-Tilt', '0 0', [float, float], '', 'PLAIN'],
        ['-Mag', '1 1 0', [float, float, float], '', 'PLAIN'],
        ['-InFmMotion', '0', int, '', 'PLAIN'],
        ['-Crop', '0 0', [int, int], '', 'PLAIN'],
        ['-Gpu', '0', [int]*9, '', 'PLAIN'],
        ['-GpuMemUsage', '0.5', float, '', 'PLAIN'],
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
        ['Software', ['EPU 1.9', 'EPU 1.8'], str, '', 'COMBO'],
        ['Type', ['Stack', 'Frames'], str, '', 'COMBO'],
        ['Camera', ['K2', 'Falcon3', 'Falcon2'], str, '', 'COMBO'],
        ['Search path frames', '', str, '', 'DIR'],
        ['Search path meta', '', str, '', 'DIR'],
        ['Input extension', ['mrc', 'dm4', 'tif', 'tiff'], str, '', 'COMBO'],
        ['Output extension', ['mrc', 'tif', 'tiff'], str, '', 'COMBO'],
        ['Project name', '', str, '', 'PLAIN'],
        ['Number of frames', '0', int, '', 'PLAIN'],
        ['Rename micrographs', ['True', 'False'], bool, '', 'COMBO'],
        ['Rename prefix', '', str, 'Rename micrographs:True', 'PLAIN'],
        ['Rename suffix', '', str, 'Rename micrographs:True', 'PLAIN'],
        ['Start number', '0', int, 'Rename micrographs:True', 'PLAIN'],
        ['Estimated mic number', '5000', int, 'Rename micrographs:True', 'PLAIN'],
        ['Project directory', '', str, '', 'DIR'],
        ['Project quota warning (%)', '80', float, '', 'PLAIN'],
        ['Project quota stop (%)', '90', float, '', 'PLAIN'],
        ['Scratch directory', '', str, '', 'DIR'],
        ['Scratch quota warning (%)', '80', float, '', 'PLAIN'],
        ['Scratch quota stop (%)', '90', float, '', 'PLAIN'],
        ['Time until notification', '25', float, '', 'PLAIN'],
        ['Phase shift warning (deg)', '110', float, '', 'PLAIN'],
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
    programs_motion, programs_ctf = tu.reduce_programs()

    copy_work = sorted(mount_dict['Copy_work'])
    copy_backup = sorted(mount_dict['Copy_backup'])
    copy_hdd = sorted(mount_dict['Copy_hdd'])

    copy_work.extend(extend_list)
    copy_backup.extend(extend_list)
    copy_hdd.extend(extend_list)
    programs_motion.extend(extend_list)
    programs_ctf.extend(extend_list)

    items = [
        ['Session to work', ['False', 'True'], bool, '', 'COMBO'],
        ['Session to HDD', ['False', 'True'], bool, '', 'COMBO'],
        ['Session to backup', ['False', 'True'], bool, '', 'COMBO'],
        ['Frames to work', ['False', 'True'], bool, '', 'COMBO'],
        ['Frames to HDD', ['False', 'True'], bool, '', 'COMBO'],
        ['Frames to backup', ['False', 'True'], bool, '', 'COMBO'],
        ['Meta to work', ['False', 'True'], bool, '', 'COMBO'],
        ['Meta to HDD', ['False', 'True'], bool, '', 'COMBO'],
        ['Meta to backup', ['False', 'True'], bool, '', 'COMBO'],
        ['Sum to work', ['False', 'True'], bool, '', 'COMBO'],
        ['Sum to HDD', ['False', 'True'], bool, '', 'COMBO'],
        ['Sum to backup', ['False', 'True'], bool, '', 'COMBO'],
        ['CTF to work', ['False', 'True'], bool, '', 'COMBO'],
        ['CTF to HDD', ['False', 'True'], bool, '', 'COMBO'],
        ['CTF to backup', ['False', 'True'], bool, '', 'COMBO'],
        ['Copy to work', copy_work, bool, '', 'COMBO'],
        ['Copy to backup', copy_backup, bool, '', 'COMBO'],
        ['Copy to HDD', copy_hdd, bool, '', 'COMBO'],
        ['Motion', programs_motion, bool, '', 'COMBO'],
        ['CTF', programs_ctf, bool, '', 'COMBO'],
        ['Compress data', ['True', 'Later', 'False'], bool, '', 'COMBO'],
        ['Delete stack after compression?', ['True', 'False'], bool, '', 'COMBO'],
        ]
    return items
