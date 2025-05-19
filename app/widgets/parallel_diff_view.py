"""
parallel_diff_view.py
=====================

左右分栏「修改前 / 修改后」对照视图。
左栏显示旧版本文本，右栏显示新版本文本；行内增删用
<span class="del"> </span> / <span class="ins"> </span> 高亮。
滚动条同步，支持折叠 "skip" 占位行。

依赖:
    • diff.qss 中需含 .ins / .del / .skip 样式
"""

from typing import List, Dict
from html import escape

from PyQt5.QtCore import Qt
from PyQt5.QtGui import QFont
from PyQt5.QtWidgets import QSplitter, QTextBrowser


class ParallelDiffView(QSplitter):
    def __init__(self, parent=None):
        super().__init__(Qt.Horizontal, parent)

        # 左旧版本
        self.left = QTextBrowser()
        self.right = QTextBrowser()

        for tb in (self.left, self.right):
            tb.setReadOnly(True)
            tb.setOpenExternalLinks(False)
            tb.setFont(QFont("Menlo, Courier New, monospace", 10))
            tb.setStyleSheet("border: none;")  # 外部面板有边框即可
            self.addWidget(tb)

        # 滚动同步
        self._lock = False
        self.left.verticalScrollBar().valueChanged.connect(self._sync_left)
        self.right.verticalScrollBar().valueChanged.connect(self._sync_right)

    # ---------------------------------------------------------------- helpers
    def _sync_left(self, value):
        if self._lock:
            return
        self._lock = True
        self.right.verticalScrollBar().setValue(value)
        self._lock = False

    def _sync_right(self, value):
        if self._lock:
            return
        self._lock = True
        self.left.verticalScrollBar().setValue(value)
        self._lock = False

    @staticmethod
    def _render_inline(inline_ops: List[List[str]], side: str) -> str:
        """
        inline_ops: [["equal","foo","foo"],["delete","bar",""],["insert","","baz"]]
        side: "a" (old) or "b" (new)
        """
        html_parts = []
        for tag, a_chunk, b_chunk in inline_ops:
            if tag == "equal":
                html_parts.append(escape(a_chunk))
            elif tag == "delete":
                if side == "a":
                    # html_parts.append(f'<span class="del">{escape(a_chunk)}</span>')
                    html_parts.append(
                        f'<span style="background:#ffeef0; text-decoration:line-through;">'
                        f'{escape(a_chunk)}</span>')
            elif tag == "insert":
                if side == "b":
                    # html_parts.append(f'<span class="ins">{escape(b_chunk)}</span>')
                    html_parts.append(
                        f'<span style="background:#e6ffed;">{escape(b_chunk)}</span>')
            elif tag == "replace":
                # 不会出现 (SequenceMatcher 不会产出 replace op 内层)
                pass
        return "".join(html_parts) or "&nbsp;"

    # ---------------------------------------------------------------- main API
    def load_chunks(self, chunks: List[Dict]):
        """
        把 paragraph_strategy 生成的 diff chunks 渲染到左右 QTextBrowser
        """
        left_lines = []
        sym_lines  = []
        right_lines = []
        row = 1

        def _add_line(sym, left_html, right_html):
            nonlocal row
            ln_html = f'<span class="ln">{row}</span>'
            # sym_html = f'<span class="sym">{sym}</span>'
            color = {"+" : "#34c759", "−": "#ff3b30", "~": "#ff9500"}.get(sym, "#888")
            sym_html = f'<span style="color:{color}; font-weight:bold;">{sym}</span>'
            left_lines.append(f"{ln_html}{sym_html}{left_html}")
            right_lines.append(f"{ln_html}{sym_html}{right_html}")
            row += 1

        for ch in chunks:
            tag = ch.get("tag")
            if tag == "equal":
                html = escape(ch.get("a_text", "")) or "&nbsp;"
                _add_line(" ", html, html)

            elif tag == "insert":
                # new = f'<span class="ins">{escape(ch.get("b_text",""))}</span>' or "&nbsp;"
                new = f'<span style="background:#e6ffed;">{escape(ch.get("b_text",""))}</span>'
                _add_line("+", "&nbsp;", new)

            elif tag == "delete":
                # old = f'<span class="del">{escape(ch.get("a_text",""))}</span>' or "&nbsp;"
                old = f'<span style="background:#ffeef0; text-decoration:line-through;">{escape(ch.get("a_text",""))}</span>'
                _add_line("−", old, "&nbsp;")

            elif tag == "replace":
                inline = ch.get("inline", [])
                old_html = self._render_inline(inline, "a")
                new_html = self._render_inline(inline, "b")
                _add_line("~", old_html, new_html)

            elif tag == "skip":
                count = ch.get("count", 0)
                skip_html = f'<span class="skip">… {count} unchanged …</span>'
                _add_line(" ", skip_html, skip_html)

        # 拼接成 <div> list
        left_html_doc = "<br>".join(left_lines)
        right_html_doc = "<br>".join(right_lines)
    
        self.left.setHtml(left_html_doc)
        self.right.setHtml(right_html_doc)