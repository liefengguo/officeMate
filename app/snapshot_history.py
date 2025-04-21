from PyQt5.QtWidgets import (
    QWidget, QVBoxLayout, QListWidget, QLabel, QMessageBox, QPushButton, QAbstractItemView
)
from core.version_db import VersionDB
from app.diff_viewer import DiffViewer
import os


class SnapshotHistoryWindow(QWidget):
    def __init__(self, file_path):
        super().__init__()
        self.setWindowTitle("快照历史")
        self.setMinimumSize(400, 300)

        self.doc_name = os.path.basename(file_path)
        self.db = VersionDB()

        self.layout = QVBoxLayout()
        self.label = QLabel(f"文档：{self.doc_name}")
        self.list_widget = QListWidget()
        self.compare_button = QPushButton("对比选中快照")
        self.compare_button.clicked.connect(self.compare_snapshots)
        self.list_widget.setSelectionMode(QAbstractItemView.MultiSelection)

        self.layout.addWidget(self.label)
        self.layout.addWidget(self.list_widget)
        self.layout.addWidget(self.compare_button)
        self.setLayout(self.layout)

        self.load_snapshots()

        self.list_widget.itemClicked.connect(self.show_snapshot_info)

    def load_snapshots(self):
        versions = self.db.get_versions(self.doc_name)
        if not versions:
            self.list_widget.addItem("暂无快照记录")
            self.list_widget.setDisabled(True)
            return

        for v in versions:
            time_str = v.get("timestamp", "未知时间")
            path_str = v.get("snapshot_path", "未知路径")
            self.list_widget.addItem(f"{time_str}  |  {path_str}")

    def show_snapshot_info(self, item):
        QMessageBox.information(self, "快照详情", item.text())

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
            self.viewer = DiffViewer(paths[0], paths[1])
            self.viewer.show()