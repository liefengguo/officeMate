"""
TxtLoader
=========

A simple snapshot loader plugin that handles plain‑text files
(`.txt`).  It implements the SnapshotLoader interface defined
in `base_loader.py` and registers itself with LoaderRegistry
so that SnapshotManager can retrieve it by extension.

This loader is deliberately minimal: it opens the file in UTF‑8
(mode "r") and returns content as either a full string (get_text)
or a list of lines (load_structured).  Real‑world usage might add
encoding detection or configurable fallback encodings.
"""

from .base_loader import SnapshotLoader
from .loader_registry import LoaderRegistry


class TxtLoader(SnapshotLoader):
    """Loader for plain‑text snapshot files (.txt)."""

    def get_text(self, file_path: str) -> str:
        """Return the entire text content of the file."""
        with open(file_path, "r", encoding="utf-8", errors="ignore") as fp:
            return fp.read()

    def load_structured(self, file_path: str):
        """Return a list of lines for structure‑aware operations."""
        with open(file_path, "r", encoding="utf-8", errors="ignore") as fp:
            return [line.rstrip("\n") for line in fp.readlines()]


# --------------------------------------------------------------------------- #
# Register the loader for .txt extension                                      #
# --------------------------------------------------------------------------- #
LoaderRegistry.register_loader(".txt", TxtLoader())
