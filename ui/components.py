

"""
ui.components
~~~~~~~~~~~~~

A small library of shared UI widgets with *no hard‑coded colors*.
Visual appearance is controlled exclusively by QSS using
  • QPushButton[type="primary" | "flat"]
  • QWidget[role="sidebar" | "toolbar"]
  • QSplitter::handle

Widgets
-------
PrimaryButton  – filled accent button for primary actions
FlatButton     – borderless text button for secondary actions
ThinSplitter   – 1‑px handle splitter (horizontal / vertical)

All widgets attempt to follow macOS / modern design conventions
while remaining cross‑platform.
"""

from __future__ import annotations

from typing import Optional

from PyQt5.QtCore import Qt
from PyQt5.QtWidgets import (
    QPushButton,
    QSplitter,
    QSplitterHandle,
)


# ------------------------------------------------------------------ Buttons
class PrimaryButton(QPushButton):
    """Round‑cornered primary button with 'type=primary' property."""

    def __init__(self, text: str = "", parent=None, *, icon=None):
        super().__init__(text, parent)
        self.setProperty("type", "primary")  # picked up by QSS
        if icon is not None:
            self.setIcon(icon)
        # Ensure focus outline is consistent
        self.setFocusPolicy(Qt.StrongFocus)


class FlatButton(QPushButton):
    """
    Borderless flat button – typically used for secondary actions
    such as 'Cancel'. Controlled by 'type=flat'.
    """

    def __init__(self, text: str = "", parent=None, *, icon=None):
        super().__init__(text, parent)
        self.setProperty("type", "flat")
        if icon is not None:
            self.setIcon(icon)
        self.setFocusPolicy(Qt.StrongFocus)


# ------------------------------------------------------------- Thin Splitter
class _OnePixelHandle(QSplitterHandle):
    """Custom splitter handle enforcing 1‑px thickness."""

    def __init__(self, orientation: Qt.Orientation, parent: "ThinSplitter"):
        super().__init__(orientation, parent)
        # Give cursor feedback
        if orientation == Qt.Horizontal:
            self.setCursor(Qt.SplitHCursor)
        else:
            self.setCursor(Qt.SplitVCursor)

    def sizeHint(self):
        base = super().sizeHint()
        if self.orientation() == Qt.Horizontal:
            return base.expandedTo(base.boundedTo(Qt.QSize(base.width(), 1)))
        else:
            return base.expandedTo(base.boundedTo(Qt.QSize(1, base.height())))


class ThinSplitter(QSplitter):
    """
    QSplitter with a 1‑pixel handle. Visual styling (color/hover)
    is provided via QSS:

        QSplitter::handle            { background: #DADADA; }
        QSplitter::handle:hover       { background: #C0C0C0; }
    """

    def __init__(self, orientation: Qt.Orientation = Qt.Horizontal, parent=None):
        super().__init__(orientation, parent)
        self.setHandleWidth(1)

    # --- override to return our custom handle -------------------
    def createHandle(self) -> QSplitterHandle:  # type: ignore[override]
        return _OnePixelHandle(self.orientation(), self)