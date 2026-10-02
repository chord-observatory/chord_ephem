# chord_ephem

Ephemeris routines for CHORD, the counterpart of CHIME's
[ch_ephem](https://github.com/chime-experiment/ch_ephem):

- `chord_ephem.observers`: `caput` `Observer`s for the CHORD instruments, with
  their positions in `chord_ephem/instruments.yaml`;
- `chord_ephem.time`: conversions between UNIX time, UTC, local (DRAO) time,
  local stellar angle / RA, LST and LSD, e.g. for the time axis of plots;
- `chord_ephem.sources`: the standard radio source catalogue.

General-purpose ephemeris routines are in
[caput](https://github.com/radiocosmology/caput) (`caput.astro`) and
[draco](https://github.com/radiocosmology/draco) (`draco.ephem`); this package
holds what is specific to CHORD.

```python
from chord_ephem.observers import chord
from chord_ephem.time import time_axis

lsa = chord.unix_to_lsa(unix_times)         # RA of the zenith (CIRS), degrees
local, label = time_axis(unix_times, "local")  # e.g. for pcolormesh
```

## Installation

```
pip install git+https://github.com/chord-observatory/chord_ephem.git
```

or, for development, `pip install -e .[test]` from a clone.

## Tests

```
python -m pytest
```

## Contributing

Follow the [CHORD pipeline guidelines](https://github.com/chord-observatory/Pipeline).
