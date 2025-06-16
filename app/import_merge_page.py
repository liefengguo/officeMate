import os
from typing import Optional
from PyQt5.QtWidgets import (
    QWidget, QHBoxLayout, QVBoxLayout, QLabel,
    QMessageBox, QFileDialog, QListWidgetItem
)
from PyQt5.QtCore import Qt

from ui.components import PrimaryButton
from core.snapshot_manager import SnapshotManager
from app.snapshot_list_widget import SnapshotListWidget
from app.diff_viewer_widget import DiffViewerWidget
from app.widgets.parallel_diff_view import ParallelDiffView
from app.widgets.snapshot_panels import SnapshotDisplayPanel
from core.i18n import _, i18n


class ImportMergePage(QWidget):
    """Page to import a document, compare with a base snapshot and merge to target."""

    def __init__(self, file_path: str, snapshot_manager: SnapshotManager, parent: Optional[QWidget] = None):
        super().__init__(parent)
        self.file_path = file_path
        self.manager = snapshot_manager
        self.doc_name = os.path.basename(file_path)

        # ---------- Left panel ----------
        left_widget = QWidget()
        left_layout = QVBoxLayout(left_widget)
        self.list_label = QLabel(_("快照列表："))
        self.list_widget = SnapshotListWidget(file_path, single_selection=True)

        self.import_btn = PrimaryButton(_("导入外部文档…"))
        self.import_btn.setFixedHeight(28)
        self.diff_btn = PrimaryButton(_("查看差异"))
        self.diff_btn.setFixedHeight(28)
        self.preview_btn = PrimaryButton(_("预览合并"))
        self.preview_btn.setFixedHeight(28)
        self.merge_btn = PrimaryButton(_("应用合并"))
        self.merge_btn.setFixedHeight(28)

        left_layout.addWidget(self.list_label)
        left_layout.addWidget(self.list_widget)
        left_layout.addWidget(self.import_btn)
        left_layout.addWidget(self.diff_btn)
        left_layout.addWidget(self.preview_btn)
        left_layout.addWidget(self.merge_btn)
        left_layout.addStretch(1)

        # ---------- Right display panel ----------
        self.display_panel = SnapshotDisplayPanel()
        self.hint_lbl = QLabel(_("👉 请选择基准快照并导入文档"))
        self.hint_lbl.setAlignment(Qt.AlignCenter)
        self.display_panel.set_widget(self.hint_lbl)

        hbox = QHBoxLayout(self)
        hbox.addWidget(left_widget, 1)
        hbox.addWidget(self.display_panel, 2)
        self.setLayout(hbox)

        # ---------- State ----------
        self._imported_path: Optional[str] = None
        self._base_path: Optional[str] = None
        self._target_meta: Optional[dict] = None
        self._preview_path: Optional[str] = None
        self._diff_ready = False

        # ---------- Signals ----------
        self.import_btn.clicked.connect(self.import_file)
        self.diff_btn.clicked.connect(self.compare_with_base)
        self.preview_btn.clicked.connect(self.preview_merge)
        self.merge_btn.clicked.connect(self.merge_into_target)
        i18n.language_changed.connect(self.retranslate_ui)

    # ---------------------------------------------------------------- utils
    def load_snapshots(self):
        self.list_widget.load_snapshots()

    def import_file(self):
        path, _selected = QFileDialog.getOpenFileName(self, _("选择对比文档"), "", "*")
        if path:
            self._imported_path = path

    def _selected_meta(self, item: QListWidgetItem) -> Optional[dict]:
        if not item:
            return None
        versions = self.manager.list_snapshots(self.doc_name)
        for v in versions:
            if v.get("snapshot_path") == item.data(1000):
                return v
        return None

    def compare_with_base(self):
        base_item = self.list_widget.currentItem()
        if not base_item or not self._imported_path:
            QMessageBox.information(self, _("提示"), _("请先选择基准快照并导入文档"))
            return
        self._base_path = base_item.data(1000)
        diff_result = self.manager.diff_engine.compare_files(self._base_path, self._imported_path)
        if diff_result.structured:
            viewer = ParallelDiffView(os.path.basename(self._base_path), os.path.basename(self._imported_path), self)
            viewer.load_chunks(diff_result.structured)
            viewer.left.setProperty("class", "diff-pane")
            viewer.right.setProperty("class", "diff-pane")
        else:
            viewer = DiffViewerWidget(self)
            viewer.set_diff_content(diff_result.raw or _("两个文档无差异。"))
        self.display_panel.set_widget(viewer)
        self.hint_lbl = None
        self._diff_ready = True

    def preview_merge(self):
        if not self._diff_ready:
            QMessageBox.information(self, _("提示"), _("请先完成基准差异查看"))
            return
        target_item = self.list_widget.currentItem()
        if not target_item:
            QMessageBox.information(self, _("提示"), _("请选择合并目标快照"))
            return
        meta = self._selected_meta(target_item)
        if not meta:
            QMessageBox.warning(self, _("错误"), _("无法获取目标快照信息"))
            return
        work_file = meta.get("file_path") or self.file_path
        try:
            patch_text, preview_path = self.manager.merge_into_work_file(
                self._base_path,
                self._imported_path,
                work_file,
                preview=True,
            )
            diff_result = self.manager.diff_engine.compare_files(work_file, preview_path)
            if diff_result.structured:
                viewer = ParallelDiffView(os.path.basename(work_file), os.path.basename(preview_path), self)
                viewer.load_chunks(diff_result.structured)
                viewer.left.setProperty("class", "diff-pane")
                viewer.right.setProperty("class", "diff-pane")
            else:
                viewer = DiffViewerWidget(self)
                viewer.set_diff_content(diff_result.raw or _("两个文档无差异。"))
            self.display_panel.set_widget(viewer)
            self._target_meta = meta
            self._preview_path = preview_path
            self.hint_lbl = None
        except Exception as e:
            QMessageBox.critical(self, _("预览失败"), str(e))

    def merge_into_target(self):
        if not self._base_path or not self._imported_path or not self._diff_ready:
            QMessageBox.information(self, _("提示"), _("请先完成差异查看"))
            return
        if self._target_meta is None:
            QMessageBox.information(self, _("提示"), _("请先预览合并效果"))
            return
        meta = self._target_meta
        work_file = meta.get("file_path") or self.file_path
        try:
            self.manager.merge_into_work_file(
                self._base_path,
                self._imported_path,
                work_file,
                preview=False,
            )
            QMessageBox.information(self, _("合并完成"), _("差异已应用到目标文档"))
            if self._preview_path and os.path.exists(self._preview_path):
                os.unlink(self._preview_path)
            self._preview_path = None
            self._target_meta = None
        except Exception as e:
            QMessageBox.critical(self, _("合并失败"), str(e))

    # ------------------------------------------------------- i18n
    def retranslate_ui(self):
        self.list_label.setText(_("快照列表："))
        self.import_btn.setText(_("导入外部文档…"))
        self.diff_btn.setText(_("查看差异"))
        self.preview_btn.setText(_("预览合并"))
        self.merge_btn.setText(_("应用合并"))
        if self.hint_lbl is not None:
            self.hint_lbl.setText(_("👉 请选择基准快照并导入文档"))
        self.load_snapshots()
