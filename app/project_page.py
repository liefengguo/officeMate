from PyQt5.QtWidgets import (
    QWidget, QHBoxLayout, QVBoxLayout, QPushButton, QStackedWidget, QLabel, QSizePolicy
)
from PyQt5.QtCore import Qt
from app.snapshot_page import SnapshotPage
from app.history_page import HistoryPage
from app.snapshot_compare_page import SnapshotComparePage
from app.settings_page import SettingsPage

class ProjectPage(QWidget):
    def __init__(self, file_path, parent=None):
        super().__init__(parent)
        self.file_path = file_path
        self.parent_window = parent

        self.main_layout = QHBoxLayout(self)
        self.toolbar_layout = QVBoxLayout()
        self.toolbar_layout.setAlignment(Qt.AlignTop)

        self.back_button = QPushButton("⬅")
        self.back_button.setFixedSize(40, 40)
        self.back_button.setSizePolicy(QSizePolicy.Fixed, QSizePolicy.Fixed)
        self.toolbar_layout.addWidget(self.back_button)

        # Left toolbar
        self.add_snapshot_btn = QPushButton("📸")
        self.history_btn = QPushButton("📜")
        self.compare_btn = QPushButton("🔍")
        self.settings_btn = QPushButton("⚙️")

        for btn in (self.add_snapshot_btn, self.history_btn):
            btn.setFixedSize(40, 40)
            btn.setSizePolicy(QSizePolicy.Fixed, QSizePolicy.Fixed)
            self.toolbar_layout.addWidget(btn)

        self.compare_btn.setFixedSize(40, 40)
        self.compare_btn.setSizePolicy(QSizePolicy.Fixed, QSizePolicy.Fixed)
        self.toolbar_layout.addWidget(self.compare_btn)

        self.toolbar_layout.addStretch(1)
        self.settings_btn.setFixedSize(40, 40)
        self.toolbar_layout.addWidget(self.settings_btn)

        # Right content area
        self.stack = QStackedWidget()
        self.page_add_snapshot = SnapshotPage(self.file_path)
        self.page_history = HistoryPage(self.file_path)
        self.page_compare = SnapshotComparePage(self.file_path)
        self.page_settings = SettingsPage()

        self.stack.addWidget(self.page_add_snapshot)  # index 0
        self.stack.addWidget(self.page_history)       # index 1
        self.stack.addWidget(self.page_compare)       # index 2
        self.stack.addWidget(self.page_settings)      # index 3

        self.add_snapshot_btn.clicked.connect(lambda: self.stack.setCurrentIndex(0))
        self.history_btn.clicked.connect(lambda: self.stack.setCurrentIndex(1))
        self.compare_btn.clicked.connect(lambda: self.stack.setCurrentIndex(2))
        self.settings_btn.clicked.connect(lambda: self.stack.setCurrentIndex(3))

        self.back_button.clicked.connect(self.back_to_home)

        self.main_layout.addLayout(self.toolbar_layout)
        self.main_layout.addWidget(self.stack)

        self.stack.setCurrentIndex(0)
        self.page_add_snapshot.snapshot_created.connect(self.handle_snapshot_created)

    def handle_snapshot_created(self, file_path):
        """当快照创建完成后，刷新所有需要的页面"""
        if hasattr(self, 'page_history'):
            self.page_history.load_snapshots()
        if hasattr(self, 'page_compare'):
            self.page_compare.list_widget.load_snapshots()

    def back_to_home(self):
        """返回软件首页"""
        if self.parent_window:
            self.parent_window.go_back_to_dashboard()