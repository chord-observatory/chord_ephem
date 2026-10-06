"""CHORD source objects.

Note: this submodule reads the radio source catalogues from disk at import
time.

Constants
=========

:const:`source_dictionary`
    The standard radio source catalogue. A `dict` whose keys are source
    names and whose values are `skyfield.starlib.Star` objects.
:const:`CasA`
    :class:`skyfield.starlib.Star` representing Cassiopeia A.
:const:`CygA`
    :class:`skyfield.starlib.Star` representing Cygnus A.
:const:`TauA`
    :class:`skyfield.starlib.Star` representing Taurus A.

Functions
=========

- :py:meth:`get_source_dictionary`
"""

from __future__ import annotations

from caput.astro.skyfield import skyfield_star_from_ra_dec
from fluxcat.catalogs import load


def get_source_dictionary(*catalogs: str) -> dict:
    """Return a source dictionary.

    Returns a dictionary containing :class:`skyfield.starlib.Star` objects for
    common radio point sources, to get the skyfield representation of a source
    from its name.

    Parameters
    ----------
    *catalogs : str
        Names of `fluxcat` catalogues. If several are given, the first is
        favoured for any sources in more than one.

    Returns
    -------
    src_dict : dict
        Keys are source names. Values are `skyfield.starlib.Star` objects.
    """
    src_dict = {}
    for catalog_name in reversed(catalogs):
        catalog = load(catalog_name)

        for name, info in catalog.items():
            names = info["alternate_names"]
            if name not in names:
                names = [name, *names]
            src_dict[name] = skyfield_star_from_ra_dec(
                info["ra"], info["dec"], tuple(names)
            )

    return src_dict


# Common radio point sources, the same as CHIME's for now
source_dictionary = get_source_dictionary(
    "primary_calibrators_perley2016",
    "specfind_v2_5Jy_vollmer2009",
    "atnf_psrcat",
    "hfb_target_list",
)

# Calibrators. Vir A (declination +12 deg) is below CHORD's declination range
# (down to +20 deg), so it is not included.
CasA = source_dictionary["CAS_A"]
CygA = source_dictionary["CYG_A"]
TauA = source_dictionary["TAU_A"]
