import os
import time
import subprocess
from PyQt5.QtWidgets import QListWidgetItem, QMessageBox, QInputDialog, QApplication
from PyQt5.QtGui import QIcon
from PyQt5.QtCore import Qt
from launcher_drag import DragDropHandler

class LauncherLogic:
    def __init__(self, ui, data):
        self.ui = ui
        self.data = data
        self.log_file = 'launcher.log'
        self.scripts_folder = os.path.abspath('.')
        self.drag_handler = DragDropHandler(self)
        self.connect_signals()
        self.load_items()
        self.update_numbers()

    def connect_signals(self):
        self.ui.btn_all.clicked.connect(self.launch_all)
        self.ui.btn_checked.clicked.connect(self.launch_checked)
        self.ui.btn_clear.clicked.connect(self.clear_checked)
        self.ui.btn_add_cmd.clicked.connect(self.add_command)
        self.ui.btn_launch_cmd.clicked.connect(self.launch_cmd)
        self.ui.btn_log.clicked.connect(self.show_log)
        self.ui.btn_open_scripts.clicked.connect(self.open_scripts_folder)
        self.ui.icon_area.model().rowsMoved.connect(self.update_numbers)
        self.ui.icon_area.itemChanged.connect(self.update_numbers)
        self.ui.icon_area.itemSelectionChanged.connect(self.update_numbers)
        self.ui.icon_area.setContextMenuPolicy(Qt.CustomContextMenu)
        self.ui.icon_area.customContextMenuRequested.connect(self.icon_context_menu)
        self.ui.cmd_area.setContextMenuPolicy(Qt.CustomContextMenu)
        self.ui.cmd_area.customContextMenuRequested.connect(self.cmd_context_menu)

    def add_icon_item(self, path):
        name = os.path.basename(path)
        item = QListWidgetItem(QIcon(path), name)
        item.setFlags(item.flags() | Qt.ItemIsUserCheckable | Qt.ItemIsEditable | Qt.ItemIsDragEnabled)
        item.setCheckState(Qt.Unchecked)
        item.setData(Qt.UserRole, path)
        self.ui.icon_area.addItem(item)
        self.save_items()
        self.update_numbers()

    def icon_context_menu(self, pos):
        item = self.ui.icon_area.itemAt(pos)
        if item:
            menu = QMessageBox()
            menu.setText(f'删除 {item.text()}?')
            menu.setStandardButtons(QMessageBox.Yes | QMessageBox.No)
            ret = menu.exec_()
            if ret == QMessageBox.Yes:
                self.ui.icon_area.takeItem(self.ui.icon_area.row(item))
                self.save_items()
                self.update_numbers()

    def cmd_context_menu(self, pos):
        item = self.ui.cmd_area.itemAt(pos)
        if item:
            menu = QMessageBox()
            menu.setText(f'删除命令: {item.text()}?')
            menu.setStandardButtons(QMessageBox.Yes | QMessageBox.No)
            ret = menu.exec_()
            if ret == QMessageBox.Yes:
                self.ui.cmd_area.takeItem(self.ui.cmd_area.row(item))
                self.save_items()

    def launch_all(self):
        self.launch_items([self.ui.icon_area.item(i) for i in range(self.ui.icon_area.count())])

    def launch_checked(self):
        items = [self.ui.icon_area.item(i) for i in range(self.ui.icon_area.count()) if self.ui.icon_area.item(i).checkState() == Qt.Checked]
        self.launch_items(items)

    def clear_checked(self):
        for i in range(self.ui.icon_area.count()):
            self.ui.icon_area.item(i).setCheckState(Qt.Unchecked)
        self.update_numbers()

    def launch_items(self, items):
        delay = self.ui.delay_spin.value()
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
        for i in range(self.ui.icon_area.count()):
            item = self.ui.icon_area.item(i)
            if item.checkState() == Qt.Checked:
                item.setText(f'{num}. {os.path.basename(item.data(Qt.UserRole))}')
                num += 1
            else:
                item.setText(os.path.basename(item.data(Qt.UserRole)))

    def add_command(self):
        text, ok = QInputDialog.getText(self.ui, '添加命令', '输入命令:')
        if ok and text.strip():
            item = QListWidgetItem(text.strip())
            self.ui.cmd_area.addItem(item)
            self.save_items()

    def launch_cmd(self):
        items = [self.ui.cmd_area.item(i) for i in range(self.ui.cmd_area.count()) if self.ui.cmd_area.item(i).isSelected()]
        for item in items:
            cmd = item.text()
            try:
                subprocess.Popen(cmd, shell=True)
                self.write_log(f'启动命令: {cmd}')
            except Exception as e:
                self.write_log(f'命令启动失败: {cmd} 错误: {e}')

    def show_log(self):
        if not os.path.exists(self.log_file):
            QMessageBox.information(self.ui, '日志', '暂无日志')
            return
        with open(self.log_file, 'r', encoding='utf-8') as f:
            log = f.read()
        dlg = QMessageBox(self.ui)
        dlg.setWindowTitle('日志')
        dlg.setText(log[-2000:] if len(log) > 2000 else log)
        dlg.exec_()

    def open_scripts_folder(self):
        path = self.scripts_folder
        if os.path.exists(path):
            os.startfile(path)
        else:
            QMessageBox.warning(self.ui, '错误', '脚本文件夹不存在')

    def write_log(self, msg):
        with open(self.log_file, 'a', encoding='utf-8') as f:
            f.write(f'{time.strftime("%Y-%m-%d %H:%M:%S")} {msg}\n')

    def save_items(self):
        self.data.save(self.ui)

    def load_items(self):
        self.data.load(self.ui) 