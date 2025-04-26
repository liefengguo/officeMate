from PyQt5.QtWidgets import QApplication
from app.main_window import MainWindow
def load_stylesheet(app):
    with open("assets/styles/office_mate.qss", "r") as f:
        app.setStyleSheet(f.read())
if __name__ == "__main__":
    import sys
    app = QApplication(sys.argv)
    load_stylesheet(app)
    window = MainWindow()
    window.show()
    sys.exit(app.exec_())