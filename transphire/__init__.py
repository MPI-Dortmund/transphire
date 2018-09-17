import pkg_resources
from pkg_resources import get_distribution
import sys
import os
import re

here = os.path.normcase(__file__)
try:
    _dist = get_distribution('transphire')
    # Normalize case for Windows systems
    dist_loc = os.path.normcase(_dist.location)
    if not here.startswith(os.path.join(dist_loc, 'transphire')):
        # not installed, but there is another version that *is*
        raise pkg_resources.DistributionNotFound
except pkg_resources.DistributionNotFound:
    try:
        pip_path = '{0}/pip'.format([path for path in sys.path if '/bin' in path][0])
        pip_output = os.popen('{0} freeze'.format(pip_path)).read()
        transphire = re.search(r'(transphire==[0-9\.]*)', pip_output)
        __version__ = transphire.group(1).split('==')[1]
    except:
        __version__ = 'XX.XX.XX'
        print('Could not find version number! Please install this project with setup.py!')
        print('Use: "pip freeze" to find the transphire version')
else:
    __version__ = _dist.version
