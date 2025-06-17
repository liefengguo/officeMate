

"""
ParagraphDiffTableView
======================
A QTableView‑based widget that renders paragraph‑level diff chunks.
It shows old line number, diff symbol (+/‑/~), new line number,
and the paragraph text with background colours controlled by QSS.

Usage:
    view = ParagraphDiffTableView(diff_chunks)
    layout.addWidget(view)

The expected `diff_chunks` format comes from ParagraphDiffStrategy:
    [
        {"tag":"insert",  "a_idx":-1, "b_idx":12, "a_text":"",   "b_text":"New paragraph"},
        {"tag":"delete",  "a_idx": 8, "b_idx":-1, "a_text":"Old","b_text":""},
        ...
    ]
"""

from typing import List, Tuple
from PySide6.QtWidgets import (
    QTableView,
    QStyledItemDelegate,
    QHeaderView,
    QAbstractItemView,
)
from PySide6.QtCore import Qt, QAbstractTableModel, QModelIndex, QVariant
from PySide6.QtGui import QColor, QFont, QPainter


# ------------------------------------------------------------------ Delegate
class DiffSymbolDelegate(QStyledItemDelegate):
    """Paint + / - / ~ symbols with colours similar to git diff."""

    def paint(self, painter: QPainter, option, index):
        symbol = index.data(Qt.DisplayRole)
        painter.save()

        if symbol == "+":
            painter.setPen(QColor("#34c759"))
        elif symbol == "-":
            painter.setPen(QColor("#ff3b30"))
        elif symbol == "~":
            painter.setPen(QColor("#ff9500"))
        else:
            painter.setPen(option.palette.color(option.palette.Text))

        painter.drawText(option.rect, Qt.AlignCenter, symbol)
        painter.restore()


# --------------------------------------------------------------------- Model
class DiffChunkModel(QAbstractTableModel):
    headers = ["旧", "", "新", "内容"]

    def __init__(self, chunks: List[dict], parent=None):
        super().__init__(parent)
        self.rows: List[Tuple[str, str, str, str, str]] = self._prepare_rows(chunks)

    # Build rows as tuples: (old_line, symbol, new_line, text, tag)
    @staticmethod
    def _prepare_rows(chunks: List[dict]):
        rows = []
        for ch in chunks:
            tag = ch.get("tag", "equal")
            old_ln = ch["a_idx"] + 1 if ch["a_idx"] >= 0 else ""
            new_ln = ch["b_idx"] + 1 if ch["b_idx"] >= 0 else ""
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

    # ------------------------------ Qt model implementation
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


# ------------------------------------------------------------------ View
class ParagraphDiffTableView(QTableView):
    """Table view wrapper ready to embed in diff pages."""

    def __init__(self, chunks: List[dict], parent=None):
        super().__init__(parent)

        self.setModel(DiffChunkModel(chunks, self))
        self._setup_view()

    def _setup_view(self):
        self.verticalHeader().setVisible(False)
        hdr = self.horizontalHeader()
        hdr.setSectionResizeMode(0, QHeaderView.ResizeToContents)
        hdr.setSectionResizeMode(1, QHeaderView.ResizeToContents)
        hdr.setSectionResizeMode(2, QHeaderView.ResizeToContents)
        hdr.setSectionResizeMode(3, QHeaderView.Stretch)

        # symbol delegate for column 1
        self.setItemDelegateForColumn(1, DiffSymbolDelegate())

        self.setWordWrap(True)
        self.setAlternatingRowColors(False)
        self.setEditTriggers(QAbstractItemView.NoEditTriggers)
        self.setSelectionMode(QAbstractItemView.NoSelection)
        self.setShowGrid(False)

        font = QFont("Menlo, Courier New, monospace")
        font.setPointSize(10)
        self.setFont(font)