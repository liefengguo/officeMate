from PyQt5.QtWidgets import (
    QMainWindow, QWidget, QVBoxLayout, QPushButton, QFileDialog, QMessageBox
)
from core.snapshot import SnapshotManager
from app.snapshot_history import SnapshotHistoryWindow


class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("DocSnap 文档快照")
        self.setFixedSize(400, 200)

        self.sm = SnapshotManager()
        self.selected_file = None

        layout = QVBoxLayout()
        self.choose_button = QPushButton("选择文档")
        self.snapshot_button = QPushButton("创建快照")
        self.history_button = QPushButton("查看快照历史")


        self.choose_button.clicked.connect(self.select_file)
        self.snapshot_button.clicked.connect(self.create_snapshot)
        self.history_button.clicked.connect(self.show_history)
        layout.addWidget(self.choose_button)
        layout.addWidget(self.snapshot_button)
        layout.addWidget(self.history_button)

        container = QWidget()
        container.setLayout(layout)
        self.setCentralWidget(container)

    def select_file(self):
        file_path, _ = QFileDialog.getOpenFileName(
            self, "选择文档", "", "文档 (*.txt *.docx);;所有文件 (*)"
        )
        if file_path:
            self.selected_file = file_path
            QMessageBox.information(self, "文档已选择", f"已选择文件：\n{file_path}")

    def create_snapshot(self):
        if not self.selected_file:
            QMessageBox.warning(self, "未选择文件", "请先选择一个文档文件！")
            return

        try:
            info = self.sm.create_snapshot(self.selected_file)
            QMessageBox.information(
                self, "快照成功",
                f"快照创建成功！\n时间：{info['timestamp']}\n路径：{info['snapshot_path']}"
            )
        except Exception as e:
            QMessageBox.critical(self, "错误", f"创建快照失败：\n{str(e)}")

    def show_history(self):
        if not self.selected_file:
            QMessageBox.warning(self, "未选择文件", "请先选择一个文档文件！")
            return

        self.history_window = SnapshotHistoryWindow(self.selected_file)
        self.history_window.show()