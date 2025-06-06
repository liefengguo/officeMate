"""
DocSnap entry point
~~~~~~~~~~~~~~~~~~~
Loads shared `_base.qss` plus the current theme via ``core.themes.apply_theme``.
"""

import sys
from PyQt5.QtWidgets import QApplication

from core.themes import apply_theme
from core.snapshot_manager import SnapshotManager
from app.main_window import MainWindow


def main() -> None:
    app = QApplication(sys.argv)

    # Apply user‑preferred (or auto) theme at startup
    apply_theme(app)

    # Create main window
    snapshot_mgr = SnapshotManager()
    window = MainWindow(snapshot_mgr)
    window.show()

    sys.exit(app.exec_())


if __name__ == "__main__":
    main()