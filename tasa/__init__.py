import pkg_resources

try:
    __version__ = pkg_resources.get_distribution("tasa").version
except pkg_resources.DistributionNotFound:
    # There's probably a better way to handle this
    __version__ = 'UNKNOWN'
