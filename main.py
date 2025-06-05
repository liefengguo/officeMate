from PyQt5.QtWidgets import QApplication
from app.main_window import MainWindow
import os
from core.snapshot_manager import SnapshotManager
def load_stylesheet(app):
    """Load main QSS and append diff highlight QSS."""
    root_dir = "assets/styles"
    main_qss = os.path.join(root_dir, "office_mate.qss")
    diff_qss = os.path.join(root_dir, "diff.qss")

    combined = ""
    if os.path.exists(main_qss):
        with open(main_qss, "r", encoding="utf-8") as f:
            combined += f.read()
    if os.path.exists(diff_qss):
        combined += "\n"  # ensure separation
        with open(diff_qss, "r", encoding="utf-8") as f:
            combined += f.read()

    if combined:
        app.setStyleSheet(combined)
if __name__ == "__main__":
    import sys
    app = QApplication(sys.argv)
    load_stylesheet(app)
    SNAPSHOT_MANAGER = SnapshotManager()
    window = MainWindow(SNAPSHOT_MANAGER)
    window.show()
    sys.exit(app.exec_())
"""
DocSnap entry point
~~~~~~~~~~~~~~~~~~~

* Detect system dark / light mode and load the corresponding QSS
  (assets/styles/dark.qss or light.qss).
* Keep legacy support for diff.qss if present.
"""

import sys
from pathlib import Path

from PyQt5.QtWidgets import QApplication

from app.main_window import MainWindow
from core.platform_utils import is_dark_mode
from core.snapshot_manager import SnapshotManager

# ------------------------------------------------------------------- stylesheet
def load_stylesheet(app: QApplication) -> None:
    """Load the appropriate theme QSS + optional diff overrides."""
    styles_dir = Path(__file__).parent / "assets" / "styles"

    theme_file = styles_dir / ("dark.qss" if is_dark_mode() else "light.qss")
    combined: str = ""

    if theme_file.exists():
        combined += theme_file.read_text(encoding="utf-8")

    # Fallback: if theme_file missing, try legacy office_mate.qss
    legacy_main = styles_dir / "office_mate.qss"
    if not combined and legacy_main.exists():
        combined += legacy_main.read_text(encoding="utf-8")

    # In dark mode we already have dedicated colors in dark.qss, so skip legacy diff.qss
    diff_qss = styles_dir / "diff.qss"
    if not is_dark_mode() and diff_qss.exists():
        combined += "\n" + diff_qss.read_text(encoding="utf-8")

    if combined:
        app.setStyleSheet(combined)


# ----------------------------------------------------------------------- main
def main() -> None:
    app = QApplication(sys.argv)
    load_stylesheet(app)

    snapshot_mgr = SnapshotManager()
    window = MainWindow(snapshot_mgr)
    window.show()

    sys.exit(app.exec_())


if __name__ == "__main__":
    main()