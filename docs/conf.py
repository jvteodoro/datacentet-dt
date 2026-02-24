"""Sphinx configuration for datacentet-dt documentation."""
from __future__ import annotations

from datetime import datetime

project = "datacentet-dt"
author = "datacentet-dt contributors"
current_year = datetime.now().year
copyright = f"{current_year}, {author}"
release = "0.1.0"
version = release

extensions = [
    "sphinx.ext.autodoc",
    "sphinx.ext.napoleon",
    "sphinx.ext.viewcode",
]

templates_path = ["_templates"]
exclude_patterns = ["_build", "Thumbs.db", ".DS_Store"]

language = "pt_BR"

html_theme = "alabaster"
html_static_path = ["_static"]

master_doc = "index"
