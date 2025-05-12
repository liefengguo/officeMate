"""
ParagraphDiffViewer
===================
A simple Qt widget that renders paragraph‑level diff results produced by
ParagraphDiffStrategy.

Usage
-----
    viewer = ParagraphDiffViewer(diff_chunks)  # diff_chunks = DiffResult.structured
    layout.addWidget(viewer)

Each chunk dict requires keys:
    tag  : "equal" | "insert" | "delete" | "replace"
    a_text / b_text : paragraph text (old/new)

Visual styling is controlled via QSS: the widget sets objectName "para"
and a dynamic property "state" (insert/delete/replace/equal) which can
be styled like:

    QLabel#para[state="insert"]  { background:#e6ffed; border-left:4px solid #34c759; }
    QLabel#para[state="delete"]  { background:#ffeef0; border-left:4px solid #ff3b30; }
    QLabel#para[state="replace"] { background:#fff5ca; border-left:4px solid #ff9500; }

"""

from typing import List, Dict
from PyQt5.QtWidgets import (
    QScrollArea,
    QWidget,
    QVBoxLayout,
    QLabel,
)
from PyQt5.QtGui import QFont, QTextOption
from PyQt5.QtCore import Qt


class ParagraphDiffViewer(QScrollArea):
    """Scrollable widget showing paragraph diff chunks."""

    def __init__(self, chunks: List[Dict], parent=None):
        super().__init__(parent)
        self.setWidgetResizable(True)

        container = QWidget()
        vbox = QVBoxLayout(container)
        vbox.setSpacing(6)
        vbox.setContentsMargins(8, 8, 8, 8)

        font = QFont("Menlo, Courier New, monospace")
        font.setPointSize(10)

        for chunk in chunks:
            tag = chunk.get("tag", "equal")
            text = {
                "insert": chunk.get("b_text", ""),
                "delete": chunk.get("a_text", ""),
                "replace": chunk.get("b_text", ""),
                "equal": chunk.get("a_text", ""),
            }.get(tag, "")

            label = QLabel(text)
            label.setWordWrap(True)
            label.setFont(font)
            label.setTextInteractionFlags(Qt.TextSelectableByMouse)
            label.setObjectName("para")
            label.setProperty("state", tag)
            vbox.addWidget(label)

            # add spacing line for readability except last
            vbox.addSpacing(2)

        vbox.addStretch(1)
        self.setWidget(container)
