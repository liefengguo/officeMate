

import os
from PyQt5.QtWidgets import QWidget, QVBoxLayout, QLabel, QListWidget, QListWidgetItem
from core.snapshot import SnapshotManager

class HistoryPage(QWidget):
    def __init__(self, file_path, parent=None):
        super().__init__(parent)
        self.file_path = file_path
        self.sm = SnapshotManager()
        self.doc_name = os.path.basename(file_path)

        self.layout = QVBoxLayout()
        self.label = QLabel(f"📜 {self.doc_name} 的快照历史")
        self.list_widget = QListWidget()

        self.layout.addWidget(self.label)
        self.layout.addWidget(self.list_widget)
        self.setLayout(self.layout)

        self.load_snapshots()

    def load_snapshots(self):
        self.list_widget.clear()
        versions = self.sm.version_db.get_versions(self.doc_name)
        if not versions:
            self.list_widget.addItem("暂无快照记录")
            return

        for v in versions:
            timestamp = v.get("timestamp", "未知时间")
            path = v.get("snapshot_path", "未知路径")
            remark = v.get("remark", "")
            display = f"{timestamp}  |  {path}"
            if remark:
                display += f"\n备注: {remark}"
            item = QListWidgetItem(display)
            self.list_widget.addItem(item)