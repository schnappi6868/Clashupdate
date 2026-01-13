#!/usr/bin/env python3
import os
import requests
from datetime import datetime
import pytz

def get_current_time():
    """获取东八区当前时间"""
    tz_shanghai = pytz.timezone('Asia/Shanghai')
    return datetime.now(tz_shanghai).strftime('%Y-%m-%d %H:%M:%S')

def test_function():
    """测试函数"""
    print("=== 测试脚本开始 ===")
    print(f"当前时间: {get_current_time()}")
    print(f"当前目录: {os.getcwd()}")
    print("目录内容:")
    for file in os.listdir('.'):
        print(f"  - {file}")
    
    # 测试网络连接
    try:
        print("\n测试网络连接...")
        test_url = "https://raw.githubusercontent.com/cler1818/Note/refs/heads/main/ceshi"
        response = requests.get(test_url, timeout=10)
        print(f"测试URL响应状态: {response.status_code}")
        print(f"响应内容前200字符: {response.text[:200]}")
    except Exception as e:
        print(f"网络测试失败: {e}")
    
    print("\n=== 测试脚本结束 ===")

if __name__ == "__main__":
    test_function()
