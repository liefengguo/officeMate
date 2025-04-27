import os
from PyQt5.QtWidgets import QWidget, QVBoxLayout, QLabel
from core.snapshot import SnapshotManager
from app.snapshot_list_widget import SnapshotListWidget

class HistoryPage(QWidget):
    def __init__(self, file_path, parent=None):
        super().__init__(parent)
        self.file_path = file_path
        self.sm = SnapshotManager()
        self.doc_name = os.path.basename(file_path)

        self.layout = QVBoxLayout()
        self.label = QLabel(f"📜 {self.doc_name} 的快照历史")
        self.list_widget = SnapshotListWidget(file_path, single_selection=True)

        self.layout.addWidget(self.label)
        self.layout.addWidget(self.list_widget)
        self.setLayout(self.layout)