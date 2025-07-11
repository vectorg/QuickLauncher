import subprocess
import time
import os
from log_filename import generate_log_filename

def run_cmd_with_log(cmd, log_dir='data/log'):
    os.makedirs(log_dir, exist_ok=True)
    log_filename = os.path.join(log_dir, generate_log_filename(cmd))
    print(f'[run_cmd_with_log] 日志路径: {log_filename}')
    try:
        with open(log_filename, 'w', encoding='utf-8') as log_file:
            process = subprocess.Popen(cmd, shell=True, stdout=subprocess.PIPE, stderr=subprocess.STDOUT)
            if process.stdout is not None:
                while True:
                    line = process.stdout.readline()
                    if not line and process.poll() is not None:
                        break
                    if line:
                        try:
                            decoded = line.decode('gbk').rstrip()
                        except UnicodeDecodeError:
                            decoded = line.decode('utf-8', errors='replace').rstrip()
                        print(decoded)
                        log_file.write(decoded + '\n')
                        log_file.flush()
            process.wait()
        print(f'命令执行完成，日志文件: {log_filename}')
        return log_filename
    except Exception as e:
        print(f'命令执行失败: {cmd} 错误: {e}')
        return None

if __name__ == '__main__':
    # 你可以修改下面的命令进行测试
    # 例如: cmd = 'echo 中文测试' 或 cmd = 'dir'
    cmd = 'echo 中文测试'
    run_cmd_with_log(cmd)
