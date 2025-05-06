from PyQt5.QtWidgets import QMainWindow, QStackedWidget
from app.main_dashboard import MainDashboard
from app.snapshot_history import SnapshotHistoryWindow
from app.project_page import ProjectPage
from core.snapshot_manager import SnapshotManager

class MainWindow(QMainWindow):
    def __init__(self, snapshot_manager: SnapshotManager):
        super().__init__()
        self.manager = snapshot_manager
        self.setWindowTitle("DocSnap 文档助手")
        self.setMinimumSize(300, 200)

        self.stack = QStackedWidget()
        self.setCentralWidget(self.stack)

        # 初始化页面
        self.dashboard = MainDashboard(parent=self, snapshot_manager=self.manager)
        self.stack.addWidget(self.dashboard)  # index 0

    def open_snapshot_history(self, file_path):
        self.snapshot_page = SnapshotHistoryWindow(file_path, parent=self, snapshot_manager=self.manager)
        if self.stack.count() == 2:
            self.stack.removeWidget(self.stack.widget(1))
        self.stack.addWidget(self.snapshot_page)  # index 1
        self.stack.setCurrentIndex(1)

    def go_back_to_dashboard(self):
        self.stack.setCurrentIndex(0)

    def open_project_page(self, file_path):
        """从主页打开项目页面"""
        # 如果之前已经打开过，先移除旧的
        if hasattr(self, 'project_page'):
            self.stack.removeWidget(self.project_page)

        # 创建新的项目页面并压入堆栈
        self.project_page = ProjectPage(file_path, snapshot_manager=self.manager, parent=self)
        self.stack.addWidget(self.project_page)  # index 1
        self.stack.setCurrentWidget(self.project_page)