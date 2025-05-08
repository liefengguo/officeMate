from PyQt5.QtWidgets import QPlainTextEdit

class DiffViewerWidget(QPlainTextEdit):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setReadOnly(True)
        self.setPlaceholderText("差异结果将在这里显示...")
        # 可以在这里统一设置字体、背景、滚动条策略等

    def set_diff_content(self, content: str):
        if not content.strip():
            self.setPlainText("没有检测到差异。")
        else:
            self.setPlainText(content)

    def clear(self):
        self.setPlainText("")