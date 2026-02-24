Documentation Structure and Auto Integration
============================================

Folder structure
----------------

- ``docs/theory``: formal models and contracts.
- ``docs/architecture``: component and layer architecture.
- ``docs/engineering``: implementation, metrics, and operations.
- ``docs/performance``: performance-focused navigation.
- ``docs/testing``: test/load-testing navigation.
- ``docs/api``: API references.
- ``docs/structure``: documentation governance.

How to add new documents
------------------------

1. Place a new ``.rst`` file in the appropriate folder.
2. Build docs; folder ``index.rst`` files are auto-generated from discovered ``.rst`` files.
3. Confirm navigation includes the new page.

How auto-integration works
--------------------------

- ``docs/conf.py`` generates/refreshes ``index.rst`` for each docs subfolder at build time.
- Generated indexes include sibling ``.rst`` files and child folder indexes.
- Root ``docs/index.rst`` links only to folder indexes, so new pages appear without manual filename edits.

How to build Sphinx
-------------------

From repository root:

::

    cd docs
    make html

Output is written to ``docs/_build/html``.

How to extend documentation safely
----------------------------------

- Preserve canonical model notation: ``System = (X, E, H, V, 𝓘, 𝓞)``.
- Keep determinism definition consistent with replay requirements.
- Keep event log as source of truth and snapshots as optimization artifacts.
- Avoid introducing architecture features not present in roadmap/blueprint.
