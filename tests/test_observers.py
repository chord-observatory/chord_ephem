import warnings
from zoneinfo import ZoneInfo

import numpy as np
import pytest

from chord_ephem import observers
from chord_ephem.observers import Observer

# (UNIX time, local Earth rotation angle at the centre of the bin) from the
# X-engine files of acq_20260911_232919_986789057, across the wrap at 360 deg.
XENGINE_ERAL = [
    (1789169358.483057, 223.35835541666532),
    (1789202058.9547627, 359.98335541666586),
    (1789202068.937206, 0.02502208333309852),
    (1789215671.6522806, 56.85835541666718),
]


def test_chord_observer():
    from chord_ephem.observers import chord

    assert isinstance(chord, Observer)
    assert chord.latitude == pytest.approx(49.32075144444)
    assert chord.longitude == pytest.approx(-119.62081125)
    assert chord.timezone == ZoneInfo("America/Vancouver")
    assert chord.rotation == 0.0
    assert list(chord.offset) == [0.0, 0.0, 0.0]
    assert "chord" in observers.all()


def test_unknown_instrument():
    with pytest.raises(AttributeError, match="Unknown instrument"):
        observers.not_an_instrument


def test_lsa_matches_xengine():
    """The CIRS RA of the zenith matches the X-engine's local ERA."""
    from chord_ephem.observers import chord

    unix, eral = np.array(XENGINE_ERAL).T
    diff = (chord.unix_to_lsa(unix) - eral + 180.0) % 360.0 - 180.0
    assert np.all(np.abs(diff) < 1e-3)


def test_parse_record():
    record = {"latitude": 1.0, "longitude": 2.0, "altitude": 3.0, "timezone": "UTC"}
    obs = observers._parse_record("test", record)
    assert (obs.latitude, obs.longitude, obs.altitude) == (1.0, 2.0, 3.0)
    assert obs.offset.x == 0.0

    record["offset"] = {"x": 1.0, "y": 2.0, "z": 3.0}
    assert tuple(observers._parse_record("test", record).offset) == (1.0, 2.0, 3.0)

    del record["timezone"]
    with warnings.catch_warnings(record=True) as w:
        warnings.simplefilter("always")
        assert observers._parse_record("test", record) is None
    assert "missing ['timezone']" in str(w[0].message)


def test_reset():
    first = observers.all()
    observers.reset()
    assert observers.all() is not first
