import requests
from datetime import datetime

print("开始更新Clash订阅...")

# 1. 获取订阅链接
url = "https://raw.githubusercontent.com/cler1818/Note/refs/heads/main/ceshi"
response = requests.get(url, timeout=30)
links = []
for line in response.text.split('\n'):
    line = line.strip()
    if line and not line.startswith('#'):
        links.append(line)

print(f"找到 {len(links)} 个链接")

# 2. 保存到订阅链接.txt
now = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
with open('订阅链接.txt', 'w', encoding='utf-8') as f:
    f.write(f"# 更新时间: {now}\n")
    f.write(f"# 源自: https://raw.githubusercontent.com/cler1818/Note/refs/heads/main/ceshi\n\n")
    for link in links:
        f.write(f"{link}\n")

print("已保存 订阅链接.txt")

# 3. 生成简单的lzhp529.yaml
with open('lzhp529.yaml', 'w', encoding='utf-8') as f:
    f.write(f"""# 更新时间: {now}
# 源自: https://raw.githubusercontent.com/cler1818/Note/refs/heads/main/ceshi

port: 7890
socks-port: 7891
mode: Rule
log-level: info

proxies:
  - name: 测试节点
    type: ss
    server: example.com
    port: 443
    cipher: aes-256-gcm
    password: password

proxy-groups:
  - name: 🚀 代理
    type: select
    proxies:
      - 测试节点

rules:
  - DOMAIN-SUFFIX,google.com,🚀 代理
  - DOMAIN-KEYWORD,github,🚀 代理
  - MATCH,🚀 代理
""")

print("已保存 lzhp529.yaml")
print("更新完成！")
