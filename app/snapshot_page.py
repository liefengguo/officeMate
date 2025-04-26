from PyQt5.QtWidgets import QWidget, QVBoxLayout, QLabel, QLineEdit, QPushButton, QMessageBox
from core.snapshot import SnapshotManager

class SnapshotPage(QWidget):
    def __init__(self, file_path, parent=None):
        super().__init__(parent)
        self.file_path = file_path
        self.sm = SnapshotManager()

        layout = QVBoxLayout()

        self.label = QLabel("📸 创建新快照")
        self.remark_input = QLineEdit()
        self.remark_input.setPlaceholderText("请输入快照备注（可选）")
        self.create_button = QPushButton("创建快照")

        layout.addWidget(self.label)
        layout.addWidget(self.remark_input)
        layout.addWidget(self.create_button)
        layout.addStretch()

        self.setLayout(layout)

        self.create_button.clicked.connect(self.create_snapshot)

    def create_snapshot(self):
        remark = self.remark_input.text()
        try:
            info = self.sm.create_snapshot(self.file_path, remark=remark)
            QMessageBox.information(self, "成功", f"快照已创建！\n时间：{info['timestamp']}")
            self.remark_input.clear()
        except Exception as e:
            QMessageBox.critical(self, "错误", f"创建快照失败：{str(e)}")
