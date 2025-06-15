

from PyQt5.QtWidgets import QWidget, QVBoxLayout, QTextEdit
from PyQt5.QtGui import QTextCharFormat, QTextCursor, QColor, QFont
from core.diff_engine import DiffEngine
from core.i18n import _, i18n

class DiffViewer(QWidget):
    def __init__(self, file1_path, file2_path):
        super().__init__()
        self.setWindowTitle(_("快照差异对比"))
        self.setMinimumSize(800, 600)

        layout = QVBoxLayout()
        self.text_edit = QTextEdit()
        self.text_edit.setReadOnly(True)
        layout.addWidget(self.text_edit)
        self.setLayout(layout)

        self.show_diff(file1_path, file2_path)

        i18n.language_changed.connect(self.retranslate_ui)

    def show_diff(self, file1, file2):
        engine = DiffEngine()
        diff_text = engine.compare_files(file1, file2)
        diff_lines = diff_text.splitlines()

        for line in diff_lines:
            if line.startswith("-"):
                self._append_colored_line(line, QColor("#ff9999"))  # 删除：红色
            elif line.startswith("+"):
                self._append_colored_line(line, QColor("#99ff99"))  # 添加：绿色
            elif line.startswith("?"):
                continue  # 忽略标注符号行
            else:
                self._append_colored_line(line, QColor("#ffffff"))  # 无变动：白色背景

    def _append_colored_line(self, text, background_color):
        cursor = self.text_edit.textCursor()
        fmt = QTextCharFormat()
        fmt.setBackground(background_color)
        fmt.setFont(QFont("Courier", 10))
        cursor.setCharFormat(fmt)
        cursor.insertText(text)
        cursor.insertText("\n")

    def retranslate_ui(self):
        self.setWindowTitle(_("快照差异对比"))
