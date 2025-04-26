from PyQt5.QtWidgets import QWidget, QVBoxLayout, QTextEdit
from PyQt5.QtGui import QFont
from core.diff_engine import read_text, read_docx

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

    def load_content(self, path):
        try:
            content = ""
            if path.endswith(".docx") or path.endswith(".bak"):
                try:
                    from docx import Document
                    Document(path)  # 尝试读取验证
                    content = read_docx(path)
                except Exception:
                    content = read_text(path)
            else:
                content = read_text(path)

            self.text_edit.setFont(QFont("Courier", 10))
            self.text_edit.setPlainText("".join(content))
        except Exception as e:
            self.text_edit.setPlainText(f"加载内容失败：{e}")