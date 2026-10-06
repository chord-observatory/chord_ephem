import datetime
from zoneinfo import ZoneInfo

import numpy as np
import pytest

from chord_ephem import time as ctime

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
