from PySide6.QtWidgets import (
    QWidget, QHBoxLayout, QVBoxLayout, QLabel,
    QTextEdit, QFileDialog, QMessageBox
)
from PySide6.QtCore import Qt
from ui.components import PrimaryButton
from core.i18n import _, i18n
from core.snapshot_manager import SnapshotManager
from app.snapshot_list_widget import SnapshotListWidget
from core.merge_utils import three_way_merge, merge_documents
import os


class SnapshotMergePage(QWidget):
    """UI for merging snapshots."""

    def __init__(self, file_path: str, snapshot_manager: SnapshotManager, parent=None):
        super().__init__(parent)
        self.file_path = file_path
        self.manager = snapshot_manager
        self.doc_name = os.path.basename(file_path)

        self.base_path = ""
        self.remote_file = ""
        self.remote_ext = ""
        self.target_path = ""
        self.merged_text = ""

        # left list
        left_widget = QWidget()
        left_layout = QVBoxLayout(left_widget)
        self.label = QLabel(_("🧩 {name} 快照合并").format(name=self.doc_name))
        self.list_widget = SnapshotListWidget(file_path, single_selection=True)
        self.list_widget.setProperty("class", "snapshot-list")
        self.base_lbl = QLabel()
        self.base_lbl.setStyleSheet("font-size:11px;color:gray;")
        self.target_lbl = QLabel()
        self.target_lbl.setStyleSheet("font-size:11px;color:gray;")
        self.import_btn = PrimaryButton(_("导入待合并文档"))
        self.diff_btn = PrimaryButton(_("查看差异"))
        self.preview_btn = PrimaryButton(_("预览合并"))
        self.export_btn = PrimaryButton(_("导出合并结果"))
        self.export_btn.setFixedHeight(28)
        self.export_btn.setEnabled(False)
        left_layout.addWidget(self.label)
        left_layout.addWidget(self.base_lbl)
        left_layout.addWidget(self.target_lbl)
        left_layout.addWidget(self.list_widget, 1)
        left_layout.addStretch()
        left_layout.addWidget(self.import_btn)
        left_layout.addWidget(self.diff_btn)
        left_layout.addWidget(self.preview_btn)
        left_layout.addWidget(self.export_btn)

        # right preview
        self.preview = QTextEdit()
        self.preview.setReadOnly(True)
        self.hint_lbl = QLabel(_("👉 首先导入文档"))
        self.hint_lbl.setAlignment(Qt.AlignCenter)
        self.info_lbl = QLabel()
        self.info_lbl.setAlignment(Qt.AlignCenter)
        self.info_lbl.setStyleSheet("font-size:11px;color:gray;")

        # display widget
        self.display = QWidget()
        display_layout = QVBoxLayout(self.display)
        display_layout.addWidget(self.hint_lbl)
        display_layout.setContentsMargins(0, 0, 0, 0)

        hbox = QHBoxLayout(self)
        hbox.addWidget(left_widget, 1)
        hbox.addWidget(self.display, 2)
        self.setLayout(hbox)

        # signals
        self.diff_btn.clicked.connect(self.show_diff)
        self.preview_btn.clicked.connect(self.preview_merged)
        self.import_btn.clicked.connect(self.import_document)
        self.export_btn.clicked.connect(self.export_result)
        self.manager.snapshot_created.connect(self.load_snapshots)
        self.manager.snapshot_deleted.connect(self.load_snapshots)

        i18n.language_changed.connect(self.retranslate_ui)

    # ------------------------------------------------------------------ actions
    def load_snapshots(self):
        self.list_widget.load_snapshots()

    def import_document(self):
        file_path, selected_filter = QFileDialog.getOpenFileName(
            self, _("选择文档"), "", _("文档 (*.txt *.docx);;所有文件 (*)")
        )
        if file_path:
            self.remote_file = file_path
            self.remote_ext = os.path.splitext(file_path)[1].lower()
            self.base_path = ""
            self.target_path = ""
            self.merged_text = ""
            self.export_btn.setEnabled(False)
            self.base_lbl.clear()
            self.target_lbl.clear()
            self.hint_lbl.setText(_("👉 选择基准快照并点击“查看差异”"))

    def show_diff(self):
        if not self.remote_file:
            QMessageBox.warning(self, _("提示"), _("请选择合并文档"))
            return
        item = self.list_widget.currentItem()
        if item is None:
            QMessageBox.warning(self, _("提示"), _("请选择基准快照"))
            return
        self.base_path = item.data(1000)
        base_title = self._snapshot_title(self.base_path)
        remote_title = os.path.basename(self.remote_file)
        self.base_lbl.setText(f"{_('基准快照：')}{base_title}")
        try:
            diff_result = self.manager.compare_snapshots(self.base_path, self.remote_file)
            if diff_result.structured:
                from app.widgets.parallel_diff_view import ParallelDiffView
                viewer = ParallelDiffView(base_title, remote_title, self)
                viewer.load_chunks(diff_result.structured)
                viewer.left.setProperty("class", "diff-pane")
                viewer.right.setProperty("class", "diff-pane")
            else:
                from app.diff_viewer_widget import DiffViewerWidget
                viewer = DiffViewerWidget(self)
                viewer.set_diff_content(diff_result.raw or _("两个快照无差异。"))
            info = f"{_('基准快照：')}{base_title}\n{_('待合并文档：')}{remote_title}"
            self._set_display_widget(viewer, info)
            self.hint_lbl.setText(_("👉 选择合并目标快照并点击“预览合并”"))
        except Exception as e:
            err = QLabel(_("对比失败：{e}").format(e=e))
            err.setAlignment(Qt.AlignCenter)
            self._set_display_widget(err)

    def preview_merged(self):
        if not self.remote_file:
            QMessageBox.warning(self, _("提示"), _("请选择合并文档"))
            return
        item = self.list_widget.currentItem()
        if item is None:
            QMessageBox.warning(self, _("提示"), _("请选择合并目标"))
            return
        self.target_path = item.data(1000)
        target_title = self._snapshot_title(self.target_path)
        self.target_lbl.setText(f"{_('合并目标快照：')}{target_title}")
        try:
            base_text = self.manager.get_snapshot_content(self.base_path)
            local_text = self.manager.get_snapshot_content(self.target_path)
            remote_text = self.manager.get_snapshot_content(self.remote_file)
            self.merged_text = three_way_merge(base_text, local_text, remote_text)
            self.preview.setPlainText(self.merged_text)
            base_title = self._snapshot_title(self.base_path)
            remote_title = os.path.basename(self.remote_file)
            info = (
                f"{_('基准快照：')}{base_title}\n"
                f"{_('合并目标快照：')}{target_title}\n"
                f"{_('待合并文档：')}{remote_title}"
            )
            self._set_display_widget(self.preview, info)
            self.export_btn.setEnabled(True)
        except Exception as e:
            err = QLabel(_("合并失败：{e}").format(e=e))
            err.setAlignment(Qt.AlignCenter)
            self._set_display_widget(err)
            self.export_btn.setEnabled(False)

    def _set_display_widget(self, widget: QWidget, info: str | None = None):
        layout = self.display.layout()  # type: QVBoxLayout
        for i in reversed(range(layout.count())):
            item = layout.itemAt(i)
            w = item.widget()
            if w is not None:
                w.setParent(None)
        if info:
            self.info_lbl.setText(info)
        else:
            self.info_lbl.clear()
        layout.addWidget(widget)
        if info:
            layout.addWidget(self.info_lbl)

    def export_result(self):
        if not self.merged_text:
            return
        if self.remote_ext == ".docx":
            filter_str = _("Word 文档 (*.docx);;所有文件 (*)")
        elif self.remote_ext == ".txt":
            filter_str = _("文本文件 (*.txt);;所有文件 (*)")
        else:
            filter_str = _("文档 (*.txt *.docx);;所有文件 (*)")

        save_path, selected_filter = QFileDialog.getSaveFileName(
            self, _("保存合并文档"), "", filter_str
        )
        if save_path:
            try:
                if not os.path.splitext(save_path)[1]:
                    save_path += self.remote_ext or ".txt"
                merge_documents(self.base_path, self.target_path, self.remote_file, save_path)
                QMessageBox.information(self, _("成功"), _("已导出合并文档"))
            except Exception as e:
                QMessageBox.critical(self, _("错误"), _("导出失败：{e}").format(e=e))

    # ------------------------------------------------------- i18n
    def retranslate_ui(self):
        self.label.setText(_("🧩 {name} 快照合并").format(name=self.doc_name))
        self.import_btn.setText(_("导入待合并文档"))
        self.diff_btn.setText(_("查看差异"))
        self.preview_btn.setText(_("预览合并"))
        self.export_btn.setText(_("导出合并结果"))
        if not self.remote_file:
            self.hint_lbl.setText(_("👉 首先导入文档"))
        elif not self.base_path:
            self.hint_lbl.setText(_("👉 选择基准快照并点击“查看差异”"))
        else:
            self.hint_lbl.setText(_("👉 选择合并目标快照并点击“预览合并”"))
        if self.base_path:
            self.base_lbl.setText(f"{_('基准快照：')}{self._snapshot_title(self.base_path)}")
        else:
            self.base_lbl.clear()
        if self.target_path:
            self.target_lbl.setText(f"{_('合并目标快照：')}{self._snapshot_title(self.target_path)}")
        else:
            self.target_lbl.clear()

    def _snapshot_title(self, path: str) -> str:
        versions = self.manager.list_snapshots(self.doc_name)
        for v in versions:
            if v.get("snapshot_path") == path:
                ts = v.get("timestamp", "")
                remark = v.get("remark") or os.path.basename(path)
                return f"{ts} – {remark}" if remark else ts
        return os.path.basename(path)

