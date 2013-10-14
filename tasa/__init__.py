import imp
import pkg_resources

try:
    __version__ = pkg_resources.get_distribution("tasa").version
except pkg_resources.DistributionNotFound:
    # There's probably a better way to handle this
    __version__ = 'UNKNOWN'


# FIXME: this should probably be lazy...
try:
    # Try to load a tasa.conf configuration file
    conf = imp.load_source('__tasa.conf', '/etc/tasa/tasa.conf')
except IOError:
    # Otherwise just return a similar but empty new module
    conf = imp.new_module('__tasa.conf')
