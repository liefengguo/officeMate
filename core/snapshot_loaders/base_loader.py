"""
SnapshotLoader
==============

This abstract base class defines a unified interface that every snapshot
loader plugin must implement. Each loader is responsible for reading a
snapshot file of a particular document format (e.g., TXT, DOCX, JSON)
and returning (1) a plain‑text representation for quick viewing / diff,
and (2) an optional structured representation for advanced features such
as structure‑aware diff.

New loaders must inherit from `SnapshotLoader` and implement the two
abstract methods below.

Design notes
------------
* Follows Single‑Responsibility Principle – solely defines the loading
  contract, no business logic.
* Enables Dependency Inversion – SnapshotManager depends on this
  abstraction rather than concrete loaders.
* Open/Closed – adding new formats requires only a new concrete subclass,
  leaving existing code untouched.
"""

from abc import ABC, abstractmethod
from typing import Any


class SnapshotLoader(ABC):
    """Abstract interface for snapshot loader plugins."""

    @abstractmethod
    def get_text(self, file_path: str) -> str:
        """
        Read the snapshot file and return a plain‑text string.

        Parameters
        ----------
        file_path : str
            Absolute path to the snapshot file.

        Returns
        -------
        str
            Plain‑text content suitable for quick preview or text diff.
        """
        raise NotImplementedError

    @abstractmethod
    def load_structured(self, file_path: str) -> Any:
        """
        Read the snapshot file and return a structured representation.

        The exact return type depends on the document format – it could be
        a list of paragraphs, a JSON object, etc. Implementations should
        document their return type.

        Parameters
        ----------
        file_path : str
            Absolute path to the snapshot file.

        Returns
        -------
        Any
            Structured data for advanced processing (e.g., structure‑aware
            diff). Can return `None` if not applicable.
        """
        raise NotImplementedError
