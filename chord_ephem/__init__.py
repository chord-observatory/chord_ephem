"""CHORD ephemeris routines."""

from importlib.metadata import PackageNotFoundError, version

try:
    __version__ = version("chord_ephem")
except PackageNotFoundError:
    # package is not installed
    pass

del version, PackageNotFoundError
