from PyQt5.QtWidgets import (
    QWidget, QVBoxLayout, QPushButton, QListWidget, QFileDialog, QMessageBox, QLabel, QSpacerItem, QSizePolicy, QListWidgetItem
)
from PyQt5.QtGui import QFont
from PyQt5.QtCore import Qt, QSize, QEvent
import os
from app.snapshot_history import SnapshotHistoryWindow
from core.recent_db import RecentDocDB
from PyQt5.QtGui import QBrush, QColor
from app.project_delegate import ProjectItemDelegate

class MainDashboard(QWidget):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("DocSnap 文档管理主页")
        self.setMinimumSize(500, 400)

        self.db = RecentDocDB()
        title_label = QLabel("📂 已添加文档列表")
        title_label.setStyleSheet("font-size: 18px; font-weight: bold; margin-top: 10px;")
        
        self.layout = QVBoxLayout()
        self.doc_list = QListWidget()
        self.doc_list.setMouseTracking(True)
        self.doc_list.setItemDelegate(ProjectItemDelegate())
        
        self.add_button = QPushButton("➕ 添加项目")
        self.add_button.setStyleSheet("padding: 6px; font-size: 14px;")

        self.doc_list.setStyleSheet("""
            QListWidget {
                background-color: #f9f9f9;
            }
        """)
        self.doc_list.setSpacing(4)

        self.layout.addWidget(self.add_button)
        self.layout.addSpacing(10)
        self.layout.addWidget(title_label)
        self.layout.addWidget(self.doc_list)
        self.setLayout(self.layout)

        # Install event filter for hover/cursor on list items
        self.doc_list.viewport().installEventFilter(self)

        self.add_button.clicked.connect(self.add_document)
        self.doc_list.itemClicked.connect(self.open_snapshot_window)

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
            self.snapshot_window = SnapshotHistoryWindow(file_path)
            self.snapshot_window.show()
            self.close()  # close dashboard
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