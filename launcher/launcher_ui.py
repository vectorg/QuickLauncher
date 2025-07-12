from PyQt5.QtWidgets import (QWidget, QVBoxLayout, QHBoxLayout, QPushButton, QListWidget, QLabel, QSpinBox, QListWidgetItem, QFileDialog, QInputDialog, QMessageBox, QStackedWidget, QSizePolicy, QFrame, QCheckBox)
from PyQt5.QtGui import QIcon
from PyQt5.QtCore import Qt, QSize
from typing import Optional, Callable
from launcher.tray_manager import TrayManager
from launcher.icon_creator import create_window_icon

# 启动器主界面类，负责界面布局和控件初始化
class LauncherUI(QWidget):
    def __init__(self):
        super().__init__()
        self.setWindowTitle('QuickLauncher')  # 设置窗口标题
        self.resize(800, 500)  # 设置窗口大小
        # 设置窗口图标
        self.setWindowIcon(create_window_icon())

        # 左侧按钮
        self.btn_software = QPushButton('软件启动')
        self.btn_command = QPushButton('命令启动')
        self.btn_software.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Expanding)
        self.btn_command.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Expanding)
        self.btn_software.setCheckable(True)
        self.btn_command.setCheckable(True)
        self.btn_software.setChecked(True)
        left_btn_layout = QVBoxLayout()
        left_btn_layout.addWidget(self.btn_software)
        left_btn_layout.addWidget(self.btn_command)
        left_btn_layout.addStretch()
        left_frame = QFrame()
        left_frame.setLayout(left_btn_layout)
        left_frame.setFixedWidth(100)

        # 右侧内容区（堆叠）
        self.stack = QStackedWidget()

        # --- 软件启动页 ---
        self.icon_area = QListWidget()
        self.icon_area.setSelectionMode(QListWidget.MultiSelection)
        self.icon_area.setDragDropMode(QListWidget.InternalMove)
        self.icon_area.setIconSize(QSize(48, 48))
        self.icon_area.setAcceptDrops(True)
        self.icon_area.setDragEnabled(True)
        self.icon_area.viewport().setAcceptDrops(True)
        self.icon_area.setDropIndicatorShown(True)
        self.icon_area.setDefaultDropAction(Qt.MoveAction)

        btn_all = QPushButton('全部启动')
        btn_checked = QPushButton('启动勾选')
        btn_clear = QPushButton('清空勾选')
        self.delay_spin = QSpinBox()
        self.delay_spin.setRange(0, 60)
        self.delay_spin.setValue(2)
        delay_label = QLabel('延迟(秒)')
        icon_btn_layout = QHBoxLayout()
        icon_btn_layout.addWidget(btn_all)
        icon_btn_layout.addWidget(btn_checked)
        icon_btn_layout.addWidget(btn_clear)
        icon_btn_layout.addWidget(delay_label)
        icon_btn_layout.addWidget(self.delay_spin)
        icon_btn_layout.addStretch()

        icon_page_layout = QVBoxLayout()
        icon_page_layout.addWidget(QLabel('图标区域（可拖动排序，拖入可添加）'))
        icon_page_layout.addWidget(self.icon_area, 2)
        icon_page_layout.addLayout(icon_btn_layout)
        icon_page = QWidget()
        icon_page.setLayout(icon_page_layout)

        # --- 命令启动页 ---
        self.cmd_area = QListWidget()
        self.cmd_area.setSelectionMode(QListWidget.MultiSelection)
        self.cmd_area.setDragDropMode(QListWidget.InternalMove)
        btn_add_cmd = QPushButton('添加命令')
        btn_launch_cmd = QPushButton('启动命令')
        btn_log = QPushButton('查看日志')
        btn_open_scripts = QPushButton('查看相关脚本文件夹')
        cmd_btn_layout = QHBoxLayout()
        cmd_btn_layout.addWidget(btn_add_cmd)
        cmd_btn_layout.addWidget(btn_launch_cmd)
        cmd_btn_layout.addWidget(btn_log)
        cmd_btn_layout.addWidget(btn_open_scripts)
        cmd_btn_layout.addStretch()
        cmd_page_layout = QVBoxLayout()
        cmd_page_layout.addWidget(QLabel('命令区域'))
        cmd_page_layout.addWidget(self.cmd_area, 2)
        cmd_page_layout.addLayout(cmd_btn_layout)
        cmd_page = QWidget()
        cmd_page.setLayout(cmd_page_layout)

        self.stack.addWidget(icon_page)
        self.stack.addWidget(cmd_page)

        # 右上角重启按钮
        self.btn_restart = QPushButton('重启程序')
        self.btn_restart.setSizePolicy(QSizePolicy.Fixed, QSizePolicy.Fixed)
        # 右上角布局
        top_right_layout = QHBoxLayout()
        top_right_layout.addStretch()
        top_right_layout.addWidget(self.btn_restart)
        # 主布局：左右分栏 + 右上角
        main_layout = QVBoxLayout()
        h_layout = QHBoxLayout()
        h_layout.addWidget(left_frame)
        h_layout.addWidget(self.stack, 1)
        main_layout.addLayout(top_right_layout)
        main_layout.addLayout(h_layout)
        self.setLayout(main_layout)

        # 按钮暴露为成员变量，便于外部连接信号
        self.btn_all = btn_all
        self.btn_checked = btn_checked
        self.btn_clear = btn_clear
        self.btn_add_cmd = btn_add_cmd
        self.btn_launch_cmd = btn_launch_cmd
        self.btn_log = btn_log
        self.btn_open_scripts = btn_open_scripts

        # 绑定左侧按钮切换内容
        self.btn_software.clicked.connect(self.show_software_page)
        self.btn_command.clicked.connect(self.show_command_page)

        self.tray_manager = TrayManager(self, 'QuickLauncher.ico')

    def show_software_page(self):
        self.stack.setCurrentIndex(0)
        self.btn_software.setChecked(True)
        self.btn_command.setChecked(False)

    def show_command_page(self):
        self.stack.setCurrentIndex(1)
        self.btn_software.setChecked(False)
        self.btn_command.setChecked(True)

    def closeEvent(self, event):
        event.ignore()
        self.hide()
        # self.tray_manager.show_message(
        #     "QuickLauncher",
        #     "程序已最小化到托盘，双击托盘图标可恢复。"
        # )

class IconItemWidget(QWidget):
    def __init__(self, icon, name, launch_time=None, parent=None):
        super().__init__(parent)
        layout = QHBoxLayout(self)
        self.checkbox = QCheckBox()
        self.name_label = QLabel(name)
        self.time_label = QLabel(launch_time or "")
        layout.addWidget(self.checkbox)
        layout.addWidget(self.name_label)
        layout.addStretch()
        layout.addWidget(self.time_label)
        layout.setContentsMargins(2, 2, 2, 2)
        self.setLayout(layout)
        self.setAttribute(Qt.WA_Hover, True)
        self.checked_order = None  # 新增：勾选顺序号
        self._item = None  # 保存对应的QListWidgetItem
        self.on_checkbox_state_changed: Optional[Callable] = None  # 外部注入的回调
        self.checkbox.stateChanged.connect(self._checkbox_state_changed)

    def set_item(self, item):
        self._item = item

    def _checkbox_state_changed(self, state):
        if self.on_checkbox_state_changed and self._item is not None:
            self.on_checkbox_state_changed(self._item)

    def mousePressEvent(self, event):
        if event.button() == Qt.LeftButton:
            self.checkbox.setChecked(not self.checkbox.isChecked())
        super().mousePressEvent(event)

    def set_launch_time(self, launch_time):
        self.time_label.setText(launch_time) 