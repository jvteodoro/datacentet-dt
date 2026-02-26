from __future__ import annotations

from collections import OrderedDict
from typing import Any


REQUIRED_FIELDS = ("run_id", "transport", "target", "profile", "seed", "git_sha")


def build_manifest(**kwargs: Any) -> OrderedDict[str, Any]:
    ordered = OrderedDict()
    for key in REQUIRED_FIELDS:
        if key not in kwargs:
            raise ValueError(f"missing required field: {key}")
        ordered[key] = kwargs[key]
    for key in sorted(k for k in kwargs.keys() if k not in ordered):
        ordered[key] = kwargs[key]
    return ordered
