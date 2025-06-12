from PyQt5.QtWidgets import (
    QMainWindow, QStackedWidget, QMenu, QAction, QActionGroup
)
from PyQt5.QtCore import QSettings
from core.themes import apply_theme, load_theme_pref, save_theme_pref

from app.main_dashboard import MainDashboard
from app.snapshot_history import SnapshotHistoryWindow
from app.project_page import ProjectPage
from core.snapshot_manager import SnapshotManager

class MainWindow(QMainWindow):
    def __init__(self, snapshot_manager: SnapshotManager):
        super().__init__()
        apply_theme()
        self.manager = snapshot_manager
        self.setWindowTitle("DocSnap 文档助手")
        self.setMinimumSize(300, 200)

        # Restore previous window size if available
        self._settings = QSettings()
        width = self._settings.value("ui/window_width")
        height = self._settings.value("ui/window_height")
        try:
            width = int(width)
            height = int(height)
        except (TypeError, ValueError):
            width = height = None
        if width and height:
            self.resize(width, height)

        self.stack = QStackedWidget()
        self.setCentralWidget(self.stack)

        # ---------------- 主题菜单 ----------------
        self._create_theme_menu()

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

    # ---------------------------------------------------------------- theme
    def _create_theme_menu(self):
        menubar = self.menuBar()

        theme_menu = QMenu("主题(&T)", self)
        act_auto  = QAction("跟随系统", self, checkable=True)
        act_light = QAction("浅色", self, checkable=True)
        act_dark  = QAction("深色", self, checkable=True)

        group = QActionGroup(self)
        for a in (act_auto, act_light, act_dark):
            a.setActionGroup(group)
            theme_menu.addAction(a)

        # 读取用户偏好（若无则 auto）
        pref = load_theme_pref()
        {"auto": act_auto,
         "light": act_light,
         "dark": act_dark}.get(pref, act_auto).setChecked(True)

        menubar.addMenu(theme_menu)

        # 切换主题
        def _on_triggered(action: QAction):
            mapping = {act_auto: "auto", act_light: "light", act_dark: "dark"}
            pref = mapping[action]
            save_theme_pref(pref)
            apply_theme(pref=pref)
        group.triggered.connect(_on_triggered)

    def closeEvent(self, event):
        """Persist window size on close."""
        self._settings.setValue("ui/window_width", self.width())
        self._settings.setValue("ui/window_height", self.height())
        super().closeEvent(event)
