import os
import time
import subprocess
import threading
import sys
from PyQt5.QtWidgets import QListWidgetItem, QMessageBox, QInputDialog, QApplication, QMenu
from PyQt5.QtGui import QIcon
from PyQt5.QtCore import Qt
from launcher.launcher_drag import DragDropHandler
from launcher.launcher_ui import IconItemWidget
from launcher.log_viewer import LogViewer
from utils import subprocess_logger
from utils.log_finder import open_command_log
from utils.process_utils import restart_program

# 启动器主逻辑类，负责界面与数据的交互和功能实现
class LauncherLogic:
    def __init__(self, ui, data):
        self.ui = ui
        self.data = data
        self.log_dir = 'data/log'  # 日志目录
        os.makedirs(self.log_dir, exist_ok=True)  # 确保日志目录存在
        self.log_file = os.path.join(self.log_dir, 'launcher.log')  # 日志文件
        self.scripts_folder = os.path.abspath('.')  # 脚本文件夹路径
        self.drag_handler = DragDropHandler(self)  # 拖拽处理器
        
        # 创建日志查看器
        self.log_viewer = LogViewer(self.ui, self.log_dir)
        
        self.connect_signals()  # 连接信号与槽
        self.checked_order_counter = 1  # 勾选顺序号计数器
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
        self.ui.icon_area.itemSelectionChanged.connect(self.update_numbers)
        self.ui.icon_area.setContextMenuPolicy(Qt.CustomContextMenu)
        self.ui.icon_area.customContextMenuRequested.connect(self.icon_context_menu)
        self.ui.cmd_area.setContextMenuPolicy(Qt.CustomContextMenu)
        self.ui.cmd_area.customContextMenuRequested.connect(self.cmd_context_menu)
        self.ui.btn_restart.clicked.connect(restart_program)
        
        # 绑定清空日志按钮
        if hasattr(self.ui, 'btn_clear_log'):
            self.ui.btn_clear_log.clicked.connect(self.log_viewer.clear_log_display)

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
        widget.set_item(item)
        widget.on_checkbox_state_changed = self.on_icon_item_changed
        self.save_items()
        self.update_numbers()

    # 图标区域右键菜单，删除图标项
    def icon_context_menu(self, pos):
        item = self.ui.icon_area.itemAt(pos)
        if item:
            menu = QMenu(self.ui.icon_area)
            action_launch = menu.addAction("立刻启动")
            action_delete = menu.addAction("删除")
            action = menu.exec_(self.ui.icon_area.mapToGlobal(pos))
            if action == action_launch:
                self.launch_items([item])
            elif action == action_delete:
                name = item.text() or os.path.basename(item.data(Qt.UserRole))
                reply = QMessageBox.question(
                    self.ui.icon_area,
                    "确认删除",
                    f"是否删除 {name}？",
                    QMessageBox.Yes | QMessageBox.No
                )
                if reply == QMessageBox.Yes:
                    self.ui.icon_area.takeItem(self.ui.icon_area.row(item))
                    self.save_items()
                    self.update_numbers()

    # 命令区域右键菜单，删除命令项
    def cmd_context_menu(self, pos):
        item = self.ui.cmd_area.itemAt(pos)
        if item:
            menu = QMenu(self.ui.cmd_area)
            action_launch = menu.addAction("立刻启动")
            action_edit = menu.addAction("编辑")
            action_open_log = menu.addAction("打开日志文件")
            action_delete = menu.addAction("删除")
            action = menu.exec_(self.ui.cmd_area.mapToGlobal(pos))
            if action == action_launch:
                cmd = item.text()
                # 使用异步方式执行命令
                log_filename = subprocess_logger.run_cmd_async_with_log(cmd)
                if log_filename:
                    self.write_log(f'异步启动命令: {cmd}，日志: {log_filename}')
                    # 设置当前监控的日志文件
                    self.log_viewer.set_current_log_file(log_filename)
            elif action == action_edit:
                old_cmd = item.text()
                input_dialog = QInputDialog(self.ui)
                input_dialog.setWindowTitle('编辑命令')
                input_dialog.setLabelText('修改命令:')
                input_dialog.setTextValue(old_cmd)
                input_dialog.resize(800, 100)
                ok = input_dialog.exec_()
                new_cmd = input_dialog.textValue()
                if ok and new_cmd.strip():
                    item.setText(new_cmd.strip())
                    self.save_items()
            elif action == action_open_log:
                success, message = open_command_log(item.text(), self.log_dir, self.ui)
                if success:
                    self.write_log(message)
                    # 查找并显示该命令的日志
                    self.log_viewer.find_and_display_cmd_log(item.text())
            elif action == action_delete:
                reply = QMessageBox.question(
                    self.ui.cmd_area,
                    "确认删除",
                    f"是否删除命令: {item.text()}？",
                    QMessageBox.Yes | QMessageBox.No
                )
                if reply == QMessageBox.Yes:
                    self.ui.cmd_area.takeItem(self.ui.cmd_area.row(item))
                    self.save_items()

    # 启动所有图标项
    def launch_all(self):
        self.launch_items([self.ui.icon_area.item(i) for i in range(self.ui.icon_area.count())])

    # 启动所有勾选的图标项
    def launch_checked(self):
        # 按checked_order排序启动
        checked_items = []
        for i in range(self.ui.icon_area.count()):
            item = self.ui.icon_area.item(i)
            widget = self.ui.icon_area.itemWidget(item)
            if widget and widget.checkbox.isChecked() and widget.checked_order is not None:
                checked_items.append((item, widget.checked_order))
        checked_items.sort(key=lambda x: x[1])
        items = [item for item, _ in checked_items]
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
                    widget.set_launch_time(time.strftime('%Y-%m-%d %H:%M:%S'))
            except Exception as e:
                self.write_log(f'启动失败: {path} 错误: {e}')
            if idx < len(items) - 1:
                QApplication.processEvents()
                time.sleep(delay)
        self.save_items()

    # 更新图标项的编号显示
    def update_numbers(self):
        # 收集所有勾选的 item 及其顺序号
        checked_items = []
        for i in range(self.ui.icon_area.count()):
            item = self.ui.icon_area.item(i)
            widget = self.ui.icon_area.itemWidget(item)
            if widget and widget.checkbox.isChecked() and widget.checked_order is not None:
                checked_items.append((item, widget.checked_order))
        # 按checked_order排序
        checked_items.sort(key=lambda x: x[1])
        # 给所有 item 设置显示
        for i in range(self.ui.icon_area.count()):
            item = self.ui.icon_area.item(i)
            path = item.data(Qt.UserRole)
            widget = self.ui.icon_area.itemWidget(item)
            if not widget:
                icon = QIcon(path)
                widget = IconItemWidget(icon, os.path.basename(path))
                self.ui.icon_area.setItemWidget(item, widget)
            # 查找item在checked_items中的序号
            idx = None
            for pos, (checked_item, _) in enumerate(checked_items):
                if item is checked_item:
                    idx = pos + 1
                    break
            if idx is not None:
                widget.name_label.setText(f'{idx}. {os.path.basename(path)}')
            else:
                widget.name_label.setText(os.path.basename(path))
        self.save_items()

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
            # 使用异步方式执行命令
            log_filename = subprocess_logger.run_cmd_async_with_log(cmd)
            if log_filename:
                self.write_log(f'异步启动命令: {cmd}，日志: {log_filename}')
                # 设置当前监控的日志文件
                self.log_viewer.set_current_log_file(log_filename)

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
        log_entry = f'{time.strftime("%Y-%m-%d %H:%M:%S")} {msg}'
        os.makedirs(self.log_dir, exist_ok=True)  # 确保日志目录存在
        with open(self.log_file, 'a', encoding='utf-8') as f:
            f.write(log_entry + '\n')

    # 保存界面数据
    def save_items(self):
        self.data.save(self.ui)

    # 加载界面数据
    def load_items(self):
        self.data.load(self.ui)
        # 恢复控件的item和回调绑定
        max_checked_order = 0
        for i in range(self.ui.icon_area.count()):
            item = self.ui.icon_area.item(i)
            widget = self.ui.icon_area.itemWidget(item)
            if widget:
                widget.set_item(item)
                widget.on_checkbox_state_changed = self.on_icon_item_changed
                # 检查最大 checked_order
                if widget.checked_order is not None and widget.checked_order > max_checked_order:
                    max_checked_order = widget.checked_order
        self.checked_order_counter = max_checked_order + 1

    def on_icon_item_changed(self, item):
        widget = self.ui.icon_area.itemWidget(item)
        if widget:
            if widget.checkbox.isChecked():
                widget.checked_order = self.checked_order_counter
                self.checked_order_counter += 1
            else:
                widget.checked_order = None
        self.update_numbers() 