from PyQt5.QtCore import QObject, QEvent
import os

class DragDropHandler(QObject):
    def __init__(self, logic):
        super().__init__()
        self.logic = logic
        self.logic.ui.icon_area.installEventFilter(self)

    def eventFilter(self, source, event):
        if source == self.logic.ui.icon_area and event.type() == QEvent.DragEnter:
            event.accept()
            return True
        if source == self.logic.ui.icon_area and event.type() == QEvent.Drop:
            for url in event.mimeData().urls():
                path = url.toLocalFile()
                if os.path.isfile(path):
                    self.logic.add_icon_item(path)
            self.logic.save_items()
            return True
        return super().eventFilter(source, event) 