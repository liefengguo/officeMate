from PyQt5.QtWidgets import QDialog, QVBoxLayout, QHBoxLayout, QLabel, QStackedWidget
from PyQt5.QtCore import Qt
from ui import PrimaryButton, FlatButton
from core.i18n import _


class OnboardingDialog(QDialog):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle(_("欢迎使用 DocSnap"))
        self.resize(420, 300)
        self.setModal(True)

        layout = QVBoxLayout(self)
        self.stack = QStackedWidget()
        layout.addWidget(self.stack, 1)

        self._add_pages()

        btn_bar = QHBoxLayout()
        btn_bar.addStretch(1)
        self.skip_btn = FlatButton(_("跳过"))
        self.next_btn = PrimaryButton(_("下一步"))
        btn_bar.addWidget(self.skip_btn)
        btn_bar.addWidget(self.next_btn)
        layout.addLayout(btn_bar)

        self.skip_btn.clicked.connect(self.reject)
        self.next_btn.clicked.connect(self._next)

    def _add_pages(self):
        pages = [
            (_("管理文档快照"), _("自动保存文档历史版本，随时回溯。")),
            (_("快速对比差异"), _("选取任意两个版本，智能展示改动。")),
            (_("多语言与主题"), _("提供多种语言和亮/暗主题，个性化体验。")),
        ]
        for title, desc in pages:
            w = QLabel(f"<h2>{title}</h2><p>{desc}</p>")
            w.setAlignment(Qt.AlignCenter)
            w.setWordWrap(True)
            self.stack.addWidget(w)

    def _next(self):
        idx = self.stack.currentIndex()
        if idx < self.stack.count() - 1:
            self.stack.setCurrentIndex(idx + 1)
            if idx + 1 == self.stack.count() - 1:
                self.next_btn.setText(_("开始使用"))
        else:
            self.accept()
