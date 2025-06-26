from __future__ import annotations

from pathlib import Path
from PySide6.QtCore import QSettings

# Shared QSettings instance stored in the repository's config.ini
_SETTINGS_PATH = Path(__file__).resolve().parent.parent / "config.ini"
_settings = QSettings(str(_SETTINGS_PATH), QSettings.IniFormat)


def get_settings() -> QSettings:
    """Return the application's QSettings object."""
    return _settings
