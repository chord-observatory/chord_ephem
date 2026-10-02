import datetime
from zoneinfo import ZoneInfo

import numpy as np
import pytest

from chord_ephem import time as ctime
from chord_ephem.observers import Observer

# 2026-09-11 23:29:18.483057 UTC, 16:29:18 PDT
T0 = 1789169358.483057
CADENCE = 9.9824
LOCAL = ZoneInfo("America/Vancouver")


def test_unix_to_local_datetime():
    dt = ctime.unix_to_local_datetime(T0)
    assert dt.tzinfo == LOCAL
    assert (dt.hour, dt.minute, dt.second) == (16, 29, 18)
    assert dt.tzname() == "PDT"

    arr = ctime.unix_to_local_datetime(np.array([T0, T0 + 3600.0]))
    assert arr.shape == (2,)
    assert arr[1] - arr[0] == datetime.timedelta(hours=1)


def test_local_datetime_to_unix():
    assert ctime.local_datetime_to_unix(2026, 9, 11, 16, 29, 18) == pytest.approx(
        np.floor(T0)
    )
    # Winter: PST is UTC-8
    assert ctime.local_datetime_to_unix(2026, 1, 1) == pytest.approx(
        datetime.datetime(2026, 1, 1, 8, tzinfo=datetime.timezone.utc).timestamp()
    )
    with pytest.raises(ValueError, match="Time zone"):
        ctime.local_datetime_to_unix(2026, 1, 1, 0, 0, 0, 0, LOCAL)


def test_chord_local_datetime():
    assert ctime.chord_local_datetime(2026, 9, 11, 16) == datetime.datetime(
        2026, 9, 11, 23
    )


def test_time_axis_simple():
    unix = T0 + CADENCE * np.arange(10)

    axis, label = ctime.time_axis(unix, "unix")
    assert np.array_equal(axis, unix)

    axis, label = ctime.time_axis(unix, "hours")
    assert axis[0] == 0.0
    assert axis[-1] == pytest.approx(9 * CADENCE / 3600)
    assert label == "Hours since 2026-09-11 23:29 UTC"

    axis, label = ctime.time_axis(unix, "utc")
    assert axis.dtype == np.dtype("datetime64[ms]")
    assert axis[0] == np.datetime64("2026-09-11T23:29:18.483")

    with pytest.raises(ValueError, match="Unknown time axis"):
        ctime.time_axis(unix, "fortnights")


def test_time_axis_local():
    unix = T0 + CADENCE * np.arange(10)
    axis, label = ctime.time_axis(unix, "local")
    assert axis[0] == np.datetime64("2026-09-11T16:29:18.483")
    assert label == "Local time (PDT)"

    # The autumn change from PDT to PST repeats an hour of local time
    unix = ctime.local_datetime_to_unix(2026, 11, 1, 0) + 600.0 * np.arange(24)
    with pytest.warns(UserWarning, match="daylight saving"):
        axis, label = ctime.time_axis(unix, "local")
    assert label == "Local time (PDT/PST)"


def test_time_axis_sidereal():
    # 13 hours, crossing LSA = 0
    unix = T0 + CADENCE * np.arange(4700)

    lsa, label = ctime.time_axis(unix, "lsa")
    assert label == "RA of zenith (CIRS) [deg]"
    assert 0 <= lsa[0] < 360
    assert lsa[-1] > 360
    assert np.all(np.diff(lsa) > 0)
    assert np.allclose(np.diff(lsa), CADENCE / 86164.0905 * 360, rtol=1e-4)

    ra, _ = ctime.time_axis(unix, "ra", unwrap=False)
    assert np.allclose(ra, lsa % 360)
    assert ra.max() < 360

    lst, label = ctime.time_axis(unix, "lst")
    assert label == "LST [h]"
    assert np.all(np.diff(lst) > 0)
    # LST and LSA differ by the equation of the origins, ~0.3 deg
    diff = (lst * 15 - lsa + 180) % 360 - 180
    assert np.all(np.abs(diff) < 1.0)

    lsd, label = ctime.time_axis(unix, "lsd")
    assert label == "LSD"
    assert np.all(np.diff(lsd) > 0)


def test_time_axis_other_observer():
    unix = np.array([T0])
    greenwich = Observer(lon=0.0, lat=51.48, timezone="Europe/London")
    axis, label = ctime.time_axis(unix, "local", obs=greenwich)
    assert axis[0] == np.datetime64("2026-09-12T00:29:18.483")
    assert label == "Local time (BST)"
