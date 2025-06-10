"""
TextDiffStrategy
================
Default fallback diff strategy: performs unified line‑level diff on plain
text content.

If a specific snapshot loader is available for an extension, it is used to
retrieve text; otherwise this strategy attempts to read the file directly
as UTF‑8 (ignoring errors). This guarantees we always have a textual diff
even for unsupported formats.

Design notes
------------
* Always returns True from `supports`, making it the final fallback in the
  strategy chain.
* Produces a DiffResult: `raw` contains unified diff text; `structured`
  remains None (reserved for future rich diff).
"""

from pathlib import Path
import difflib

from .base_strategy import DiffStrategy, DiffResult
from ..snapshot_loaders.loader_registry import LoaderRegistry


class TextDiffStrategy(DiffStrategy):
    """Line‑level text diff, acts as fallback."""

    # ------------------------------------------------------------------ utils
    def _read_text(self, loader, path: str) -> str:
        """
        Try loader.get_text first; if loader is None or fails, read file
        as UTF‑8 best‑effort.
        """
        if loader:
            try:
                return loader.get_text(path)
            except Exception:
                pass  # fallback below
        try:
            return Path(path).read_text(encoding="utf-8", errors="ignore")
        except Exception:
            return ""

    # ------------------------------------------------------- DiffStrategy API
    def supports(self, loader_a, loader_b) -> bool:
        """Always supports; acts as catch‑all strategy."""
        return True

    def diff(self, path_a: str, path_b: str) -> DiffResult:
        """Return unified diff of two text snapshots."""
        ext_a = Path(path_a).suffix
        ext_b = Path(path_b).suffix
        loader_a = LoaderRegistry.get_loader(ext_a)
        loader_b = LoaderRegistry.get_loader(ext_b)

        text_a = self._read_text(loader_a, path_a)
        text_b = self._read_text(loader_b, path_b)

        diff_lines = difflib.unified_diff(
            text_a.splitlines(),
            text_b.splitlines(),
            fromfile=Path(path_a).name,
            tofile=Path(path_b).name,
            lineterm="",
        )
        return DiffResult(raw="\n".join(diff_lines))
