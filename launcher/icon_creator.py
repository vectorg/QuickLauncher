from PyQt5.QtGui import QIcon, QPixmap, QPainter, QColor, QFont
from PyQt5.QtCore import Qt

def create_tray_icon(size=32):
    pixmap = QPixmap(size, size)
    pixmap.fill(QColor("white"))
    painter = QPainter(pixmap)
    painter.setRenderHint(QPainter.Antialiasing)
    font = QFont("Arial", int(size * 0.5), QFont.Bold)
    painter.setFont(font)
    painter.setPen(QColor("blue"))
    painter.drawText(pixmap.rect(), Qt.AlignCenter, "Q")
    painter.end()
    return QIcon(pixmap) 