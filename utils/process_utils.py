import sys
import os

def restart_program():
    """重启当前程序"""
    python = sys.executable
    os.execl(python, python, *sys.argv)
