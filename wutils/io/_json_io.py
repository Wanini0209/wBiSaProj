"""Implementation module for _json_io.py."""

import json
from pathlib import Path
from typing import Any


def json_dump(obj: Any, path: str | Path, **kwargs: Any) -> None:
    """
    Serialize a Python object to a JSON file using UTF-8 encoding.

    Parameters
    ----------
    obj : Any
        The Python object to serialize.
    path : str | Path
        The destination file path.
    **kwargs : Any
        Additional keyword arguments passed to ``json.dump`` (e.g., indent,
        sort_keys).

    Returns
    -------
    None
    """
    # Implements Rule-01 (Force UTF-8), Rule-02 (Support str/Path),
    # Rule-03 (Context Manager)
    with open(path, mode="w", encoding="utf-8") as f:
        # Fix: Ensure non-ASCII characters are written as unescaped UTF-8 by default
        # to satisfy TC-DUMP-HAPPY-001. User can still override via kwargs.
        kwargs.setdefault("ensure_ascii", False)
        # Implements Rule-04 (Kwargs propagation), Rule-05 (Propagate TypeError)
        json.dump(obj, f, **kwargs)


def json_load(path: str | Path, **kwargs: Any) -> Any:
    """
    Deserialize a JSON file to a Python object using UTF-8 encoding.

    Parameters
    ----------
    path : str | Path
        The source file path.
    **kwargs : Any
        Additional keyword arguments passed to ``json.load``.

    Returns
    -------
    Any
        The deserialized Python object (usually a dict or list).
    """
    # Implements Rule-06 (Force UTF-8), Rule-07 (Support str/Path),
    # Rule-08 (Context Manager)
    with open(path, encoding="utf-8") as f:
        # Implements Rule-09 (Kwargs propagation)
        return json.load(f, **kwargs)
