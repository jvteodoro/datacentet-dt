"""Sphinx configuration for datacentet-dt documentation."""
from __future__ import annotations

from datetime import datetime
import importlib
import os
from pathlib import Path
import sys
import types

project = "datacentet-dt"
author = "datacentet-dt contributors"
current_year = datetime.now().year
copyright = f"{current_year}, {author}"
release = "0.1.0"
version = release

DOCS_DIR = Path(__file__).resolve().parent
ROOT_DIR = DOCS_DIR.parent
SRC_DIR = ROOT_DIR / "src"
sys.path.insert(0, str(ROOT_DIR))
sys.path.insert(0, str(SRC_DIR))


def _configure_digital_twin_namespace_alias() -> None:
    """Expose ``digital_twin.*`` aliases for docs without changing source layout."""
    if "digital_twin" in sys.modules:
        return

    package = types.ModuleType("digital_twin")
    package.__path__ = [str(SRC_DIR)]
    sys.modules["digital_twin"] = package

    for subpackage in ("application", "domain"):
        try:
            module = importlib.import_module(subpackage)
        except ModuleNotFoundError:
            continue

        setattr(package, subpackage, module)
        sys.modules[f"digital_twin.{subpackage}"] = module


def _title_from_dirname(dirname: str) -> str:
    return dirname.replace("_", " ").replace("-", " ").title()


def _autogenerate_folder_indexes() -> None:
    """Create/refresh index.rst for each docs subfolder to keep nav in sync."""
    skip_dirs = {"_build", "_static", "_templates", ".git"}
    for folder in sorted(p for p in DOCS_DIR.rglob("*") if p.is_dir()):
        if folder == DOCS_DIR:
            continue
        if any(part in skip_dirs for part in folder.parts):
            continue

        rst_files = sorted(
            p.stem for p in folder.glob("*.rst") if p.name != "index.rst"
        )
        child_indexes = sorted(
            p.name for p in folder.iterdir() if p.is_dir() and (p / "index.rst").exists()
        )

        title = _title_from_dirname(folder.name)
        lines = [title, "=" * len(title), "", ".. toctree::", "   :maxdepth: 2", ""]
        if rst_files:
            lines.extend(f"   {name}" for name in rst_files)
        if child_indexes:
            if rst_files:
                lines.append("")
            lines.extend(f"   {name}/index" for name in child_indexes)
        if not rst_files and not child_indexes:
            lines.extend(["", "This section currently has no child pages."])

        (folder / "index.rst").write_text("\n".join(lines) + "\n", encoding="utf-8")


def setup(app):
    _autogenerate_folder_indexes()


_configure_digital_twin_namespace_alias()

extensions = [
    "sphinx.ext.autodoc",
    "sphinx.ext.autosummary",
    "sphinx.ext.napoleon",
    "sphinx.ext.mathjax",
    "sphinx.ext.viewcode",
]

autosummary_generate = True
templates_path = ["_templates"]
exclude_patterns = ["_build", "Thumbs.db", ".DS_Store"]
language = "en"

html_theme = "alabaster"
html_static_path = ["_static"]
html_theme_options = {
    "page_width": "1200px",
    "sidebar_width": "280px",
    "fixed_sidebar": True,
}

autodoc_typehints = "description"
master_doc = "index"
