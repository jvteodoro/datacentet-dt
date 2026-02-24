"""Sphinx configuration for datacentet-dt documentation."""
from __future__ import annotations
from datetime import datetime
import importlib
import os
import sys
import types

project = "datacentet-dt"
author = "datacentet-dt contributors"
current_year = datetime.now().year
copyright = f"{current_year}, {author}"
release = "0.1.0"
version = release

ROOT_DIR = os.path.abspath('..')
SRC_DIR = os.path.abspath('../src')
sys.path.insert(0, ROOT_DIR)
sys.path.insert(0, SRC_DIR)


def _configure_digital_twin_namespace_alias() -> None:
    """Expose ``digital_twin.*`` aliases for docs without changing source layout."""
    if "digital_twin" in sys.modules:
        return

    package = types.ModuleType("digital_twin")
    package.__path__ = [SRC_DIR]
    sys.modules["digital_twin"] = package

    for subpackage in ("application", "domain"):
        try:
            module = importlib.import_module(subpackage)
        except ModuleNotFoundError:
            continue

        setattr(package, subpackage, module)
        sys.modules[f"digital_twin.{subpackage}"] = module


_configure_digital_twin_namespace_alias()

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
