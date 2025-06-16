# app/history_page.py
import os
from functools import partial
from html import escape

from PyQt5.QtCore import Qt, QSettings
from PyQt5.QtWidgets import (
    QWidget, QHBoxLayout, QVBoxLayout, QLabel, QListWidget, QListWidgetItem,
    QMessageBox
)
import sip
from core.i18n import _, i18n
from ui.components import PrimaryButton, FlatButton

from core.snapshot_manager import SnapshotManager
from app.widgets.snapshot_panels import SnapshotDisplayPanel           # 新增
from app.diff_viewer_widget import DiffViewerWidget
from core.snapshot_loaders.loader_registry import LoaderRegistry
from core.diff_strategies.paragraph_strategy import ParagraphDiffStrategy
from app.widgets.parallel_diff_view import _tokens_to_html, MONO_STYLE


class HistoryPage(QWidget):
    """快照历史页：中间快照列表 + 右侧预览 / diff"""

    def __init__(self, file_path, snapshot_manager: SnapshotManager, parent=None):
        super().__init__(parent)
        self.file_path = file_path
        self.sm = snapshot_manager
        self.doc_name = os.path.basename(file_path)

        # ---------- 中间列：快照列表 + 操作按钮 ----------
        mid_widget = QWidget()
        mid_layout = QVBoxLayout(mid_widget)
        self.label = QLabel(_("📜 {name} 的快照历史").format(name=self.doc_name))
        self.list_widget = QListWidget()
        self.list_widget.setProperty("class", "snapshot-list")
        self.list_widget.setSelectionMode(QListWidget.SingleSelection)

        self.btn_restore = FlatButton(_("恢复所选快照"))
        self.btn_restore.setFixedHeight(28)
        self.btn_restore.clicked.connect(self.restore_selected)

        mid_layout.addWidget(self.label)
        mid_layout.addWidget(self.list_widget, 1)
        mid_layout.addWidget(self.btn_restore)
        self.btn_delete = PrimaryButton(_("删除所选快照"))
        self.btn_delete.setFixedHeight(28)
        self.btn_delete.clicked.connect(self.delete_selected)
        mid_layout.addWidget(self.btn_delete)
        mid_layout.addStretch()

        # ---------- 右侧显示面板 ----------
        self.display_panel = SnapshotDisplayPanel()

        # ---------- 主水平布局 ----------
        hbox = QHBoxLayout(self)
        hbox.addWidget(mid_widget, 1)
        hbox.addWidget(self.display_panel, 2)
        self.setLayout(hbox)

        # ---------- 连接信号 ----------
        self.list_widget.itemSelectionChanged.connect(self.handle_selection_changed)
        self.list_widget.itemClicked.connect(self.preview_selected)
        self.sm.snapshot_created.connect(self.load_snapshots)
        self.sm.snapshot_deleted.connect(self.load_snapshots)

        # 初始加载
        self.load_snapshots()
        self.hint = QLabel(_("👉 选择快照查看内容或恢复"))
        self.hint.setAlignment(Qt.AlignCenter)
        self.display_panel.set_widget(self.hint)

        i18n.language_changed.connect(self.retranslate_ui)

    # ---------------------------------------------------------------- list
    def load_snapshots(self):
        self.list_widget.clear()
        versions = self.sm.list_snapshots(self.doc_name)
        if not versions:
            self.list_widget.addItem(_("暂无快照记录"))
            return

        versions.sort(key=lambda v: v.get("timestamp", ""), reverse=True)
        for v in versions:
            title = v.get("remark", "") or os.path.basename(v.get("snapshot_path", ""))
            ts = v.get("timestamp", "")
            text = f"{title}\n{ts}"
            list_item = QListWidgetItem(text)
            list_item.setData(Qt.UserRole, v)
            self.list_widget.addItem(list_item)

    def handle_selection_changed(self):
        # no custom widget highlighting needed
        pass



    def restore_selected(self):
        items = self.list_widget.selectedItems()
        if not items:
            QMessageBox.information(self, _("提示"), _("请先选择要恢复的快照"))
            return
        meta = items[0].data(Qt.UserRole)
        if not isinstance(meta, dict):
            QMessageBox.warning(self, _("提示"), _("无法获取快照信息"))
            return
        self.sm.restore_snapshot(meta)

    def delete_selected(self):
        row = self.list_widget.currentRow()          # 先拿行号
        if row < 0:
            QMessageBox.information(self, _("提示"), _("请先选择要删除的快照"))
            return

        meta_item = self.list_widget.item(row)
        meta = meta_item.data(Qt.UserRole)
        if not isinstance(meta, dict):
            QMessageBox.warning(self, _("提示"), _("无法获取快照信息"))
            return

        # 二次确认
        if QMessageBox.question(self, _("删除快照"),
                                _("确定删除该快照？"),
                                QMessageBox.Yes | QMessageBox.No) != QMessageBox.Yes:
            return

        # 删除数据文件 / 元数据
        self.sm.delete_snapshot(self.doc_name, meta)

        # 解除预览 & 从列表移除
        del_lbl = QLabel(_("✂️ 已删除快照"))
        del_lbl.setAlignment(Qt.AlignCenter)
        self.display_panel.set_widget(del_lbl)
        # self.list_widget.takeItem(row)               # 直接按行删除，避免引用 item
    # ---------------------------------------------------------------- view / delete
    def _build_preview_widget(self, path: str):
        """根据文件类型构建预览控件"""
        try:
            ext = os.path.splitext(path)[1]
            loader = LoaderRegistry.get_loader(ext)

            from PyQt5.QtWidgets import QTextBrowser

            if loader and hasattr(loader, "load_structured"):
                compact = QSettings().value("diff/compact_style", False, type=bool)
                paragraphs = ParagraphDiffStrategy._paragraph_texts(loader, path)
                width = len(str(len(paragraphs)))
                style = f"display:inline-block;width:{width}ch;text-align:right;"
                numbered = [
                    f'<span class="ln" style="{style}">{i}</span> '
                    + (_tokens_to_html(p, show_tokens=not compact) or "&nbsp;")
                    for i, p in enumerate(paragraphs, 1)
                ]
                html = f"<div style='{MONO_STYLE}'>" + "<br>".join(numbered) + "</div>"

                browser = QTextBrowser()
                browser.setProperty("class", "diff-pane")
                browser.setOpenExternalLinks(False)
                browser.setReadOnly(True)
                browser.setHtml(html)
                return browser

            else:
                if loader:
                    text = loader.get_text(path)
                else:
                    with open(path, "r", encoding="utf-8", errors="ignore") as f:
                        text = f.read()

                lines = text.splitlines()
                width = len(str(len(lines)))
                style = f"display:inline-block;width:{width}ch;text-align:right;"
                numbered = [
                    f'<span class="ln" style="{style}">{i}</span> {escape(line)}'
                    for i, line in enumerate(lines, 1)
                ]
                html = f"<div style='{MONO_STYLE}'>" + "<br>".join(numbered) + "</div>"

                browser = QTextBrowser()
                browser.setProperty("class", "diff-pane")
                browser.setOpenExternalLinks(False)
                browser.setReadOnly(True)
                browser.setHtml(html)
                return browser

        except Exception as e:
            err = QLabel(_("无法读取快照内容：{e}").format(e=e))
            err.setAlignment(Qt.AlignCenter)
            return err

    # ----------- new direct preview ------------
    def preview_selected(self, item):
        meta = item.data(Qt.UserRole)
        if not isinstance(meta, dict):
            return

        # ---- 构建正文预览组件 ----
        content_widget = self._build_preview_widget(meta["snapshot_path"])

        # ---- 包装：标题 + 正文 ----
        wrapper = QWidget()
        vbox = QVBoxLayout(wrapper)
        vbox.setContentsMargins(0, 0, 0, 0)
        vbox.setSpacing(4)

        remark = meta.get("remark") or os.path.basename(meta.get("snapshot_path", ""))
        ts     = meta.get("timestamp", "")
        header_lbl = QLabel(f"{remark}  –  {ts}")
        header_lbl.setProperty("class", "h3")

        vbox.addWidget(header_lbl, 0)
        vbox.addWidget(content_widget, 1)

        self.display_panel.set_widget(wrapper)

    # ------------------------------------------------------- i18n
    def retranslate_ui(self):
        self.label.setText(_("📜 {name} 的快照历史").format(name=self.doc_name))
        self.btn_restore.setText(_("恢复所选快照"))
        self.btn_delete.setText(_("删除所选快照"))
        if self.hint is not None and not sip.isdeleted(self.hint):
            self.hint.setText(_("👉 选择快照查看内容或恢复"))
        self.load_snapshots()
