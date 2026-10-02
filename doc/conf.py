"""Sphinx configuration for chord_ephem."""

project = "chord_ephem"
author = "The CHORD Collaboration"

extensions = [
    "sphinx.ext.autodoc",
    "sphinx.ext.autosummary",
    "sphinx.ext.intersphinx",
    "sphinx.ext.napoleon",
]

autosummary_generate = True
napoleon_numpy_docstring = True
intersphinx_mapping = {
    "python": ("https://docs.python.org/3", None),
    "numpy": ("https://numpy.org/doc/stable", None),
    "caput": ("https://caput.readthedocs.io/en/latest", None),
}

html_theme = "sphinx_rtd_theme"
