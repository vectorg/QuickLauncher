from PyQt5.QtWidgets import QSystemTrayIcon, QMenu, QAction, QApplication
from PyQt5.QtGui import QKeySequence
from PyQt5.QtCore import Qt
from launcher.icon_creator import create_tray_icon
from utils.process_utils import restart_program

class TrayManager:
    def __init__(self, parent_widget, icon_path=None):
        self.parent = parent_widget
        self.tray_icon = QSystemTrayIcon(self.parent)
        # 使用自定义Q字母图标
        self.tray_icon.setIcon(create_tray_icon())
        # 托盘菜单
        tray_menu = QMenu()
        self.restore_action = QAction("显示主界面(&A)", self.parent)
        self.quit_action = QAction("退出(&E)", self.parent)
        self.restart_action = QAction("重启程序(&R)", self.parent)
        
        # 设置快捷键
        self.restore_action.setShortcut(QKeySequence("A"))
        self.quit_action.setShortcut(QKeySequence("E"))
        self.restart_action.setShortcut(QKeySequence("R"))
        
        tray_menu.addAction(self.restore_action)
        tray_menu.addAction(self.restart_action)
        tray_menu.addAction(self.quit_action)
        self.tray_icon.setContextMenu(tray_menu)
        # 信号连接
        self.restore_action.triggered.connect(self.show_and_focus_window)
        self.quit_action.triggered.connect(QApplication.instance().quit)
        self.restart_action.triggered.connect(restart_program)
        self.tray_icon.activated.connect(self.on_tray_activated)
        self.tray_icon.show()

    def show_message(self, title, message, mtype=QSystemTrayIcon.Information, timeout=2000):
        self.tray_icon.showMessage(title, message, mtype, timeout)

    def on_tray_activated(self, reason):
        if reason == QSystemTrayIcon.DoubleClick:
            self.show_and_focus_window()
            
    def show_and_focus_window(self):
        """显示窗口并聚焦"""
        self.parent.show()
        self.parent.setWindowState(self.parent.windowState() & ~Qt.WindowMinimized | Qt.WindowActive)
        self.parent.activateWindow()
        self.parent.raise_()
