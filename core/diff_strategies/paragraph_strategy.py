"""
ParagraphDiffStrategy 2.0
=========================
• 段落级 diff（equal / delete / insert / replace）
• "replace" 段生成行内增删列表 inline_ops，用于词/字符级高亮
• 连续 equal 段落 > CONTEXT_LINES*2 折叠为 "skip" 块
"""

from pathlib import Path
from typing import List, Dict
from PyQt5.QtCore import QSettings
import difflib

from .base_strategy import DiffStrategy, DiffResult
from ..snapshot_loaders.loader_registry import LoaderRegistry


CONTEXT_LINES = 3           # 保留前后上下文段落数


class ParagraphDiffStrategy(DiffStrategy):
    """Docx / 富文本 段落级 diff（支持行内变化和折叠）"""

    # ------------------------------------------------ helper
    @staticmethod
    def _paragraph_texts(loader, path: str) -> List[str]:
        """调用 loader.load_structured → 返回带样式 token 的段落文本列表"""
        try:
            struct = loader.load_structured(path)
        except Exception:
            return []
        if not struct:
            return []
        if isinstance(struct[0], str):
            return struct

        settings = QSettings()
        detect_color = settings.value("diff/detect_color", True, type=bool)
        detect_size = settings.value("diff/detect_size", True, type=bool)
        detect_ls = settings.value("diff/detect_line_spacing", True, type=bool)
        detect_media = settings.value("diff/detect_images", True, type=bool)

        texts: List[str] = []
        for p in struct:
            if not isinstance(p, dict):
                texts.append(str(p))
                continue
            runs = p.get("runs")
            parts = []
            ls = p.get("line_spacing")
            if ls is not None and detect_ls:
                parts.append(f"<ls:{ls}/>" )
            align = p.get("alignment")
            if align:
                parts.append(f"<align:{align}/>")
            if p.get("numbering"):
                parts.append("<num/>")
            if not runs:
                parts.append(p.get("text", ""))
                texts.append("".join(parts))
                continue

            for r in runs:
                r_type = r.get("type", "text")
                if r_type == "image":
                    if detect_media:
                        parts.append("<image/>")
                    continue
                if r_type == "table":
                    rows = r.get("rows", [])
                    table_text = "\n".join(" | ".join(row) for row in rows)
                    if detect_media:
                        parts.append(f"<table>{table_text}</table>")
                    else:
                        parts.append(table_text)
                    continue

                txt = r.get("text", "")
                if r.get("bold"):
                    txt = f"<b>{txt}</b>"
                if r.get("italic"):
                    txt = f"<i>{txt}</i>"
                if r.get("underline"):
                    txt = f"<u>{txt}</u>"
                font = r.get("font")
                if font:
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
        """计算段内增删，返回 [tag, a_chunk, b_chunk] 列表"""
        sm = difflib.SequenceMatcher(None, a, b, autojunk=False)
        return [[tag, a[i1:i2], b[j1:j2]]
                for tag, i1, i2, j1, j2 in sm.get_opcodes()]

    # ------------------------------------------------ strategy API
    def supports(self, loader_a, loader_b) -> bool:
        return all(
            hasattr(loader, "load_structured") for loader in (loader_a, loader_b)
        )

    def diff(self, path_a: str, path_b: str) -> DiffResult:
        loader_a = LoaderRegistry.get_loader(Path(path_a).suffix)
        loader_b = LoaderRegistry.get_loader(Path(path_b).suffix)

        para_a = self._paragraph_texts(loader_a, path_a)
        para_b = self._paragraph_texts(loader_b, path_b)

        sm = difflib.SequenceMatcher(None, para_a, para_b, autojunk=False)
        chunks: List[Dict] = []
        raw: List[str] = []

        def add_equal(idx_a: int, idx_b: int):
            text = para_a[idx_a]
            chunks.append({"tag": "equal", "a_idx": idx_a, "b_idx": idx_b,
                           "a_text": text, "b_text": text})
            raw.append(f"  {text}")

        def add_skip(n: int):
            chunks.append({"tag": "skip", "count": n})
            raw.append(f"... {n} unchanged paragraphs ...")

        for tag, i1, i2, j1, j2 in sm.get_opcodes():
            if tag == "equal":
                span = i2 - i1
                if span > CONTEXT_LINES * 2:
                    # 头 N + skip + 尾 N
                    for off in range(CONTEXT_LINES):
                        add_equal(i1 + off, j1 + off)
                    add_skip(span - 2 * CONTEXT_LINES)
                    for off in range(CONTEXT_LINES):
                        add_equal(i2 - CONTEXT_LINES + off,
                                  j2 - CONTEXT_LINES + off)
                else:
                    for off in range(span):
                        add_equal(i1 + off, j1 + off)

            elif tag == "delete":
                for idx in range(i1, i2):
                    text = para_a[idx]
                    chunks.append({"tag": "delete", "a_idx": idx, "b_idx": -1,
                                   "a_text": text, "b_text": ""})
                    raw.append(f"- {text}")

            elif tag == "insert":
                for idx in range(j1, j2):
                    text = para_b[idx]
                    chunks.append({"tag": "insert", "a_idx": -1, "b_idx": idx,
                                   "a_text": "", "b_text": text})
                    raw.append(f"+ {text}")

            elif tag == "replace":
                a_text = "\n".join(para_a[i1:i2])
                b_text = "\n".join(para_b[j1:j2])
                inline = self._inline_ops(a_text, b_text)
                chunks.append({"tag": "replace",
                               "a_idx": i1, "b_idx": j1,
                               "a_text": a_text, "b_text": b_text,
                               "inline": inline})
                raw.append(f"- {a_text}")
                raw.append(f"+ {b_text}")

        return DiffResult("\n".join(raw), structured=chunks)
