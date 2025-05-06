from PyQt5.QtWidgets import (
    QWidget, QVBoxLayout, QListWidget, QLabel, QMessageBox, QPushButton, QAbstractItemView
)
from core.snapshot_manager import SnapshotManager
from app.diff_viewer import DiffViewer
import os
from functools import partial
from app.preview_window import PreviewWindow

class SnapshotHistoryWindow(QWidget):
    def __init__(self, file_path, snapshot_manager: SnapshotManager, parent=None):
        super().__init__(parent)
        self.parent_window = parent
        self.doc_name = os.path.basename(file_path)
        self.setWindowTitle("快照历史")
        self.setMinimumSize(400, 300)

        self.doc_name = os.path.basename(file_path)
        self.manager = snapshot_manager
        self.manager.snapshot_created.connect(self.load_snapshots)
        self.manager.snapshot_deleted.connect(self.load_snapshots)

        self.layout = QVBoxLayout()
        self.back_button = QPushButton("← 返回主页")
        self.back_button.clicked.connect(self.go_back)
        self.layout.addWidget(self.back_button)

        self.label = QLabel(f"文档：{self.doc_name}")
        self.list_widget = QListWidget()
        self.compare_button = QPushButton("对比选中快照")
        self.compare_button.clicked.connect(self.compare_snapshots)
        self.preview_button = QPushButton("查看快照内容")
        self.preview_button.clicked.connect(self.preview_snapshots)
        self.list_widget.setSelectionMode(QAbstractItemView.MultiSelection)

        self.layout.addWidget(self.label)
        self.layout.addWidget(self.list_widget)
        self.layout.addWidget(self.compare_button)
        self.layout.addWidget(self.preview_button)
        self.setLayout(self.layout)

        self.preview_windows = []
        self.load_snapshots()

    def go_back(self):
        if self.parent_window:
            self.parent_window.go_back_to_dashboard()

    def load_snapshots(self):
        """刷新快照列表"""
        self.list_widget.clear()
        versions = self.manager.list_snapshots(self.doc_name)
        if not versions:
            self.list_widget.addItem("暂无快照记录")
            self.list_widget.setDisabled(True)
            return
        self.list_widget.setDisabled(False)
        for v in versions:
            time_str = v.get("timestamp", "未知时间")
            path_str = v.get("snapshot_path", "未知路径")
            self.list_widget.addItem(f"{time_str}  |  {path_str}")

    def preview_snapshots(self):
        items = self.list_widget.selectedItems()
        if not items:
            QMessageBox.information(self, "提示", "请至少选择一个快照进行预览")
            return

        for item in items:
            parts = item.text().split("  |  ")
            if len(parts) == 2:
                file_path = parts[1].strip()
                preview = PreviewWindow(file_path)
                self.preview_windows.append(preview)  # Prevent GC
                preview.show()

    def compare_snapshots(self):
        items = self.list_widget.selectedItems()
        if len(items) != 2:
            QMessageBox.warning(self, "选择错误", "请选择两个快照进行对比")
            return

        paths = []
        for item in items:
            parts = item.text().split("  |  ")
            if len(parts) == 2:
                paths.append(parts[1].strip())

        if len(paths) == 2:
            diff = self.manager.compare_snapshots(paths[0], paths[1])
            viewer = DiffViewer(diff_text=diff)
            viewer.show()