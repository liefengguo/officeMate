from PyQt5.QtWidgets import QWidget, QVBoxLayout, QLabel, QLineEdit, QPushButton, QMessageBox, QListWidgetItem  # if needed (not used here)
from core.snapshot_manager import SnapshotManager
from app.diff_viewer_widget import DiffViewerWidget
import os
class SnapshotPage(QWidget):
    """页面通过共享的 SnapshotManager 进行快照操作"""
    def __init__(self, file_path, snapshot_manager: SnapshotManager, parent=None):
        super().__init__(parent)
        self.file_path = file_path
        self.manager = snapshot_manager

        layout = QVBoxLayout()

        self.label = QLabel("📸 创建新快照")
        self.remark_input = QLineEdit()
        self.remark_input.setPlaceholderText("请输入快照备注（可选）")
        self.create_button = QPushButton("创建快照")

        self.compare_button = QPushButton("对比当前文档与最新快照")
        self.diff_result_view = DiffViewerWidget()

        layout.addWidget(self.label)
        layout.addWidget(self.remark_input)
        layout.addWidget(self.create_button)
        layout.addWidget(self.compare_button)
        layout.addWidget(self.diff_result_view)
        layout.addStretch()

        self.setLayout(layout)

        self.create_button.clicked.connect(self.create_snapshot)
        self.compare_button.clicked.connect(self.compare_with_latest)

    def create_snapshot(self):
        remark = self.remark_input.text()
        try:
            info = self.manager.create_snapshot(self.file_path, remark=remark)
            QMessageBox.information(self, "成功", f"快照已创建！\n时间：{info['timestamp']}")
            self.remark_input.clear()

        except Exception as e:
            QMessageBox.critical(self, "错误", f"创建快照失败：{str(e)}")

    def compare_with_latest(self):
        try:
            doc_name = os.path.basename(self.file_path)
            versions = self.manager.list_snapshots(doc_name)
            if not versions:
                self.diff_result_view.set_diff_content("没有可用的快照进行对比。")
                return

            latest_version = sorted(versions, key=lambda v: v.get("timestamp", ""), reverse=True)[0]
            latest_snapshot_path = latest_version.get("snapshot_path")

            diff_result = self.manager.compare_snapshots(latest_snapshot_path, self.file_path)

            if not diff_result.strip():
                self.diff_result_view.set_diff_content("当前文档与最新快照没有任何差异。")
            else:
                self.diff_result_view.set_diff_content(diff_result)

        except Exception as e:
            self.diff_result_view.set_diff_content(f"对比失败：{str(e)}")
