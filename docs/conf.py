"""Sphinx configuration for datacentet-dt documentation."""
from __future__ import annotations
from datetime import datetime
import os
import sys

project = "datacentet-dt"
author = "datacentet-dt contributors"
current_year = datetime.now().year
copyright = f"{current_year}, {author}"
release = "0.1.0"
version = release

sys.path.insert(0, os.path.abspath('..'))
sys.path.insert(0, os.path.abspath('../src'))

extensions = [
    'sphinx.ext.autodoc',
    'sphinx.ext.napoleon',
    'sphinx.ext.mathjax',
    'sphinx.ext.viewcode',
]

templates_path = ["_templates"]
exclude_patterns = ["_build", "Thumbs.db", ".DS_Store"]

language = "pt_BR"

html_theme = "alabaster"
html_static_path = ["_static"]
#html_theme = 'sphinx_rtd_theme'
#autodoc_member_order = 'bysource'
autodoc_typehints = 'description'

master_doc = "index"

