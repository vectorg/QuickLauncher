import os
import time
import subprocess
from PyQt5.QtWidgets import QListWidgetItem, QMessageBox, QInputDialog, QApplication
from PyQt5.QtGui import QIcon
from PyQt5.QtCore import Qt
from launcher_drag import DragDropHandler
from launcher_ui import IconItemWidget

# 启动器主逻辑类，负责界面与数据的交互和功能实现
class LauncherLogic:
    def __init__(self, ui, data):
        self.ui = ui
        self.data = data
        self.log_file = 'launcher.log'  # 日志文件
        self.scripts_folder = os.path.abspath('.')  # 脚本文件夹路径
        self.drag_handler = DragDropHandler(self)  # 拖拽处理器
        self.connect_signals()  # 连接信号与槽
        self.load_items()  # 加载数据
        self.update_numbers()  # 更新编号显示

    # 连接所有按钮和控件的信号
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

    # 添加图标项到图标区域
    def add_icon_item(self, path):
        name = os.path.basename(path)
        item = QListWidgetItem()
        icon = QIcon(path)
        widget = IconItemWidget(icon, name)
        item.setData(Qt.UserRole, path)
        self.ui.icon_area.addItem(item)
        self.ui.icon_area.setItemWidget(item, widget)
        widget.checkbox.setChecked(False)
        self.save_items()
        self.update_numbers()

    # 图标区域右键菜单，删除图标项
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

    # 命令区域右键菜单，删除命令项
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

    # 启动所有图标项
    def launch_all(self):
        self.launch_items([self.ui.icon_area.item(i) for i in range(self.ui.icon_area.count())])

    # 启动所有勾选的图标项
    def launch_checked(self):
        items = [self.ui.icon_area.item(i) for i in range(self.ui.icon_area.count())
                 if self.ui.icon_area.itemWidget(self.ui.icon_area.item(i)).checkbox.isChecked()]
        self.launch_items(items)

    # 清空所有勾选
    def clear_checked(self):
        for i in range(self.ui.icon_area.count()):
            widget = self.ui.icon_area.itemWidget(self.ui.icon_area.item(i))
            if widget:
                widget.checkbox.setChecked(False)
        self.update_numbers()

    # 启动传入的图标项列表
    def launch_items(self, items):
        delay = self.ui.delay_spin.value()  # 启动间隔
        for idx, item in enumerate(items):
            path = item.data(Qt.UserRole)
            try:
                subprocess.Popen([path], shell=True)
                self.write_log(f'启动: {path}')
                # 设置启动时间
                widget = self.ui.icon_area.itemWidget(item)
                if widget:
                    widget.set_launch_time(time.strftime('%H:%M:%S'))
            except Exception as e:
                self.write_log(f'启动失败: {path} 错误: {e}')
            if idx < len(items) - 1:
                QApplication.processEvents()
                time.sleep(delay)

    # 更新图标项的编号显示
    def update_numbers(self):
        num = 1
        for i in range(self.ui.icon_area.count()):
            item = self.ui.icon_area.item(i)
            path = item.data(Qt.UserRole)
            widget = self.ui.icon_area.itemWidget(item)
            if not widget:
                icon = QIcon(path)
                widget = IconItemWidget(icon, os.path.basename(path))
                self.ui.icon_area.setItemWidget(item, widget)
            if widget.checkbox.isChecked():
                widget.name_label.setText(f'{num}. {os.path.basename(path)}')
                num += 1
            else:
                widget.name_label.setText(os.path.basename(path))

    # 添加命令到命令区域
    def add_command(self):
        text, ok = QInputDialog.getText(self.ui, '添加命令', '输入命令:')
        if ok and text.strip():
            item = QListWidgetItem(text.strip())
            self.ui.cmd_area.addItem(item)
            self.save_items()

    # 启动选中的命令
    def launch_cmd(self):
        items = [self.ui.cmd_area.item(i) for i in range(self.ui.cmd_area.count()) if self.ui.cmd_area.item(i).isSelected()]
        for item in items:
            cmd = item.text()
            try:
                subprocess.Popen(cmd, shell=True)
                self.write_log(f'启动命令: {cmd}')
            except Exception as e:
                self.write_log(f'命令启动失败: {cmd} 错误: {e}')

    # 显示日志内容
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

    # 打开脚本文件夹
    def open_scripts_folder(self):
        path = self.scripts_folder
        if os.path.exists(path):
            os.startfile(path)
        else:
            QMessageBox.warning(self.ui, '错误', '脚本文件夹不存在')

    # 写入日志
    def write_log(self, msg):
        with open(self.log_file, 'a', encoding='utf-8') as f:
            f.write(f'{time.strftime("%Y-%m-%d %H:%M:%S")} {msg}\n')

    # 保存界面数据
    def save_items(self):
        self.data.save(self.ui)

    # 加载界面数据
    def load_items(self):
        self.data.load(self.ui) 