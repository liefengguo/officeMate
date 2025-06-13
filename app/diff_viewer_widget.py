from PyQt5.QtWidgets import QPlainTextEdit
from core.i18n import _

class DiffViewerWidget(QPlainTextEdit):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setReadOnly(True)
        self.setPlaceholderText(_("差异结果将在这里显示..."))
        # 可以在这里统一设置字体、背景、滚动条策略等

    def set_diff_content(self, content: str):
        if not content.strip():
            self.setPlainText(_("没有检测到差异。"))
        else:
            self.setPlainText(content)

    def clear(self):
        self.setPlainText("")