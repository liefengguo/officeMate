"""
DocxLoader
==========

Snapshot loader plugin for Microsoft Word documents (.docx).

Uses `python-docx` to extract text and paragraph structure.  Registering
itself with LoaderRegistry enables SnapshotManager to automatically load
.docx snapshots via plugin architecture.

Note: Ensure `python-docx` is installed:
    pip install python-docx
"""

from __future__ import annotations

from typing import List
from pathlib import Path

try:
    from docx import Document
except ModuleNotFoundError as exc:  # pillow dependency missing?
    raise ImportError(
        "The 'python-docx' package is required for DocxLoader. "
        "Install it with: pip install python-docx"
    ) from exc

from .base_loader import SnapshotLoader
from .loader_registry import LoaderRegistry


class DocxLoader(SnapshotLoader):
    """Loader for .docx snapshot files."""

    def get_text(self, file_path: str) -> str:
        """Return concatenated text of all paragraphs."""
        doc = Document(file_path)
        paragraphs: List[str] = [para.text for para in doc.paragraphs]
        return "\n".join(paragraphs)

    def load_structured(self, file_path: str):
        """
        Return a list of paragraph dicts for structure-aware diff.

        Each dict contains:
            'text'   : paragraph text
            'style'  : style name (if any)
            'index'  : paragraph index (0-based)
        """
        doc = Document(file_path)
        structured = []
        for idx, para in enumerate(doc.paragraphs):
            structured.append(
                {
                    "index": idx,
                    "text": para.text,
                    "style": para.style.name if para.style else None,
                }
            )
        return structured


# --------------------------------------------------------------------------- #
# Auto‑register the loader for .docx extension                                #
# --------------------------------------------------------------------------- #
LoaderRegistry.register_loader(".docx", DocxLoader())
