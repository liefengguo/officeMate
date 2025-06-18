from PySide6.QtWidgets import (
    QWidget, QHBoxLayout, QVBoxLayout, QStackedWidget, QLabel, QSizePolicy
)
from ui.components import FlatButton
from PySide6.QtCore import Qt
from app.snapshot_page import SnapshotPage
from app.history_page import HistoryPage
from app.snapshot_compare_page import SnapshotComparePage
from app.settings_page import SettingsPage

class ProjectPage(QWidget):
    def __init__(self, file_path, snapshot_manager, parent=None):
        super().__init__(parent)
        self.file_path = file_path
        self.manager = snapshot_manager
        self.parent_window = parent

        self.main_layout = QHBoxLayout(self)
        self.toolbar_layout = QVBoxLayout()
        self.toolbar_layout.setAlignment(Qt.AlignTop)
        self.toolbar_layout.setSpacing(20)

        self.back_button = FlatButton("⬅")
        self.back_button.setFixedSize(40, 40)
        self.back_button.setSizePolicy(QSizePolicy.Fixed, QSizePolicy.Fixed)
        self.toolbar_layout.addWidget(self.back_button)

        # Left toolbar
        self.add_snapshot_btn = FlatButton("📸")
        self.history_btn = FlatButton("📜")
        self.compare_btn = FlatButton("🔍")
        # Gear emoji with text presentation avoids font issues on some systems
        self.settings_btn = FlatButton("⚙")

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

        # wrap toolbar in a sidebar widget for QSS
        self.sidebar = QWidget()
        self.sidebar.setProperty("role", "sidebar")
        self.sidebar.setLayout(self.toolbar_layout)

        # Right content area
        self.stack = QStackedWidget()
        self.page_add_snapshot = SnapshotPage(self.file_path, self.manager)
        self.page_history = HistoryPage(self.file_path, self.manager)
        self.page_compare = SnapshotComparePage(self.file_path, self.manager)
        self.page_settings = SettingsPage()

        self.stack.addWidget(self.page_add_snapshot)  # index 0
        self.stack.addWidget(self.page_history)       # index 1
        self.stack.addWidget(self.page_compare)       # index 2
        self.stack.addWidget(self.page_settings)      # index 3

        self.add_snapshot_btn.clicked.connect(lambda: self.stack.setCurrentIndex(0))
        self.history_btn.clicked.connect(lambda: self.stack.setCurrentIndex(1))
        self.compare_btn.clicked.connect(self.open_compare_page)
        self.settings_btn.clicked.connect(lambda: self.stack.setCurrentIndex(3))

        self.back_button.clicked.connect(self.back_to_home)

        self.main_layout.addWidget(self.sidebar)
        self.main_layout.addWidget(self.stack)

        self.stack.setCurrentIndex(0)
        # Ensure snapshot_created and snapshot_deleted signals are connected
        self.manager.snapshot_created.connect(self.handle_snapshot_created)
        self.manager.snapshot_deleted.connect(self.handle_snapshot_created)

    def open_compare_page(self):
        """显示快照对比页并刷新按钮状态"""
        self.stack.setCurrentIndex(2)
        if self.page_compare:
            self.page_compare.update_button_visibility()

    def handle_snapshot_created(self, *_):
        """当快照创建完成后，刷新所有需要的页面"""
        if self.page_history:
            self.page_history.load_snapshots()
        if self.page_compare:
            self.page_compare.load_snapshots()

    def back_to_home(self):
        """返回软件首页"""
        if self.parent_window:
            self.parent_window.go_back_to_dashboard()
