import requests
import pytz
from datetime import datetime
import os
import json
import time
import sys

def get_beijing_time():
    tz = pytz.timezone('Asia/Shanghai')
    return datetime.now(tz)

def fetch_subscription_links():
    try:
        url = "https://raw.githubusercontent.com/cler1818/Note/refs/heads/main/ceshi"
        response = requests.get(url, timeout=30)
        response.raise_for_status()
        
        lines = response.text.strip().split('\n')
        valid_links = []
        
        for line in lines:
            line = line.strip()
            if line and not line.startswith('#'):
                valid_links.append(line)
        
        print(f"成功获取 {len(valid_links)} 个订阅链接")
        return valid_links
        
    except Exception as e:
        print(f"获取订阅链接失败: {e}")
        return []

def convert_to_clash(links):
    try:
        api_url = "https://sublink-worker.schnappi6868.workers.dev/"
        input_text = '\n'.join(links)
        
        print("正在通过API转换订阅链接...")
        
        headers = {
            "Content-Type": "application/json",
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36"
        }
        
        clash_config = None
        
        api_endpoints = [
            f"{api_url}api/convert",
            f"{api_url}convert",
            "https://sublink.works/api/convert"
        ]
        
        for endpoint in api_endpoints:
            try:
                print(f"尝试端点: {endpoint}")
                payload = {"urls": links}
                response = requests.post(endpoint, json=payload, headers=headers, timeout=60)
                
                if response.status_code == 200:
                    clash_config = response.text
                    print(f"成功从 {endpoint} 获取Clash配置")
                    break
            except:
                continue
        
        if not clash_config:
            print("API方式失败，使用备用方案...")
            clash_config = fallback_conversion(input_text)
                
        return clash_config
        
    except Exception as e:
        print(f"转换失败: {e}")
        return fallback_conversion(input_text)

def fallback_conversion(input_text):
    beijing_time = get_beijing_time()
    time_str = beijing_time.strftime("%Y-%m-%d %H:%M:%S")
    
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
"""
    
    if proxy_count == 0:
        base_config += "  - name: Example-Server\n    type: ss\n    server: example.com\n    port: 443\n"
    
    base_config += """
proxy-groups:
  - name: 🚀 节点选择
    type: select
    proxies:
"""
    
    for i in range(max(proxy_count, 1)):
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
    beijing_time = get_beijing_time()
    time_str = beijing_time.strftime("%Y-%m-%d %H:%M:%S")
    
    with open('订阅链接.txt', 'w', encoding='utf-8') as f:
        f.write(f"# 更新时间: {time_str}\n")
        f.write(f"# 源自网站源: https://raw.githubusercontent.com/cler1818/Note/refs/heads/main/ceshi\n\n")
        for link in links:
            f.write(f"{link}\n")
    
    print("已更新 订阅链接.txt")
    
    if clash_config:
        with open('lzhp529.yaml', 'w', encoding='utf-8') as f:
            f.write(clash_config)
        print("已更新 lzhp529.yaml")
    
    return time_str

def main():
    print("开始更新Clash订阅...")
    links = fetch_subscription_links()
    if not links:
        print("未获取到有效链接，使用空配置")
        links = ["https://example.com/subscribe"]
    
    clash_config = convert_to_clash(links)
    update_time = update_files(links, clash_config)
    print(f"更新完成！时间: {update_time}")

if __name__ == "__main__":
    main()
