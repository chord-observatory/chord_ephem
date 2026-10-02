"""CHORD time routines.

Conversions from UNIX time (the `time` axis of CHORD timestreams) to the times
used at CHORD: UTC, local time at the instrument, the local stellar angle (the
CIRS RA of the zenith), LST and LSD.

Functions
=========

- :py:meth:`unix_to_local_datetime`
- :py:meth:`local_datetime_to_unix`
- :py:meth:`chord_local_datetime`
- :py:meth:`time_axis`
"""

from __future__ import annotations

import datetime
import warnings
from typing import TYPE_CHECKING, Any

import numpy as np

if TYPE_CHECKING:
    from caput.astro.observer import Observer

# Kinds of time axis that `time_axis` can make
TIME_AXES = ("unix", "hours", "utc", "local", "lsa", "ra", "lst", "lsd")


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


def _unwrap(angle: np.ndarray, period: float) -> np.ndarray:
    """Unwrap a periodic angle so that it is continuous, starting in [0, period)."""
    out = np.unwrap(angle, period=period)
    return out - period * np.floor(out[0] / period)


def time_axis(
    unix: np.ndarray,
    kind: str = "local",
    obs: Observer | None = None,
    unwrap: bool = True,
) -> tuple[np.ndarray, str]:
    """Convert UNIX times into a time axis for plotting, with a label.

    Parameters
    ----------
    unix : np.ndarray
        UNIX times in seconds, e.g. the `time` axis of a timestream.
    kind : str
        The kind of axis:

        - "unix": UNIX time in seconds.
        - "hours": hours since the first sample.
        - "utc": UTC, as `datetime64`.
        - "local": local time at the observer, as `datetime64` holding the
          local wall-clock time (with no time zone, so that matplotlib shows
          it as is).
        - "lsa" or "ra": local stellar angle in degrees, i.e. the CIRS RA of
          the zenith, as used for the RA axis of draco sidereal streams.
        - "lst": local (apparent, equinox based) sidereal time in hours.
        - "lsd": local sidereal day, as a float.
    obs : Observer, optional
        The observer. Defaults to CHORD.
    unwrap : bool
        For "lsa", "ra" and "lst", remove the jump at 360 degrees or 24 hours
        so that the axis increases monotonically. The values then go above
        360 degrees (24 hours); take them modulo 360 (24) for display.

    Returns
    -------
    axis : np.ndarray
        The time axis, the same length as `unix`.
    label : str
        An axis label.
    """
    unix = np.asarray(unix, dtype=np.float64)

    if kind not in TIME_AXES:
        raise ValueError(f"Unknown time axis {kind!r}. Use one of {TIME_AXES}.")

    if kind == "unix":
        return unix.copy(), "UNIX time [s]"

    if kind == "hours":
        start = datetime.datetime.fromtimestamp(unix[0], tz=datetime.timezone.utc)
        return (unix - unix[0]) / 3600.0, f"Hours since {start:%Y-%m-%d %H:%M} UTC"

    if kind == "utc":
        return (unix * 1e3).astype("datetime64[ms]"), "UTC"

    obs = _default_observer(obs)

    if kind == "local":
        local = unix_to_local_datetime(unix, obs)
        offsets = np.array([dt.utcoffset().total_seconds() for dt in local])
        axis = ((unix + offsets) * 1e3).astype("datetime64[ms]")
        names = list(dict.fromkeys(dt.tzname() for dt in local))
        if np.any(np.diff(axis) < np.timedelta64(0, "ms")):
            warnings.warn(
                "Local time goes backwards (a daylight saving time change); "
                "use another kind of time axis for this span."
            )
        return axis, f"Local time ({'/'.join(names)})"

    if kind in ("lsa", "ra"):
        lsa = obs.unix_to_lsa(unix)
        if unwrap:
            lsa = _unwrap(lsa, 360.0)
        return lsa, "RA of zenith (CIRS) [deg]"

    if kind == "lst":
        lst = obs.unix_to_lst(unix) / 15.0
        if unwrap:
            lst = _unwrap(lst, 24.0)
        return lst, "LST [h]"

    # lsd
    return obs.unix_to_lsd(unix), "LSD"
