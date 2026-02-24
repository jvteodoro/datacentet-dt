import os
import sys

ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..'))
SRC = os.path.join(ROOT, 'src')
if SRC not in sys.path:
    sys.path.insert(0, SRC)

project = 'Digital Twin — Codex Explained Code'
author = 'Project Contributors'
extensions = [
    'sphinx.ext.autodoc',
    'sphinx.ext.autosummary',
    'sphinx.ext.napoleon',
    'sphinx.ext.graphviz',
    'sphinx.ext.inheritance_diagram',
]
autosummary_generate = True
autodoc_typehints = 'description'
exclude_patterns = ['_build']
html_theme = 'alabaster'
master_doc = 'index'
