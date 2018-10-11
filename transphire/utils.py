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


import shutil


def copy(file_in: str, file_out: str) -> None:
    """
    Copy file_in to a new location file_out.

    If copy2 fails because of permissions, fall back to copyfile.

    Arguments:
    file_in - Input file
    file_out - Output file/directory

    Return:
    None
    """

    try:
        shutil.copy2(file_in, file_out)
    except PermissionError: # pragma: no cover | Cannot be tested on one file system
        shutil.copyfile(file_in, file_out)
