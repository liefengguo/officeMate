from PyQt5.QtWidgets import QWidget, QVBoxLayout, QTextEdit
from PyQt5.QtGui import QFont
import os
from core.snapshot_loaders.loader_registry import LoaderRegistry
from core.diff_strategies.paragraph_strategy import ParagraphDiffStrategy
from app.widgets.parallel_diff_view import _tokens_to_html, MONO_STYLE

class PreviewWindow(QWidget):
    def __init__(self, file_path):
        super().__init__()
        self.setWindowTitle("快照内容预览")
        self.setMinimumSize(400, 300)

        layout = QVBoxLayout()
        self.text_edit = QTextEdit()
        self.text_edit.setReadOnly(True)
        self.text_edit.setStyleSheet(MONO_STYLE)
        layout.addWidget(self.text_edit)
        self.setLayout(layout)
        self.load_content(file_path)

    def load_content(self, path: str):
        """Load snapshot content using LoaderRegistry."""
        try:
            _, ext = os.path.splitext(path)
            loader = LoaderRegistry.get_loader(ext)
            html = ""
            if loader and hasattr(loader, "load_structured"):
                paras = ParagraphDiffStrategy._paragraph_texts(loader, path)
                html_parts = [_tokens_to_html(p) for p in paras]
                html = "<br>".join(html_parts)
                self.text_edit.setHtml(f"<div style='{MONO_STYLE}'>{html}</div>")
            else:
                if loader:
                    text = loader.get_text(path)
                else:
                    with open(path, "r", encoding="utf-8", errors="ignore") as fp:
                        text = fp.read()
                self.text_edit.setFont(QFont("Courier", 10))
                self.text_edit.setStyleSheet(MONO_STYLE)
                self.text_edit.setPlainText(text)
        except Exception as e:
            self.text_edit.setPlainText(f"加载内容失败：{e}")