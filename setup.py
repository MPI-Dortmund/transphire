import setuptools
import os
import re

here = os.path.abspath(os.path.dirname(__file__))

def get_version():
    init_file = os.path.join(here, 'transphire', '__init__.py')
    with open(init_file) as read:
        data = read.read()
    return re.search("^__version__ = '(.*)'$", data, re.M).group(1)


with open(os.path.join(here, 'README.md'), encoding='utf-8') as f:
    long_description = f.read()

with open(os.path.join(here, 'requirements.txt'), encoding='utf-8') as f:
    requirements = f.read().split()
requirements.remove('PyQt5')


setuptools.setup(
    name='transphire',
    version=get_version(),
    description='Automated post data aquisition processing tool',
    long_description=long_description,
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
    install_requires = requirements,
    classifiers = (
        'Programming Language :: Python :: 3.6',
        'License :: OSI Approved :: GNU General Public License v3 or later (GPLv3+)',
        'Operating System :: POSIX :: Linux',
        'Environment :: X11 Applications :: Qt',
        'Development Status :: 4 - Beta'
        ),
    )

