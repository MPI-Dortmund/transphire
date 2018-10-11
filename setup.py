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
import setuptools


THIS_FILE = os.path.abspath(os.path.dirname(__file__))

with open(os.path.join(THIS_FILE, 'README.md'), encoding='utf-8') as f:
    LONG_DESCRIPTION = f.read()

setuptools.setup(
    name='transphire',
    version='2.0.0',
    description='Automated post data aquisition processing tool',
    long_description=LONG_DESCRIPTION,
    url='https://github.com/mstabrin/transphire',
    author='Markus Stabrin',
    author_email='markus.stabrin@tu-dortmund.de',
    license='GPLv3',
    packages=setuptools.find_packages(exclude=[]),
    include_package_data=True,
    entry_points={
        'console_scripts': [
            'transphire = transphire.__main__:run_package'
            ]
        },
    install_requires = [
        'numpy>=1.15.0,<1.16.0',
        'matplotlib>=2.2.0,<2.3.0',
        'pexpect>=4.6.0,<4.7.0',
        'cython>=0.28.0,<0.29.0',
        'telepot>=12.0,<13.0',
        'imageio>=2.3.0,<2.4.0',
        'transphire_transform>=0.0.1',
        ],
    classifiers = (
        'Programming Language :: Python :: 3.7',
        'License :: OSI Approved :: GNU General Public License v3 or later (GPLv3+)',
        'Operating System :: POSIX :: Linux',
        'Environment :: X11 Applications :: Qt',
        'Development Status :: 4 - Beta'
        ),
    )
