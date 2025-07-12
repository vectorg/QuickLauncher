import sys
from PyQt5.QtWidgets import QApplication
from launcher.launcher_ui import LauncherUI
from launcher.launcher_logic import LauncherLogic
from launcher.launcher_data import LauncherData

# 程序入口
if __name__ == '__main__':
    # 创建Qt应用
    app = QApplication(sys.argv)
    # 创建UI界面
    ui = LauncherUI()
    # 创建数据管理对象
    data = LauncherData()
    # 创建逻辑处理对象，连接UI和数据
    logic = LauncherLogic(ui, data)
    # 显示主界面
    ui.show()
    # 进入主事件循环
    sys.exit(app.exec_()) 