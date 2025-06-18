from PySide6.QtWidgets import QStyledItemDelegate, QStyle
from PySide6.QtGui import QFont, QColor, QPainter
from PySide6.QtCore import QRectF, QSize, Qt
from PySide6.QtGui import QPalette

class ProjectItemDelegate(QStyledItemDelegate):
    RADIUS = 6
    MARGIN = 2

    def paint(self, painter: QPainter, option, index):
        painter.save()
        painter.setRenderHint(QPainter.Antialiasing, True)

        # -----------------------------------------------------------------
        # Determine card rectangle (leave margin so neighbouring cards
        # don't stick together visually)
        r = option.rect.adjusted(self.MARGIN, self.MARGIN,
                                 -self.MARGIN, -self.MARGIN)

        # Data
        doc_path = index.data(1000) or ""
        file_name = doc_path.split("/")[-1] if doc_path else index.data()

        # -----------------------------------------------------------------
        # Colors – rely on palette so that light/dark themes auto‑adapt
        pal = option.palette
        if option.state & QStyle.State_Selected:
            bg_color = pal.highlight().color()
            text_color = pal.highlightedText().color()
        elif option.state & QStyle.State_MouseOver:
            # subtle hover tint: 4% opacity of highlight
            hl = pal.highlight().color()
            bg_color = QColor(hl.red(), hl.green(), hl.blue(), 25)
            text_color = pal.text().color()
        else:
            bg_color = pal.base().color()
            text_color = pal.text().color()

        # -----------------------------------------------------------------
        # Draw card background
        painter.setPen(Qt.NoPen)
        painter.setBrush(bg_color)
        painter.drawRoundedRect(QRectF(r), self.RADIUS, self.RADIUS)

        # -----------------------------------------------------------------
        # Draw texts
        name_rect = QRectF(r.left() + 12, r.top() + 6, r.width() - 24, 18)
        path_rect = QRectF(r.left() + 12, r.top() + 26, r.width() - 24, 16)

        name_font = QFont()
        name_font.setPointSize(14)
        name_font.setWeight(QFont.Bold)
        painter.setFont(name_font)
        painter.setPen(text_color)
        painter.drawText(name_rect, Qt.AlignLeft | Qt.AlignVCenter, file_name)

        path_font = QFont()
        path_font.setPointSize(9)
        painter.setFont(path_font)
        # path color = text darker(150) in light theme, lighten in dark
        path_pen = QColor(text_color)
        if pal.color(QPalette.Base).value() < 128:  # dark theme
            path_pen = QColor(text_color).lighter(150)
        else:
            path_pen = QColor(text_color).darker(150)
        painter.setPen(path_pen)
        painter.drawText(path_rect, Qt.AlignLeft | Qt.AlignVCenter, doc_path)

        painter.restore()

    def sizeHint(self, option, index):
        # Width adapts to view; height is fixed
        width = option.widget.width() - 2 * self.MARGIN if option.widget else option.rect.width()
        return QSize(width, 60)
