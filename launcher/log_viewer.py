import os
import time
from PyQt5.QtWidgets import QWidget, QVBoxLayout, QLabel, QTextEdit, QSplitter, QPushButton, QHBoxLayout
from PyQt5.QtCore import Qt, QTimer, pyqtSignal, QObject
from PyQt5.QtGui import QTextCursor
from utils.log_finder import find_command_log_files

class LogSignals(QObject):
    """用于日志更新的信号类"""
    log_update = pyqtSignal(str)
    log_file_changed = pyqtSignal(str)

class LogViewer:
    """日志查看器类，负责显示和更新命令执行日志"""
    def __init__(self, ui, log_dir='data/log'):
        self.ui = ui
        self.log_dir = log_dir
        self.current_log_file = None
        self.last_log_size = 0
        self.signals = LogSignals()
        
        # 创建日志显示区域
        self.create_log_display()
        
        # 创建日志监控定时器
        self.log_timer = QTimer()
        self.log_timer.timeout.connect(self.check_for_new_logs)
        self.log_timer.start(1000)  # 每秒检查一次
        
        # 连接信号
        self.signals.log_update.connect(self.update_log_display)
        self.signals.log_file_changed.connect(self.display_log_file)
    
    def create_log_display(self):
        """创建日志显示区域"""
        # 创建日志显示文本框
        self.ui.log_display = QTextEdit()
        self.ui.log_display.setReadOnly(True)
        self.ui.log_display.setPlaceholderText("命令执行日志将显示在这里...")
        self.ui.log_display.setLineWrapMode(QTextEdit.NoWrap)
        
        # 创建清空日志按钮
        self.ui.btn_clear_log = QPushButton('清空日志')
        self.ui.btn_clear_log.clicked.connect(self.clear_log_display)
        
        # 如果命令启动页已经初始化，则添加日志区域
        if hasattr(self.ui, 'cmd_area') and hasattr(self.ui, 'stack'):
            # 获取命令启动页
            cmd_page = self.ui.stack.widget(1)
            
            # 检查当前布局类型
            if cmd_page.layout() is None:
                # 如果没有布局，创建一个新的垂直布局
                cmd_page_layout = QVBoxLayout()
                cmd_page.setLayout(cmd_page_layout)
            
            # 清除之前的内容
            while cmd_page.layout().count():
                item = cmd_page.layout().takeAt(0)
                if item.widget():
                    item.widget().setParent(None)
            
            # 重新创建命令区域布局
            cmd_area_layout = QVBoxLayout()
            cmd_area_layout.addWidget(QLabel('命令区域'))
            cmd_area_layout.addWidget(self.ui.cmd_area)
            
            # 恢复命令按钮布局
            cmd_btn_layout = QHBoxLayout()
            cmd_btn_layout.addWidget(self.ui.btn_add_cmd)
            cmd_btn_layout.addWidget(self.ui.btn_launch_cmd)
            cmd_btn_layout.addWidget(self.ui.btn_log)
            cmd_btn_layout.addWidget(self.ui.btn_open_scripts)
            cmd_btn_layout.addWidget(self.ui.btn_clear_log)
            cmd_btn_layout.addStretch()
            
            cmd_area_layout.addLayout(cmd_btn_layout)
            
            # 命令区域面板
            cmd_widget = QWidget()
            cmd_widget.setLayout(cmd_area_layout)
            
            # 日志区域布局
            log_layout = QVBoxLayout()
            log_layout.addWidget(QLabel('命令执行日志'))
            log_layout.addWidget(self.ui.log_display)
            
            # 添加清空日志按钮到日志区域
            log_btn_layout = QHBoxLayout()
            log_btn_layout.addWidget(self.ui.btn_clear_log)
            log_btn_layout.addStretch()
            log_layout.addLayout(log_btn_layout)
            
            log_widget = QWidget()
            log_widget.setLayout(log_layout)
            
            # 使用分割器
            splitter = QSplitter(Qt.Horizontal)
            splitter.addWidget(cmd_widget)
            splitter.addWidget(log_widget)
            splitter.setSizes([300, 500])  # 设置初始宽度比例
            
            # 添加到命令页布局
            cmd_page.layout().addWidget(splitter)
    
    def set_current_log_file(self, log_file):
        """设置当前要监控的日志文件"""
        self.current_log_file = log_file
        self.last_log_size = 0
        # 通知UI更新
        self.signals.log_file_changed.emit(log_file)
    
    def display_log_file(self, log_file):
        """显示日志文件内容"""
        # 清空当前日志显示
        self.ui.log_display.clear()
        if log_file and os.path.exists(log_file):
            # 添加标题
            self.ui.log_display.append(f"=== 正在监控日志文件: {os.path.basename(log_file)} ===\n")
            
            # 读取日志文件内容
            try:
                with open(log_file, 'r', encoding='utf-8', errors='replace') as f:
                    content = f.read()
                    self.ui.log_display.append(content)
                    self.last_log_size = os.path.getsize(log_file)
            except Exception as e:
                self.ui.log_display.append(f"读取日志失败: {str(e)}")
        else:
            self.ui.log_display.append("没有可显示的日志文件")
    
    def check_for_new_logs(self):
        """检查日志文件是否有更新"""
        if self.current_log_file and os.path.exists(self.current_log_file):
            try:
                # 获取当前文件大小
                current_size = os.path.getsize(self.current_log_file)
                if current_size > self.last_log_size:
                    # 有新内容，读取新增部分
                    with open(self.current_log_file, 'r', encoding='utf-8', errors='replace') as f:
                        f.seek(self.last_log_size)
                        new_content = f.read()
                        if new_content:
                            # 更新到UI
                            self.signals.log_update.emit(new_content)
                    # 更新记录的文件大小
                    self.last_log_size = current_size
            except Exception as e:
                print(f"监控日志文件出错: {e}")
    
    def update_log_display(self, text):
        """更新日志显示内容"""
        cursor = self.ui.log_display.textCursor()
        cursor.movePosition(QTextCursor.End)
        self.ui.log_display.setTextCursor(cursor)
        self.ui.log_display.insertPlainText(text)
        self.ui.log_display.ensureCursorVisible()
    
    def clear_log_display(self):
        """清空日志显示区域"""
        self.ui.log_display.clear()
    
    def find_and_display_cmd_log(self, cmd):
        """查找并显示指定命令的日志"""
        log_file = find_command_log_files(cmd, self.log_dir)
        if log_file:
            self.set_current_log_file(log_file)
            return True
        return False 