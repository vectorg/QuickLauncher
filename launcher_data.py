import os
import json
from PyQt5.QtWidgets import QListWidgetItem
from PyQt5.QtGui import QIcon
from PyQt5.QtCore import Qt

# 启动器数据管理类，负责保存和加载界面数据
class LauncherData:
    def __init__(self, data_file='launcher_data.json'):
        # 数据文件路径
        self.data_file = data_file

    # 保存界面数据到文件
    def save(self, ui):
        data = {
            # 保存图标区域的文件路径和勾选状态
            'icons': [(ui.icon_area.item(i).data(Qt.UserRole), ui.icon_area.item(i).checkState() == Qt.Checked) for i in range(ui.icon_area.count())],
            # 保存命令区域的所有命令文本
            'cmds': [ui.cmd_area.item(i).text() for i in range(ui.cmd_area.count())]
        }
        # 写入JSON文件
        with open(self.data_file, 'w', encoding='utf-8') as f:
            json.dump(data, f, ensure_ascii=False, indent=2)

    # 从文件加载界面数据
    def load(self, ui):
        if not os.path.exists(self.data_file):
            return
        with open(self.data_file, 'r', encoding='utf-8') as f:
            data = json.load(f)
        # 恢复图标区域
        for path, checked in data.get('icons', []):
            if os.path.exists(path):
                item = QListWidgetItem(QIcon(path), os.path.basename(path))
                # 设置可勾选、可编辑、可拖动
                item.setFlags(item.flags() | Qt.ItemIsUserCheckable | Qt.ItemIsEditable | Qt.ItemIsDragEnabled)
                item.setCheckState(Qt.Checked if checked else Qt.Unchecked)
                item.setData(Qt.UserRole, path)
                ui.icon_area.addItem(item)
        # 恢复命令区域
        for cmd in data.get('cmds', []):
            ui.cmd_area.addItem(QListWidgetItem(cmd)) 