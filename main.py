"""
DocSnap entry point
~~~~~~~~~~~~~~~~~~~
Loads shared `base.qss` plus the current theme via ``core.themes.apply_theme``.
"""

import sys
import os
from pathlib import Path
from PySide6.QtWidgets import QApplication
from PySide6.QtGui import QIcon
from PySide6.QtCore import QCoreApplication, QSettings

# Set application identifiers before any path lookups
QCoreApplication.setOrganizationName("OfficeMate")
QCoreApplication.setApplicationName("OfficeMate")

from core.themes import apply_theme
from core.i18n import set_language
from core.snapshot_manager import SnapshotManager
from core.platform_utils import get_app_data_dir
from app.main_window import MainWindow


def main() -> None:
    app = QApplication(sys.argv)
    icon_path = Path(__file__).resolve().parent / "assets" / "img" / "icon.png"
    app.setWindowIcon(QIcon(str(icon_path)))

    # --- Configure persistent settings path cross-platform ---
    settings_dir = get_app_data_dir()
    QSettings.setDefaultFormat(QSettings.IniFormat)
    QSettings.setPath(QSettings.IniFormat, QSettings.UserScope, str(settings_dir))

    lang = os.getenv("DOCSNAP_LANG")
    if lang:
        set_language(lang)

    # Apply user‑preferred (or auto) theme at startup
    apply_theme(app)

    # Create main window
    snapshot_mgr = SnapshotManager()
    window = MainWindow(snapshot_mgr)
    window.setWindowIcon(QIcon(str(icon_path)))
    window.show()

    sys.exit(app.exec())


if __name__ == "__main__":
    main()
