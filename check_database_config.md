# 数据库配置检查指南

## 数据库架构

你的项目有两个数据库环境：

### 1. 本地数据库（开发用）
- **连接**: `postgresql://postgres:postgres@localhost:5432/doctor_review`
- **位置**: 你的Mac电脑
- **用途**: 本地测试
- **状态**: 目前是空的（没有数据）

### 2. 远程数据库（生产用）
- **连接**: Railway自动提供
- **位置**: Railway云端
- **用途**: WhatsApp用户的真实数据
- **状态**: 包含你的搜索记录、配额等

## 如何访问Railway数据库

### 方法1：通过Railway Dashboard（推荐）

1. 登录 https://railway.app/
2. 选择你的项目
3. 查看左侧栏，应该有两个服务：
   - `doctor-review-bot` (Python应用)
   - `postgres` (数据库)

4. 点击 `postgres` 服务
5. 选择 "Data" 或 "Query" 标签
6. 在这里可以运行SQL查询

### 方法2：如果没有PostgreSQL服务

如果你没有看到PostgreSQL，可能使用了外部数据库服务。

检查Railway环境变量：
1. 点击你的Python应用服务
2. 选择 "Variables" 标签
3. 查找 `DATABASE_URL` 变量
4. 这会告诉你实际使用的数据库地址

常见的数据库服务：
- **Supabase**: 连接字符串包含 `supabase.co`
- **Neon**: 连接字符串包含 `neon.tech`
- **Railway PostgreSQL**: 连接字符串包含 `railway.app`

## 更新管理员配额的SQL

无论使用哪个数据库，运行以下SQL：

```sql
-- 更新管理员配额为500/月
UPDATE user_sessions
SET daily_quota = 500, role = 'admin'
WHERE user_id = '+60173745939';

-- 验证更新
SELECT user_id, role, daily_quota, today_usage, total_searches
FROM user_sessions
WHERE user_id = '+60173745939';
```

## 数据流向图

```
WhatsApp用户
    ↓
Twilio API
    ↓
Railway服务器 (Python应用)
    ↓
Railway数据库 (或其他云数据库)
    ↓
存储用户数据、配额、搜索记录
```

你的本地数据库和这个流程完全无关。

## 问题：为什么我的配额显示是50而不是500？

**原因**: 你的用户记录在实现500配额功能之前就已经创建了，数据库中存储的是旧值50。

**解决**: 运行上面的SQL更新语句。

## 截图参考

如果你在Railway看到类似这样的结构：

```
📁 doctor-review-bot (项目)
  ├── 🚀 web (Python应用)
  └── 🗄️ postgres (数据库)
```

说明你有Railway PostgreSQL。

如果只看到：
```
📁 doctor-review-bot (项目)
  └── 🚀 web (Python应用)
```

说明你可能使用外部数据库服务，需要检查环境变量。
