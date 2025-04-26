from PyQt5.QtWidgets import QWidget, QVBoxLayout, QLabel

class SettingsPage(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)

        layout = QVBoxLayout()
        label = QLabel("⚙️ 软件设置界面（待完善）")
        layout.addWidget(label)
        self.setLayout(layout)