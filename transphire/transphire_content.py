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
        ['WIDGETS MAIN', '5', int, '', 'PLAIN', ''],
        ['WIDGETS ADVANCED', '5', int, '', 'PLAIN', ''],
        ['--conf', '', str, '', 'FILE', 'Main'],
        ['--weights', '', str, '', 'FILE', 'Main'],
        ['--threshold', '0.3', float, '', 'PLAIN', 'Main'],
        ['Pixel size (A/px)', '1', float, 'Filter micrographs:True', 'PLAIN', 'Main'],
        ['Box size', '200', int, '', 'PLAIN', 'Main'],
        ['Filter micrographs', ['True', 'False'], bool, '', 'COMBO', 'Advanced'],
        ['Filter value high pass (A)', '9999', float, 'Filter micrographs:True', 'PLAIN', 'Advanced'],
        ['Filter value low pass (A)', '10', float, 'Filter micrographs:True', 'PLAIN', 'Advanced'],
        ['--patch', '-1', int, '', 'PLAIN', 'Advanced'],
        ['--gpu', '0', [int]*99, '', 'PLAIN', 'Advanced'],
        ['Split Gpu?', ['True', 'False'], bool, '', 'COMBO', 'Advanced'],
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
        ['WIDGETS MAIN', '7', int, '', 'PLAIN', ''],
        ['WIDGETS ADVANCED', '7', int, '', 'PLAIN', ''],
        ['--apix', '-1', float, '', 'PLAIN', 'Main'],
        ['--Cs', '2.0', float, '', 'PLAIN', 'Main'],
        ['--voltage', '300', float, '', 'PLAIN', 'Main'],
        ['--ac', '10', float, '', 'PLAIN', 'Main'],
        ['--f_start', '-1', float, '', 'PLAIN', 'Main'],
        ['--f_stop', '-1', float, '', 'PLAIN', 'Main'],
        ['Phase plate', ['False', 'True'], bool, '', 'COMBO', 'Main'],
        ['--defocus_min', '0.3', float, 'Phase plate:True', 'PLAIN', 'Main'],
        ['--defocus_max', '9.0', float, 'Phase plate:True', 'PLAIN', 'Main'],
        ['--defocus_step', '0.1', float, 'Phase plate:True', 'PLAIN', 'Main'],
        ['--phase_min', '5', float, 'Phase plate:True', 'PLAIN', 'Main'],
        ['--phase_max', '175', float, 'Phase plate:True', 'PLAIN', 'Main'],
        ['--phase_step', '5', float, 'Phase plate:True', 'PLAIN', 'Main'],
        ['--wn', '512', float, '', 'PLAIN', 'Advanced'],
        ['--kboot', '16', float, '', 'PLAIN', 'Advanced'],
        ['--overlap_x', '50', float, '', 'PLAIN', 'Advanced'],
        ['--overlap_y', '50', float, '', 'PLAIN', 'Advanced'],
        ['--edge_x', '0', float, '', 'PLAIN', 'Advanced'],
        ['--pap', ['False', 'True'], bool, '', 'COMBO', 'Advanced'],
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
        ['WIDGETS MAIN', '7', int, '', 'PLAIN', ''],
        ['WIDGETS ADVANCED', '7', int, '', 'PLAIN', ''],
        ['--apix', '1.34', float, '', 'PLAIN', 'Main'],
        ['--dstep', '14.0', float, '', 'PLAIN', 'Main'],
        ['--kV', '300', float, '', 'PLAIN', 'Main'],
        ['--cs', '2.7', float, '', 'PLAIN', 'Main'],
        ['--ac', '0.1', float, '', 'PLAIN', 'Main'],
        ['Phase plate', ['False', 'True'], bool, '', 'COMBO', 'Main'],
        ['--phase_shift_L', '0.0', float, 'Phase plate:True', 'PLAIN', 'Main'],
        ['--phase_shift_H', '180.0', float, 'Phase plate:True', 'PLAIN', 'Main'],
        ['--phase_shift_S', '5.0', float, 'Phase plate:True', 'PLAIN', 'Main'],
        ['--phase_shift_T', '1', int, 'Phase plate:True', 'PLAIN', 'Main'],
        ['--defL', '5000', float, '', 'PLAIN', 'Main'],
        ['--defH', '90000', float, '', 'PLAIN', 'Main'],
        ['--defS', '500', float, '', 'PLAIN', 'Main'],
        ['--astm', '1000', float, '', 'PLAIN', 'Main'],
        ['--bfac', '150', float, '', 'PLAIN', 'Advanced'],
        ['--resL', '50', float, '', 'PLAIN', 'Advanced'],
        ['--resH', '4', float, '', 'PLAIN', 'Advanced'],
        ['--boxsize', '1024', int, '', 'PLAIN', 'Advanced'],
        ['--overlap', '0.5', float, '', 'PLAIN', 'Advanced'],
        ['--convsize', '85', float, '', 'PLAIN', 'Advanced'],
        ['--do_EPA', '0', int, '', 'PLAIN', 'Advanced'],
        ['--do_Hres_ref', '0', int, '', 'PLAIN', 'Advanced'],
        ['--Href_resL', '15.0', float, '', 'PLAIN', 'Advanced'],
        ['--Href_resH', '4.0', float, '', 'PLAIN', 'Advanced'],
        ['--Href_bfac', '50', float, '', 'PLAIN', 'Advanced'],
        ['--refine_after_EPA', '0', int, '', 'PLAIN', 'Advanced'],
        ['--estimate_B', '1', int, '', 'PLAIN', 'Advanced'],
        ['--B_resL', '15', float, '', 'PLAIN', 'Advanced'],
        ['--B_resH', '6', float, '', 'PLAIN', 'Advanced'],
        ['Use movies', ['False', 'True'], bool, '', 'COMBO', 'Advanced'],
        ['--do_mdef_refine', '0', int, 'Use movies:True', 'PLAIN', 'Advanced'],
        ['--mdef_ave_type', '0', int, 'Use movies:True', 'PLAIN', 'Advanced'],
        ['--mdef_aveN', '7', int, 'Use movies:True', 'PLAIN', 'Advanced'],
        ['--mdef_fit', '0', int, 'Use movies:True', 'PLAIN', 'Advanced'],
        ['--do_local_refine', '0', int, '', 'PLAIN', 'Advanced'],
        ['--local_radius', '1024', float, '', 'PLAIN', 'Advanced'],
        ['--local_boxsize', '512', float, '', 'PLAIN', 'Advanced'],
        ['--local_overlap', '0.5', float, '', 'PLAIN', 'Advanced'],
        ['--local_avetype', '0', float, '', 'PLAIN', 'Advanced'],
        ['--do_phase_flip', '0', int, '', 'PLAIN', 'Advanced'],
        ['--do_validation', '0', int, '', 'PLAIN', 'Advanced'],
        ['--ctfout_resL', '100.0', float, '', 'PLAIN', 'Advanced'],
        ['--ctfout_resH', '2.8', float, '', 'PLAIN', 'Advanced'],
        ['--ctfout_bfac', '50', float, '', 'PLAIN', 'Advanced'],
        ['--gid', '0', [int]*99, '', 'PLAIN', 'Advanced'],
        ['Split Gpu?', ['True', 'False'], bool, '', 'COMBO', 'Advanced'],
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
        ['WIDGETS MAIN', '7', int, '', 'PLAIN', 'Main'],
        ['WIDGETS ADVANCED', '7', int, '', 'PLAIN', 'Main'],
        ['--apix', '1.34', float, '', 'PLAIN', 'Main'],
        ['--dstep', '14.0', float, '', 'PLAIN', 'Main'],
        ['--kV', '300', float, '', 'PLAIN', 'Main'],
        ['--cs', '2.7', float, '', 'PLAIN', 'Main'],
        ['--ac', '0.1', float, '', 'PLAIN', 'Main'],
        ['Phase plate', ['False', 'True'], bool, '', 'COMBO', 'Main'],
        ['--phase_shift_L', '0.0', float, 'Phase plate:True', 'PLAIN', 'Main'],
        ['--phase_shift_H', '180.0', float, 'Phase plate:True', 'PLAIN', 'Main'],
        ['--phase_shift_S', '0.0', float, 'Phase plate:True', 'PLAIN', 'Main'],
        ['--phase_shift_T', '1', int, 'Phase plate:True', 'PLAIN', 'Main'],
        ['--defL', '5000', float, '', 'PLAIN', 'Main'],
        ['--defH', '90000', float, '', 'PLAIN', 'Main'],
        ['--defS', '500', float, '', 'PLAIN', 'Main'],
        ['--bfac', '150', float, '', 'PLAIN', 'Main'],
        ['--astm', '1000', float, '', 'PLAIN', 'Advanced'],
        ['--only_search_ps', '0', int, 'Phase plate:True', 'PLAIN', 'Advanced'],
        ['--cosearch_refine_ps', '0', int, 'Phase plate:True', 'PLAIN', 'Advanced'],
        ['--resL', '50', float, '', 'PLAIN', 'Advanced'],
        ['--resH', '4', float, '', 'PLAIN', 'Advanced'],
        ['--boxsize', '1024', int, '', 'PLAIN', 'Advanced'],
        ['--overlap', '0.5', float, '', 'PLAIN', 'Advanced'],
        ['--convsize', '85', float, '', 'PLAIN', 'Advanced'],
        ['--refine_2d_T', '1', int, '', 'PLAIN', 'Advanced'],
        ['--smooth_resL', '0', float, '', 'PLAIN', 'Advanced'],
        ['--do_basic_rotave', '0', int, '', 'PLAIN', 'Advanced'],
        ['--do_EPA', '0', int, '', 'PLAIN', 'Advanced'],
        ['--refine_after_EPA', '0', int, '', 'PLAIN', 'Advanced'],
        ['--do_Hres_ref', '0', int, '', 'PLAIN', 'Advanced'],
        ['--Href_resL', '15.0', float, '', 'PLAIN', 'Advanced'],
        ['--Href_resH', '4.0', float, '', 'PLAIN', 'Advanced'],
        ['--Href_bfac', '50', float, '', 'PLAIN', 'Advanced'],
        ['--Href_PS_err', '2', float, '', 'PLAIN', 'Advanced'],
        ['--Href_U_err', '100', float, '', 'PLAIN', 'Advanced'],
        ['--Href_V_err', '100', float, '', 'PLAIN', 'Advanced'],
        ['--Href_A_err', '5', float, '', 'PLAIN', 'Advanced'],
        ['--estimate_B', '1', int, '', 'PLAIN', 'Advanced'],
        ['--B_resL', '15', float, '', 'PLAIN', 'Advanced'],
        ['--B_resH', '6', float, '', 'PLAIN', 'Advanced'],
        ['Use movies', ['False', 'True'], bool, '', 'COMBO', 'Advanced'],
        ['--do_mdef_refine', '0', int, 'Use movies:True', 'PLAIN', 'Advanced'],
        ['--mdef_ave_type', '0', int, 'Use movies:True', 'PLAIN', 'Advanced'],
        ['--mdef_aveN', '7', int, 'Use movies:True', 'PLAIN', 'Advanced'],
        ['--mdef_fit', '0', int, 'Use movies:True', 'PLAIN', 'Advanced'],
        ['--do_local_refine', '0', int, '', 'PLAIN', 'Advanced'],
        ['--local_radius', '1024', float, '', 'PLAIN', 'Advanced'],
        ['--local_boxsize', '512', float, '', 'PLAIN', 'Advanced'],
        ['--local_overlap', '0.5', float, '', 'PLAIN', 'Advanced'],
        ['--local_avetype', '0', float, '', 'PLAIN', 'Advanced'],
        ['--do_phase_flip', '0', int, '', 'PLAIN', 'Advanced'],
        ['--do_validation', '0', int, '', 'PLAIN', 'Advanced'],
        ['--ctfout_resL', '100.0', float, '', 'PLAIN', 'Advanced'],
        ['--ctfout_resH', '2.78', float, '', 'PLAIN', 'Advanced'],
        ['--ctfout_bfac', '50', float, '', 'PLAIN', 'Advanced'],
        ['--gid', '0', [int]*99, '', 'PLAIN', 'Advanced'],
        ['Split Gpu?', ['True', 'False'], bool, '', 'COMBO', 'Advanced'],
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
        ['WIDGETS MAIN', '8', int, '', 'PLAIN', 'Main'],
        ['WIDGETS ADVANCED', '8', int, '', 'PLAIN', 'Main'],
        ['IMOD header', '', str, '', 'FILE', 'Main'],
        ['IMOD newstack', '', str, '', 'FILE', 'Main'],
        ['IMOD mrc2tif', '', str, '', 'FILE', 'Main'],
        ['IMOD dm2mrc', '', str, '', 'FILE', 'Main'],
        ['e2proc2d.py', '', str, '', 'FILE', 'Main'],
        ['SumMovie v1.0.2', '', str, '', 'FILE', 'Main'],
        ]
    function_dict = tu.get_function_dict()
    for key in sorted(function_dict.keys()):
        if function_dict[key]['executable']:
            items.append([key, '', str, '', 'FILE', 'Main'])
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
        ['Font', '8', float, '', 'PLAIN', ''],
        ['Width adjustment', '1', float, '', 'PLAIN', ''],
        ['Height adjustment', '1', float, '', 'PLAIN', ''],
        ['Start button', '14', float, '', 'PLAIN', ''],
        ['Notification edit', '16', float, '', 'PLAIN', ''],
        ['Notification check', '10', float, '', 'PLAIN', ''],
        ['Notification button', '26', float, '', 'PLAIN', ''],
        ['Mount button', '18', float, '', 'PLAIN', ''],
        ['Frame entry', '5', float, '', 'PLAIN', ''],
        ['Frame button', '8', float, '', 'PLAIN', ''],
        ['Frame label', '8', float, '', 'PLAIN', ''],
        ['Setting widget', '22', float, '', 'PLAIN', ''],
        ['Setting widget large', '44', float, '', 'PLAIN', ''],
        ['Status name', '12', float, '', 'PLAIN', ''],
        ['Status info', '12', float, '', 'PLAIN', ''],
        ['Status quota', '12', float, '', 'PLAIN', ''],
        ['Widget height', '1.5', float, '', 'PLAIN', ''],
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
        ['Image', file_name, str, '', 'FILE', ''],
        ['Project name pattern', '', str, '', 'PLAIN', ''],
        ['Project name pattern example', '', str, '', 'PLAIN', ''],
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
        ['WIDGETS MAIN', '10', int, '', 'PLAIN', ''],
        ['WIDGETS ADVANCED', '10', int, '', 'PLAIN', ''],
        ['Project quota warning (%)', '80', float, '', 'PLAIN', 'Main'],
        ['Project quota stop (%)', '90', float, '', 'PLAIN', 'Main'],
        ['Scratch quota warning (%)', '80', float, '', 'PLAIN', 'Main'],
        ['Scratch quota stop (%)', '90', float, '', 'PLAIN', 'Main'],
        ['Time until notification', '25', float, '', 'PLAIN', 'Main'],
        ['Nr. of values used for median', '5', int, '', 'PLAIN', 'Main'],
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
                    ['{0} warning'.format(key), '-1000000 1000000', [float, float], '', 'PLAIN', 'Main'],
                    )
                items.append(
                    ['{0} skip'.format(key), '-1000000 1000000', [float, float], '', 'PLAIN', 'Main'],
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
        ['Bot token', '', str, '', 'PLAIN', ''],
        [
            'Default names telegram',
            'name1:telegram_name1;name2:telegram_name2',
            str,
            '',
            'PLAIN',
            '',
            ],
        ['SMTP server', '', str, '', 'PLAIN', ''],
        ['E-Mail adress', '', str, '', 'PLAIN'],
        [
            'Default names email',
            'name1:telegram_name1;name2:telegram_name2',
            str,
            '',
            'PLAIN',
            '',
            ],
        ['Number of users', '3', int, '', 'PLAIN', ''],
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
            ''
            ],
        ['Find', '1', int, 'Find;Copy', 'PLAIN', ''],
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
            'PLAIN',
            '',
            ],
        [
            'Motion',
            '2',
            int,
            'Motion;' +
            'Sum to work:Copy to work:Copy_work,' +
            'Sum to HDD:Copy to HDD:Copy_hdd,' +
            'Sum to backup:Copy to backup:Copy_backup,' +
            'CTF_sum:CTF,' +
            'CTF_frames:CTF,' +
            '!CTF_frames:!CTF_sum:Compress data:Compress,' +
            '!CTF_frames:!CTF_sum:!Compress data:Frames to work:Copy to work:Copy_work,' +
            '!CTF_frames:!CTF_sum:!Compress data:Frames to HDD:Copy to HDD:Copy_hdd,' +
            '!CTF_frames:!CTF_sum:!Compress data:Frames to backup:Copy to backup:Copy_backup',
            'PLAIN',
            '',
            ],
        [
            'CTF',
            '2',
            int,
            'CTF;' +
            'CTF to work:Copy to work:Copy_work,' +
            'CTF to HDD:Copy to HDD:Copy_hdd,' +
            'CTF to backup:Copy to backup:Copy_backup,' +
            'Motion:Picking:Picking,' +
            '!Picking:Compress data:Compress,' +
            '!Picking:!Compress data:Frames to work:Copy to work:Copy_work,' +
            '!Picking:!Compress data:Frames to HDD:Copy to HDD:Copy_hdd,' +
            '!Picking:!Compress data:Frames to backup:Copy to backup:Copy_backup',
            'PLAIN',
            '',
            ],
        [
            'Picking',
            '2',
            int,
            'Picking;' +
            'Picking to work:Copy to work:Copy_work,' +
            'Picking to HDD:Copy to HDD:Copy_hdd,' +
            'Picking to backup:Copy to backup:Copy_backup,' +
            'Compress data:Compress,' +
            '!Compress data:Frames to work:Copy to work:Copy_work,' +
            '!Compress data:Frames to HDD:Copy to HDD:Copy_hdd,' +
            '!Compress data:Frames to backup:Copy to backup:Copy_backup',
            'PLAIN',
            '',
            ],
        [
            'Compress',
            '2',
            int,
            'Compress;' +
            'Frames to backup:Copy to backup:Copy_backup,' +
            'Frames to HDD:Copy to HDD:Copy_hdd,' +
            'Frames to work:Copy to work:Copy_work',
            'PLAIN',
            '',
            ],
        ['Copy_work', '1', int, 'Copy_work;', 'PLAIN', ''],
        ['Copy_hdd', '1', int, 'Copy_hdd;', 'PLAIN', ''],
        ['Copy_backup', '1', int, 'Copy_backup;', 'PLAIN', ''],
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
        ['WIDGETS MAIN', '7', int, '', 'PLAIN', ''],
        ['WIDGETS ADVANCED', '7', int, '', 'PLAIN', ''],
        ['Pixel size', '1.0', float, '', 'PLAIN', 'Main'],
        ['Acceleration voltage', '300.0', float, '', 'PLAIN', 'Main'],
        ['Spherical aberration', '2.7', float, '', 'PLAIN', 'Main'],
        ['Min resolution(A)', '30', float, '', 'PLAIN', 'Main'],
        ['Max resolution(A)', '5', float, '', 'PLAIN', 'Main'],
        ['Min defocus(A)', '5000', float, '', 'PLAIN', 'Main'],
        ['Max defocus(A)', '50000', float, '', 'PLAIN', 'Main'],
        ['Step defocus(A)', '500', float, '', 'PLAIN', 'Main'],
        ['Amplitude contrast', '0.07', float, '', 'PLAIN', 'Main'],
        ['Phase shift', ['False', 'True'], bool, '', 'COMBO', 'Main'],
        ['Min phase(rad)', '0', float, 'Phase shift:True', 'PLAIN', 'Main'],
        ['Max phase(rad)', '3.15', float, 'Phase shift:True', 'PLAIN', 'Main'],
        ['Step phase(rad)', '0.5', float, 'Phase shift:True', 'PLAIN', 'Main'],
        ['Amplitude spectrum', '512', float, '', 'PLAIN', 'Advanced'],
        ['High accuracy', ['True', 'False'], bool, '', 'COMBO', 'Advanced'],
        ['Know astigmatism', ['True', 'False'], bool, '', 'COMBO', 'Advanced'],
        ['Restrain astigmatism', ['True', 'False'], bool, 'Know astigmatism:False', 'COMBO', 'Advanced'],
        ['Expected astigmatism', '200', float, 'Restrain astigmatism:True', 'PLAIN', 'Advanced'],
        ['Astigmatism', '0', float, 'Know astigmatism:True', 'PLAIN', 'Advanced'],
        ['Astigmatism angle', '0', float, 'Know astigmatism:True', 'PLAIN', 'Advanced'],
        ['Resample micrographs', ['True', 'False'], bool, '', 'COMBO', 'Advanced'],
        ['Use movies', ['False', 'True'], bool, '', 'COMBO', 'Advanced'],
        ['Combine frames', '1', int, 'Use movies:True', 'PLAIN', 'Advanced'],
        ['Movie is gain-corrected?', ['True', 'False'], bool, 'Use movies:True', 'COMBO', 'Advanced'],
        ['Gain file', '', str, 'Movie is gain-corrected?:False', 'FILE', 'Advanced'],
        ['Correct mag. distort.', ['False', 'True'], bool, 'Use movies:True', 'COMBO', 'Advanced'],
        ['Mag. dist. angle', '0.0', float, 'Correct mag. distort.:True', 'PLAIN', 'Advanced'],
        ['Mag. dist. major scale', '1.0', float, 'Correct mag. distort.:True', 'PLAIN', 'Advanced'],
        ['Mag. dist. minor scale', '1.0', float, 'Correct mag. distort.:True', 'PLAIN', 'Advanced'],
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
        ['Mount name', name, str, '', 'PLAIN', ''],
        ['Protocol', ['smbfs', 'cifs', 'nfs'], str, '', 'COMBO', ''],
        ['Protocol version', '2.0', float, '', 'PLAIN', ''],
        ['sec', ['ntlmssp', 'krb5', 'krb5i', 'ntlm', 'ntlmi', 'ntlmv2', 'ntlmv2i', 'ntlmsspi', 'none'], str, '', 'COMBO', ''],
        ['gid', '', str, '', 'PLAIN', ''],
        ['Domain', '', str, '', 'PLAIN', ''],
        ['IP', '', str, '', 'PLAIN', ''],
        ['Folder', '', str, '', 'PLAIN', ''],
        ['Need folder extension?', ['False', 'True'], bool, '', 'COMBO', ''],
        ['Default user', '', str, '', 'PLAIN', ''],
        ['Is df giving the right quota?', ['True', 'False'], bool, '', 'COMBO', ''],
        ['Target UID exists here and on target?', ['True', 'False'], bool, '', 'COMBO', ''],
        ['Need sudo for mount?', ['False', 'True'], bool, '', 'COMBO', ''],
        ['Need sudo for copy?', ['False', 'True'], bool, '', 'COMBO', ''],
        ['SSH address', '', str, '', 'PLAIN', ''],
        ['Quota command', '', str, '', 'PLAIN', ''],
        ['Quota / TB', '', float, '', 'PLAIN', ''],
        ['Typ', ['Copy', 'Copy_work', 'Copy_backup'], str, '', 'COMBO', ''],
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
        ['WIDGETS MAIN', '5', int, '', 'PLAIN', ''],
        ['WIDGETS ADVANCED', '5', int, '', 'PLAIN', ''],
        ['-FmDose', '0', float, '', 'PLAIN', 'Main'],
        ['-PixSize', '0', float, '', 'PLAIN', 'Main'],
        ['-kV', '300', float, '', 'PLAIN', 'Main'],
        ['-Patch', '0 0', [int, int], '', 'PLAIN', 'Main'],
        ['-Bft', '100', float, '', 'PLAIN', 'Main'],
        ['-Throw', '0', int, '', 'PLAIN', 'Main'],
        ['-Trunc', '0', int, '', 'PLAIN', 'Main'],
        ['-Gain', '', str, '', 'FILE', 'Main'],
        ['-RotGain', '0', int, '', 'PLAIN', 'Main'],
        ['-FlipGain', '0', int, '', 'PLAIN', 'Main'],
        ['-MaskCent', '0 0', [float, float], '', 'PLAIN', 'Advanced'],
        ['-MaskSize', '1 1', [float, float], '', 'PLAIN', 'Advanced'],
        ['-Iter', '7', int, '', 'PLAIN', 'Advanced'],
        ['-Tol', '0.5', float, '', 'PLAIN', 'Advanced'],
        ['-PhaseOnly', '0', int, '', 'PLAIN', 'Advanced'],
        ['-StackZ', '0', int, '', 'PLAIN', 'Advanced'],
        ['-FtBin', '1', float, '', 'PLAIN', 'Advanced'],
        ['-InitDose', '0', float, '', 'PLAIN', 'Advanced'],
        ['-Group', '1', int, '', 'PLAIN', 'Advanced'],
        ['-FmRef', '-1', int, '', 'PLAIN', 'Advanced'],
        ['-DefectFile', '', str, '', 'FILE', 'Advanced'],
        ['-Tilt', '0 0', [float, float], '', 'PLAIN', 'Advanced'],
        ['-Mag', '1 1 0', [float, float, float], '', 'PLAIN', 'Advanced'],
        ['-InFmMotion', '0', int, '', 'PLAIN', 'Advanced'],
        ['-Crop', '0 0', [int, int], '', 'PLAIN', 'Advanced'],
        ['-Gpu', '0', [int]*99, '', 'PLAIN', 'Advanced'],
        ['Split Gpu?', ['True', 'False'], bool, '', 'COMBO', 'Advanced'],
        ['dose cutoff', '4', float, '', 'PLAIN', 'Advanced'],
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
        ['WIDGETS MAIN', '5', int, '', 'PLAIN', ''],
        ['WIDGETS ADVANCED', '5', int, '', 'PLAIN', ''],
        ['-FmDose', '0', float, '', 'PLAIN', 'Main'],
        ['-PixSize', '0', float, '', 'PLAIN', 'Main'],
        ['-kV', '300', float, '', 'PLAIN', 'Main'],
        ['-Patch', '0 0 0', [int, int, int], '', 'PLAIN', 'Main'],
        ['-Bft', '100', float, '', 'PLAIN', 'Main'],
        ['-Throw', '0', int, '', 'PLAIN', 'Main'],
        ['-Trunc', '0', int, '', 'PLAIN', 'Main'],
        ['-Gain', '', str, '', 'FILE', 'Main'],
        ['-RotGain', '0', int, '', 'PLAIN', 'Main'],
        ['-FlipGain', '0', int, '', 'PLAIN', 'Main'],
        ['-MaskCent', '0 0', [float, float], '', 'PLAIN', 'Advanced'],
        ['-MaskSize', '1 1', [float, float], '', 'PLAIN', 'Advanced'],
        ['-Iter', '7', int, '', 'PLAIN', 'Advanced'],
        ['-Tol', '0.5', float, '', 'PLAIN', 'Advanced'],
        ['-PhaseOnly', '0', int, '', 'PLAIN', 'Advanced'],
        ['-StackZ', '0', int, '', 'PLAIN', 'Advanced'],
        ['-FtBin', '1', float, '', 'PLAIN', 'Advanced'],
        ['-InitDose', '0', float, '', 'PLAIN', 'Advanced'],
        ['-Group', '1', int, '', 'PLAIN', 'Advanced'],
        ['-FmRef', '-1', int, '', 'PLAIN', 'Advanced'],
        ['-DefectFile', '', str, '', 'FILE', 'Advanced'],
        ['-Dark', '', str, '', 'FILE', 'Advanced'],
        ['-Tilt', '0 0', [float, float], '', 'PLAIN', 'Advanced'],
        ['-Mag', '1 1 0', [float, float, float], '', 'PLAIN', 'Advanced'],
        ['-InFmMotion', '0', int, '', 'PLAIN', 'Advanced'],
        ['-Crop', '0 0', [int, int], '', 'PLAIN', 'Advanced'],
        ['-Gpu', '0', [int]*99, '', 'PLAIN', 'Advanced'],
        ['Split Gpu?', ['True', 'False'], bool, '', 'COMBO', 'Advanced'],
        ['dose cutoff', '4', float, '', 'PLAIN', 'Advanced'],
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
        ['WIDGETS MAIN', '5', int, '', 'PLAIN', ''],
        ['WIDGETS ADVANCED', '5', int, '', 'PLAIN', ''],
        ['-FmDose', '0', float, '', 'PLAIN', 'Main'],
        ['-PixSize', '0', float, '', 'PLAIN', 'Main'],
        ['-kV', '300', float, '', 'PLAIN', 'Main'],
        ['-Patch', '0 0 0', [int, int, int], '', 'PLAIN', 'Main'],
        ['-Bft', '500 150', [float, float], '', 'PLAIN', 'Main'],
        ['-Throw', '0', int, '', 'PLAIN', 'Main'],
        ['-Trunc', '0', int, '', 'PLAIN', 'Main'],
        ['-Gain', '', str, '', 'FILE', 'Main'],
        ['-RotGain', '0', int, '', 'PLAIN', 'Main'],
        ['-FlipGain', '0', int, '', 'PLAIN', 'Main'],
        ['-MaskCent', '0 0', [float, float], '', 'PLAIN', 'Advanced'],
        ['-MaskSize', '1 1', [float, float], '', 'PLAIN', 'Advanced'],
        ['-Iter', '7', int, '', 'PLAIN', 'Advanced'],
        ['-Tol', '0.5', float, '', 'PLAIN', 'Advanced'],
        ['-PhaseOnly', '0', int, '', 'PLAIN', 'Advanced'],
        ['-StackZ', '0', int, '', 'PLAIN', 'Advanced'],
        ['-FtBin', '1', float, '', 'PLAIN', 'Advanced'],
        ['-InitDose', '0', float, '', 'PLAIN', 'Advanced'],
        ['-Group', '1', int, '', 'PLAIN', 'Advanced'],
        ['-FmRef', '-1', int, '', 'PLAIN', 'Advanced'],
        ['-DefectFile', '', str, '', 'FILE', 'Advanced'],
        ['-Dark', '', str, '', 'FILE', 'Advanced'],
        ['-Tilt', '0 0', [float, float], '', 'PLAIN', 'Advanced'],
        ['-Mag', '1 1 0', [float, float, float], '', 'PLAIN', 'Advanced'],
        ['-InFmMotion', '0', int, '', 'PLAIN', 'Advanced'],
        ['-Crop', '0 0', [int, int], '', 'PLAIN', 'Advanced'],
        ['-Gpu', '0', [int]*99, '', 'PLAIN', 'Advanced'],
        ['-GpuMemUsage', '0.5', float, '', 'PLAIN', 'Advanced'],
        ['Split Gpu?', ['True', 'False'], bool, '', 'COMBO', 'Advanced'],
        ['dose cutoff', '4', float, '', 'PLAIN', 'Advanced'],
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
        ['WIDGETS MAIN', '7', int, '', 'PLAIN', ''],
        ['WIDGETS ADVANCED', '7', int, '', 'PLAIN', ''],
        ['Software', ['EPU 1.9', 'EPU 1.8'], str, '', 'COMBO', 'Main'],
        ['Type', ['Stack', 'Frames'], str, '', 'COMBO', 'Main'],
        ['Camera', ['K2', 'Falcon3', 'Falcon2'], str, '', 'COMBO', 'Main'],
        ['Search path frames', '', str, '', 'DIR', 'Main'],
        ['Search path meta', '', str, '', 'DIR', 'Main'],
        ['Input extension', ['mrc', 'dm4', 'tif', 'tiff'], str, '', 'COMBO', 'Main'],
        ['Output extension', ['mrc', 'tif', 'tiff'], str, '', 'COMBO', 'Main'],
        ['Project name', '', str, '', 'PLAIN', 'Main'],
        ['Number of frames', '0', int, '', 'PLAIN', 'Main'],
        ['Rename micrographs', ['True', 'False'], bool, '', 'COMBO', 'Main'],
        ['Rename prefix', '', str, 'Rename micrographs:True', 'PLAIN', 'Main'],
        ['Rename suffix', '', str, 'Rename micrographs:True', 'PLAIN', 'Main'],
        ['Start number', '0', int, 'Rename micrographs:True', 'PLAIN', 'Main'],
        ['Estimated mic number', '5000', int, 'Rename micrographs:True', 'PLAIN', 'Main'],
        ['Project directory', '', str, '', 'DIR', 'Advanced'],
        ['Scratch directory', '', str, '', 'DIR', 'Advanced'],
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
        ['WIDGETS MAIN', '8', int, '', 'PLAIN', ''],
        ['WIDGETS ADVANCED', '8', int, '', 'PLAIN', ''],
        ['Copy to work', copy_work, bool, '', 'COMBO', 'Main'],
        ['Copy to backup', copy_backup, bool, '', 'COMBO', 'Main'],
        ['Copy to HDD', copy_hdd, bool, '', 'COMBO', 'Main'],
        ['Motion', programs_motion, bool, '', 'COMBO', 'Main'],
        ['CTF', programs_ctf, bool, '', 'COMBO', 'Main'],
        ['Picking', programs_picking, bool, '', 'COMBO', 'Main'],
        ['Compress data', ['True', 'Later', 'False'], bool, '', 'COMBO', 'Main'],
        ['Session to work', ['False', 'True'], bool, '', 'COMBO', 'Advanced'],
        ['Session to HDD', ['False', 'True'], bool, '', 'COMBO', 'Advanced'],
        ['Session to backup', ['False', 'True'], bool, '', 'COMBO', 'Advanced'],
        ['Frames to work', ['False', 'True'], bool, '', 'COMBO', 'Advanced'],
        ['Frames to HDD', ['False', 'True'], bool, '', 'COMBO', 'Advanced'],
        ['Frames to backup', ['False', 'True'], bool, '', 'COMBO', 'Advanced'],
        ['Meta to work', ['False', 'True'], bool, '', 'COMBO', 'Advanced'],
        ['Meta to HDD', ['False', 'True'], bool, '', 'COMBO', 'Advanced'],
        ['Meta to backup', ['False', 'True'], bool, '', 'COMBO', 'Advanced'],
        ['Sum to work', ['False', 'True'], bool, '', 'COMBO', 'Advanced'],
        ['Sum to HDD', ['False', 'True'], bool, '', 'COMBO', 'Advanced'],
        ['Sum to backup', ['False', 'True'], bool, '', 'COMBO', 'Advanced'],
        ['CTF to work', ['False', 'True'], bool, '', 'COMBO', 'Advanced'],
        ['CTF to HDD', ['False', 'True'], bool, '', 'COMBO', 'Advanced'],
        ['CTF to backup', ['False', 'True'], bool, '', 'COMBO', 'Advanced'],
        ['Picking to work', ['False', 'True'], bool, '', 'COMBO', 'Advanced'],
        ['Picking to HDD', ['False', 'True'], bool, '', 'COMBO', 'Advanced'],
        ['Picking to backup', ['False', 'True'], bool, '', 'COMBO', 'Advanced'],
        ['Delete data after copy?', ['True', 'False'], bool, '', 'COMBO', 'Advanced'],
        ['Delete stack after compression?', ['True', 'False'], bool, '', 'COMBO', 'Advanced'],
        ]
    return items
