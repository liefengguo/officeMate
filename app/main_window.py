from PyQt5.QtWidgets import (
    QMainWindow, QStackedWidget, QMenu, QAction, QActionGroup
)
from PyQt5.QtCore import QSettings, QSize
from core.i18n import _, i18n
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
        self.setWindowTitle(_("DocSnap 文档助手"))
        self.setMinimumSize(300, 200)

        # Restore separate sizes for dashboard and content pages
        self._settings = QSettings()
        home_w = self._settings.value("ui/home_width", 500, type=int)
        home_h = self._settings.value("ui/home_height", 400, type=int)
        page_w = self._settings.value("ui/page_width", 800, type=int)
        page_h = self._settings.value("ui/page_height", 600, type=int)
        self.home_size = QSize(home_w, home_h)
        self.page_size = QSize(page_w, page_h)

        # Start with dashboard size
        self.resize(self.home_size)

        self.stack = QStackedWidget()
        self.setCentralWidget(self.stack)

        # ---------------- 主题菜单 ----------------
        self._create_theme_menu()

        i18n.language_changed.connect(self.retranslate_ui)

        # 初始化页面
        self.dashboard = MainDashboard(parent=self, snapshot_manager=self.manager)
        self.stack.addWidget(self.dashboard)  # index 0

    # ------------------------------------------------------- i18n
    def retranslate_ui(self):
        self.setWindowTitle(_("DocSnap 文档助手"))
        self.theme_menu.setTitle(_("主题(&T)"))
        self.act_auto.setText(_("跟随系统"))
        self.act_light.setText(_("浅色"))
        self.act_dark.setText(_("深色"))
        if hasattr(self, 'dashboard'):
            self.dashboard.retranslate_ui()

    def open_snapshot_history(self, file_path):
        # Store dashboard size before switching
        self._store_current_size()
        self.snapshot_page = SnapshotHistoryWindow(file_path, parent=self, snapshot_manager=self.manager)
        if self.stack.count() == 2:
            self.stack.removeWidget(self.stack.widget(1))
        self.stack.addWidget(self.snapshot_page)  # index 1
        self.stack.setCurrentIndex(1)
        self.resize(self.page_size)

    def go_back_to_dashboard(self):
        # Persist page size and restore dashboard size
        self._store_current_size()
        self.stack.setCurrentIndex(0)
        self.resize(self.home_size)

    def open_project_page(self, file_path):
        """从主页打开项目页面"""
        # 如果之前已经打开过，先移除旧的
        if hasattr(self, 'project_page'):
            self.stack.removeWidget(self.project_page)

        # 创建新的项目页面并压入堆栈
        # Store dashboard size before switching
        self._store_current_size()
        self.project_page = ProjectPage(file_path, snapshot_manager=self.manager, parent=self)
        self.stack.addWidget(self.project_page)  # index 1
        self.stack.setCurrentWidget(self.project_page)
        self.resize(self.page_size)

    # ---------------------------------------------------------------- theme
    def _create_theme_menu(self):
        menubar = self.menuBar()

        self.theme_menu = QMenu(_("主题(&T)"), self)
        self.act_auto  = QAction(_("跟随系统"), self, checkable=True)
        self.act_light = QAction(_("浅色"), self, checkable=True)
        self.act_dark  = QAction(_("深色"), self, checkable=True)

        group = QActionGroup(self)
        for a in (self.act_auto, self.act_light, self.act_dark):
            a.setActionGroup(group)
            self.theme_menu.addAction(a)

        # 读取用户偏好（若无则 auto）
        pref = load_theme_pref()
        {"auto": self.act_auto,
         "light": self.act_light,
         "dark": self.act_dark}.get(pref, self.act_auto).setChecked(True)

        menubar.addMenu(self.theme_menu)

        # 切换主题
        def _on_triggered(action: QAction):
            mapping = {self.act_auto: "auto", self.act_light: "light", self.act_dark: "dark"}
            pref = mapping[action]
            save_theme_pref(pref)
            apply_theme(pref=pref)
        group.triggered.connect(_on_triggered)

    def _store_current_size(self):
        """Save current window size depending on active page."""
        if self.stack.currentIndex() == 0:
            self.home_size = self.size()
            self._settings.setValue("ui/home_width", self.home_size.width())
            self._settings.setValue("ui/home_height", self.home_size.height())
        else:
            self.page_size = self.size()
            self._settings.setValue("ui/page_width", self.page_size.width())
            self._settings.setValue("ui/page_height", self.page_size.height())

    def closeEvent(self, event):
        """Persist window size on close."""
        self._store_current_size()
        super().closeEvent(event)
