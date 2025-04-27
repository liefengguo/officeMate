import os
from PyQt5.QtWidgets import QWidget, QVBoxLayout, QLabel, QPushButton, QMessageBox
from core.snapshot import SnapshotManager
from core.diff_engine import DiffEngine
from PyQt5.QtWidgets import QPlainTextEdit
from app.snapshot_list_widget import SnapshotListWidget
class SnapshotComparePage(QWidget):
    def __init__(self, file_path, parent=None):
        super().__init__(parent)
        self.file_path = file_path
        self.sm = SnapshotManager()
        self.doc_name = os.path.basename(file_path)

        self.layout = QVBoxLayout()
        self.label = QLabel(f"🔍 {self.doc_name} 快照对比")
        self.list_widget = SnapshotListWidget(file_path, single_selection=False)
        self.compare_button = QPushButton("对比选中的两个快照")

        self.layout.addWidget(self.label)
        self.layout.addWidget(self.list_widget)
        self.layout.addWidget(self.compare_button)
        self.setLayout(self.layout)

        self.compare_button.clicked.connect(self.compare_snapshots)
        self.list_widget.itemSelectionChanged.connect(self.check_selection_limit)

        self.diff_viewer = QPlainTextEdit()
        self.diff_viewer.setReadOnly(True)  # 只读，不可编辑
        self.layout.addWidget(self.diff_viewer)

    def compare_snapshots(self):
        items = self.list_widget.selectedItems()
        if len(items) != 2:
            QMessageBox.warning(self, "提示", "请选择两个快照进行对比")
            return

        versions = self.sm.version_db.get_versions(self.doc_name)

        selected_versions = []
        for item in items:
            path = item.data(1000)
            match = next((v for v in versions if v.get("snapshot_path") == path), None)
            if match:
                selected_versions.append((path, match.get("timestamp", "")))

        if len(selected_versions) != 2:
            QMessageBox.warning(self, "错误", "读取快照信息失败")
            return

        selected_versions.sort(key=lambda x: x[1])
        base_path, latest_path = selected_versions[0][0], selected_versions[1][0]

        try:
            engine = DiffEngine()
            diff_result = engine.compare_files(base_path, latest_path)
            self.diff_viewer.setPlainText(diff_result)
        except Exception as e:
            self.diff_viewer.setPlainText(f"对比失败：{str(e)}")

    def check_selection_limit(self):
        items = self.list_widget.selectedItems()
        if len(items) > 2:
            first_selected_item = items[0]
            self.list_widget.blockSignals(True)  # 防止触发死循环
            first_selected_item.setSelected(False)
            self.list_widget.blockSignals(False)