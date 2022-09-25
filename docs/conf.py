"""Sphinx configuration."""
project = "Log License"
author = "Martin Closter Jespersen"
copyright = "2022, Martin Closter Jespersen"
extensions = [
    "sphinx.ext.autodoc",
    "sphinx.ext.napoleon",
    "sphinx_click",
    "myst_parser",
]
autodoc_typehints = "description"
html_theme = "furo"
