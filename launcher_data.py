import os
import json
from PyQt5.QtWidgets import QListWidgetItem
from PyQt5.QtGui import QIcon
from PyQt5.QtCore import Qt

class LauncherData:
    def __init__(self, data_file='launcher_data.json'):
        self.data_file = data_file

    def save(self, ui):
        data = {
            'icons': [(ui.icon_area.item(i).data(Qt.UserRole), ui.icon_area.item(i).checkState() == Qt.Checked) for i in range(ui.icon_area.count())],
            'cmds': [ui.cmd_area.item(i).text() for i in range(ui.cmd_area.count())]
        }
        with open(self.data_file, 'w', encoding='utf-8') as f:
            json.dump(data, f, ensure_ascii=False, indent=2)

    def load(self, ui):
        if not os.path.exists(self.data_file):
            return
        with open(self.data_file, 'r', encoding='utf-8') as f:
            data = json.load(f)
        for path, checked in data.get('icons', []):
            if os.path.exists(path):
                item = QListWidgetItem(QIcon(path), os.path.basename(path))
                item.setFlags(item.flags() | Qt.ItemIsUserCheckable | Qt.ItemIsEditable | Qt.ItemIsDragEnabled)
                item.setCheckState(Qt.Checked if checked else Qt.Unchecked)
                item.setData(Qt.UserRole, path)
                ui.icon_area.addItem(item)
        for cmd in data.get('cmds', []):
            ui.cmd_area.addItem(QListWidgetItem(cmd)) 