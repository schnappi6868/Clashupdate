#!/usr/bin/env python3
import requests
import yaml
import pytz
from datetime import datetime
import re
import os
import sys

def get_beijing_time():
    """获取北京时间"""
    beijing_tz = pytz.timezone('Asia/Shanghai')
    return datetime.now(beijing_tz)

def fetch_source_content():
    """从GitHub获取源内容"""
    url = "https://raw.githubusercontent.com/cler1818/Note/refs/heads/main/ceshi"
    
    try:
        response = requests.get(url, timeout=10)
        response.raise_for_status()
        content = response.text
        
        # 过滤掉注释行（以#开头或包含备注的行）
        lines = content.strip().split('\n')
        filtered_lines = []
        
        for line in lines:
            line_stripped = line.strip()
            # 保留非空行且不是注释的行
            if line_stripped and not line_stripped.startswith('#') and '备注' not in line_stripped:
                filtered_lines.append(line_stripped)
        
        return '\n'.join(filtered_lines)
    except Exception as e:
        print(f"获取源内容失败: {e}")
        return None

def convert_to_clash(subscription_links):
    """通过API转换为Clash配置"""
    api_url = "https://sublink.works/api/"
    base_url = "https://sublink-worker.schnappi6868.workers.dev/"
    
    # 构建请求数据
    data = {
        "url": subscription_links,
        "target": "clash",
        "rename": "",
        "include": "",
        "exclude": "",
        "config": "",
        "emoji": "true"
    }
    
    try:
        # 首先获取转换后的内容
        response = requests.post(api_url, json=data, timeout=30)
        response.raise_for_status()
        
        # 从API响应中提取Clash配置
        result = response.json()
        
        if 'content' in result:
            return result['content']
        elif 'data' in result and 'content' in result['data']:
            return result['data']['content']
        else:
            print("API响应格式异常:", result)
            return None
            
    except Exception as e:
        print(f"转换Clash配置失败: {e}")
        # 尝试备用方法：直接访问worker
        try:
            worker_url = "https://sublink-worker.schnappi6868.workers.dev/"
            response = requests.post(worker_url, data={
                "url": subscription_links,
                "target": "clash"
            }, timeout=30)
            response.raise_for_status()
            return response.text
        except Exception as e2:
            print(f"备用方法也失败: {e2}")
            return None

def update_yaml_file(clash_content, source_content):
    """更新YAML文件"""
    if not clash_content:
        return False
    
    # 获取当前时间
    beijing_time = get_beijing_time()
    time_str = beijing_time.strftime("%Y-%m-%d %H:%M:%S %Z")
    
    # 创建更新内容头部
    header = f"""# =========================================
# 自动更新时间: {time_str}
# 源地址: https://raw.githubusercontent.com/cler1818/Note/refs/heads/main/ceshi
# 源内容: {source_content[:100]}...（共{len(source_content)}字符）
# =========================================

"""
    
    # 组合内容
    final_content = header + clash_content
    
    # 写入文件
    with open('lzhp529.yaml', 'w', encoding='utf-8') as f:
        f.write(final_content)
    
    return True

def commit_and_push():
    """提交更改到GitHub"""
    try:
        # 配置git
        os.system('git config --global user.name "github-actions[bot]"')
        os.system('git config --global user.email "github-actions[bot]@users.noreply.github.com"')
        
        # 获取当前北京时间
        beijing_time = get_beijing_time()
        time_str = beijing_time.strftime("%H:%M:%S")
        
        # 添加、提交和推送
        os.system('git add lzhp529.yaml')
        os.system(f'git commit -m "🔄 自动更新Clash配置 [{time_str}]"')
        os.system('git push origin HEAD')
        
        print(f"✅ 更新完成并提交，时间: {time_str}")
        return True
    except Exception as e:
        print(f"提交失败: {e}")
        return False

def main():
    print("🔄 开始更新Clash配置...")
    
    # 1. 获取源内容
    print("📥 获取源内容...")
    source_content = fetch_source_content()
    if not source_content:
        print("❌ 无法获取源内容")
        sys.exit(1)
    
    print(f"✅ 获取到源内容，长度: {len(source_content)} 字符")
    
    # 2. 转换为Clash配置
    print("⚙️ 转换为Clash配置...")
    clash_content = convert_to_clash(source_content)
    if not clash_content:
        print("❌ 无法转换为Clash配置")
        sys.exit(1)
    
    print(f"✅ 转换成功，长度: {len(clash_content)} 字符")
    
    # 3. 更新YAML文件
    print("📝 更新YAML文件...")
    if update_yaml_file(clash_content, source_content):
        print("✅ YAML文件更新成功")
    else:
        print("❌ YAML文件更新失败")
        sys.exit(1)
    
    # 4. 提交更改
    print("🚀 提交更改到GitHub...")
    if commit_and_push():
        print("🎉 所有操作完成！")
    else:
        print("⚠️ 更新成功但提交失败")

if __name__ == "__main__":
    main()
