from __future__ import annotations

import os
from PySide6.QtCore import Qt
from PySide6.QtWidgets import (
    QWidget, QHBoxLayout, QVBoxLayout, QLabel, QListWidget, QListWidgetItem
)
from core.i18n import _, i18n
from core.snapshot_manager import SnapshotManager
from app.widgets.snapshot_panels import SnapshotDisplayPanel
from app.widgets.parallel_diff_view import ParallelDiffView
from app.diff_viewer_widget import DiffViewerWidget


class SnapshotTimelinePage(QWidget):
    """Display snapshots in a timeline and show diffs between versions."""

    def __init__(self, file_path: str, snapshot_manager: SnapshotManager, parent: QWidget | None = None) -> None:
        super().__init__(parent)
        self.file_path = file_path
        self.manager = snapshot_manager
        self.doc_name = os.path.basename(file_path)

        # --- Left column: label + list ---
        left_widget = QWidget()
        left_layout = QVBoxLayout(left_widget)
        self.label = QLabel(_("📈 {name} 的快照时间线").format(name=self.doc_name))
        left_layout.addWidget(self.label)
        self.list_widget = QListWidget()
        self.list_widget.setProperty("class", "snapshot-list")
        self.list_widget.itemClicked.connect(self.show_diff)
        left_layout.addWidget(self.list_widget, 1)

        # --- Right display panel ---
        self.display_panel = SnapshotDisplayPanel()
        self.hint_label = QLabel(_("👉 从左侧选择快照查看变更"))
        self.hint_label.setAlignment(Qt.AlignCenter)
        self.display_panel.set_widget(self.hint_label)

        layout = QHBoxLayout(self)
        layout.addWidget(left_widget, 1)
        layout.addWidget(self.display_panel, 2)
        self.setLayout(layout)

        self.versions: list[dict] = []
        self.load_snapshots()
        i18n.language_changed.connect(self.retranslate_ui)

    # ---------------------------------------------------------------- list
    def load_snapshots(self) -> None:
        self.list_widget.clear()
        self.versions = self.manager.list_snapshots(self.doc_name)
        if not self.versions:
            self.list_widget.addItem(_("暂无快照记录"))
            return

        for v in self.versions:
            title = v.get("remark", "") or os.path.basename(v.get("snapshot_path", ""))
            ts = v.get("timestamp", "")
            display = f"{title}\n{ts}"
            item = QListWidgetItem(display)
            item.setData(Qt.UserRole, v)
            self.list_widget.addItem(item)

    # ---------------------------------------------------------------- diff
    def show_diff(self, item: QListWidgetItem) -> None:
        meta = item.data(Qt.UserRole)
        if not isinstance(meta, dict):
            return
        idx = self.list_widget.row(item)
        if idx + 1 >= len(self.versions):
            lbl = QLabel(_("没有更早的快照用于比较。"))
            lbl.setAlignment(Qt.AlignCenter)
            self.display_panel.set_widget(lbl)
            self.hint_label = lbl
            return

        base_meta = self.versions[idx + 1]
        latest_meta = meta

        def _title(m: dict) -> str:
            ts = m.get("timestamp", "")
            remark = m.get("remark") or os.path.basename(m.get("snapshot_path", ""))
            return f"{ts} – {remark}" if remark else ts

        base_path = base_meta["snapshot_path"]
        latest_path = latest_meta["snapshot_path"]

        try:
            diff_result = self.manager.compare_snapshots(base_path, latest_path)
            if diff_result.structured:
                viewer = ParallelDiffView(_title(base_meta), _title(latest_meta), self)
                viewer.load_chunks(diff_result.structured)
                viewer.left.setProperty("class", "diff-pane")
                viewer.right.setProperty("class", "diff-pane")
            else:
                viewer = DiffViewerWidget(self)
                viewer.set_diff_content(diff_result.raw or _("两个快照无差异。"))
            self.display_panel.set_widget(viewer)
            self.hint_label = None
        except Exception as e:
            err = DiffViewerWidget(self)
            err.set_diff_content(_("对比失败：{e}").format(e=e))
            self.display_panel.set_widget(err)
            self.hint_label = None

    # ------------------------------------------------------- i18n
    def retranslate_ui(self) -> None:
        if self.hint_label:
            self.hint_label.setText(_("👉 从左侧选择快照查看变更"))
        self.label.setText(_("📈 {name} 的快照时间线").format(name=self.doc_name))
        self.load_snapshots()
