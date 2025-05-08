from PyQt5.QtWidgets import QWidget, QLabel, QPushButton, QHBoxLayout, QVBoxLayout
from PyQt5.QtCore import Qt, pyqtSignal

class SnapshotItemWidget(QWidget):
    view_requested = pyqtSignal()
    delete_requested = pyqtSignal()

    def __init__(self, title, timestamp, parent=None):
        super().__init__(parent)

        self.label_title = QLabel(title)
        self.label_time = QLabel(timestamp)

        self.view_button = QPushButton("查看")
        self.delete_button = QPushButton("删除")

        self.view_button.clicked.connect(self.view_requested.emit)
        self.delete_button.clicked.connect(self.delete_requested.emit)

        # 设置按钮的样式，初始透明
        self.view_button.setStyleSheet("""
            QPushButton {
                background-color: transparent;
                border: none;
                color: rgba(0, 0, 0, 0.3);  /* 半透明文字 */
                font-size: 12px;
            }
            QPushButton:hover {
                color: rgba(0, 0, 0, 1);  /* 鼠标悬停时显示完整颜色 */
            }
        """)

        self.delete_button.setStyleSheet("""
            QPushButton {
                background-color: transparent;
                border: none;
                color: rgba(0, 0, 0, 0.3);  /* 半透明文字 */
                font-size: 12px;
            }
            QPushButton:hover {
                color: rgba(0, 0, 0, 1);  /* 鼠标悬停时显示完整颜色 */
            }
        """)

        # 布局
        layout = QHBoxLayout()
        text_layout = QVBoxLayout()
        text_layout.addWidget(self.label_title)
        text_layout.addWidget(self.label_time)

        layout.addLayout(text_layout)
        layout.addStretch()
        layout.addWidget(self.view_button)
        layout.addWidget(self.delete_button)

        self.setLayout(layout)

    def set_selected(self, selected):
        """根据是否选中控制按钮透明度"""
        if selected:
            self.view_button.setStyleSheet("""
                QPushButton {
                    background-color: transparent;
                    border: none;
                    color: rgba(0, 0, 0, 1);  /* 完全显示文字 */
                    font-size: 12px;
                }
                QPushButton:hover {
                    color: rgba(0, 0, 0, 1);  /* 鼠标悬停时显示完整颜色 */
                }
            """)
            self.delete_button.setStyleSheet("""
                QPushButton {
                    background-color: transparent;
                    border: none;
                    color: rgba(0, 0, 0, 1);  /* 完全显示文字 */
                    font-size: 12px;
                }
                QPushButton:hover {
                    color: rgba(0, 0, 0, 1);  /* 鼠标悬停时显示完整颜色 */
                }
            """)
        else:
            self.view_button.setStyleSheet("""
                QPushButton {
                    background-color: transparent;
                    border: none;
                    color: rgba(0, 0, 0, 0.3);  /* 半透明文字 */
                    font-size: 12px;
                }
                QPushButton:hover {
                    color: rgba(0, 0, 0, 1);  /* 鼠标悬停时显示完整颜色 */
                }
            """)
            self.delete_button.setStyleSheet("""
                QPushButton {
                    background-color: transparent;
                    border: none;
                    color: rgba(0, 0, 0, 0.3);  /* 半透明文字 */
                    font-size: 12px;
                }
                QPushButton:hover {
                    color: rgba(0, 0, 0, 1);  /* 鼠标悬停时显示完整颜色 */
                }
            """)
