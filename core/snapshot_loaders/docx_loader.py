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

from typing import List, Dict, Any
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
            'runs'   : list of run dicts with rich style info

        Run dict example::

            {
                "type": "text",         # or "image" placeholder
                "text": "Hello",
                "font": "Arial",
                "size": 12.0,
                "bold": True,
                "italic": False,
                "underline": False,
            }
        """
        doc = Document(file_path)
        structured: List[Dict[str, Any]] = []

        from docx.text.paragraph import Paragraph
        from docx.table import Table
        from docx.oxml.text.paragraph import CT_P
        from docx.oxml.table import CT_Tbl

        idx = 0
        for element in doc.element.body:
            if isinstance(element, CT_P):
                para = Paragraph(element, doc)
                runs = []
                line_spacing = None
                align_type = None
                numbered = False
                try:
                    ls_val = para.paragraph_format.line_spacing
                    if ls_val is not None:
                        if hasattr(ls_val, 'pt'):
                            line_spacing = float(ls_val.pt)
                        else:
                            line_spacing = float(ls_val)
                except Exception:
                    pass
                try:
                    align_enum = para.paragraph_format.alignment
                    if align_enum is not None:
                        align_type = str(align_enum).split('.')[-1]
                except Exception:
                    pass
                try:
                    if para._p.pPr is not None and para._p.pPr.numPr is not None:
                        numbered = True
                except Exception:
                    pass

                for run in para.runs:
                    # detect drawing (images) within the run
                    has_img = False
                    try:
                        if run._element.xpath('.//pic:pic') or run._element.xpath('.//w:drawing'):
                            has_img = True
                    except Exception:
                        pass
                    if has_img:
                        runs.append({"type": "image"})
                        continue

                    size_val = None
                    color_val = None
                    try:
                        if run.font.size is not None:
                            size_val = float(run.font.size.pt)
                        if run.font.color is not None and run.font.color.rgb is not None:
                            color_val = str(run.font.color.rgb)
                    except Exception:
                        pass

                    runs.append(
                        {
                            "type": "text",
                            "text": run.text,
                            "font": getattr(run.font, "name", None),
                            "size": size_val,
                            "bold": bool(run.bold),
                            "italic": bool(run.italic),
                            "underline": bool(run.underline),
                            "color": color_val,
                        }
                    )

                structured.append(
                    {
                        "index": idx,
                        "text": para.text,
                        "style": para.style.name if para.style else None,
                        "runs": runs,
                        "line_spacing": line_spacing,
                        "alignment": align_type,
                        "numbering": numbered,
                    }
                )
                idx += 1
            elif isinstance(element, CT_Tbl):
                tbl = Table(element, doc)
                rows_data = []
                for row in tbl.rows:
                    cell_texts = []
                    for cell in row.cells:
                        # join all paragraph texts within the cell
                        text = " ".join(p.text for p in cell.paragraphs).strip()
                        cell_texts.append(text)
                    rows_data.append(cell_texts)

                text_lines = [" | ".join(r) for r in rows_data]

                structured.append(
                    {
                        "index": idx,
                        "text": "\n".join(text_lines),
                        "style": None,
                        "runs": [{"type": "table", "rows": rows_data}],
                    }
                )
                idx += 1

        return structured


# --------------------------------------------------------------------------- #
# Auto‑register the loader for .docx extension                                #
# --------------------------------------------------------------------------- #
LoaderRegistry.register_loader(".docx", DocxLoader())
