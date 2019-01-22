import setuptools
import os

here = os.path.abspath(os.path.dirname(__file__))

with open(os.path.join(here, 'README.md'), encoding='utf-8') as f:
    long_description = f.read()

setuptools.setup(
    name='transphire',
    version='1.4.25',
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
        'numpy>=1.14.0,<1.15.0',
        'matplotlib>=2.2.0,<2.3.0',
        'pexpect>=4.6.0,<4.7.0',
        'cython>=0.28.0,<0.29.0',
        'telepot>=12.0,<13.0',
        'imageio>=2.3.0,<2.4.0',
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

