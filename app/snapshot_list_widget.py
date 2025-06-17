from PySide6.QtWidgets import QListWidget, QListWidgetItem
import os
from core.snapshot import SnapshotManager
from core.i18n import _, i18n

class SnapshotListWidget(QListWidget):
    def __init__(self, file_path, single_selection=True, parent=None):
        super().__init__(parent)
        self.file_path = file_path
        self.sm = SnapshotManager()

        # 设置单选 or 多选模式
        if single_selection:
            self.setSelectionMode(QListWidget.SingleSelection)
        else:
            self.setSelectionMode(QListWidget.MultiSelection)

        self.load_snapshots()

        i18n.language_changed.connect(self.load_snapshots)

    def load_snapshots(self):
        """加载快照数据到列表"""
        self.clear()
        doc_name = os.path.basename(self.file_path)
        versions = self.sm.version_db.get_versions(doc_name)

        if not versions:
            self.addItem(_("暂无快照记录"))
            return

        versions.sort(key=lambda v: v.get("timestamp", ""), reverse=True)

        for v in versions:
            timestamp = v.get("timestamp", _("未知时间"))
            path = v.get("snapshot_path", _("未知路径"))
            remark = v.get("remark", "")

            title = remark.strip() if remark.strip() else os.path.basename(path)
            time_part = timestamp

            # 用两行文字分开显示
            display = f"{title}\n{time_part}"

            item = QListWidgetItem(display)
            item.setData(1000, path)  # 保存快照路径，供后续对比用
            self.addItem(item)