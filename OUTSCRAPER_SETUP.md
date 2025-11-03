# Outscraper API 设置指南

## 步骤1：注册账户并获取API Key

### 1. 访问Outscraper官网
打开浏览器，访问：https://outscraper.com/

### 2. 注册账户
- 点击右上角 "Sign Up" 或 "Start Free"
- 使用Google账户登录，或者使用邮箱注册
- 免费账户包含：**500条免费评价/月**

### 3. 获取API Key
注册后，会自动跳转到Dashboard：

1. 在Dashboard页面，点击左侧菜单 **"API"** 或 **"API Keys"**
2. 你会看到一个API key，类似：
   ```
   YXNkZmFzZGZhc2RmYXNkZmFzZGZhc2RmYXNkZmFzZGY=
   ```
3. 点击 **"Copy"** 复制API key

### 4. 启用Google Maps API
- 确保你的账户已启用 "Google Maps" 服务
- 在Dashboard查看 "Available Services"
- 应该看到 ✅ Google Maps Reviews

---

## 步骤2：本地测试

### 方法A：临时设置（当前终端）

```bash
# 设置环境变量
export OUTSCRAPER_API_KEY='你的API_key'

# 验证是否设置成功
echo $OUTSCRAPER_API_KEY

# 运行测试
python3 test_outscraper_doctor.py
```

### 方法B：永久设置（推荐）

#### macOS/Linux:

```bash
# 编辑配置文件
nano ~/.zshrc   # 如果使用zsh
# 或
nano ~/.bashrc  # 如果使用bash

# 添加以下行：
export OUTSCRAPER_API_KEY='你的API_key'

# 保存并退出（Ctrl+O, Enter, Ctrl+X）

# 重新加载配置
source ~/.zshrc  # 或 source ~/.bashrc

# 验证
echo $OUTSCRAPER_API_KEY
```

#### Windows (PowerShell):

```powershell
# 设置环境变量
$env:OUTSCRAPER_API_KEY = "你的API_key"

# 验证
echo $env:OUTSCRAPER_API_KEY
```

---

## 步骤3：添加到.env文件（可选）

```bash
# 在项目根目录创建或编辑.env文件
cd /Users/lucyy/Desktop/coding/project02-docreview

# 添加Outscraper API key
echo "OUTSCRAPER_API_KEY=你的API_key" >> .env
```

**注意**：`.env`文件应该被`.gitignore`忽略，不要提交到Git！

---

## 步骤4：运行测试

```bash
# 测试Outscraper API
python3 test_outscraper_doctor.py
```

**预期输出**：
```
==========================================
🔍 测试：搜索 Dr. Nicholas Lim Lye Tak 的 Google Maps 评价
==========================================

📍 步骤1: 搜索医生所在的医院...
✅ 找到 3 个地点:

1. Columbia Asia Hospital Petaling Jaya
   地址: Petaling Jaya, Malaysia
   评分: 4.5 (5558 条评价)
   Place ID: ChIJjR6RfF5JzDERv1dmkS2Bw8o

...

📝 步骤2: 获取医院的评价...
✅ 获取到 100 条评价

🔍 步骤3: 过滤提到 'Dr. Nicholas Lim Lye Tak' 的评价...
✅ 找到 X 条提到医生的评价
```

---

## 步骤5：配置Railway环境变量

### 方法1：通过Railway Dashboard（推荐）

1. 访问：https://railway.app/dashboard
2. 选择项目：`doctor-review-bot`
3. 点击服务
4. 点击 **Variables** 标签
5. 点击 **New Variable**
6. 添加：
   - 变量名：`OUTSCRAPER_API_KEY`
   - 变量值：`你的API_key`
7. **点击 Deploy 按钮**（重要！）

### 方法2：通过Railway CLI

```bash
# 确保已连接到项目
railway link

# 设置环境变量
railway variables set OUTSCRAPER_API_KEY="你的API_key"

# 验证
railway variables
```

---

## 常见问题

### Q1：免费额度是多少？
A：每月500条免费评价。对于测试足够了。

### Q2：如何查看剩余额度？
A：
```python
python3 -c "
import os
import sys
sys.path.append('src')
from src.search.outscraper_client import OutscraperClient, OutscraperConfig

config = OutscraperConfig(api_key=os.getenv('OUTSCRAPER_API_KEY'))
client = OutscraperClient(config)

info = client.get_account_info()
if info:
    print(f'账户余额: ${info.get(\"balance\", 0)}')
    print(f'使用情况: {info}')
"
```

### Q3：费用如何计算？
A：
- 前500条：免费
- 500-100,000条：$3 / 1000条
- 100,000+条：$1 / 1000条

例如：获取100条评价 × 1次搜索 = 免费

### Q4：API Key在哪里？
A：登录 https://outscraper.com/ → Dashboard → API Keys

### Q5：如何测试API Key是否有效？
```bash
export OUTSCRAPER_API_KEY='你的key'
python3 -c "
import os
import requests

api_key = os.getenv('OUTSCRAPER_API_KEY')
response = requests.get(
    'https://api.outscraper.com/account',
    headers={'X-API-KEY': api_key}
)
print(f'Status: {response.status_code}')
print(f'Response: {response.json()}')
"
```

---

## 下一步

1. ✅ 设置API key
2. ✅ 运行 `python3 test_outscraper_doctor.py`
3. ✅ 检查结果
4. ✅ 如果成功，配置Railway
5. ✅ 部署并测试

---

## 支持

- 官方文档：https://outscraper.com/docs/
- API文档：https://outscraper.com/api-docs/
- 定价：https://outscraper.com/pricing/
