# chord_ephem

This package provides ephemeris routines for CHORD.

- `chord_ephem.observers`: `caput` `Observer`s for the CHORD instruments, with
  their positions in `chord_ephem/instruments.yaml`;
- `chord_ephem.time`: conversions between UNIX time and local (DRAO) time;
- `chord_ephem.sources`: the standard radio source catalogue.

General-purpose ephemeris routines are in
[caput](https://github.com/radiocosmology/caput) (`caput.astro`) and
[draco](https://github.com/radiocosmology/draco) (`draco.ephem`); this package
holds what is specific to CHORD.

```python
from chord_ephem.observers import chord
from chord_ephem.time import unix_to_local_datetime

lsa = chord.unix_to_lsa(unix_times)  # RA of the zenith (CIRS), degrees
local = unix_to_local_datetime(unix_times)  # time zone aware datetimes
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
