"""CHORD ephemeris routines.

Instrument observers
====================

Ephemeris routines which need the position of the observer are available from
the instrument `Observer` instances in :py:mod:`chord_ephem.observers`:

    >>> from chord_ephem.observers import chord
    >>> chord.solar_transit(...)

These subclass `caput.astro.observer.Observer` and can be used wherever a
`caput` observer is expected. The instrument positions are defined in the data
file `instruments.yaml` provided with the package.

Time
====

:py:mod:`chord_ephem.time` converts UNIX times to the times used at CHORD: UTC,
local (DRAO) time, the local stellar angle (the CIRS RA of the zenith), LST and
LSD, for instance to label the time axis of a waterfall plot.

Right Ascension
===============

As for CHIME, RA is given in the Celestial Intermediate Reference System
(CIRS), whose origin does not precess. The RA of the zenith in CIRS is the
local stellar angle (LSA, :py:meth:`Observer.unix_to_lsa`), which is what
`draco` uses for the RA axis of sidereal streams. The local sidereal time (LST,
:py:meth:`Observer.unix_to_lst`) is instead measured from the equinox, and
differs from the LSA by the equation of the origins (about 0.3 degrees today).

Radio sources
=============

:py:mod:`chord_ephem.sources` provides the standard radio source catalogue:

    >>> from chord_ephem.sources import source_dictionary, CasA
"""

from importlib.metadata import PackageNotFoundError, version

try:
    __version__ = version("chord_ephem")
except PackageNotFoundError:
    # package is not installed
    pass

del version, PackageNotFoundError
