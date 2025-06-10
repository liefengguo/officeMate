from PyQt5.QtWidgets import QTextBrowser, QWidget, QHBoxLayout

class ParallelDiffView(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        left_tb  = QTextBrowser()
        right_tb = QTextBrowser()
        # mark for QSS styling
        left_tb.setProperty("class", "diff-pane")
        right_tb.setProperty("class", "diff-pane")

        layout = QHBoxLayout(self)
        layout.addWidget(left_tb)
        layout.addWidget(right_tb)
        # expose panes for outer logic (e.g., scroll sync)
        self.left = left_tb
        self.right = right_tb
