import os
from PyQt5.QtWidgets import QWidget, QVBoxLayout, QLabel, QListWidget, QListWidgetItem
from core.snapshot import SnapshotManager
from app.snapshot_item_widget import SnapshotItemWidget

class HistoryPage(QWidget):
    def __init__(self, file_path, parent=None):
        super().__init__(parent)
        self.file_path = file_path
        self.sm = SnapshotManager()
        self.doc_name = os.path.basename(file_path)

        self.layout = QVBoxLayout()
        self.label = QLabel(f"📜 {self.doc_name} 的快照历史")
        self.list_widget = QListWidget()
        self.list_widget.setSelectionMode(QListWidget.SingleSelection)
        self.load_snapshots()
        self.list_widget.itemSelectionChanged.connect(self.handle_selection_changed)

        self.layout.addWidget(self.label)
        self.layout.addWidget(self.list_widget)
        self.setLayout(self.layout)

    def load_snapshots(self):
        self.list_widget.clear()
        versions = self.sm.version_db.get_versions(self.doc_name)
        if not versions:
            self.list_widget.addItem("暂无快照记录")
            return
        versions.sort(key=lambda v: v.get("timestamp", ""), reverse=True)
        for v in versions:
            title = v.get("remark", "") or os.path.basename(v.get("snapshot_path", ""))
            timestamp = v.get("timestamp", "")

            item_widget = SnapshotItemWidget(title, timestamp)
            list_item = QListWidgetItem()
            list_item.setSizeHint(item_widget.sizeHint())

            self.list_widget.addItem(list_item)
            self.list_widget.setItemWidget(list_item, item_widget)

    def handle_selection_changed(self):
        for i in range(self.list_widget.count()):
            item = self.list_widget.item(i)
            widget = self.list_widget.itemWidget(item)
            if widget:
                widget.set_selected(item.isSelected())