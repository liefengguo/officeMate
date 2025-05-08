

"""
LoaderRegistry
==============

A lightweight registry that maps file extensions to snapshot loader
instances.  Loader plugins register themselves at import time:

    LoaderRegistry.register_loader(".txt", TxtLoader())

SnapshotManager (or any other component) can then retrieve the loader:

    loader = LoaderRegistry.get_loader(".txt")
    if loader:
        text = loader.get_text(file_path)

The registry is case‑insensitive and treats extensions with or without
a leading dot equivalently (".txt" == "txt").

Design goals
------------
* Single responsibility: only manages extension‑>loader mapping.
* Open/Closed: new loaders register themselves without modifying this file.
* Thread‑safe for typical UI usage (single thread); for multi‑threading,
  consider adding locks.
"""

from typing import Dict, Optional
from .base_loader import SnapshotLoader


class LoaderRegistry:
    """Central registry for snapshot loader plugins."""

    _loaders: Dict[str, SnapshotLoader] = {}

    # --------------------------------------------------------------------- API
    @classmethod
    def register_loader(cls, ext: str, loader: SnapshotLoader) -> None:
        """
        Register a loader instance for the given file extension.

        Parameters
        ----------
        ext : str
            File extension, e.g., ".txt" or "txt".  Case‑insensitive.
        loader : SnapshotLoader
            An instance implementing the SnapshotLoader interface.
        """
        if not ext:
            raise ValueError("Extension may not be empty")
        key = cls._normalize_ext(ext)
        cls._loaders[key] = loader

    @classmethod
    def get_loader(cls, ext: str) -> Optional[SnapshotLoader]:
        """
        Retrieve a loader instance for the given extension.

        Returns None if no loader is registered.
        """
        if not ext:
            return None
        key = cls._normalize_ext(ext)
        return cls._loaders.get(key)

    # ------------------------------------------------------------------ helper
    @staticmethod
    def _normalize_ext(ext: str) -> str:
        """
        Normalize extension by stripping leading dot and forcing lower case.
        """
        return ext.lower().lstrip(".")