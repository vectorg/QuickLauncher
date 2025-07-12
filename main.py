import sys
import os
from PyQt5.QtWidgets import QApplication
from launcher.launcher_ui import LauncherUI
from launcher.launcher_logic import LauncherLogic
from launcher.launcher_data import LauncherData

# 自动切换到脚本目录
os.chdir(os.path.dirname(os.path.abspath(__file__)))

# 设置编码
# os.system('chcp 65001') # 会打印 Active code page: 65001
# 不打印，静默执行
import subprocess
subprocess.run('chcp 65001', shell=True, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
os.environ['PYTHONIOENCODING'] = 'utf-8'
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
