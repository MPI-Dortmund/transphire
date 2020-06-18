import setuptools
import os

here = os.path.abspath(os.path.dirname(__file__))

with open(os.path.join(here, 'README.md'), encoding='utf-8') as f:
    long_description = f.read()

setuptools.setup(
    name='transphire',
    version='1.5.0',
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
    install_requires = [
        'numpy',
        'matplotlib',
        'pexpect',
        'cython',
        'telepot',
        'imageio',
        'hyperspy',
        'mrcfile',
        ],
    classifiers = (
        'Programming Language :: Python :: 3.6',
        'License :: OSI Approved :: GNU General Public License v3 or later (GPLv3+)',
        'Operating System :: POSIX :: Linux',
        'Environment :: X11 Applications :: Qt',
        'Development Status :: 4 - Beta'
        ),
    )

