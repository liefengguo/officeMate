from PyQt5.QtWidgets import QApplication
from app.main_window import MainWindow
import os
from core.snapshot_manager import SnapshotManager
def load_stylesheet(app):
    qss_path = "assets/styles/office_mate.qss"
    if os.path.exists(qss_path):
        with open(qss_path, "r", encoding="utf-8") as f:
            app.setStyleSheet(f.read())
if __name__ == "__main__":
    import sys
    app = QApplication(sys.argv)
    load_stylesheet(app)
    SNAPSHOT_MANAGER = SnapshotManager()
    window = MainWindow(SNAPSHOT_MANAGER)
    window.show()
    sys.exit(app.exec_())