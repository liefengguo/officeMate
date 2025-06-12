# app/snapshot_page.py
from PyQt5.QtWidgets import QWidget, QHBoxLayout, QLabel, QMessageBox
from PyQt5.QtCore import Qt

import os

from core.snapshot_manager import SnapshotManager
from app.widgets.snapshot_panels import SnapshotMiddlePanel, SnapshotDisplayPanel
from app.widgets.parallel_diff_view import ParallelDiffView
from app.diff_viewer_widget import DiffViewerWidget

class SnapshotPage(QWidget):
    """
    “添加快照”页：中间交互区(备注输入/按钮) + 右侧显示区(差异或提示)
    """

    def __init__(self, file_path: str, snapshot_manager: SnapshotManager, parent=None):
        super().__init__(parent)
        self.file_path = file_path
        self.manager = snapshot_manager

        # ---------- 中间交互面板（备注模式） ----------
        self.middle_panel = SnapshotMiddlePanel(mode="note")
        # ---------- 右侧显示面板 ----------
        self.display_panel = SnapshotDisplayPanel()

        # ---------- 主水平布局 ----------
        layout = QHBoxLayout(self)
        layout.addWidget(self.middle_panel, 1)   # stretch 1
        layout.addWidget(self.display_panel, 2)  # stretch 2
        self.setLayout(layout)

        # ---------- 连接信号 ----------
        self.middle_panel.snapshotCreated.connect(self.on_create_snapshot)
        self.middle_panel.compareRequested.connect(self.compare_with_latest)

        # 初始右侧提示
        hint_lbl = QLabel("👉 在左侧填写备注并点击“创建快照”")
        hint_lbl.setAlignment(Qt.AlignCenter)
        self.display_panel.set_widget(hint_lbl)

    # ----------------------------------------------------------------- 槽函数
    def on_create_snapshot(self, remark: str):
        try:
            info = self.manager.create_snapshot(self.file_path, remark=remark)
            QMessageBox.information(self, "成功", f"快照已创建！\n时间：{info['timestamp']}")
            # 清空备注输入框
            self.middle_panel.clear()
            # 更新右侧提示
            lbl = QLabel("✅ 快照已创建！")
            lbl.setAlignment(Qt.AlignCenter)
            self.display_panel.set_widget(lbl)
        except Exception as e:
            QMessageBox.critical(self, "错误", f"创建快照失败：{e}")

    def compare_with_latest(self):
        try:
            # 找到最新快照文件
            doc_name = os.path.basename(self.file_path)
            versions = self.manager.list_snapshots(doc_name)
            if not versions:
                warn_lbl = QLabel("⚠️ 没有可用快照进行对比")
                warn_lbl.setAlignment(Qt.AlignCenter)
                self.display_panel.set_widget(warn_lbl)
                return

            latest_version = max(versions, key=lambda v: v.get("timestamp", ""))
            latest_snapshot_path = latest_version["snapshot_path"]

            # 获取 diff 结果
            diff_result = self.manager.compare_snapshots(latest_snapshot_path, self.file_path)

            # 选择合适 viewer
            if diff_result.structured:
                # viewer = ParagraphDiffTableView(diff_result.structured, self)
                viewer = ParallelDiffView("历史对比", "最新文档", self)
                viewer.load_chunks(diff_result.structured)
                # ① 让左右浏览器走统一 QSS
                viewer.left.setProperty("class", "diff-pane")
                viewer.right.setProperty("class", "diff-pane")
            else:
                viewer = DiffViewerWidget(self)
                viewer.set_diff_content(diff_result.raw or "当前文档与最新快照没有任何差异。")

            self.display_panel.set_widget(viewer)

        except Exception as e:
            err_view = DiffViewerWidget(self)
            err_view.set_diff_content(f"对比失败：{e}")
            self.display_panel.set_widget(err_view)