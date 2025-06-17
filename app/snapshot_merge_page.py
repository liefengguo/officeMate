from PySide6.QtWidgets import (
    QWidget, QHBoxLayout, QVBoxLayout, QLabel, QListWidgetItem,
    QTextEdit, QFileDialog, QMessageBox
)
from PySide6.QtCore import Qt
from ui.components import PrimaryButton
from core.i18n import _, i18n
from core.snapshot_manager import SnapshotManager
from app.snapshot_list_widget import SnapshotListWidget
from core.merge_utils import three_way_merge
import os


class SnapshotMergePage(QWidget):
    """UI for merging snapshots."""

    def __init__(self, file_path: str, snapshot_manager: SnapshotManager, parent=None):
        super().__init__(parent)
        self.file_path = file_path
        self.manager = snapshot_manager
        self.doc_name = os.path.basename(file_path)

        self.base_path = ""
        self.remote_path = ""
        self.target_path = ""
        self.merged_text = ""

        # left list
        left_widget = QWidget()
        left_layout = QVBoxLayout(left_widget)
        self.label = QLabel(_("🧩 {name} 快照合并").format(name=self.doc_name))
        self.list_widget = SnapshotListWidget(file_path, single_selection=True)
        self.list_widget.setProperty("class", "snapshot-list")
        self.export_btn = PrimaryButton(_("导出合并结果"))
        self.export_btn.setFixedHeight(28)
        self.export_btn.setEnabled(False)
        left_layout.addWidget(self.label)
        left_layout.addWidget(self.list_widget, 1)
        left_layout.addWidget(self.export_btn)
        left_layout.addStretch()

        # right preview
        self.preview = QTextEdit()
        self.preview.setReadOnly(True)
        self.hint_lbl = QLabel(_("👉 首先选择基准快照"))
        self.hint_lbl.setAlignment(Qt.AlignCenter)

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
        self.list_widget.itemClicked.connect(self.handle_click)
        self.export_btn.clicked.connect(self.export_result)
        self.manager.snapshot_created.connect(self.load_snapshots)
        self.manager.snapshot_deleted.connect(self.load_snapshots)

        i18n.language_changed.connect(self.retranslate_ui)

    # ------------------------------------------------------------------ actions
    def load_snapshots(self):
        self.list_widget.load_snapshots()

    def handle_click(self, item: QListWidgetItem):
        path = item.data(1000)
        if not path:
            return
        if not self.base_path:
            self.base_path = path
            self.hint_lbl.setText(_("👉 选择用于对比的快照"))
            return
        if not self.remote_path:
            self.remote_path = path
            self.show_diff()
            self.hint_lbl.setText(_("👉 选择合并目标快照"))
            return
        self.target_path = path
        self.preview_merged()

    def show_diff(self):
        try:
            diff_result = self.manager.compare_snapshots(self.base_path, self.remote_path)
            from app.diff_viewer_widget import DiffViewerWidget
            viewer = DiffViewerWidget(self)
            viewer.set_diff_content(diff_result.raw or _("两个快照无差异。"))
            self._set_display_widget(viewer)
        except Exception as e:
            err = QLabel(_("对比失败：{e}").format(e=e))
            err.setAlignment(Qt.AlignCenter)
            self._set_display_widget(err)

    def preview_merged(self):
        try:
            base_text = self.manager.get_snapshot_content(self.base_path)
            local_text = self.manager.get_snapshot_content(self.target_path)
            remote_text = self.manager.get_snapshot_content(self.remote_path)
            self.merged_text = three_way_merge(base_text, local_text, remote_text)
            self.preview.setPlainText(self.merged_text)
            self._set_display_widget(self.preview)
            self.export_btn.setEnabled(True)
        except Exception as e:
            err = QLabel(_("合并失败：{e}").format(e=e))
            err.setAlignment(Qt.AlignCenter)
            self._set_display_widget(err)
            self.export_btn.setEnabled(False)

    def _set_display_widget(self, widget: QWidget):
        layout = self.display.layout()  # type: QVBoxLayout
        for i in reversed(range(layout.count())):
            item = layout.itemAt(i)
            w = item.widget()
            if w is not None:
                w.setParent(None)
        layout.addWidget(widget)

    def export_result(self):
        if not self.merged_text:
            return
        save_path, _ = QFileDialog.getSaveFileName(
            self, _("保存合并文档"), "", _("文档 (*.txt);;所有文件 (*)")
        )
        if save_path:
            try:
                with open(save_path, "w", encoding="utf-8") as fp:
                    fp.write(self.merged_text)
                QMessageBox.information(self, _("成功"), _("已导出合并文档"))
            except Exception as e:
                QMessageBox.critical(self, _("错误"), _("导出失败：{e}").format(e=e))

    # ------------------------------------------------------- i18n
    def retranslate_ui(self):
        self.label.setText(_("🧩 {name} 快照合并").format(name=self.doc_name))
        self.export_btn.setText(_("导出合并结果"))
        if not self.base_path:
            self.hint_lbl.setText(_("👉 首先选择基准快照"))
        elif not self.remote_path:
            self.hint_lbl.setText(_("👉 选择用于对比的快照"))
        elif not self.target_path:
            self.hint_lbl.setText(_("👉 选择合并目标快照"))

