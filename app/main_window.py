from PyQt5.QtWidgets import QMainWindow, QStackedWidget
from app.main_dashboard import MainDashboard
from app.snapshot_history import SnapshotHistoryWindow

class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("DocSnap 文档助手")
        self.setMinimumSize(300, 200)

        self.stack = QStackedWidget()
        self.setCentralWidget(self.stack)

        # 初始化页面
        self.dashboard = MainDashboard(parent=self)
        self.stack.addWidget(self.dashboard)  # index 0

    def open_snapshot_history(self, file_path):
        self.snapshot_page = SnapshotHistoryWindow(file_path, parent=self)
        if self.stack.count() == 2:
            self.stack.removeWidget(self.stack.widget(1))
        self.stack.addWidget(self.snapshot_page)  # index 1
        self.stack.setCurrentIndex(1)

    def go_back_to_dashboard(self):
        self.stack.setCurrentIndex(0)