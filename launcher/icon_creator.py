from PyQt5.QtGui import QIcon, QPixmap, QPainter, QColor, QFont
from PyQt5.QtCore import Qt

def create_tray_icon(size=32):
    pixmap = QPixmap(size, size)
    # pixmap.fill(QColor("white"))
    pixmap.fill(QColor(0, 0, 0, 0))
    painter = QPainter(pixmap)
    painter.setRenderHint(QPainter.Antialiasing)
    font = QFont("Arial", int(size * 0.6), QFont.Bold)
    painter.setFont(font)
    # painter.setPen(QColor("blue"))
    painter.setPen(QColor(100, 180, 255))
    painter.drawText(pixmap.rect(), Qt.AlignCenter, "Q")
    painter.end()
    return QIcon(pixmap)

def create_window_icon(size=32):
    return create_tray_icon()
    # pixmap = QPixmap(size, size)
    # pixmap.fill(QColor("white"))
    # painter = QPainter(pixmap)
    # painter.setRenderHint(QPainter.Antialiasing)
    # font = QFont("Arial", int(size * 0.5), QFont.Bold)
    # painter.setFont(font)
    # # 设置淡蓝色
    # painter.setPen(QColor(100, 180, 255))
    # painter.drawText(pixmap.rect(), Qt.AlignCenter, "QS")
    # painter.end()
    # return QIcon(pixmap)
