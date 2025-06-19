"""
core.themes
~~~~~~~~~~~

Centralised theme handling for DocSnap.

Usage
------
>>> from PySide6.QtWidgets import QApplication
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

import sys
from pathlib import Path
from typing import Optional

from PySide6.QtCore import QSettings
from PySide6.QtWidgets import QApplication

from core.platform_utils import is_dark_mode

# --------------------------------------------------------------------------- fs
_STYLES_DIR = Path(__file__).resolve().parent.parent / "assets" / "styles"
base_QSS_NAME = "base.qss"

def _read_qss(filename: str) -> str:
    """Return stylesheet contents if the .qss file exists, else empty str."""
    fp = _STYLES_DIR / filename
    return fp.read_text(encoding="utf-8") if fp.exists() else ""


# ---------------------------------------------------------------------- public
def load_theme_pref() -> str:
    """Return stored preference: 'auto' (default) | 'light' | 'dark'."""
    return QSettings().value("ui/theme", "auto")


def save_theme_pref(pref: str) -> None:
    """Persist preference in QSettings."""
    if pref not in ("auto", "light", "dark"):
        raise ValueError("pref must be 'auto', 'light' or 'dark'")
    QSettings().setValue("ui/theme", pref)


def _pick_theme_file(pref: str) -> str:
    """Translate preference into qss filename."""
    if pref == "auto":
        pref = "dark" if is_dark_mode() else "light"
    return f"{pref}.qss"  # 'light.qss' / 'dark.qss'


def apply_theme(app: Optional[QApplication] = None, pref: str | None = None) -> None:
    """
    Apply (or re-apply) theme to *app*.

    If *pref* is None -> use stored preference (or 'auto').
    If *app* is None  -> use QApplication.instance().
    """
    if app is None:
        app = QApplication.instance()
        if app is None:
            raise RuntimeError("No QApplication instance available")

    if pref is None:
        pref = load_theme_pref()
    elif pref not in ("auto", "light", "dark"):
        raise ValueError("pref must be 'auto', 'light' or 'dark'")

    base_qss  = _read_qss(base_QSS_NAME)
    theme_qss = _read_qss(_pick_theme_file(pref))
    # 最终样式 = 公共样式 + 当前主题样式
    app.setStyleSheet(base_qss + "\n" + theme_qss)
