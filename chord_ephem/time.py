"""CHORD time routines.

Conversions between UNIX time (the `time` axis of CHORD timestreams) and local
time at the instrument. Sidereal times (LSA, LST, LSD) are methods of the
observers in :py:mod:`chord_ephem.observers`.

Functions
=========

- :py:meth:`unix_to_local_datetime`
- :py:meth:`local_datetime_to_unix`
- :py:meth:`chord_local_datetime`
"""

from __future__ import annotations

import datetime
from typing import TYPE_CHECKING, Any

import numpy as np

if TYPE_CHECKING:
    from caput.astro.observer import Observer


def _default_observer(obs: Observer | None) -> Observer:
    if obs is None:
        from .observers import chord as obs
    return obs


def unix_to_local_datetime(
    unix: float | np.ndarray, obs: Observer | None = None
) -> datetime.datetime | np.ndarray:
    """Convert UNIX times to time-zone aware datetimes in the local time zone.

    Parameters
    ----------
    unix : float or np.ndarray
        UNIX time(s) in seconds.
    obs : Observer, optional
        The observer, whose `timezone` is used. Defaults to CHORD.

    Returns
    -------
    dt : datetime.datetime or np.ndarray
        A datetime, or an object array of datetimes for array input.
    """
    tz = _default_observer(obs).timezone

    if np.ndim(unix) == 0:
        return datetime.datetime.fromtimestamp(float(unix), tz=tz)

    unix = np.asarray(unix, dtype=np.float64)
    out = np.empty(unix.shape, dtype=object)
    for ii, tt in np.ndenumerate(unix):
        out[ii] = datetime.datetime.fromtimestamp(tt, tz=tz)
    return out


def local_datetime_to_unix(*args: Any, obs: Observer | None = None) -> float:
    """Convert a local date and time at the observer to UNIX time.

    Parameters
    ----------
    *args
        Any valid arguments to the constructor of :class:`datetime.datetime`
        except `tzinfo`: the local date and time.
    obs : Observer, optional
        The observer, whose `timezone` is used. Defaults to CHORD.

    Returns
    -------
    unix : float
        UNIX time in seconds.
    """
    dt = datetime.datetime(*args)
    if dt.tzinfo is not None:
        raise ValueError("Time zone should not be supplied.")
    return dt.replace(tzinfo=_default_observer(obs).timezone).timestamp()


def chord_local_datetime(*args: Any) -> datetime.datetime:
    """Convert a local date and time at CHORD to a naive UTC datetime.

    The counterpart of `ch_ephem.time.chime_local_datetime`.

    Parameters
    ----------
    *args
        Any valid arguments to the constructor of :class:`datetime.datetime`
        except `tzinfo`: the local date and time at CHORD.

    Returns
    -------
    dt : datetime.datetime
        Time zone naive date and time, in UTC.
    """
    unix = local_datetime_to_unix(*args)
    return datetime.datetime.fromtimestamp(unix, tz=datetime.timezone.utc).replace(
        tzinfo=None
    )
