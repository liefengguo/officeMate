# app/snapshot_compare_page.py
import os
from functools import partial
from PyQt5.QtCore import Qt
from PyQt5.QtWidgets import (
    QWidget, QHBoxLayout, QVBoxLayout, QLabel,
    QListWidgetItem, QMessageBox
)
from ui.components import PrimaryButton

from core.snapshot_manager import SnapshotManager
from app.snapshot_list_widget import SnapshotListWidget
# from app.widgets.paragraph_diff_table_view import ParagraphDiffTableView
from app.widgets.parallel_diff_view import ParallelDiffView
from app.diff_viewer_widget import DiffViewerWidget
from app.widgets.snapshot_panels import SnapshotDisplayPanel


class SnapshotComparePage(QWidget):
    """
    快照对比页
    左侧(中间列)：快照多选列表 + “对比”按钮
    右侧       ：显示 ParagraphDiffTableView / DiffViewerWidget
    """

    def __init__(self, file_path, parent=None, snapshot_manager: SnapshotManager = None):
        # 兼容老调用顺序
        if isinstance(parent, SnapshotManager) and snapshot_manager is None:
            snapshot_manager = parent
            parent = None
        super().__init__(parent)

        self.manager: SnapshotManager = snapshot_manager
        self.file_path = file_path
        self.doc_name = os.path.basename(file_path)

        # ------------------------ 左侧交互区 ------------------------ #
        mid_widget = QWidget()
        mid_layout = QVBoxLayout(mid_widget)
        self.label = QLabel(f"🔍 {self.doc_name} 快照对比")
        self.list_widget = SnapshotListWidget(file_path, single_selection=False)
        self.list_widget.setProperty("class", "snapshot-list")
        self.compare_button = PrimaryButton("对比选中的两个快照")
        self.compare_button.setFixedHeight(28)
        mid_layout.addWidget(self.label)
        mid_layout.addWidget(self.list_widget, 1)
        mid_layout.addWidget(self.compare_button)
        mid_layout.addStretch()

        # ------------------------ 右侧显示区 ------------------------ #
        self.display_panel = SnapshotDisplayPanel()
        hint_lbl = QLabel("👉 请选择两个快照后点击“对比”")
        hint_lbl.setAlignment(Qt.AlignCenter)
        self.display_panel.set_widget(hint_lbl)

        # ------------------------ 主水平布局 ------------------------ #
        hbox = QHBoxLayout(self)
        hbox.addWidget(mid_widget, 1)
        hbox.addWidget(self.display_panel, 2)
        self.setLayout(hbox)

        # ------------------------ 信号连接 ------------------------ #
        self.manager.snapshot_created.connect(self.load_snapshots)
        self.manager.snapshot_deleted.connect(self.load_snapshots)
        self.compare_button.clicked.connect(self.compare_snapshots)
        self.list_widget.itemSelectionChanged.connect(self.check_selection_limit)

        self.load_snapshots()

    # ---------------------------------------------------------------- list
    def load_snapshots(self):
        """重新加载快照数据"""
        self.list_widget.clear()
        versions = self.manager.list_snapshots(self.doc_name)
        if not versions:
            self.list_widget.addItem("暂无快照记录")
            empty_lbl = QLabel("📭 没有快照可用")
            empty_lbl.setAlignment(Qt.AlignCenter)
            self.display_panel.set_widget(empty_lbl)
            return

        for v in sorted(versions, key=lambda x: x.get("timestamp", ""), reverse=True):
            path = v.get("snapshot_path")
            title = v.get("remark", "") or os.path.basename(path)
            ts = v.get("timestamp", "")
            display = f"{title}\n{ts}"
            item = QListWidgetItem(display)
            item.setData(Qt.UserRole, path)
            self.list_widget.addItem(item)

        # 清空右侧旧内容
        reset_lbl = QLabel("👉 请选择两个快照后点击“对比”")
        reset_lbl.setAlignment(Qt.AlignCenter)
        self.display_panel.set_widget(reset_lbl)

    # ---------------------------------------------------------------- compare
    def compare_snapshots(self):
        items = self.list_widget.selectedItems()
        if len(items) != 2:
            QMessageBox.warning(self, "提示", "请选择两个快照进行对比")
            return

        paths = [it.data(Qt.UserRole) for it in items]
        versions = self.manager.list_snapshots(self.doc_name)

        meta_map = {v["snapshot_path"]: v for v in versions}
        try:
            v1, v2 = (meta_map[p] for p in paths)
        except KeyError:
            QMessageBox.warning(self, "错误", "读取快照信息失败")
            return

        # 按时间排序：旧 -> 新
        if v1["timestamp"] > v2["timestamp"]:
            base_path, latest_path = v2["snapshot_path"], v1["snapshot_path"]
        else:
            base_path, latest_path = v1["snapshot_path"], v2["snapshot_path"]

        base_meta   = meta_map.get(base_path, {})
        latest_meta = meta_map.get(latest_path, {})

        def _title(meta: dict) -> str:
            ts     = meta.get("timestamp", "")
            remark = meta.get("remark") or os.path.basename(meta.get("snapshot_path", ""))  # fallback
            return f"{ts} – {remark}" if remark else ts

        left_title  = _title(base_meta)
        right_title = _title(latest_meta)

        try:
            diff_result = self.manager.compare_snapshots(base_path, latest_path)

            if diff_result.structured:
                # viewer = ParagraphDiffTableView(diff_result.structured, self)
                viewer = ParallelDiffView(left_title, right_title, self)
                viewer.load_chunks(diff_result.structured)
                viewer.left.setProperty("class", "diff-pane")
                viewer.right.setProperty("class", "diff-pane")
            else:
                viewer = DiffViewerWidget(self)
                viewer.set_diff_content(diff_result.raw or "两个快照无差异。")

            self.display_panel.set_widget(viewer)

        except Exception as e:
            err = DiffViewerWidget(self)
            err.set_diff_content(f"对比失败：{e}")
            self.display_panel.set_widget(err)

    # ---------------------------------------------------------------- utils
    def check_selection_limit(self):
        """只保留最新的两条选中"""
        items = self.list_widget.selectedItems()
        while len(items) > 2:
            items[0].setSelected(False)
            items = self.list_widget.selectedItems()