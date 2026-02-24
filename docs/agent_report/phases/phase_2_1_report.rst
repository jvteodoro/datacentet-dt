Phase 2.1 Structural Refactor Report
====================================

1. Phase Overview
-----------------

- **Phase number:** 2.1
- **Date:** 2026-02-24
- **Commit reference (if available):** 2d7ed77
- **Scope:** Structural-efficiency audit/report only (no behavior extension).

2. Structural Changes Introduced
--------------------------------

- **Before (Phase 2 behavior):**

  - A Phase 2 baseline copied multiple state structures at each transition (global-copy pattern), creating :math:`O(|nodes| + |links| + |active\_flows|)` style costs in practice.

- **After (Phase 2.1 behavior):**

  - State is split into structural topology + dynamic flow state.
  - Transition-local metadata is carried in ``TransitionCandidate`` instead of committed state.
  - Flow events use copy-on-write for dynamic structures; topology references are reused on flow transitions.

- **Direct evidence in current code:**

  - Structural split in ``TwinState(topology, link_backlog, active_flows)`` and ``NetworkTopology``. ``src/digital_twin/domain/state.py`` (L13-L30).
  - Transition-local metadata outside committed state via ``TransitionCandidate``. ``src/digital_twin/domain/transition.py`` (L9-L14).
  - Flow events reuse topology and only materialize dynamic copies when needed. ``src/digital_twin/domain/transition.py`` (L31-L33, L107-L149).

3. State Model Refactor
-----------------------

- **NetworkTopology separation:** **Implemented.**

  - ``NetworkTopology`` now owns:

    - ``node_index``
    - ``reverse_node_index``
    - ``adjacency``
    - ``link_capacity``
    - ``link_index``

  - Source: ``src/digital_twin/domain/state.py`` (L13-L20).

- **TwinState explicit field list (current):**

  - ``version_counter``
  - ``event_counter``
  - ``topology``
  - ``link_backlog``
  - ``active_flows``

  - Source: ``src/digital_twin/domain/state.py`` (L22-L30).

- **Immutable vs dynamic components (as implemented):**

  - Structural component: ``topology`` (contains node/link structure data). ``src/digital_twin/domain/state.py`` (L13-L20, L28).
  - Dynamic component: ``link_backlog`` and ``active_flows``. ``src/digital_twin/domain/state.py`` (L29-L30).

4. Copy-On-Write Analysis
-------------------------

- **link_backlog behavior:**

  - ``FlowStarted`` and ``FlowEnded`` set ``backlog = None`` and only allocate ``list(link_backlog)`` on first modified link.
  - Source: ``src/digital_twin/domain/transition.py`` (L107-L113, L135-L141).
  - Converted back to tuple after updates.
  - Source: ``src/digital_twin/domain/transition.py`` (L115-L117, L143-L145).

- **active_flows behavior:**

  - Copied only on flow add/remove paths:

    - ``flow_copy = dict(active_flows)`` then insert in ``FlowStarted``.
    - ``flow_copy = dict(active_flows)`` then delete in ``FlowEnded``.

  - Source: ``src/digital_twin/domain/transition.py`` (L118-L127, L146-L149).

- **Are node_index/adjacency/link_capacity copied per FlowStarted/FlowEnded?**

  - **No.** Flow branches read from ``topology`` and do not execute topology-copy blocks.
  - Source: topology-copy code exists only in ``AddNode``/``AddLink`` blocks. ``src/digital_twin/domain/transition.py`` (L38-L58, L60-L85).

- **Complexity per event (current implementation):**

  - ``FlowStarted`` / ``FlowEnded``:

    - path processing: :math:`O(path\_length)` (loop over path edges).
    - backlog copy once: :math:`O(|links|)` due to ``list(link_backlog)``.
    - active flow dict copy: :math:`O(|active\_flows|)` due to ``dict(active_flows)``.

  - Therefore, strict :math:`O(path\_length)` is **not fully achieved** in current Python structure.

5. Validation Locality
----------------------

- **Modified-entity validation only:** **Yes.**

  - Validator iterates over ``candidate.modified_link_indices`` and ``candidate.modified_flow_ids`` only.
  - Source: ``src/digital_twin/domain/validation.py`` (L18-L35).

- **No global topology scan in validation:** **Yes (in current code).**

  - Capacity lookup is direct index access per modified link.
  - Source: ``src/digital_twin/domain/validation.py`` (L19-L21).

6. Removal of Auxiliary Metadata
--------------------------------

- **Are ``modified_link_indices`` and ``modified_flow_ids`` in committed TwinState?** **No.**

  - ``TwinState`` fields do not contain ``modified_*``.
  - Source: ``src/digital_twin/domain/state.py`` (L22-L30).

- **Where do they exist?**

  - In ``TransitionCandidate`` only (transition-local artifact).
  - Source: ``src/digital_twin/domain/transition.py`` (L9-L14, L158-L162).

- **Commit behavior confirms this separation:**

  - Ingestion commits ``candidate.state`` (state only), not metadata object fields.
  - Source: ``src/digital_twin/domain/twin.py`` (L53-L60).

7. Determinism & Replay Preservation
------------------------------------

- **Replay equality still holds:** **Yes (tested).**

  - Replay test asserts equality of state, snapshot and event log.
  - Source: ``tests/domain/test_deterministic_replay.py`` (L20-L32).

- **Event ordering preserved:** **Yes.**

  - Ingestion pipeline remains normalize :math:`\rightarrow` transition :math:`\rightarrow` validate :math:`\rightarrow` commit.
  - Source: ``src/digital_twin/domain/twin.py`` (L49-L62).

- **Snapshot immutability / no aliasing intent preserved:** **Yes.**

  - Snapshot stores ``link_backlog=tuple(state.link_backlog)``.
  - Source: ``src/digital_twin/domain/snapshot.py`` (L19-L27).

8. Performance Implications
---------------------------

- **Phase 2 vs 2.1 theoretical comparison (from current code):**

  - Phase 2.1 removes topology copies from flow events (improvement).
  - Validation locality is reduced to modified entities only.
  - However, flow events still copy full dynamic containers:

    - ``list(link_backlog)`` => :math:`O(|links|)`
    - ``dict(active_flows)`` => :math:`O(|active\_flows|)`

  - Source: ``src/digital_twin/domain/transition.py`` (L111, L139, L118, L146).

- **Is hyperscale constraint (:math:`O(path\_length)` per flow event) fully satisfied now?**

  - **No (strictly).**
  - Current implementation is structurally improved but still includes dynamic-container full-copy costs.

9. Structural Risk Assessment
-----------------------------

- **SAFE WITH WARNING**

  - SAFE: topology separation, transition-local metadata, deterministic pipeline, local validation.
  - WARNING: strict :math:`O(path\_length)` target is not fully met because of dynamic container copies per flow event.

10. Phase Gate Decision
-----------------------

- **Passed with warnings**

  - Structural refactor goals are substantially implemented.
  - Remaining warning is strict asymptotic cost on dynamic copies for flow events.


Mandatory Analysis Questions (Explicit Answers)
------------------------------------------------

1. **Is full state copy per event eliminated?**

   - **Partially.** Topology full-copy on flow events was eliminated; dynamic full copies still occur.

2. **Is topology structurally separated from dynamic state?**

   - **Yes.**

3. **Are node_index, adjacency, link_capacity no longer copied per FlowStarted/FlowEnded?**

   - **Yes.**

4. **Is link_backlog copy-on-write?**

   - **Yes, but whole-container copy on first write.**

5. **Is active_flows copy-on-write?**

   - **Yes, with whole-dict copy on add/remove.**

6. **Are modified_link_indices and modified_flow_ids removed from committed TwinState?**

   - **Yes.**

7. **Does replay equality still hold?**

   - **Yes (per test evidence).**

8. **Is per-event complexity now O(path_length)?**

   - **No, not strictly, due to full dynamic container copies in flow events.**
