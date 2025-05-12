import os
from PyQt5.QtWidgets import QWidget, QVBoxLayout, QLabel, QPushButton, QMessageBox
from core.snapshot_manager import SnapshotManager
from PyQt5.QtWidgets import QPlainTextEdit, QListWidgetItem
from app.snapshot_list_widget import SnapshotListWidget
from app.diff_viewer_widget import DiffViewerWidget
from app.widgets.paragraph_diff_viewer import ParagraphDiffViewer

class SnapshotComparePage(QWidget):
    def __init__(self, file_path, parent=None, snapshot_manager: SnapshotManager = None):
        if isinstance(parent, SnapshotManager) and snapshot_manager is None:
            # Handle legacy call order: (file_path, snapshot_manager)
            snapshot_manager = parent
            parent = None
        super().__init__(parent)

        # ensure we have a manager instance
        self.manager: SnapshotManager = snapshot_manager

        self.file_path = file_path
        # 同步刷新：监听快照增删信号
        self.manager.snapshot_created.connect(self.load_snapshots)
        self.manager.snapshot_deleted.connect(self.load_snapshots)
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

        self.diff_viewer = DiffViewerWidget()

        self.layout.addWidget(self.diff_viewer)

    def load_snapshots(self):
        """重新加载快照数据（使用 SnapshotManager 列表接口）"""
        self.list_widget.clear()
        versions = self.manager.list_snapshots(self.doc_name)
        if not versions:
            self.list_widget.addItem("暂无快照记录")
            return
        for v in versions:
            path = v.get("snapshot_path")
            title = v.get("remark", "") or os.path.basename(path)
            timestamp = v.get("timestamp", "")
            display = f"{title}\n{timestamp}"
            item = QListWidgetItem(display)
            item.setData(1000, path)
            self.list_widget.addItem(item)
        # 清空旧 diff
        # self.diff_viewer.set_diff_content("")
        if isinstance(self.diff_viewer, DiffViewerWidget):
            self.diff_viewer.set_diff_content("")
        else:
            # 若当前是 ParagraphDiffViewer → 切回空文本 viewer
            new_v = DiffViewerWidget()
            new_v.set_diff_content("")
            self.layout.replaceWidget(self.diff_viewer, new_v)
            self.diff_viewer.deleteLater()
            self.diff_viewer = new_v

    def compare_snapshots(self):
        items = self.list_widget.selectedItems()
        if len(items) != 2:
            QMessageBox.warning(self, "提示", "请选择两个快照进行对比")
            return

        versions = self.manager.list_snapshots(self.doc_name)

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
            diff_result = self.manager.compare_snapshots(base_path, latest_path)

            # Choose appropriate viewer
            if hasattr(diff_result, "structured") and diff_result.structured:
                new_viewer = ParagraphDiffViewer(diff_result.structured)
            else:
                new_viewer = DiffViewerWidget()
                raw_text = getattr(diff_result, "raw", str(diff_result))
                new_viewer.set_diff_content(raw_text)

            # Replace old viewer
            self.layout.replaceWidget(self.diff_viewer, new_viewer)
            self.diff_viewer.deleteLater()
            self.diff_viewer = new_viewer

        except Exception as e:
            error_viewer = DiffViewerWidget()
            error_viewer.set_diff_content(f"对比失败：{str(e)}")
            self.layout.replaceWidget(self.diff_viewer, error_viewer)
            self.diff_viewer.deleteLater()
            self.diff_viewer = error_viewer

    def check_selection_limit(self):
        items = self.list_widget.selectedItems()
        if len(items) > 2:
            first_selected_item = items[0]
            self.list_widget.blockSignals(True)  # 防止触发死循环
            first_selected_item.setSelected(False)
            self.list_widget.blockSignals(False)