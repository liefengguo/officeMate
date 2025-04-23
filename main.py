# main.py
from PyQt5.QtWidgets import QApplication
from app.main_dashboard import MainDashboard

if __name__ == "__main__":
    import sys
    app = QApplication(sys.argv)
    window = MainDashboard()  # 👈 启动主页
    window.show()
    sys.exit(app.exec_())