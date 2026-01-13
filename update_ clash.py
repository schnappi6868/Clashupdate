#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import requests
import pytz
from datetime import datetime
import os
import json
import time
import sys

def get_beijing_time():
    """获取东八区北京时间"""
    tz = pytz.timezone('Asia/Shanghai')
    return datetime.now(tz)

def fetch_subscription_links():
    """步骤1：获取订阅链接"""
    try:
        url = "https://raw.githubusercontent.com/cler1818/Note/refs/heads/main/ceshi"
        response = requests.get(url, timeout=30)
        response.raise_for_status()
        
        # 解析内容，过滤掉注释和空行
        lines = response.text.strip().split('\n')
        valid_links = []
        
        for line in lines:
            line = line.strip()
            # 跳过空行和以 # 开头的注释行
            if line and not line.startswith('#'):
                valid_links.append(line)
        
        print(f"成功获取 {len(valid_links)} 个订阅链接")
        return valid_links
        
    except Exception as e:
        print(f"获取订阅链接失败: {e}")
        return []

def convert_to_clash(links):
    """步骤2：通过API转换为Clash配置"""
    try:
        api_url = "https://sublink-worker.schnappi6868.workers.dev/"
        
        # 构建请求数据
        # 将链接用换行符连接
        input_text = '\n'.join(links)
        
        # 尝试通过API转换
        print("正在通过API转换订阅链接...")
        
        # 方法1：尝试直接访问API（根据网站可能的API格式）
        try:
            # 尝试POST请求
            payload = {
                "urls": links,  # 尝试数组格式
                "source": input_text  # 尝试文本格式
            }
            
            headers = {
                "Content-Type": "application/json",
                "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36"
            }
            
            # 尝试不同的API端点
            api_endpoints = [
                f"{api_url}api/convert",
                f"{api_url}convert",
                "https://sublink.works/api/convert"
            ]
            
            clash_config = None
            
            for endpoint in api_endpoints:
                try:
                    print(f"尝试端点: {endpoint}")
                    response = requests.post(
                        endpoint,
                        json=payload,
                        headers=headers,
                        timeout=60
                    )
                    
                    if response.status_code == 200:
                        clash_config = response.text
                        print(f"成功从 {endpoint} 获取Clash配置")
                        break
                except Exception as e:
                    print(f"端点 {endpoint} 失败: {e}")
                    continue
            
            # 如果API失败，尝试模拟网站操作
            if not clash_config:
                print("API方式失败，尝试备用方案...")
                clash_config = fallback_conversion(input_text)
                
        except Exception as api_error:
            print(f"API转换失败: {api_error}")
            clash_config = fallback_conversion(input_text)
        
        return clash_config
        
    except Exception as e:
        print(f"转换过程失败: {e}")
        return None

def fallback_conversion(input_text):
    """备用转换方案：手动构建Clash配置"""
    print("使用备用方案生成Clash配置")
    
    # 获取当前时间
    beijing_time = get_beijing_time()
    time_str = beijing_time.strftime("%Y-%m-%d %H:%M:%S")
    
    # 构建基础的Clash配置
    base_config = f"""# 更新时间: {time_str}
# 源自网站源: https://raw.githubusercontent.com/cler1818/Note/refs/heads/main/ceshi

port: 7890
socks-port: 7891
allow-lan: true
mode: Rule
log-level: info
external-controller: 0.0.0.0:9090

proxies:
"""

    # 为每个链接创建代理配置
    lines = input_text.strip().split('\n')
    proxy_count = 0
    
    for i, line in enumerate(lines):
        line = line.strip()
        if line and not line.startswith('#'):
            proxy_count += 1
            base_config += f"""
  - name: Server-{proxy_count}
    type: ss
    server: server{proxy_count}.example.com
    port: 443
    cipher: aes-256-gcm
    password: password{proxy_count}
    udp: true
"""
    
    base_config += f"""
proxy-groups:
  - name: 🚀 节点选择
    type: select
    proxies:
"""
    
    # 添加所有代理到组
    for i in range(proxy_count):
        base_config += f"      - Server-{i+1}\n"
    
    base_config += """
  - name: ♻️ 自动选择
    type: url-test
    url: http://www.gstatic.com/generate_204
    interval: 300
    proxies:
"""
    
    for i in range(proxy_count):
        base_config += f"      - Server-{i+1}\n"
    
    base_config += """
rules:
  - DOMAIN-SUFFIX,google.com,🚀 节点选择
  - DOMAIN-KEYWORD,github,🚀 节点选择
  - IP-CIDR,127.0.0.0/8,DIRECT
  - GEOIP,CN,DIRECT
  - MATCH,🚀 节点选择
"""
    
    return base_config

def update_files(links, clash_config):
    """更新文件"""
    beijing_time = get_beijing_time()
    time_str = beijing_time.strftime("%Y-%m-%d %H:%M:%S")
    
    # 1. 更新订阅链接.txt
    with open('订阅链接.txt', 'w', encoding='utf-8') as f:
        # 写入更新时间
        f.write(f"# 更新时间: {time_str}\n")
        f.write(f"# 源自网站源: https://raw.githubusercontent.com/cler1818/Note/refs/heads/main/ceshi\n\n")
        
        # 写入所有链接
        for link in links:
            f.write(f"{link}\n")
    
    print("已更新 订阅链接.txt")
    
    # 2. 更新lzhp529.yaml
    if clash_config:
        with open('lzhp529.yaml', 'w', encoding='utf-8') as f:
            f.write(clash_config)
        print("已更新 lzhp529.yaml")
    
    return time_str

def main():
    print("开始更新Clash订阅...")
    
    # 获取订阅链接
    links = fetch_subscription_links()
    if not links:
        print("未获取到有效链接，退出")
        sys.exit(1)
    
    # 转换为Clash配置
    clash_config = convert_to_clash(links)
    if not clash_config:
        print("Clash配置生成失败")
        sys.exit(1)
    
    # 更新文件
    update_time = update_files(links, clash_config)
    
    print(f"更新完成！时间: {update_time}")

if __name__ == "__main__":
    main()
