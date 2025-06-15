from PyQt5.QtWidgets import (
    QWidget, QVBoxLayout, QListWidget, QLabel, QMessageBox, QAbstractItemView, QListWidgetItem
)
from PyQt5.QtCore import Qt
from core.i18n import _, i18n
from ui.components import FlatButton, PrimaryButton
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
        self.setWindowTitle(_("快照历史"))
        self.setMinimumSize(400, 300)

        self.doc_name = os.path.basename(file_path)
        self.manager = snapshot_manager
        self.manager.snapshot_created.connect(self.load_snapshots)
        self.manager.snapshot_deleted.connect(self.load_snapshots)

        self.layout = QVBoxLayout()
        self.back_button = FlatButton(_("← 返回主页"))
        self.back_button.clicked.connect(self.go_back)
        self.layout.addWidget(self.back_button)

        self.label = QLabel(_("文档：{name}").format(name=self.doc_name))
        self.list_widget = QListWidget()
        self.list_widget.setProperty("class", "snapshot-list")
        self.compare_button = PrimaryButton(_("对比选中快照"))
        self.compare_button.setFixedHeight(28)
        self.compare_button.clicked.connect(self.compare_snapshots)
        self.preview_button = FlatButton(_("查看快照内容"))
        self.preview_button.clicked.connect(self.preview_snapshots)
        self.list_widget.setSelectionMode(QAbstractItemView.MultiSelection)
        self.layout.addWidget(self.label)
        self.layout.addWidget(self.list_widget)
        self.layout.addWidget(self.compare_button)
        self.layout.addWidget(self.preview_button)
        self.setLayout(self.layout)

        self.preview_windows = []
        self.load_snapshots()

        i18n.language_changed.connect(self.retranslate_ui)

    def go_back(self):
        if self.parent_window:
            self.parent_window.go_back_to_dashboard()

    def load_snapshots(self):
        """刷新快照列表"""
        self.list_widget.clear()

        versions = self.manager.list_snapshots(self.doc_name)
        if not versions:
            self.list_widget.addItem(_("暂无快照记录"))
            self.list_widget.setDisabled(True)
            return

        self.list_widget.setDisabled(False)
        for v in versions:
            time_str = v.get("timestamp", _("未知时间"))
            remark   = v.get("remark", "")
            display  = f"{time_str}  {remark}".strip()
            item = QListWidgetItem(display)
            # 将快照实际路径存入 UserRole，避免再 split text。
            item.setData(Qt.UserRole, v.get("snapshot_path", ""))
            self.list_widget.addItem(item)

    def preview_snapshots(self):
        items = self.list_widget.selectedItems()
        if not items:
            QMessageBox.information(self, _("提示"), _("请至少选择一个快照进行预览"))
            return

        for item in items:
            file_path = item.data(Qt.UserRole)
            if file_path:
                preview = PreviewWindow(file_path)
                self.preview_windows.append(preview)  # Prevent GC
                preview.show()

    def compare_snapshots(self):
        items = self.list_widget.selectedItems()
        paths = [it.data(Qt.UserRole) for it in items if it.data(Qt.UserRole)]
        if len(paths) != 2:
            QMessageBox.warning(self, _("选择错误"), _("请选择两个快照进行对比"))
            return

        diff = self.manager.compare_snapshots(paths[0], paths[1])
        viewer = DiffViewer(diff_text=diff)
        viewer.show()

    # ------------------------------------------------------- i18n
    def retranslate_ui(self):
        self.setWindowTitle(_("快照历史"))
        self.back_button.setText(_("← 返回主页"))
        self.label.setText(_("文档：{name}").format(name=self.doc_name))
        self.compare_button.setText(_("对比选中快照"))
        self.preview_button.setText(_("查看快照内容"))
        self.load_snapshots()
