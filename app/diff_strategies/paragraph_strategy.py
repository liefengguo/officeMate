# core/diff_strategies/paragraph_strategy.py
"""
ParagraphDiffStrategy 2.0
-------------------------
* 段落级 diff
* 行内增删词高亮 (inline ops)
* 折叠连续 equal 段落为 skip 块
"""

from pathlib import Path
from typing import List, Dict
import re
from PyQt5.QtCore import QSettings
from core.i18n import _
import difflib

from .base_strategy import DiffStrategy, DiffResult
from ..snapshot_loaders.loader_registry import LoaderRegistry


CONTEXT_LINES = 3           # 折叠时保留上下文行数


class ParagraphDiffStrategy(DiffStrategy):

    # ------------------------- helpers
    _TAG_RE = re.compile(r"<[^>]+>")

    @classmethod
    def _plain(cls, text: str) -> str:
        """Remove markup tags used for styling comparison."""
        return cls._TAG_RE.sub("", text)
    @staticmethod
    def _paragraph_texts(loader, path: str) -> List[str]:
        struct = loader.load_structured(path)
        if not struct:
            return []
        if isinstance(struct[0], str):
            return struct
        settings = QSettings()
        detect_bold = settings.value("diff/detect_bold", True, type=bool)
        detect_italic = settings.value("diff/detect_italic", True, type=bool)
        detect_underline = settings.value("diff/detect_underline", True, type=bool)
        detect_font = settings.value("diff/detect_font", True, type=bool)
        detect_color = settings.value("diff/detect_color", True, type=bool)
        detect_size = settings.value("diff/detect_size", True, type=bool)
        detect_ls = settings.value("diff/detect_line_spacing", True, type=bool)
        detect_align = settings.value("diff/detect_alignment", True, type=bool)
        detect_num = settings.value("diff/detect_numbering", True, type=bool)
        detect_img = settings.value("diff/detect_images", True, type=bool)
        detect_table = settings.value("diff/detect_tables", True, type=bool)

        texts: List[str] = []
        for p in struct:
            if not isinstance(p, dict):
                texts.append(str(p))
                continue
            runs = p.get("runs")
            parts = []
            ls = p.get("line_spacing")
            if ls is not None and detect_ls:
                parts.append(f"<ls:{ls}/>")
            align = p.get("alignment")
            if align and detect_align:
                parts.append(f"<align:{align}/>")
            if p.get("numbering") and detect_num:
                parts.append("<num/>")
            if not runs:
                parts.append(p.get("text", ""))
                texts.append("".join(parts))
                continue

            for r in runs:
                r_type = r.get("type", "text")
                if r_type == "image":
                    if detect_img:
                        parts.append("<image/>")
                    continue
                if r_type == "table":
                    rows = r.get("rows", [])
                    table_text = "\n".join(" | ".join(row) for row in rows)
                    if detect_table:
                        parts.append(f"<table>{table_text}</table>")
                    else:
                        parts.append(table_text)
                    continue

                txt = r.get("text", "")
                if r.get("bold") and detect_bold:
                    txt = f"<b>{txt}</b>"
                if r.get("italic") and detect_italic:
                    txt = f"<i>{txt}</i>"
                if r.get("underline") and detect_underline:
                    txt = f"<u>{txt}</u>"
                font = r.get("font")
                if font and detect_font:
                    txt = f"<font:{font}>{txt}</font>"
                size = r.get("size")
                if size is not None and detect_size:
                    txt = f"<size:{size}>{txt}</size>"
                color = r.get("color")
                if color and detect_color:
                    txt = f"<color:{color}>{txt}</color>"
                parts.append(txt)

            texts.append("".join(parts))
        return texts

    @staticmethod
    def _inline_ops(a: str, b: str):
        """Return list[tag, a_chunk, b_chunk] for replace lines."""
        sm = difflib.SequenceMatcher(None, a, b, autojunk=False)
        ops = []
        for tag, i1, i2, j1, j2 in sm.get_opcodes():
            ops.append([tag, a[i1:i2], b[j1:j2]])
        return ops

    # ------------------------- DiffStrategy API
    def supports(self, loader_a, loader_b) -> bool:
        return all(
            hasattr(loader, "load_structured") for loader in (loader_a, loader_b)
        )

    def diff(self, path_a: str, path_b: str) -> DiffResult:
        loader_a = LoaderRegistry.get_loader(Path(path_a).suffix)
        loader_b = LoaderRegistry.get_loader(Path(path_b).suffix)

        para_a = self._paragraph_texts(loader_a, path_a)
        para_b = self._paragraph_texts(loader_b, path_b)

        plain_a = [self._plain(t) for t in para_a]
        plain_b = [self._plain(t) for t in para_b]

        sm = difflib.SequenceMatcher(None, plain_a, plain_b, autojunk=False)
        if (len(para_a) + len(para_b) > 200) and sm.quick_ratio() < 0.3:
            a_text = "\n".join(para_a)
            b_text = "\n".join(para_b)
            inline = self._inline_ops(a_text, b_text)
            chunks = [{
                "tag": "replace",
                "a_idx": 0,
                "b_idx": 0,
                "a_text": a_text,
                "b_text": b_text,
                "inline": inline,
            }]
            raw_lines = [f"- {a_text}", f"+ {b_text}"]
            return DiffResult("\n".join(raw_lines), structured=chunks)

        chunks: List[Dict] = []
        raw_lines: List[str] = []

        def add_skip(count: int):
            chunks.append({"tag": "skip", "count": count})
            raw_lines.append(_("... {count} 段未变 ...").format(count=count))

        for tag, i1, i2, j1, j2 in sm.get_opcodes():
            if tag == "equal":
                span_len = i2 - i1
                if span_len > 2 * CONTEXT_LINES:
                    # 保留首尾 context，折叠中间
                    head = range(i1, i1 + CONTEXT_LINES)
                    tail = range(i2 - CONTEXT_LINES, i2)
                    for idx in head:
                        chunks.append({"tag": "equal",
                                       "a_idx": idx, "b_idx": j1 + (idx - i1),
                                       "a_text": para_a[idx],
                                       "b_text": para_b[j1 + (idx - i1)]})
                        raw_lines.append(f"  {para_a[idx]}")
                    add_skip(span_len - 2 * CONTEXT_LINES)
                    for idx in tail:
                        chunks.append({"tag": "equal",
                                       "a_idx": idx, "b_idx": j1 + (idx - i1),
                                       "a_text": para_a[idx],
                                       "b_text": para_b[j1 + (idx - i1)]})
                        raw_lines.append(f"  {para_a[idx]}")
                else:
                    for idx in range(i1, i2):
                        chunks.append({"tag": "equal",
                                       "a_idx": idx, "b_idx": j1 + (idx - i1),
                                       "a_text": para_a[idx],
                                       "b_text": para_b[j1 + (idx - i1)]})
                        raw_lines.append(f"  {para_a[idx]}")

            elif tag == "delete":
                for idx in range(i1, i2):
                    chunks.append({"tag": "delete",
                                   "a_idx": idx, "b_idx": -1,
                                   "a_text": para_a[idx], "b_text": ""})
                    raw_lines.append(f"- {para_a[idx]}")

            elif tag == "insert":
                for idx in range(j1, j2):
                    chunks.append({"tag": "insert",
                                   "a_idx": -1, "b_idx": idx,
                                   "a_text": "", "b_text": para_b[idx]})
                    raw_lines.append(f"+ {para_b[idx]}")

            elif tag == "replace":
                a_text = "\n".join(para_a[i1:i2])
                b_text = "\n".join(para_b[j1:j2])
                inline = self._inline_ops(a_text, b_text)
                chunks.append({"tag": "replace",
                               "a_idx": i1, "b_idx": j1,
                               "a_text": a_text, "b_text": b_text,
                               "inline": inline})
                raw_lines.append(f"- {a_text}")
                raw_lines.append(f"+ {b_text}")

        return DiffResult("\n".join(raw_lines), structured=chunks)
