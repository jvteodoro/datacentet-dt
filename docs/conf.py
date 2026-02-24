import os
import sys

sys.path.insert(0, os.path.abspath('..'))
sys.path.insert(0, os.path.abspath('../src'))

project = 'datacentet-dt'

extensions = [
    'sphinx.ext.autodoc',
    'sphinx.ext.napoleon',
    'sphinx.ext.mathjax',
    'sphinx.ext.viewcode',
]

html_theme = 'sphinx_rtd_theme'
autodoc_member_order = 'bysource'
autodoc_typehints = 'description'
