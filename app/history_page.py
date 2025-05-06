import os
from functools import partial
from PyQt5.QtWidgets import QWidget, QVBoxLayout, QLabel, QListWidget, QListWidgetItem
from core.snapshot_manager import SnapshotManager
from app.snapshot_item_widget import SnapshotItemWidget

class HistoryPage(QWidget):
    def __init__(self, file_path, snapshot_manager: SnapshotManager, parent=None):
        super().__init__(parent)
        self.file_path = file_path
        self.sm = snapshot_manager
        self.doc_name = os.path.basename(file_path)

        self.layout = QVBoxLayout()
        self.label = QLabel(f"📜 {self.doc_name} 的快照历史")
        self.list_widget = QListWidget()
        self.list_widget.setSelectionMode(QListWidget.SingleSelection)
        self.load_snapshots()
        self.list_widget.itemSelectionChanged.connect(self.handle_selection_changed)
        self.sm.snapshot_created.connect(self.load_snapshots)
        self.sm.snapshot_deleted.connect(self.load_snapshots)

        self.layout.addWidget(self.label)
        self.layout.addWidget(self.list_widget)
        self.setLayout(self.layout)

    def load_snapshots(self):
        """加载快照数据到列表"""
        self.list_widget.clear()
        versions = self.sm.list_snapshots(self.doc_name)
        if not versions:
            self.list_widget.addItem("暂无快照记录")
            return
        versions.sort(key=lambda v: v.get("timestamp", ""), reverse=True)
        for v in versions:
            title = v.get("remark", "") or os.path.basename(v.get("snapshot_path", ""))
            timestamp = v.get("timestamp", "")

            item_widget = SnapshotItemWidget(title, timestamp)
            item_widget.view_requested.connect(partial(self.view_snapshot, item_widget))
            item_widget.delete_requested.connect(partial(self.delete_snapshot, item_widget))
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

    def view_snapshot(self, widget):
        """查看快照内容"""
        from PyQt5.QtWidgets import QMessageBox
        import docx
        versions = self.sm.list_snapshots(self.doc_name)
        target_version = None
        for v in versions:
            title = v.get("remark", "") or os.path.basename(v.get("snapshot_path", ""))
            if title == widget.label_title.text():
                target_version = v
                break
        if target_version:
            path = target_version.get("snapshot_path")
            try:
                if path.endswith(".txt"):
                    with open(path, 'r', encoding='utf-8') as f:
                        content = f.read()
                elif path.endswith(".docx"):
                    doc = docx.Document(path)
                    content = "\n".join([para.text for para in doc.paragraphs])
                else:
                    content = "(不支持的文件格式)"

                QMessageBox.information(self, "快照内容", content[:1000] + "..." if len(content) > 1000 else content)
            except Exception as e:
                QMessageBox.critical(self, "错误", f"无法读取快照内容：{str(e)}")
        else:
            QMessageBox.warning(self, "警告", "未找到对应快照。")

    def delete_snapshot(self, widget):
        """删除快照"""
        from PyQt5.QtWidgets import QMessageBox
        confirm = QMessageBox.question(self, "删除快照", "确定要删除这个快照吗？", QMessageBox.Yes | QMessageBox.No)
        if confirm == QMessageBox.Yes:
            # Find the version info
            versions = self.sm.list_snapshots(self.doc_name)
            target_version = None
            for v in versions:
                title = v.get("remark", "") or os.path.basename(v.get("snapshot_path", ""))
                if title == widget.label_title.text():
                    target_version = v
                    break
            if target_version:
                self.sm.delete_snapshot(self.doc_name, target_version)

            # Remove from list
            for i in range(self.list_widget.count()):
                item = self.list_widget.item(i)
                if self.list_widget.itemWidget(item) == widget:
                    self.list_widget.takeItem(i)
                    break