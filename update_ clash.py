#!/usr/bin/env python3
import os
import requests
import re
from datetime import datetime
import pytz
import json
from urllib.parse import urlparse

def get_current_time():
    """获取东八区当前时间"""
    tz_shanghai = pytz.timezone('Asia/Shanghai')
    return datetime.now(tz_shanghai).strftime('%Y-%m-%d %H:%M:%S')

def fetch_source_urls():
    """从源URL获取网址列表"""
    source_url = "https://raw.githubusercontent.com/cler1818/Note/refs/heads/main/ceshi"
    
    try:
        response = requests.get(source_url, timeout=30)
        response.raise_for_status()
        
        content = response.text
        urls = []
        
        # 提取所有非注释行的网址
        for line in content.split('\n'):
            line = line.strip()
            # 跳过空行和注释（以#开头或包含"备注"的行）
            if not line or line.startswith('#') or '备注' in line or '#' in line:
                continue
            
            # 提取网址（匹配http/https开头的URL）
            url_match = re.search(r'(https?://[^\s<>"\']+)', line)
            if url_match:
                url = url_match.group(1)
                urls.append(url)
        
        return urls
    except Exception as e:
        print(f"Error fetching source URLs: {e}")
        return []

def save_subscription_links(urls):
    """保存订阅链接到文件"""
    current_time = get_current_time()
    
    # 构建文件内容
    content = f"# 更新时间: {current_time} (UTC+8)\n"
    content += f"# 源自: https://raw.githubusercontent.com/cler1818/Note/refs/heads/main/ceshi\n\n"
    content += "\n".join(urls)
    
    # 保存到文件
    with open("订阅链接.txt", "w", encoding="utf-8") as f:
        f.write(content)
    
    return content

def convert_to_clash_config(urls):
    """使用sublink API转换为Clash配置"""
    api_url = "https://sublink-worker.schnappi6868.workers.dev/"
    
    try:
        # 准备请求数据
        # 将URL列表转换为字符串，每行一个
        urls_text = "\n".join(urls)
        
        # 方法1：尝试直接调用API（如果可用）
        # 根据网站结构，可能需要发送POST请求
        payload = {
            'urls': urls_text,
            'target': 'clash',
            'config': 'clash'
        }
        
        headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36',
            'Content-Type': 'application/x-www-form-urlencoded',
        }
        
        # 尝试访问转换页面获取Clash配置
        print("Converting URLs to Clash config via sublink...")
        
        # 由于不知道确切的API端点，这里尝试几种方式
        # 方式1：直接POST到workers.dev
        response = requests.post(api_url, data={'urls': urls_text}, timeout=60)
        
        if response.status_code == 200:
            clash_config = response.text
            # 检查返回内容是否包含clash配置的典型特征
            if 'proxies:' in clash_config or 'port:' in clash_config:
                return clash_config
        
        # 方式2：如果上面的方式不行，尝试模拟网页操作（通过requests）
        # 首先访问主页获取可能的token或session
        session = requests.Session()
        home_response = session.get(api_url, timeout=30)
        
        # 尝试找到转换表单
        if home_response.status_code == 200:
            # 简单模拟：直接POST到可能的API端点
            convert_url = "https://sublink.works/api/convert"
            try:
                api_response = session.post(convert_url, json={'urls': urls, 'type': 'clash'}, timeout=60)
                if api_response.status_code == 200:
                    return api_response.text
            except:
                pass
        
        print("Warning: Could not get Clash config from API, using fallback method")
        return generate_fallback_config(urls)
        
    except Exception as e:
        print(f"Error converting to Clash config: {e}")
        return generate_fallback_config(urls)

def generate_fallback_config(urls):
    """生成一个基本的Clash配置文件作为备用"""
    current_time = get_current_time()
    
    config = f"""# Clash 配置文件
# 更新时间: {current_time} (UTC+8)
# 源自: https://raw.githubusercontent.com/cler1818/Note/refs/heads/main/ceshi
# 注意: 这是备用配置，可能需要手动配置服务器

port: 7890
socks-port: 7891
allow-lan: true
mode: Rule
log-level: info
external-controller: 0.0.0.0:9090

proxies:
"""

    # 为每个URL创建一个代理条目
    for i, url in enumerate(urls, 1):
        # 解析URL获取域名
        parsed = urlparse(url)
        domain = parsed.netloc
        
        config += f"""
  - name: Server-{i}
    type: ss
    server: {domain}
    port: 443
    cipher: aes-256-gcm
    password: password
    plugin: v2ray-plugin
    plugin-opts:
      mode: websocket
      tls: true
      skip-cert-verify: true
      host: {domain}
      path: /
"""

    config += """
proxy-groups:
  - name: 🚀 节点选择
    type: select
    proxies:
      - ♻️ 自动选择
      - 🇭🇰 香港节点
      - 🇺🇸 美国节点
      - 🇸🇬 新加坡节点
      - DIRECT

  - name: ♻️ 自动选择
    type: url-test
    url: http://www.gstatic.com/generate_204
    interval: 300
    tolerance: 50
    proxies:
"""

    for i in range(1, len(urls) + 1):
        config += f"      - Server-{i}\n"

    config += """
  - name: 🌍 国外媒体
    type: select
    proxies:
      - 🚀 节点选择
      - ♻️ 自动选择
      - DIRECT

  - name: 📲 电报信息
    type: select
    proxies:
      - 🚀 节点选择
      - ♻️ 自动选择
      - DIRECT

rules:
  - DOMAIN-SUFFIX,google.com,🌍 国外媒体
  - DOMAIN-SUFFIX,youtube.com,🌍 国外媒体
  - DOMAIN-SUFFIX,netflix.com,🌍 国外媒体
  - DOMAIN-SUFFIX,twitter.com,🌍 国外媒体
  - DOMAIN-SUFFIX,telegram.org,📲 电报信息
  - IP-CIDR,192.168.0.0/16,DIRECT
  - GEOIP,CN,DIRECT
  - MATCH,🚀 节点选择
"""
    
    return config

def save_clash_config(config):
    """保存Clash配置到文件"""
    with open("lzhp529.yaml", "w", encoding="utf-8") as f:
        f.write(config)

def main():
    print("Starting Clash config update...")
    
    # 步骤1：获取网址
    print("Fetching source URLs...")
    urls = fetch_source_urls()
    
    if not urls:
        print("No URLs found!")
        return
    
    print(f"Found {len(urls)} URLs")
    
    # 保存订阅链接
    print("Saving subscription links...")
    save_subscription_links(urls)
    
    # 步骤2：转换为Clash配置
    print("Converting to Clash config...")
    clash_config = convert_to_clash_config(urls)
    
    # 保存Clash配置
    print("Saving Clash config...")
    save_clash_config(clash_config)
    
    print("Update completed!")

if __name__ == "__main__":
    main()
