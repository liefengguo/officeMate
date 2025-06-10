"""
core.themes
~~~~~~~~~~~

Centralised theme handling for DocSnap.

Usage
------
>>> from PyQt5.QtWidgets import QApplication
>>> from core.themes import apply_theme, save_theme_pref
>>> app = QApplication([])
>>> apply_theme(app)               # load stored or auto theme
>>> save_theme_pref("dark")        # persist preference ("auto"|"light"|"dark")
>>> apply_theme(app, "dark")       # immediately switch

Functions
---------
load_theme_pref()  -> str
save_theme_pref(pref: str) -> None
apply_theme(app: QApplication | None = None, pref: str | None = None) -> None
"""

from __future__ import annotations

from pathlib import Path
from typing import Optional

from PyQt5.QtCore import QSettings
from PyQt5.QtWidgets import QApplication

from core.platform_utils import is_dark_mode


class ThemeManager:
    """Load, save and apply QSS themes."""

    STYLES_DIR = Path(__file__).resolve().parent.parent / "assets" / "styles"
    BASE_QSS_NAME = "_base.qss"

    # -------------- filesystem helpers -----------------
    def _read_qss(self, filename: str) -> str:
        fp = self.STYLES_DIR / filename
        return fp.read_text(encoding="utf-8") if fp.exists() else ""

    def _pick_theme_file(self, pref: str) -> str:
        if pref == "auto":
            pref = "dark" if is_dark_mode() else "light"
        return f"{pref}.qss"

    # ----------------- settings API --------------------
    def load_pref(self) -> str:
        """Return stored preference ('auto' by default)."""
        return QSettings().value("ui/theme", "auto")

    def save_pref(self, pref: str) -> None:
        if pref not in ("auto", "light", "dark"):
            raise ValueError("pref must be 'auto', 'light' or 'dark'")
        QSettings().setValue("ui/theme", pref)

    # ------------------- main API ----------------------
    def apply(self, app: Optional[QApplication] = None, pref: str | None = None) -> None:
        if app is None:
            app = QApplication.instance()
            if app is None:
                raise RuntimeError("No QApplication instance available")

        if pref is None:
            pref = self.load_pref()
        elif pref not in ("auto", "light", "dark"):
            raise ValueError("pref must be 'auto', 'light' or 'dark'")

        base_qss = self._read_qss(self.BASE_QSS_NAME)
        theme_qss = self._read_qss(self._pick_theme_file(pref))
        app.setStyleSheet(base_qss + "\n" + theme_qss)


# ----------------------- module-level helpers -----------------------
_manager = ThemeManager()

def load_theme_pref() -> str:
    return _manager.load_pref()


def save_theme_pref(pref: str) -> None:
    _manager.save_pref(pref)


def apply_theme(app: Optional[QApplication] = None, pref: str | None = None) -> None:
    _manager.apply(app, pref)

