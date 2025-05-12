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