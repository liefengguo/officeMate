from PyQt5.QtWidgets import (
    QWidget, QVBoxLayout, QListWidget, QFileDialog, QMessageBox, QLabel,
    QListWidgetItem
)
from ui.components import PrimaryButton
from PyQt5.QtCore import Qt, QSize, QEvent
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
        self.setWindowTitle("DocSnap 文档管理主页")
        self.setMinimumSize(500, 400)

        self.db = RecentDocDB()
        title_label = QLabel("📂 已添加文档列表")
        title_label.setStyleSheet("font-size: 18px; font-weight: bold; margin-top: 10px;")
        
        self.layout = QVBoxLayout()
        self.doc_list = QListWidget()
        self.doc_list.setMouseTracking(True)
        self.doc_list.setItemDelegate(ProjectItemDelegate())
        
        self.add_button = PrimaryButton("➕ 添加项目")
        # print(self.add_button.property("type"))
        # print("lalala----: ",self.add_button.styleSheet())

        self.doc_list.setSpacing(4)

        self.layout.addWidget(self.add_button)
        self.layout.addSpacing(10)
        self.layout.addWidget(title_label)
        self.layout.addWidget(self.doc_list)
        self.setLayout(self.layout)

        # Install event filter for hover/cursor on list items
        self.doc_list.viewport().installEventFilter(self)

        self.add_button.clicked.connect(self.add_document)
        # self.doc_list.itemClicked.connect(self.open_snapshot_window)
        self.doc_list.itemClicked.connect(self.open_project_page)
        self.refresh_list()

    def refresh_list(self):
        self.doc_list.clear()
        docs = self.db.get_all()
        if not docs:
            self.doc_list.addItem("暂无文档，点击上方按钮添加")
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
            self, "选择文档", "", "文档 (*.txt *.docx);;所有文件 (*)"
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
            QMessageBox.warning(self, "文件不存在", f"该文件无法访问：\n{file_path}")

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

    def open_project_page(self, item):
        file_path = item.data(1000)
        if os.path.exists(file_path):
            # 通过 parent_window 触发页面切换
            self.parent_window.open_project_page(file_path)
        else:
            QMessageBox.warning(self, "文件不存在", f"无法访问：{file_path}")