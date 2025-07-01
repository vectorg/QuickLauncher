from PyQt5.QtCore import QObject, QEvent
import os

# 拖拽处理类，实现图标区域的拖拽添加功能
class DragDropHandler(QObject):
    def __init__(self, logic):
        super().__init__()
        self.logic = logic
        # 安装事件过滤器到图标区域，实现自定义拖拽处理
        self.logic.ui.icon_area.installEventFilter(self)

    # 事件过滤器，处理拖拽进入和放下事件
    def eventFilter(self, source, event):
        # 拖拽进入图标区域时，接受事件
        if source == self.logic.ui.icon_area and event.type() == QEvent.DragEnter:
            event.accept()
            return True
        # 拖拽放下时，添加文件到图标区域
        if source == self.logic.ui.icon_area and event.type() == QEvent.Drop:
            for url in event.mimeData().urls():
                path = url.toLocalFile()
                if os.path.isfile(path):
                    self.logic.add_icon_item(path)
            # 拖拽后保存数据
            self.logic.save_items()
            return True
        return super().eventFilter(source, event) 