

"""
DiffChunkModel
==============
Qt model that converts paragraph‑level diff chunks (from ParagraphDiffStrategy)
into a 4‑column table:

    旧行号 | 符号 | 新行号 | 文本

A diff chunk dict must contain:
    tag   : "insert" | "delete" | "replace" | "equal"
    a_idx : old paragraph index (or -1)
    b_idx : new paragraph index (or -1)
    a_text / b_text : paragraph strings
"""

from typing import List, Tuple
from PySide6.QtCore import (
    Qt,
    QAbstractTableModel,
    QModelIndex,
    QVariant,
)
from PySide6.QtGui import QColor


class DiffChunkModel(QAbstractTableModel):
    headers = ["旧", "", "新", "内容"]

    def __init__(self, chunks: List[dict], parent=None):
        super().__init__(parent)
        self.rows: List[Tuple[str, str, str, str, str]] = self._prepare_rows(chunks)

    # --------------------------------------------------------- helpers
    @staticmethod
    def _prepare_rows(chunks: List[dict]):
        rows = []
        for ch in chunks:
            tag = ch.get("tag", "equal")
            old_ln = ch["a_idx"] + 1 if ch.get("a_idx", -1) >= 0 else ""
            new_ln = ch["b_idx"] + 1 if ch.get("b_idx", -1) >= 0 else ""
            if tag == "insert":
                sym = "+"
                text = ch.get("b_text", "")
            elif tag == "delete":
                sym = "-"
                text = ch.get("a_text", "")
            elif tag == "replace":
                sym = "~"
                text = ch.get("b_text", "")
            else:
                sym = ""
                text = ch.get("a_text", "")
            rows.append((str(old_ln), sym, str(new_ln), text, tag))
        return rows

    # --------------------------------------------------------- Qt overrides
    def rowCount(self, parent=QModelIndex()):
        return len(self.rows)

    def columnCount(self, parent=QModelIndex()):
        return 4

    def data(self, index: QModelIndex, role=Qt.DisplayRole):
        if not index.isValid():
            return QVariant()

        row_data = self.rows[index.row()]
        col = index.column()
        tag = row_data[4]

        if role == Qt.DisplayRole:
            return row_data[col]

        if role == Qt.BackgroundRole and col == 3:
            if tag == "insert":
                return QColor("#e6ffed")
            if tag == "delete":
                return QColor("#ffeef0")
            if tag == "replace":
                return QColor("#fff5ca")

        if role == Qt.TextAlignmentRole and col != 3:
            return Qt.AlignCenter

        return QVariant()

    def headerData(self, section, orientation, role=Qt.DisplayRole):
        if orientation == Qt.Horizontal and role == Qt.DisplayRole:
            return self.headers[section]
        return QVariant()