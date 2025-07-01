from PyQt5.QtWidgets import (QWidget, QVBoxLayout, QHBoxLayout, QPushButton, QListWidget, QLabel, QSpinBox, QListWidgetItem, QFileDialog, QInputDialog, QMessageBox)
from PyQt5.QtGui import QIcon
from PyQt5.QtCore import Qt, QSize

class LauncherUI(QWidget):
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

        self.cmd_area = QListWidget()
        self.cmd_area.setSelectionMode(QListWidget.MultiSelection)
        self.cmd_area.setDragDropMode(QListWidget.InternalMove)

        btn_all = QPushButton('全部启动')
        btn_checked = QPushButton('启动勾选')
        btn_clear = QPushButton('清空勾选')
        self.delay_spin = QSpinBox()
        self.delay_spin.setRange(0, 60)
        self.delay_spin.setValue(2)
        delay_label = QLabel('延迟(秒)')

        btn_add_cmd = QPushButton('添加命令')
        btn_launch_cmd = QPushButton('启动命令')
        btn_log = QPushButton('查看日志')
        btn_open_scripts = QPushButton('查看相关脚本文件夹')

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

        # 按钮暴露，便于外部连接
        self.btn_all = btn_all
        self.btn_checked = btn_checked
        self.btn_clear = btn_clear
        self.btn_add_cmd = btn_add_cmd
        self.btn_launch_cmd = btn_launch_cmd
        self.btn_log = btn_log
        self.btn_open_scripts = btn_open_scripts 