# 测试指南

## 测试概述

本项目包含完整的性能测试套件，用于验证系统在各种场景下的表现。

---

## 性能测试结果

### 测试环境
- **平台**: macOS (Darwin 24.6.0)
- **Python**: 3.10+
- **数据库**: SQLite (开发环境)
- **模式**: Mock Mode（无需真实 API）

### 测试指标

#### 1. 缓存性能 ✅
- **Cache Miss 平均响应**: 9ms
- **Cache Hit 平均响应**: 9ms
- **加速比**: 1.0x（Mock 模式下均从内存返回）

**说明**: 在 Mock 模式下，所有查询都很快。在生产环境使用真实 API 时，缓存命中会显著快于 API 调用（预计 5-10x 加速）。

#### 2. 并发负载测试 ✅
- **并发用户数**: 10
- **总请求数**: 10
- **成功率**: 100% (10/10)
- **总处理时间**: 0.07s
- **平均响应时间**: 41ms
- **最小响应时间**: 18ms
- **最大响应时间**: 64ms
- **P95 响应时间**: 64ms

**结论**: 系统可以轻松处理 10 个并发用户，所有请求在 100ms 内完成。

#### 3. 响应一致性测试 ✅
- **测试次数**: 5 次
- **平均响应时间**: 9ms
- **标准差**: 1ms
- **变异系数**: 11.9%

**结论**: 响应时间非常稳定，变异系数低于 15%。

---

## 运行测试

### 前置条件

1. **启动应用**:
```bash
# 激活虚拟环境
source venv/bin/activate

# 启动服务
python src/main.py
```

2. **确保服务运行在 http://localhost:8000**

### 执行性能测试

```bash
# 运行完整性能测试套件
python tests/test_performance.py
```

### 测试内容

测试脚本会自动执行：

1. **健康检查**: 验证服务器可访问性
2. **缓存性能测试**: 比较缓存命中和未命中的响应时间
3. **并发负载测试**: 模拟 10 个用户同时发送请求
4. **响应一致性测试**: 验证多次查询的稳定性

---

## 手动测试

### 1. 健康检查

```bash
curl http://localhost:8000/health
```

预期输出：
```json
{
  "status": "healthy",
  "environment": "development",
  "database": "connected"
}
```

### 2. 测试 Webhook 验证

```bash
curl "http://localhost:8000/webhook/whatsapp?hub.mode=subscribe&hub.verify_token=your_verify_token&hub.challenge=test123"
```

预期输出：
```
test123
```

### 3. 测试消息处理

```bash
curl -X POST http://localhost:8000/webhook/whatsapp/test \
  -H "Content-Type: application/json" \
  -d '{
    "from": "+1234567890",
    "text": "李医生"
  }'
```

预期输出：
```json
{
  "status": "received",
  "from": "+1234567890",
  "text": "李医生"
}
```

查看日志，应该看到：
- 📨 收到消息
- 🔍 搜索医生评价
- ✅/❌ 缓存命中/未命中
- 📝 记录搜索日志
- 📤 发送格式化回复

### 4. 查看统计数据

```bash
curl http://localhost:8000/api/stats/daily
```

预期输出：
```json
{
  "total_searches": 15,
  "cache_hits": 10,
  "cache_hit_rate": 66.7,
  "avg_response_time_ms": 9.2,
  "total_cost_usd": 0.0,
  "total_api_calls": 0
}
```

---

## 性能基准

### 开发环境 (Mock 模式)

| 指标 | 目标 | 实际 | 状态 |
|------|------|------|------|
| 单次查询响应 | <100ms | 9ms | ✅ 优秀 |
| 并发 10 用户 P95 | <500ms | 64ms | ✅ 优秀 |
| 缓存命中率 | >60% | N/A (Mock) | ⏭️  待生产验证 |
| 系统稳定性 (CV) | <20% | 11.9% | ✅ 优秀 |

### 生产环境预期 (真实 API)

| 指标 | 目标值 |
|------|--------|
| Cache Miss (首次查询) | <10s |
| Cache Hit (缓存查询) | <500ms |
| 缓存命中率 | 60-70% |
| 并发 30 用户 P95 | <15s |
| API 成本 (30用户/月) | $3-5 |

---

## 压力测试

### 测试更高并发

修改 `tests/test_performance.py` 中的并发数：

```python
# 测试 30 个并发用户
results["concurrent"] = await self.test_concurrent_load(num_users=30)
```

### 测试缓存穿透

```python
# 测试 100 次不同的医生查询（模拟缓存穿透）
for i in range(100):
    result = await self.send_whatsapp_message(f"医生{i}")
```

---

## 监控建议

### 生产环境监控指标

1. **响应时间**
   - P50, P95, P99 响应时间
   - Cache hit vs miss 比例

2. **API 使用量**
   - 每日 API 调用次数
   - 每日 API 成本
   - 错误率

3. **用户活跃度**
   - 每日活跃用户
   - 每用户查询次数
   - 配额使用情况

4. **系统健康**
   - 数据库连接状态
   - 内存使用
   - CPU 使用率

### Railway 平台监控

```bash
# 查看实时日志
railway logs --tail

# 查看资源使用
railway status
```

---

## 故障排查

### 测试失败常见原因

**问题**: `Server not available`
- **原因**: 应用未启动
- **解决**: 运行 `python src/main.py`

**问题**: 响应时间过长
- **原因**: 数据库查询慢或网络延迟
- **解决**: 检查数据库连接，查看日志

**问题**: 并发测试失败
- **原因**: 端口被占用或资源不足
- **解决**: 重启应用，增加系统资源

---

## 下一步优化

基于测试结果，可以考虑：

1. ✅ **当前性能优秀** - Mock 模式下响应极快
2. 🔄 **生产环境验证** - 使用真实 API 测试
3. 📊 **缓存策略优化** - 根据热门医生调整 TTL
4. 🚀 **扩展性测试** - 测试更大规模用户（50+）
5. 💰 **成本优化** - 监控实际 API 使用成本

---

## 性能测试最佳实践

1. **定期测试**: 每次重大更新后运行性能测试
2. **多环境测试**: 在开发、测试、生产环境分别验证
3. **记录基准**: 保存每次测试结果，追踪性能变化
4. **模拟真实场景**: 使用真实的医生名称和查询模式
5. **监控生产**: 使用 Sentry 或类似工具监控生产环境

---

## 总结

✅ **系统性能优秀**
- 所有测试通过
- 响应时间低于目标值
- 并发处理能力良好
- 响应稳定性高

🚀 **准备部署**
- 完成所有功能开发
- 性能测试通过
- 可以开始生产环境部署

📖 **参考文档**
- [DEPLOYMENT_GUIDE.md](./DEPLOYMENT_GUIDE.md) - 部署指南
- [README.md](./README.md) - 使用指南
