import os
import re
import json
from PyQt5.QtWidgets import QMessageBox
from utils.log_filename import get_base_log_filename

def find_command_log_files(command, log_dir='data/log'):
    """
    查找命令对应的日志文件
    
    Args:
        command: 命令字符串
        log_dir: 日志目录路径
        
    Returns:
        str: 最新日志文件的完整路径，如果没找到返回None
    """
    if not os.path.exists(log_dir):
        return None
        
    base_filename = get_base_log_filename(command)
    
    # 查找匹配的日志文件
    matching_files = []
    for filename in os.listdir(log_dir):
        if filename.startswith(base_filename + "_") and filename.endswith(".log"):
            matching_files.append(filename)
    
    if matching_files:
        # 按修改时间排序，选择最新的日志文件
        matching_files.sort(key=lambda x: os.path.getmtime(os.path.join(log_dir, x)), reverse=True)
        latest_log = os.path.join(log_dir, matching_files[0])
        return latest_log
    
    return None

def open_command_log(command, log_dir='data/log', parent_widget=None):
    """
    打开命令对应的日志文件
    
    Args:
        command: 命令字符串
        log_dir: 日志目录路径
        parent_widget: 父窗口组件，用于显示消息框
    """
    log_file = find_command_log_files(command, log_dir)
    
    if log_file:
        try:
            os.startfile(log_file)
            return True, f'打开日志文件: {log_file}'
        except Exception as e:
            if parent_widget:
                QMessageBox.warning(parent_widget, '错误', f'无法打开日志文件: {e}')
            return False, f'无法打开日志文件: {e}'
    else:
        base_filename = get_base_log_filename(command)
        if parent_widget:
            QMessageBox.information(parent_widget, '提示', 
                                 f'未找到命令对应的日志文件:\n命令: {command}\n基础文件名: {base_filename}')
        return False, f'未找到命令对应的日志文件: {command}'

def test_log_finder():
    """测试日志文件查找功能"""
    print("=== 日志文件查找测试 ===")
    
    # 从launcher_data.json读取前五个命令进行测试
    try:
        with open('data/launcher_data.json', 'r', encoding='utf-8') as f:
            data = json.load(f)
            test_commands = data.get('cmds', [])[:5]  # 取前五个命令
    except Exception as e:
        print(f"读取launcher_data.json失败: {e}")
        # 使用默认测试命令
        test_commands = [
            "cmd",
            "python.exe test.py",
            "notepad.exe test.txt"
        ]
    
    print(f"测试命令数量: {len(test_commands)}")
    
    for i, cmd in enumerate(test_commands, 1):
        print(f"\n--- 测试 {i}: {cmd} ---")
        
        # 查找日志文件
        log_file = find_command_log_files(cmd)
        
        if log_file:
            print(f"✓ 找到日志文件: {log_file}")
            # 显示文件信息
            try:
                stat = os.stat(log_file)
                print(f"  文件大小: {stat.st_size} 字节")
                print(f"  修改时间: {os.path.getmtime(log_file)}")
            except Exception as e:
                print(f"  获取文件信息失败: {e}")
        else:
            print("✗ 未找到对应的日志文件")
            base_filename = get_base_log_filename(cmd)
            print(f"  期望的基础文件名: {base_filename}")
    
    print("\n=== 测试完成 ===")

if __name__ == "__main__":
    test_log_finder() 