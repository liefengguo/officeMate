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
from PyQt5.QtWidgets import QSplitter, QTextBrowser, QWidget, QVBoxLayout, QLabel

from core.platform_utils import is_dark_mode
_IS_DARK = is_dark_mode()

class ParallelDiffView(QSplitter):
    def __init__(self, left_title: str = "", right_title: str = "", parent=None):
        super().__init__(Qt.Horizontal, parent)

        # 左右容器：标题 QLabel + QTextBrowser
        left_tb  = QTextBrowser()
        right_tb = QTextBrowser()

        # 统一 TextBrowser 外观
        for tb in (left_tb, right_tb):
            tb.setReadOnly(True)
            tb.setOpenExternalLinks(False)
            tb.setFont(QFont("Menlo, Courier New, monospace", 10))
            tb.setStyleSheet("border: none;")  # 外部面板有边框即可

        # --- 组装左侧 ---
        left_container = QWidget()
        left_layout = QVBoxLayout(left_container)
        left_layout.setContentsMargins(0, 0, 0, 0)
        self.left_title_lbl = QLabel(left_title)
        self.left_title_lbl.setStyleSheet("font-weight:bold; padding:4px 2px;")
        left_layout.addWidget(self.left_title_lbl)
        left_layout.addWidget(left_tb)

        # --- 组装右侧 ---
        right_container = QWidget()
        right_layout = QVBoxLayout(right_container)
        right_layout.setContentsMargins(0, 0, 0, 0)
        self.right_title_lbl = QLabel(right_title)
        self.right_title_lbl.setStyleSheet("font-weight:bold; padding:4px 2px;")
        right_layout.addWidget(self.right_title_lbl)
        right_layout.addWidget(right_tb)

        # 将两侧容器加入 splitter
        self.addWidget(left_container)
        self.addWidget(right_container)

        # 对外暴露的 QTextBrowser 引用（保持旧接口兼容）
        self.left  = left_tb
        self.right = right_tb

        # 滚动同步
        self._lock = False
        self.left.verticalScrollBar().valueChanged.connect(self._sync_left)
        self.right.verticalScrollBar().valueChanged.connect(self._sync_right)

    # ---------------------------------------------------------------- public
    def set_titles(self, left_title: str, right_title: str):
        """Update header labels shown above the diff panes."""
        self.left_title_lbl.setText(left_title)
        self.right_title_lbl.setText(right_title)

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
                    style = (
                        "background:#ffd8d8; color:#000000; text-decoration:line-through;"
                        if not _IS_DARK
                        else "background:#4d1a1a; color:#bf7a7a; text-decoration:line-through;"
                    )
                    html_parts.append(f'<span style="{style}">{escape(a_chunk)}</span>')
            elif tag == "insert":
                if side == "b":
                    style = (
                        "background:#d7ffd7; color:#000000;"
                        if not _IS_DARK
                        else "background:#0d3a18; color:#7abf7a;"
                    )
                    html_parts.append(f'<span style="{style}">{escape(b_chunk)}</span>')
            elif tag == "replace":
                # 不会出现 (SequenceMatcher 不会产出 replace op 内层)
                pass
        return "".join(html_parts) or "&nbsp;"

    # ---------------------------------------------------------------- main API
    def load_chunks(self, chunks: List[Dict]):
        """渲染左右 HTML，带行号和符号"""
        left_lines, right_lines = [], []
        old_idx, new_idx = 1, 1        # 行号计数

        def ln_html(n):    # 行号灰色
            return f'<span class="ln">{n:>4}</span> '

        def sym_html(sym):
            color = {"-":"#ff3b30", "+":"#34c759", "~":"#ff9500"}.get(sym, "#888")
            return f'<span class="sym" style="color:{color}">{sym}</span> '

        for ch in chunks:
            tag = ch["tag"]

            if tag == "equal":
                text = escape(ch["a_text"] or "")
                left_lines.append(ln_html(old_idx) + "&nbsp;" + text)
                right_lines.append(ln_html(new_idx) + "&nbsp;" + text)
                old_idx += 1
                new_idx += 1

            elif tag == "delete":
                style = (
                    "background:#ffd8d8; color:#000000; text-decoration:line-through;"
                    if not _IS_DARK
                    else "background:#4d1a1a; color:#bf7a7a; text-decoration:line-through;"
                )
                span = f'<span style="{style}">{escape(ch["a_text"])}</span>'
                left_lines.append(ln_html(old_idx) + sym_html("-") + span)
                right_lines.append(ln_html("") + "&nbsp;")
                old_idx += 1

            elif tag == "insert":
                style = (
                    "background:#d7ffd7; color:#000000;"
                    if not _IS_DARK
                    else "background:#0d3a18; color:#7abf7a;"
                )
                span = f'<span style="{style}">{escape(ch["b_text"])}</span>'
                left_lines.append(ln_html("") + "&nbsp;")
                right_lines.append(ln_html(new_idx) + sym_html("+") + span)
                new_idx += 1

            elif tag == "replace":
                # 行内高亮
                inline = ch.get("inline", [])
                left_html = self._render_inline(inline, "a")
                right_html = self._render_inline(inline, "b")
                left_lines.append(ln_html(old_idx) + sym_html("~") + left_html)
                right_lines.append(ln_html(new_idx) + sym_html("~") + right_html)
                old_idx += 1
                new_idx += 1

            elif tag == "skip":
                skip_html = (f'<span class="skip">… {ch["count"]} unchanged '
                                f'paragraphs …</span>')
                left_lines.append(skip_html)
                right_lines.append(skip_html)

        self.left.setHtml("<br>".join(left_lines))
        self.right.setHtml("<br>".join(right_lines))