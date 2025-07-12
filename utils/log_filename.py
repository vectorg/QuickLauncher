# log_filename.py
"""
日志文件名生成与基础名提取工具：
1. get_base_log_filename(command):
   - 取命令字符串按空白分割为各部分。
   - 如果第一段以 .exe 结尾（不区分大小写），则所有部分都用 os.path.basename 取最后一段，再用下划线 _ 连接。
   - 否则，直接用下划线 _ 连接所有部分，并将路径分隔符（:/、\）替换为安全字符（- 或 ;）。
   - 最后对文件名做安全过滤，只保留字母、数字、下划线、分号和连字符，其余全部替换为下划线。
   - 返回不带时间戳和扩展名的基础名。
2. generate_log_filename(command):
   - 基于 get_base_log_filename 结果，拼接当前时间戳（格式：%Y%m%d_%H%M%S），加 .log 后缀。
"""

import os
import time
import re

def get_base_log_filename(command: str) -> str:
    """
    根据命令字符串生成日志文件的基础名（不含时间戳和扩展名）
    """
    parts = command.strip().split()
    if not parts:
        filename = "empty_command"
    elif parts[0].lower().endswith('.exe'):
        new_parts = [os.path.basename(p) for p in parts]
        filename = "_".join(new_parts)
    else:
        filename = "_".join(parts).replace(":\\", "-").replace("\\", "-").replace("/", ";")
    # 只保留安全字符，其余全部替换为下划线
    filename = re.sub(r'[^a-zA-Z0-9_;-]', '_', filename)
    return filename

def generate_log_filename(command: str) -> str:
    """
    根据命令字符串生成带时间戳的完整日志文件名（含 .log 后缀）
    """
    timestamp = time.strftime('%Y%m%d_%H%M%S')
    base = get_base_log_filename(command)
    return f"{base}_{timestamp}.log"

# 示例
if __name__ == "__main__":
    cmds = [
        r"C:\Python39\python.exe C:\myproject\main.py --arg1 val1",
        r"D:\software\notepad.exe C:\myproject\main.py",
        r"python.exe script.py",
        r"for /l %i in (1,1,100) do (echo %i & timeout /t 1 >nul)",
        r"  "
    ]
    for cmd in cmds:
        print(f"命令: {cmd}")
        print(f"基础名: {get_base_log_filename(cmd)}")
        print(f"日志文件名: {generate_log_filename(cmd)}")
        print("-" * 30)