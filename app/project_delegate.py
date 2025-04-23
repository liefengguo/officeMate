from PyQt5.QtWidgets import QStyledItemDelegate, QApplication
from PyQt5.QtGui import QFont, QColor, QPainter, QCursor
from PyQt5.QtCore import QRect, QSize, Qt
from PyQt5.QtWidgets import QStyle
class ProjectItemDelegate(QStyledItemDelegate):
    def paint(self, painter, option, index):
        doc_path = index.data(1000)
        file_name = doc_path.split("/")[-1] if doc_path else index.data()

        painter.save()
        # Draw background based on state
        if option.state & QStyle.State_Selected:
            painter.fillRect(option.rect, QColor("#bae7ff"))
        elif option.state & QStyle.State_MouseOver:
            painter.fillRect(option.rect, QColor("#e6f7ff"))
        else:
            painter.fillRect(option.rect, QColor("#ffffff"))

        # Layout rectangles
        rect = option.rect.adjusted(10, 4, -10, -4)
        name_rect = QRect(rect.left(), rect.top(), rect.width(), rect.height() // 2)
        path_rect = QRect(rect.left(), rect.center().y(), rect.width(), rect.height() // 2)

        # Project name
        name_font = QFont("Arial", 12, QFont.Bold)
        painter.setFont(name_font)
        painter.setPen(QColor("#000000"))
        painter.drawText(name_rect, Qt.AlignLeft | Qt.AlignVCenter, file_name)

        # Path
        path_font = QFont("Arial", 9)
        painter.setFont(path_font)
        painter.setPen(QColor("#888888"))
        painter.drawText(path_rect, Qt.AlignLeft | Qt.AlignVCenter, doc_path)

        painter.restore()

    def sizeHint(self, option, index):
        return QSize(300, 50)