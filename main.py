import sys
from PyQt5.QtWidgets import QApplication
from launcher_ui import LauncherUI
from launcher_logic import LauncherLogic
from launcher_data import LauncherData

if __name__ == '__main__':
    app = QApplication(sys.argv)
    ui = LauncherUI()
    data = LauncherData()
    logic = LauncherLogic(ui, data)
    ui.show()
    sys.exit(app.exec_()) 