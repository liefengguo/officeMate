

"""
ParagraphDiffStrategy
=====================
Structure‑aware diff strategy operating on **paragraph lists** extracted
by SnapshotLoader implementations (e.g., DocxLoader).

A loader is considered paragraph‑aware if it implements
`load_structured()` and returns an **ordered list** where the `.text`
field (or the item itself if it is str) represents the paragraph text.

This strategy:
1. Calls `loader.load_structured()` to obtain paragraph sequences for
   both snapshots.
2. Uses `difflib.SequenceMatcher` on the *text* sequence to compute
   opcodes (equal / insert / delete / replace).
3. Builds a human‑readable unified diff (paragraph‑level) for fallback
   display (`DiffResult.raw`).
4. Builds a machine‑readable list of diff chunks (`DiffResult.structured`)
   each with:
        {
            "tag": "equal|insert|delete|replace",
            "a_idx": index in old snapshot or -1,
            "b_idx": index in new snapshot or -1,
            "a_text": old paragraph text,
            "b_text": new paragraph text
        }
   This will later be consumed by UI for coloured rendering.

If either loader lacks `load_structured`, `supports()` returns False so
that DiffEngine falls back to TextDiffStrategy.

Author: DocSnap team
"""

from pathlib import Path
from typing import List, Dict
import difflib

from .base_strategy import DiffStrategy, DiffResult
from ..snapshot_loaders.loader_registry import LoaderRegistry


class ParagraphDiffStrategy(DiffStrategy):
    """Docx paragraph‑level diff."""

    # ---------------------------------------------------- helper: extract list
    def _paragraph_texts(self, loader, path: str) -> List[str]:
        """Return list of paragraph strings using loader.load_structured()."""
        try:
            struct = loader.load_structured(path)
        except Exception:
            return []

        if not struct:
            return []

        # Accept either list[str] or list[dict] with 'text' key
        if isinstance(struct[0], str):
            return struct
        try:
            return [para["text"] for para in struct]
        except Exception:
            # Fallback: best‑effort str() on each element
            return [str(p) for p in struct]

    # ------------------------------------------------------- DiffStrategy API
    def supports(self, loader_a, loader_b) -> bool:
        """Support if both loaders implement load_structured()."""
        return all(
            hasattr(loader, "load_structured") and callable(getattr(loader, "load_structured"))
            for loader in (loader_a, loader_b)
        )

    def diff(self, path_a: str, path_b: str) -> DiffResult:
        """Return paragraph‑level DiffResult (raw + structured)."""
        loader_a = LoaderRegistry.get_loader(Path(path_a).suffix)
        loader_b = LoaderRegistry.get_loader(Path(path_b).suffix)

        para_a = self._paragraph_texts(loader_a, path_a)
        para_b = self._paragraph_texts(loader_b, path_b)

        sm = difflib.SequenceMatcher(None, para_a, para_b, autojunk=False)
        chunks: List[Dict] = []
        raw_lines: List[str] = []

        for tag, i1, i2, j1, j2 in sm.get_opcodes():
            if tag == "equal":
                for idx in range(i1, i2):
                    raw_lines.append(f"  {para_a[idx]}")
                chunks.append(
                    {"tag": "equal", "a_idx": i1, "b_idx": j1, "a_text": "\n".join(para_a[i1:i2]),
                     "b_text": "\n".join(para_b[j1:j2])}
                )
            elif tag == "delete":
                for idx in range(i1, i2):
                    raw_lines.append(f"- {para_a[idx]}")
                    chunks.append({"tag": "delete", "a_idx": idx, "b_idx": -1,
                                   "a_text": para_a[idx], "b_text": ""})
            elif tag == "insert":
                for idx in range(j1, j2):
                    raw_lines.append(f"+ {para_b[idx]}")
                    chunks.append({"tag": "insert", "a_idx": -1, "b_idx": idx,
                                   "a_text": "", "b_text": para_b[idx]})
            elif tag == "replace":
                # mark old paragraphs
                for idx in range(i1, i2):
                    raw_lines.append(f"- {para_a[idx]}")
                # mark new paragraphs
                for idx in range(j1, j2):
                    raw_lines.append(f"+ {para_b[idx]}")
                chunks.append(
                    {"tag": "replace",
                     "a_idx": i1, "b_idx": j1,
                     "a_text": "\n".join(para_a[i1:i2]),
                     "b_text": "\n".join(para_b[j1:j2])}
                )

        return DiffResult(raw="\n".join(raw_lines), structured=chunks)