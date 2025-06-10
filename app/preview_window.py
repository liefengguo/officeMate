from PyQt5.QtWidgets import QWidget, QVBoxLayout, QTextEdit
from PyQt5.QtGui import QFont
import os
from core.snapshot_loaders.loader_registry import LoaderRegistry


class PreviewWindow(QWidget):
    def __init__(self, file_path):
        super().__init__()
        self.setWindowTitle("快照内容预览")
        self.setMinimumSize(400, 300)

        layout = QVBoxLayout()
        self.text_edit = QTextEdit()
        self.text_edit.setReadOnly(True)
        layout.addWidget(self.text_edit)
        self.setLayout(layout)
        self.load_content(file_path)

    def load_content(self, path: str):
        """Load snapshot content using LoaderRegistry."""
        try:
            _, ext = os.path.splitext(path)
            loader = LoaderRegistry.get_loader(ext)
            if loader:
                text = loader.get_text(path)
            else:
                # Fallback plain UTF‑8 read
                with open(path, "r", encoding="utf-8", errors="ignore") as fp:
                    text = fp.read()
            self.text_edit.setFont(QFont("Courier", 10))
            self.text_edit.setPlainText(text)
        except Exception as e:
            self.text_edit.setPlainText(f"加载内容失败：{e}")
