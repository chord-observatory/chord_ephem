import pytest

from chord_ephem import sources


def test_calibrators():
    assert sources.CasA is sources.source_dictionary["CAS_A"]
    assert sources.CasA.ra.hours == pytest.approx(23.391, abs=1e-3)
    assert sources.CygA.dec.degrees == pytest.approx(40.73, abs=1e-2)
