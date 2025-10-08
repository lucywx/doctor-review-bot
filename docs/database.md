# 数据库设计文档

## 1. 数据库概述

使用 PostgreSQL 作为主数据库，主要用于：
- **缓存医生评价数据**（降低 API 成本）
- **记录搜索日志**（分析用户行为）
- **管理用户会话**（访问控制）

---

## 2. 核心表结构

### 2.1 doctor_reviews（医生评价缓存表）

这是系统最核心的表，按照你的要求设计。

```sql
CREATE TABLE doctor_reviews (
    -- 主键
    id SERIAL PRIMARY KEY,

    -- 医生标识
    doctor_id VARCHAR(255) NOT NULL,          -- 医生唯一标识（姓名+地区 hash）
    doctor_name VARCHAR(255) NOT NULL,        -- 医生姓名
    doctor_specialty VARCHAR(100),            -- 专科（如：心内科、骨科）
    hospital_name VARCHAR(255),               -- 所属医院
    location VARCHAR(255),                    -- 地区

    -- 数据来源
    source VARCHAR(50) NOT NULL,              -- 数据源：google_maps, facebook, hospital_website
    url TEXT NOT NULL,                        -- 原始链接

    -- 评价内容
    snippet TEXT NOT NULL,                    -- 评价摘要/原文
    sentiment VARCHAR(20),                    -- 情感分类：positive, negative, neutral
    rating DECIMAL(2,1),                      -- 评分（1.0-5.0），可能为 NULL
    review_date DATE,                         -- 评价发布日期

    -- 缓存管理
    hash VARCHAR(64) UNIQUE NOT NULL,         -- 内容去重 hash（MD5/SHA256）
    fetched_at TIMESTAMP NOT NULL DEFAULT NOW(), -- 抓取时间
    valid_until TIMESTAMP NOT NULL,           -- 缓存有效期

    -- 显示策略
    display_policy VARCHAR(50) DEFAULT 'normal', -- normal, featured, hidden

    -- 元数据
    metadata JSONB,                           -- 扩展字段（如：点赞数、回复数）
    created_at TIMESTAMP DEFAULT NOW(),
    updated_at TIMESTAMP DEFAULT NOW()
);

-- 索引优化
CREATE INDEX idx_doctor_id ON doctor_reviews(doctor_id);
CREATE INDEX idx_doctor_name ON doctor_reviews(doctor_name);
CREATE INDEX idx_valid_until ON doctor_reviews(valid_until);
CREATE INDEX idx_source ON doctor_reviews(source);
CREATE INDEX idx_sentiment ON doctor_reviews(sentiment);
CREATE INDEX idx_hash ON doctor_reviews(hash);

-- 组合索引（加速缓存查询）
CREATE INDEX idx_doctor_valid ON doctor_reviews(doctor_id, valid_until);
```

#### 字段说明

| 字段 | 类型 | 说明 | 示例 |
|------|------|------|------|
| `doctor_id` | VARCHAR(255) | 医生唯一标识，可用 `MD5(姓名+医院+地区)` | `a3f2c1e8...` |
| `source` | VARCHAR(50) | 数据源标识 | `google_maps`, `facebook`, `hospital_website` |
| `url` | TEXT | 评价原始链接 | `https://maps.google.com/...` |
| `snippet` | TEXT | 评价内容（200-500 字） | "张医生态度很好，耐心..." |
| `hash` | VARCHAR(64) | 去重 hash，防止重复存储 | `SHA256(url+snippet)` |
| `fetched_at` | TIMESTAMP | 数据抓取时间 | `2025-10-08 10:30:00` |
| `valid_until` | TIMESTAMP | 缓存失效时间 | `2025-10-15 10:30:00` (7天后) |
| `display_policy` | VARCHAR(50) | 显示策略 | `normal`, `featured`, `hidden` |

#### display_policy 说明

- **normal**：正常显示
- **featured**：优先展示（高质量评价）
- **hidden**：隐藏（疑似垃圾评论）

---

### 2.2 search_logs（搜索日志表）

记录每次用户搜索，用于分析和成本追踪。

```sql
CREATE TABLE search_logs (
    id SERIAL PRIMARY KEY,

    -- 用户信息
    user_id VARCHAR(100),                     -- WhatsApp 用户 ID（匿名化）
    session_id VARCHAR(100),                  -- 会话 ID

    -- 搜索信息
    doctor_name VARCHAR(255) NOT NULL,        -- 搜索的医生姓名
    doctor_id VARCHAR(255),                   -- 对应的 doctor_id
    location VARCHAR(255),                    -- 搜索地区

    -- 性能指标
    cache_hit BOOLEAN DEFAULT FALSE,          -- 是否命中缓存
    response_time_ms INTEGER,                 -- 响应时间（毫秒）
    sources_used TEXT[],                      -- 使用的数据源数组
    results_count INTEGER,                    -- 返回结果数

    -- 成本追踪
    api_calls_count INTEGER DEFAULT 0,        -- API 调用次数
    estimated_cost_usd DECIMAL(10,4),         -- 估算成本（美元）

    -- 错误信息
    error_message TEXT,                       -- 错误信息（如果有）

    -- 时间戳
    created_at TIMESTAMP DEFAULT NOW()
);

-- 索引
CREATE INDEX idx_user_id ON search_logs(user_id);
CREATE INDEX idx_doctor_name_log ON search_logs(doctor_name);
CREATE INDEX idx_created_at ON search_logs(created_at);
CREATE INDEX idx_cache_hit ON search_logs(cache_hit);
```

---

### 2.3 user_sessions（用户会话表）

管理 WhatsApp 用户访问控制和配额。

```sql
CREATE TABLE user_sessions (
    id SERIAL PRIMARY KEY,

    -- 用户标识
    user_id VARCHAR(100) UNIQUE NOT NULL,     -- WhatsApp 用户 ID（hash）
    phone_number_hash VARCHAR(64),            -- 手机号 hash（不存原号码）

    -- 权限管理
    is_active BOOLEAN DEFAULT TRUE,           -- 是否激活
    role VARCHAR(20) DEFAULT 'user',          -- user, admin, beta_tester

    -- 配额管理
    daily_quota INTEGER DEFAULT 50,           -- 每日搜索配额
    today_usage INTEGER DEFAULT 0,            -- 今日已用次数
    total_searches INTEGER DEFAULT 0,         -- 累计搜索次数

    -- 时间信息
    first_seen_at TIMESTAMP DEFAULT NOW(),
    last_active_at TIMESTAMP DEFAULT NOW(),
    quota_reset_at DATE DEFAULT CURRENT_DATE,

    -- 元数据
    metadata JSONB                            -- 扩展信息（如：偏好设置）
);

-- 索引
CREATE INDEX idx_user_id_session ON user_sessions(user_id);
CREATE INDEX idx_is_active ON user_sessions(is_active);
CREATE INDEX idx_quota_reset ON user_sessions(quota_reset_at);
```

---

### 2.4 doctors（医生主表）

存储医生基本信息，作为评价表的主表。

```sql
CREATE TABLE doctors (
    id SERIAL PRIMARY KEY,

    -- 基本信息
    doctor_id VARCHAR(255) UNIQUE NOT NULL,   -- 医生唯一标识
    name VARCHAR(255) NOT NULL,               -- 姓名
    specialty VARCHAR(100),                   -- 专科
    hospital_name VARCHAR(255),               -- 医院
    location VARCHAR(255),                    -- 地区

    -- 聚合统计
    total_reviews INTEGER DEFAULT 0,          -- 总评论数
    positive_reviews INTEGER DEFAULT 0,       -- 正面评论数
    negative_reviews INTEGER DEFAULT 0,       -- 负面评论数
    average_rating DECIMAL(2,1),              -- 平均评分

    -- 元数据
    google_place_id VARCHAR(255),             -- Google Place ID
    facebook_page_id VARCHAR(255),            -- Facebook Page ID
    official_website TEXT,                    -- 官方网站

    -- 时间戳
    created_at TIMESTAMP DEFAULT NOW(),
    updated_at TIMESTAMP DEFAULT NOW()
);

-- 索引
CREATE INDEX idx_doctor_id_main ON doctors(doctor_id);
CREATE INDEX idx_name ON doctors(name);
CREATE INDEX idx_hospital ON doctors(hospital_name);
```

---

## 3. 关系图

```
doctors (1)  ───────  (*) doctor_reviews
   ↑                           ↓
   │                       (source: google_maps)
   │                       (source: facebook)
   │                       (source: hospital_website)
   │
   └────────  (*) search_logs

user_sessions (1)  ───────  (*) search_logs
```

---

## 4. 核心查询

### 4.1 查询缓存数据

```sql
-- 查询某医生的有效缓存评价
SELECT
    source,
    url,
    snippet,
    sentiment,
    rating,
    review_date
FROM doctor_reviews
WHERE doctor_id = 'a3f2c1e8...'
  AND valid_until > NOW()
  AND display_policy != 'hidden'
ORDER BY
    CASE sentiment
        WHEN 'positive' THEN 1
        WHEN 'neutral' THEN 2
        WHEN 'negative' THEN 3
    END,
    rating DESC NULLS LAST,
    review_date DESC
LIMIT 20;
```

### 4.2 插入新评价（带去重）

```sql
-- 使用 ON CONFLICT 防止重复插入
INSERT INTO doctor_reviews (
    doctor_id, doctor_name, source, url, snippet,
    sentiment, rating, hash, valid_until
)
VALUES (
    'a3f2c1e8...', '张医生', 'google_maps',
    'https://...', '医生很专业...', 'positive', 4.5,
    'hash_value', NOW() + INTERVAL '7 days'
)
ON CONFLICT (hash) DO NOTHING;
```

### 4.3 清理过期缓存

```sql
-- 定期清理（可设置为 Cron Job）
DELETE FROM doctor_reviews
WHERE valid_until < NOW() - INTERVAL '30 days';
```

### 4.4 统计缓存命中率

```sql
SELECT
    DATE(created_at) AS date,
    COUNT(*) AS total_searches,
    SUM(CASE WHEN cache_hit THEN 1 ELSE 0 END) AS cache_hits,
    ROUND(100.0 * SUM(CASE WHEN cache_hit THEN 1 ELSE 0 END) / COUNT(*), 2) AS hit_rate
FROM search_logs
WHERE created_at >= NOW() - INTERVAL '7 days'
GROUP BY DATE(created_at)
ORDER BY date DESC;
```

### 4.5 计算每日成本

```sql
SELECT
    DATE(created_at) AS date,
    SUM(estimated_cost_usd) AS daily_cost,
    COUNT(*) AS total_searches,
    AVG(estimated_cost_usd) AS avg_cost_per_search
FROM search_logs
WHERE created_at >= NOW() - INTERVAL '30 days'
GROUP BY DATE(created_at)
ORDER BY date DESC;
```

---

## 5. 缓存策略实现

### 5.1 缓存有效期规则

```python
def calculate_valid_until(doctor_id, search_count):
    """
    根据搜索热度动态设置缓存时间
    """
    if search_count >= 10:  # 热门医生
        return datetime.now() + timedelta(days=7)
    elif search_count >= 5:
        return datetime.now() + timedelta(days=5)
    else:  # 冷门医生
        return datetime.now() + timedelta(days=3)
```

### 5.2 缓存刷新策略

- **被动刷新**：缓存过期后，下次查询时重新抓取
- **主动预热**：每日凌晨 2 点刷新热门医生数据

```sql
-- 查找需要预热的热门医生
SELECT doctor_id, COUNT(*) AS search_count
FROM search_logs
WHERE created_at >= NOW() - INTERVAL '7 days'
GROUP BY doctor_id
HAVING COUNT(*) >= 5
ORDER BY search_count DESC
LIMIT 50;
```

---

## 6. 数据去重策略

### 6.1 Hash 计算

```python
import hashlib

def generate_hash(url, snippet):
    """
    生成内容唯一 hash
    """
    content = f"{url}|{snippet}"
    return hashlib.sha256(content.encode()).hexdigest()
```

### 6.2 去重逻辑

- 相同 `url + snippet` 视为重复
- 插入时使用 `ON CONFLICT (hash) DO NOTHING`
- 定期清理 30 天前的过期数据

---

## 7. 性能优化

### 7.1 分区表（可选，大数据量时）

```sql
-- 按时间分区
CREATE TABLE doctor_reviews_2025_10 PARTITION OF doctor_reviews
FOR VALUES FROM ('2025-10-01') TO ('2025-11-01');
```

### 7.2 查询优化

- 使用覆盖索引减少回表
- 定期 VACUUM 和 ANALYZE
- 对 JSONB 字段建 GIN 索引

```sql
CREATE INDEX idx_metadata_gin ON doctor_reviews USING GIN (metadata);
```

---

## 8. 备份与恢复

### 8.1 每日备份

```bash
# 备份数据库
pg_dump -U username -d doctor_review_db > backup_$(date +%Y%m%d).sql

# 压缩
gzip backup_$(date +%Y%m%d).sql
```

### 8.2 恢复数据

```bash
# 恢复
gunzip backup_20251008.sql.gz
psql -U username -d doctor_review_db < backup_20251008.sql
```

---

## 9. 监控指标

### 9.1 数据库健康

```sql
-- 表大小监控
SELECT
    tablename,
    pg_size_pretty(pg_total_relation_size(tablename::text)) AS size
FROM pg_tables
WHERE schemaname = 'public'
ORDER BY pg_total_relation_size(tablename::text) DESC;
```

### 9.2 慢查询监控

```sql
-- 开启慢查询日志
ALTER SYSTEM SET log_min_duration_statement = 1000; -- 1秒以上
SELECT pg_reload_conf();
```

---

## 10. 初始化脚本

完整的数据库初始化 SQL：

```sql
-- 创建数据库
CREATE DATABASE doctor_review_db;

-- 连接数据库
\c doctor_review_db;

-- 创建所有表（见上述表结构）
-- ...

-- 插入测试数据
INSERT INTO doctors (doctor_id, name, specialty, hospital_name, location)
VALUES
    ('test_001', '张医生', '心内科', '北京协和医院', '北京'),
    ('test_002', '李医生', '骨科', '上海瑞金医院', '上海');

-- 创建定时清理函数
CREATE OR REPLACE FUNCTION cleanup_old_reviews()
RETURNS void AS $$
BEGIN
    DELETE FROM doctor_reviews WHERE valid_until < NOW() - INTERVAL '30 days';
END;
$$ LANGUAGE plpgsql;

-- 设置定时任务（需要 pg_cron 扩展）
CREATE EXTENSION IF NOT EXISTS pg_cron;
SELECT cron.schedule('cleanup-old-reviews', '0 2 * * *', 'SELECT cleanup_old_reviews()');
```

---

## 11. 扩展设计

### 11.1 未来可能添加的表

- `review_keywords`：关键词提取表
- `doctor_trends`：医生评价趋势分析
- `user_favorites`：用户收藏列表
- `alerts`：评价变动提醒

### 11.2 JSONB 扩展字段示例

```json
{
  "metadata": {
    "likes_count": 15,
    "replies_count": 3,
    "verified_patient": true,
    "visit_date": "2025-09-15",
    "treatment_type": "复诊",
    "wait_time_minutes": 30
  }
}
```
