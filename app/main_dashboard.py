from PySide6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QListWidget, QFileDialog, QMessageBox, QLabel,
    QListWidgetItem, QMenu, QSizePolicy
)
from ui.components import PrimaryButton
from PySide6.QtCore import Qt, QSize, QEvent
from core.i18n import _, i18n
import os
from app.snapshot_history import SnapshotHistoryWindow
from core.recent_db import RecentDocDB
from app.project_delegate import ProjectItemDelegate
from core.snapshot_manager import SnapshotManager

class MainDashboard(QWidget):
    def __init__(self, snapshot_manager: SnapshotManager, parent=None):
        super().__init__(parent)
        self.manager = snapshot_manager
        self.parent_window = parent
        self.setWindowTitle(_("DocSnap 文档管理主页"))
        self.setMinimumSize(500, 400)

        self.db = RecentDocDB()
        self.title_label = QLabel(_("📂 已添加文档列表"))
        self.title_label.setProperty("class", "h2")
        
        self.layout = QVBoxLayout(self)
        self.layout.setSpacing(10)
        self.layout.setContentsMargins(12, 12, 12, 12)

        self.doc_list = QListWidget()
        self.doc_list.setProperty("class", "snapshot-list")
        self.doc_list.setFrameShape(QListWidget.NoFrame)
        self.doc_list.setMouseTracking(True)
        self.doc_list.setItemDelegate(ProjectItemDelegate())
        self.doc_list.setContextMenuPolicy(Qt.CustomContextMenu)
        self.doc_list.customContextMenuRequested.connect(self.show_context_menu)

        self.doc_list.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Expanding)
        
        self.add_button = PrimaryButton(_("➕ 添加项目"))

        self.doc_list.setSpacing(4)

        self.layout.addWidget(self.title_label)
        self.layout.addWidget(self.doc_list, 1)

        btn_row = QHBoxLayout()
        btn_row.addStretch(1)
        btn_row.addWidget(self.add_button)
        self.layout.addLayout(btn_row)

        # Install event filter for hover/cursor on list items
        self.doc_list.viewport().installEventFilter(self)

        self.add_button.clicked.connect(self.add_document)
        # self.doc_list.itemClicked.connect(self.open_snapshot_window)
        self.doc_list.itemClicked.connect(self.open_project_page)
        self.refresh_list()

        i18n.language_changed.connect(self.retranslate_ui)

    # ------------------------------------------------------- i18n
    def retranslate_ui(self):
        self.setWindowTitle(_("DocSnap 文档管理主页"))
        self.title_label.setText(_("📂 已添加文档列表"))
        self.add_button.setText(_("➕ 添加项目"))
        self.refresh_list()

    def refresh_list(self):
        self.doc_list.clear()
        docs = self.db.get_all()
        if not docs:
            self.doc_list.addItem(_("暂无文档，点击上方按钮添加"))
            self.doc_list.setDisabled(True)
        else:
            self.doc_list.setDisabled(False)
            for doc_path in docs:
                item = QListWidgetItem()
                item.setData(1000, doc_path)
                item.setToolTip(doc_path)
                item.setSizeHint(QSize(300, 50))
                self.doc_list.addItem(item)
    def add_document(self):
        file_path, _ = QFileDialog.getOpenFileName(
            self, _("选择文档"), "", _("文档 (*.txt *.docx);;所有文件 (*)")
        )
        if file_path:
            self.db.add(file_path)
            self.refresh_list()

    def open_snapshot_window(self, item):
        file_path = item.data(1000)
        if os.path.exists(file_path):
            if self.parent_window:
                self.parent_window.open_snapshot_history(file_path)
        else:
            QMessageBox.warning(self, _("文件不存在"), _("该文件无法访问：\n{path}").format(path=file_path))

    def eventFilter(self, source, event):
        if source is self.doc_list.viewport():
            if event.type() == QEvent.MouseMove:
                item = self.doc_list.itemAt(event.pos())
                if item:
                    self.doc_list.viewport().setCursor(Qt.PointingHandCursor)
                else:
                    self.doc_list.viewport().setCursor(Qt.ArrowCursor)
                self.doc_list.viewport().update()
        return super().eventFilter(source, event)

    def show_context_menu(self, pos):
        item = self.doc_list.itemAt(pos)
        if not item or not item.data(1000):
            return
        menu = QMenu(self)
        remove_act = menu.addAction(_("移除项目"))
        action = menu.exec(self.doc_list.viewport().mapToGlobal(pos))
        if action == remove_act:
            file_path = item.data(1000)
            reply = QMessageBox.question(
                self,
                _("移除项目"),
                _("确定从列表移除该项目？"),
                QMessageBox.Yes | QMessageBox.No,
            )
            if reply == QMessageBox.Yes:
                self.db.remove(file_path)
                self.refresh_list()

    def open_project_page(self, item):
        file_path = item.data(1000)
        if os.path.exists(file_path):
            # 通过 parent_window 触发页面切换
            self.parent_window.open_project_page(file_path)
        else:
            QMessageBox.warning(self, _("文件不存在"), _("无法访问：{path}").format(path=file_path))
