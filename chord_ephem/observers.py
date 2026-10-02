"""Observers for CHORD instruments.

This module provides `caput.astro.observer.Observer` objects for the CHORD
instruments. Their positions come from the `instruments.yaml` file provided
with this module, and any instrument defined there has an importable
Observer in `chord_ephem.observers`:

    >>> from chord_ephem.observers import chord
    >>> print(chord.latitude)
    49.32075144444

To get all the available instrument observers, use :py:meth:`all`, which
returns a dict of Observer objects:

    >>> import chord_ephem.observers
    >>> chord_ephem.observers.all()
    {'chord': <chord_ephem.observers.Observer object at 0x7f2225b264d0>}

The Observers subclass `caput.astro.observer.Observer` to also provide the
local time zone, and the rotation and tangent-space offset of the array:

    >>> print(chord.timezone)
    America/Vancouver
    >>> print(list(chord.offset))
    [0.0, 0.0, 0.0]

Functions
=========

- :py:meth:`all`
- :py:meth:`reset`
"""

from __future__ import annotations

import datetime
import pathlib
import warnings
from collections import namedtuple
from zoneinfo import ZoneInfo

import yaml
from caput.astro.observer import Observer as CaputObserver

# LSD start time. This is the same as CHIME's, so that LSDs are the same for
# both instruments.
_lsd_start = datetime.datetime(2013, 11, 15)

# Initialised on first use
_observers = None

# Tangent-space offset representation
Offset = namedtuple("Offset", ["x", "y", "z"])


class Observer(CaputObserver):
    """Representation of a CHORD instrument on the Earth.

    This extends `caput.astro.observer.Observer` with:

    Observer.timezone:
        the local time zone, as a :class:`zoneinfo.ZoneInfo`.
    Observer.rotation:
        rotation of the array in degrees anti-clockwise looking down from
        above (e.g. westward from north).
    Observer.offset:
        offset in metres of the array zero point in the right-handed tangent
        space anchored at (lat, lon, alt). A positive x offset is eastward, a
        positive y offset is northward and a positive z offset is upward.

    Parameters
    ----------
    lon, lat : float
        East longitude and north latitude in degrees.
    alt : float
        Altitude above mean sea level in metres.
    timezone : str
        IANA name of the local time zone.
    rot : float
        Rotation of the array in degrees.
    offset : sequence of float
        (x, y, z) offset of the array zero point in metres.
    lsd_start : datetime.datetime, optional
        Start of the local sidereal day count.
    sf_wrapper : caput.astro.skyfield.SkyfieldWrapper, optional
        Skyfield wrapper to use.
    """

    def __init__(
        self,
        lon=0.0,
        lat=0.0,
        alt=0.0,
        timezone="UTC",
        rot=0.0,
        offset=(0.0, 0.0, 0.0),
        lsd_start=None,
        sf_wrapper=None,
    ):
        super().__init__(lon, lat, alt, lsd_start, sf_wrapper)
        self.timezone = ZoneInfo(timezone)
        self.rotation = rot
        self.offset = Offset(*offset)


def _parse_record(name: str, record: dict) -> Observer | None:
    """Make an Observer from an `instruments.yaml` record, or warn and return None."""
    missing = [
        key
        for key in ("latitude", "longitude", "altitude", "timezone")
        if key not in record
    ]
    offset = record.get("offset", {"x": 0.0, "y": 0.0, "z": 0.0})
    missing += [f"offset.{key}" for key in "xyz" if key not in offset]

    if missing:
        warnings.warn(f'Unable to create observer for "{name}": missing {missing}')
        return None

    return Observer(
        lat=float(record["latitude"]),
        lon=float(record["longitude"]),
        alt=float(record["altitude"]),
        timezone=str(record["timezone"]),
        rot=float(record.get("rotation", 0.0)),
        offset=tuple(float(offset[key]) for key in "xyz"),
        lsd_start=_lsd_start,
    )


def all() -> dict[str, Observer]:
    """Return a dict of all available Observers, keyed by name."""
    global _observers
    if _observers is None:
        with pathlib.Path(__file__).with_name("instruments.yaml").open() as f:
            data = yaml.safe_load(f)

        _observers = {}
        for name, record in data.items():
            obs = _parse_record(name, record)
            if obs is not None:
                _observers[name] = obs

    return _observers


def reset() -> None:
    """Unload all the observers.

    Use this function if you've changed `instruments.yaml` on disk, to clear
    the module's cache of Observers.
    """
    global _observers
    _observers = None


def __getattr__(name: str) -> Observer:
    """Retrieve the `Observer` for the instrument named.

    Don't call this function directly; just import the instrument you want
    from the module:

        >>> from chord_ephem.observers import chord

    Parameters
    ----------
    name : str
        Name of the instrument Observer to retrieve.

    Returns
    -------
    observer : Observer
        The Observer object for the named instrument.

    Raises
    ------
    AttributeError
        Data for the instrument named could not be found.
    """
    # Load observers from disk, if necessary
    observers = all()

    try:
        return observers[name]
    except KeyError as e:
        raise AttributeError(f"Unknown instrument: {name}") from e
