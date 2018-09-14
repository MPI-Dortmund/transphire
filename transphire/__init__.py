import pkg_resources
from pkg_resources import get_distribution
import os

try:
    _dist = get_distribution('transphire')
    # Normalize case for Windows systems
    dist_loc = os.path.normcase(_dist.location)
    here = os.path.normcase(__file__)
    if not here.startswith(os.path.join(dist_loc, 'transphire')):
        # not installed, but there is another version that *is*
        raise pkg_resources.DistributionNotFound
except pkg_resources.DistributionNotFound:
    try:
        pip_output = os.popen('{0}/../../../../bin/pip freeze'.format(os.path.dirname(here))).read()
        transphire = re.search(r'(transphire==[0-9\.]*)', pip_output)
        __version__ = transphire.group(1).split('==')[1]
    except:
        __version__ = 'Please install this project with setup.py'
else:
    __version__ = _dist.version
