import subprocess
import time
import os
import threading
from utils.log_filename import generate_log_filename

def run_cmd_with_log(cmd, log_dir='data/log', append_mode=False, existing_log_filename=None):
    """
    运行命令并将输出写入日志文件
    
    Args:
        cmd: 要执行的命令
        log_dir: 日志目录
        append_mode: 是否以追加模式打开日志文件
        existing_log_filename: 已存在的日志文件名（用于追加模式）
        
    Returns:
        str: 日志文件路径或None(如果执行失败)
    """
    os.makedirs(log_dir, exist_ok=True)
    
    # 确定日志文件名
    if append_mode and existing_log_filename:
        log_filename = existing_log_filename
    else:
        log_filename = os.path.join(log_dir, generate_log_filename(cmd))
        print(f'[run_cmd_with_log] 日志路径: {log_filename}')
    
    try:
        # 根据模式打开文件
        file_mode = 'a' if append_mode else 'w'
        with open(log_filename, file_mode, encoding='utf-8') as log_file:
            # 写入开始执行的标记（如果不是追加模式，或者是追加模式但没有指定要跳过）
            start_time = time.strftime('%Y-%m-%d %H:%M:%S')
            log_file.write(f"=== 开始执行命令 [{start_time}]: {cmd} ===\n")
            log_file.flush()
            
            process = subprocess.Popen(cmd, shell=True, stdout=subprocess.PIPE, 
                                      stderr=subprocess.STDOUT, encoding='utf-8', errors='replace')
            
            if process.stdout is not None:
                for line in process.stdout:
                    decoded = line.rstrip()
                    print(decoded)
                    log_file.write(decoded + '\n')
                    log_file.flush()  # 确保实时写入文件
                    
            exit_code = process.wait()
            
            # 写入结束执行的标记
            end_time = time.strftime('%Y-%m-%d %H:%M:%S')
            log_file.write(f"\n=== 命令执行完成 [{end_time}] 退出代码: {exit_code} ===\n")
            log_file.flush()
            
        print(f'命令执行完成，日志文件: {log_filename}')
        return log_filename
    except Exception as e:
        print(f'命令执行失败: {cmd} 错误: {e}')
        # 尝试记录错误到日志文件
        try:
            with open(log_filename, 'a', encoding='utf-8') as log_file:
                log_file.write(f"\n=== 执行出错: {str(e)} ===\n")
        except:
            pass
        return None

def run_cmd_async_with_log(cmd, log_dir='data/log'):
    """
    异步运行命令并将输出写入日志文件
    
    Args:
        cmd: 要执行的命令
        log_dir: 日志目录
        
    Returns:
        str: 日志文件路径
    """
    # 创建日志文件
    os.makedirs(log_dir, exist_ok=True)
    log_filename = os.path.join(log_dir, generate_log_filename(cmd))
    
    # 先写入准备执行信息
    with open(log_filename, 'w', encoding='utf-8') as log_file:
        start_time = time.strftime('%Y-%m-%d %H:%M:%S')
        log_file.write(f"=== 准备执行命令 [{start_time}]: {cmd} ===\n")
        log_file.write("正在启动...\n\n")
        log_file.flush()
    
    # 创建线程运行命令
    def run_in_thread():
        # 在线程中以追加模式调用同步方法
        run_cmd_with_log(cmd, log_dir, append_mode=True, existing_log_filename=log_filename)
        
    # 创建并开启线程
    thread = threading.Thread(target=run_in_thread)
    thread.daemon = True
    thread.start()
    
    # 立即返回日志文件名
    return log_filename

if __name__ == '__main__':
    # 你可以修改下面的命令进行测试
    # 例如: cmd = 'echo 中文测试' 或 cmd = 'dir'
    cmd = 'echo 中文测试'
    run_cmd_with_log(cmd)
