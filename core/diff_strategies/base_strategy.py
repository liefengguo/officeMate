"""
Base diff strategy interface and result container
=================================================

Each concrete strategy implements diff() and supports().

DiffResult.raw: plain‑text unified diff for fallback display.
DiffResult.structured: optional rich diff object for advanced UI.
"""

from abc import ABC, abstractmethod
from dataclasses import dataclass
from typing import Any


@dataclass
class DiffResult:
    """Container for diff output."""

    raw: str
    structured: Any | None = None


class DiffStrategy(ABC):
    """Strategy interface for comparing two snapshot files."""

    @abstractmethod
    def supports(self, loader_a, loader_b) -> bool:
        """Return True if this strategy can handle the two loaders."""
        ...

    @abstractmethod
    def diff(self, path_a: str, path_b: str) -> DiffResult:
        """Compute diff and return DiffResult."""
        ...
