import sys
import os
import time
import subprocess
from PyQt5.QtWidgets import (QApplication, QWidget, QVBoxLayout, QHBoxLayout, QPushButton, QListWidget, QListWidgetItem, QFileDialog, QInputDialog, QMessageBox, QLabel, QCheckBox, QSpinBox)
from PyQt5.QtGui import QIcon
from PyQt5.QtCore import Qt, QTimer, QSize

class Launcher(QWidget):
    def __init__(self):
        super().__init__()
        self.setWindowTitle('QuickLauncher')
        self.resize(800, 500)
        self.icon_area = QListWidget()
        self.icon_area.setSelectionMode(QListWidget.MultiSelection)
        self.icon_area.setDragDropMode(QListWidget.InternalMove)
        self.icon_area.setIconSize(QSize(48, 48))
        self.icon_area.setSpacing(8)
        self.icon_area.setAcceptDrops(True)
        self.icon_area.setDragEnabled(True)
        self.icon_area.viewport().setAcceptDrops(True)
        self.icon_area.setDropIndicatorShown(True)
        self.icon_area.setDefaultDropAction(Qt.MoveAction)
        self.icon_area.model().rowsMoved.connect(self.update_numbers)
        self.icon_area.itemChanged.connect(self.update_numbers)
        self.icon_area.itemSelectionChanged.connect(self.update_numbers)
        self.icon_area.setContextMenuPolicy(Qt.CustomContextMenu)
        self.icon_area.customContextMenuRequested.connect(self.icon_context_menu)

        # 命令区域
        self.cmd_area = QListWidget()
        self.cmd_area.setSelectionMode(QListWidget.MultiSelection)
        self.cmd_area.setDragDropMode(QListWidget.InternalMove)
        self.cmd_area.setContextMenuPolicy(Qt.CustomContextMenu)
        self.cmd_area.customContextMenuRequested.connect(self.cmd_context_menu)

        # 按钮区
        btn_all = QPushButton('全部启动')
        btn_all.clicked.connect(self.launch_all)
        btn_checked = QPushButton('启动勾选')
        btn_checked.clicked.connect(self.launch_checked)
        btn_clear = QPushButton('清空勾选')
        btn_clear.clicked.connect(self.clear_checked)
        self.delay_spin = QSpinBox()
        self.delay_spin.setRange(0, 60)
        self.delay_spin.setValue(2)
        delay_label = QLabel('延迟(秒)')

        btn_add_cmd = QPushButton('添加命令')
        btn_add_cmd.clicked.connect(self.add_command)
        btn_launch_cmd = QPushButton('启动命令')
        btn_launch_cmd.clicked.connect(self.launch_cmd)
        btn_log = QPushButton('查看日志')
        btn_log.clicked.connect(self.show_log)
        btn_open_scripts = QPushButton('查看相关脚本文件夹')
        btn_open_scripts.clicked.connect(self.open_scripts_folder)

        # 布局
        icon_btn_layout = QHBoxLayout()
        icon_btn_layout.addWidget(btn_all)
        icon_btn_layout.addWidget(btn_checked)
        icon_btn_layout.addWidget(btn_clear)
        icon_btn_layout.addWidget(delay_label)
        icon_btn_layout.addWidget(self.delay_spin)
        icon_btn_layout.addStretch()

        cmd_btn_layout = QHBoxLayout()
        cmd_btn_layout.addWidget(btn_add_cmd)
        cmd_btn_layout.addWidget(btn_launch_cmd)
        cmd_btn_layout.addWidget(btn_log)
        cmd_btn_layout.addWidget(btn_open_scripts)
        cmd_btn_layout.addStretch()

        main_layout = QVBoxLayout()
        main_layout.addLayout(icon_btn_layout)
        main_layout.addWidget(QLabel('图标区域（可拖动排序，拖入可添加）'))
        main_layout.addWidget(self.icon_area, 2)
        main_layout.addLayout(cmd_btn_layout)
        main_layout.addWidget(QLabel('命令区域'))
        main_layout.addWidget(self.cmd_area, 1)
        self.setLayout(main_layout)

        self.log_file = 'launcher.log'
        self.scripts_folder = os.path.abspath('.')
        self.icon_area.installEventFilter(self)
        self.load_items()
        self.update_numbers()

    def eventFilter(self, source, event):
        if source == self.icon_area and event.type() == event.DragEnter:
            event.accept()
            return True
        if source == self.icon_area and event.type() == event.Drop:
            for url in event.mimeData().urls():
                path = url.toLocalFile()
                if os.path.isfile(path):
                    self.add_icon_item(path)
            self.save_items()
            return True
        return super().eventFilter(source, event)

    def add_icon_item(self, path):
        name = os.path.basename(path)
        item = QListWidgetItem(QIcon(path), name)
        item.setFlags(item.flags() | Qt.ItemIsUserCheckable | Qt.ItemIsEditable | Qt.ItemIsDragEnabled)
        item.setCheckState(Qt.Unchecked)
        item.setData(Qt.UserRole, path)
        self.icon_area.addItem(item)
        self.save_items()
        self.update_numbers()

    def icon_context_menu(self, pos):
        item = self.icon_area.itemAt(pos)
        if item:
            menu = QMessageBox()
            menu.setText(f'删除 {item.text()}?')
            menu.setStandardButtons(QMessageBox.Yes | QMessageBox.No)
            ret = menu.exec_()
            if ret == QMessageBox.Yes:
                self.icon_area.takeItem(self.icon_area.row(item))
                self.save_items()
                self.update_numbers()

    def cmd_context_menu(self, pos):
        item = self.cmd_area.itemAt(pos)
        if item:
            menu = QMessageBox()
            menu.setText(f'删除命令: {item.text()}?')
            menu.setStandardButtons(QMessageBox.Yes | QMessageBox.No)
            ret = menu.exec_()
            if ret == QMessageBox.Yes:
                self.cmd_area.takeItem(self.cmd_area.row(item))
                self.save_items()

    def launch_all(self):
        self.launch_items([self.icon_area.item(i) for i in range(self.icon_area.count())])

    def launch_checked(self):
        items = [self.icon_area.item(i) for i in range(self.icon_area.count()) if self.icon_area.item(i).checkState() == Qt.Checked]
        self.launch_items(items)

    def clear_checked(self):
        for i in range(self.icon_area.count()):
            self.icon_area.item(i).setCheckState(Qt.Unchecked)
        self.update_numbers()

    def launch_items(self, items):
        delay = self.delay_spin.value()
        for idx, item in enumerate(items):
            path = item.data(Qt.UserRole)
            try:
                subprocess.Popen([path], shell=True)
                self.write_log(f'启动: {path}')
            except Exception as e:
                self.write_log(f'启动失败: {path} 错误: {e}')
            if idx < len(items) - 1:
                QApplication.processEvents()
                time.sleep(delay)

    def update_numbers(self):
        num = 1
        for i in range(self.icon_area.count()):
            item = self.icon_area.item(i)
            if item.checkState() == Qt.Checked:
                item.setText(f'{num}. {os.path.basename(item.data(Qt.UserRole))}')
                num += 1
            else:
                item.setText(os.path.basename(item.data(Qt.UserRole)))

    def add_command(self):
        text, ok = QInputDialog.getText(self, '添加命令', '输入命令:')
        if ok and text.strip():
            item = QListWidgetItem(text.strip())
            self.cmd_area.addItem(item)
            self.save_items()

    def launch_cmd(self):
        items = [self.cmd_area.item(i) for i in range(self.cmd_area.count()) if self.cmd_area.item(i).isSelected()]
        for item in items:
            cmd = item.text()
            try:
                subprocess.Popen(cmd, shell=True)
                self.write_log(f'启动命令: {cmd}')
            except Exception as e:
                self.write_log(f'命令启动失败: {cmd} 错误: {e}')

    def show_log(self):
        if not os.path.exists(self.log_file):
            QMessageBox.information(self, '日志', '暂无日志')
            return
        with open(self.log_file, 'r', encoding='utf-8') as f:
            log = f.read()
        dlg = QMessageBox(self)
        dlg.setWindowTitle('日志')
        dlg.setText(log[-2000:] if len(log) > 2000 else log)
        dlg.exec_()

    def open_scripts_folder(self):
        path = self.scripts_folder
        if os.path.exists(path):
            os.startfile(path)
        else:
            QMessageBox.warning(self, '错误', '脚本文件夹不存在')

    def write_log(self, msg):
        with open(self.log_file, 'a', encoding='utf-8') as f:
            f.write(f'{time.strftime("%Y-%m-%d %H:%M:%S")} {msg}\n')

    def save_items(self):
        data = {
            'icons': [(self.icon_area.item(i).data(Qt.UserRole), self.icon_area.item(i).checkState() == Qt.Checked) for i in range(self.icon_area.count())],
            'cmds': [self.cmd_area.item(i).text() for i in range(self.cmd_area.count())]
        }
        import json
        with open('launcher_data.json', 'w', encoding='utf-8') as f:
            json.dump(data, f, ensure_ascii=False, indent=2)

    def load_items(self):
        import json
        if not os.path.exists('launcher_data.json'):
            return
        with open('launcher_data.json', 'r', encoding='utf-8') as f:
            data = json.load(f)
        for path, checked in data.get('icons', []):
            if os.path.exists(path):
                item = QListWidgetItem(QIcon(path), os.path.basename(path))
                item.setFlags(item.flags() | Qt.ItemIsUserCheckable | Qt.ItemIsEditable | Qt.ItemIsDragEnabled)
                item.setCheckState(Qt.Checked if checked else Qt.Unchecked)
                item.setData(Qt.UserRole, path)
                self.icon_area.addItem(item)
        for cmd in data.get('cmds', []):
            self.cmd_area.addItem(QListWidgetItem(cmd))

if __name__ == '__main__':
    app = QApplication(sys.argv)
    win = Launcher()
    win.show()
    sys.exit(app.exec_()) 