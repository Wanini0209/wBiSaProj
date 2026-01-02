"""Implementation module for _pickle_io.py."""

import pickle
from pathlib import Path
from typing import Any


def pickle_dump(obj: Any, path: str | Path, **kwargs: Any) -> None:
    """
    Serialize a Python object and write it to the specified file path.

    Parameters
    ----------
    obj : Any
        The Python object to serialize.
    path : str | Path
        Target file path, supporting string or Path objects.
    **kwargs : Any
        Additional arguments passed to pickle.dump (e.g., protocol).

    Returns
    -------
    None

    Raises
    ------
    OSError
        If file creation or writing fails (e.g., permission denied).
    pickle.PickleError
        If the object cannot be pickled.
    TypeError
        If the path type is invalid.
    """
    # Implements Rule-01: Automatic resource management (Context Manager) with 'wb'
    # Implements Rule-02: Polymorphic path support (str/Path handled by open)
    # Implements Rule-03: Argument propagation
    with open(path, "wb") as f:
        pickle.dump(obj, f, **kwargs)


def pickle_load(path: str | Path, **kwargs: Any) -> Any:
    """
    Read and restore a Python object from the specified file path.

    Parameters
    ----------
    path : str | Path
        Source file path, supporting string or Path objects.
    **kwargs : Any
        Additional arguments passed to pickle.load (e.g., encoding).

    Returns
    -------
    Any
        The restored Python object.

    Raises
    ------
    FileNotFoundError
        If the file does not exist.
    OSError
        If the file cannot be opened (e.g., permission denied).
    pickle.PickleError
        If the file content is invalid or corrupted.
    TypeError
        If the path type is invalid.
    """
    # Implements Rule-04: Automatic resource management (Context Manager) with 'rb'
    # Implements Rule-05: Polymorphic path support (str/Path handled by open)
    # Implements Rule-06: Argument propagation
    with open(path, "rb") as f:
        return pickle.load(f, **kwargs)
