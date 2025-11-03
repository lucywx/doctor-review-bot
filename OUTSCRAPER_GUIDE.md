# Outscraper集成指南

## 🚀 快速开始

### 1. 注册Outscraper账户
- 访问 [Outscraper官网](https://outscraper.com/)
- 点击"注册"按钮
- 填写邮箱和密码完成注册

### 2. 获取API密钥
- 登录后进入仪表板
- 找到"API Keys"部分
- 复制您的API密钥

### 3. 设置环境变量
```bash
export OUTSCRAPER_API_KEY='your_api_key_here'
```

### 4. 运行测试
```bash
python test_outscraper.py
```

## 📊 功能特性

### 商家搜索
- 按类别和位置搜索商家
- 获取商家基本信息（名称、地址、电话、网站等）
- 支持评分和评论数量

### 评论提取
- 批量获取商家评论
- 包含评论者信息、评分、内容
- 支持时间戳和有用投票数

### 费用控制
- 每月500条评论免费
- 实时费用估算
- 支持预付费和后付费

## 💰 定价结构

| 套餐 | 评论数量 | 价格 |
|------|----------|------|
| 免费 | 1-500条 | $0 |
| 中级 | 501-100,000条 | $3/1000条 |
| 企业 | >100,000条 | $1/1000条 |

## 🔧 API使用示例

### 基本商家搜索
```python
from src.search.outscraper_client import OutscraperClient, OutscraperConfig

config = OutscraperConfig(api_key="your_api_key")
client = OutscraperClient(config)

# 搜索咖啡店
businesses = client.search_businesses(
    query="咖啡店",
    location="北京",
    limit=10
)
```

### 获取评论
```python
# 获取特定商家的评论
reviews = client.get_business_reviews(
    place_id="ChIJ...",  # Google Place ID
    limit=50
)
```

### 综合搜索
```python
# 搜索商家并获取评论
result = client.search_with_reviews(
    query="餐厅",
    location="上海",
    business_limit=5,
    reviews_per_business=20
)
```

## 📈 集成到现有项目

### 1. 添加到搜索聚合器
```python
# 在 src/search/aggregator.py 中添加
from .outscraper_client import OutscraperClient, OutscraperConfig

class SearchAggregator:
    def __init__(self):
        # 现有代码...
        self.outscraper_client = None
        if os.getenv('OUTSCRAPER_API_KEY'):
            config = OutscraperConfig(api_key=os.getenv('OUTSCRAPER_API_KEY'))
            self.outscraper_client = OutscraperClient(config)
    
    def search_with_outscraper(self, query, location=None):
        if not self.outscraper_client:
            return []
        
        return self.outscraper_client.search_businesses(
            query=query,
            location=location,
            limit=20
        )
```

### 2. 添加到WhatsApp处理流程
```python
# 在 src/whatsapp/handler.py 中添加
def handle_outscraper_search(self, message):
    """处理Outscraper搜索请求"""
    query = self.extract_search_query(message)
    location = self.extract_location(message)
    
    if self.outscraper_client:
        result = self.outscraper_client.search_with_reviews(
            query=query,
            location=location,
            business_limit=5,
            reviews_per_business=10
        )
        
        return self.format_outscraper_results(result)
```

## ⚠️ 注意事项

### 1. 费用控制
- 使用预付费方式控制支出
- 定期检查账户余额
- 使用费用估算功能

### 2. 请求限制
- 避免过于频繁的请求
- 实现适当的重试机制
- 监控API使用情况

### 3. 数据保存
- 结果仅保存30天
- 及时下载和备份数据
- 考虑本地存储策略

## 🔍 故障排除

### 常见问题

1. **API密钥无效**
   - 检查环境变量设置
   - 确认API密钥正确
   - 验证账户状态

2. **请求失败**
   - 检查网络连接
   - 确认API限制
   - 查看错误日志

3. **数据为空**
   - 检查搜索参数
   - 确认位置有效性
   - 尝试不同查询词

### 调试技巧
```python
# 启用详细日志
import logging
logging.basicConfig(level=logging.DEBUG)

# 检查账户信息
account_info = client.get_account_info()
print(f"账户状态: {account_info}")
```

## 📚 相关文档

- [Outscraper官方文档](https://outscraper.com/docs)
- [Google Maps API文档](https://developers.google.com/maps/documentation)
- [项目集成指南](./docs/api-integration.md)
