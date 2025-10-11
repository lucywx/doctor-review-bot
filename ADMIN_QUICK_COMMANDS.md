# Admin Quick Commands - 管理员快速查询

## 📱 通过 WhatsApp（推荐）

发送给 bot 号码 `+1 415 523 8886`:

```
pending          - 查看待审批用户
approve +60xxx   - 批准用户
reject +60xxx    - 拒绝用户
```

---

## 💻 通过数据库查询

**数据库路径**:
```bash
/Users/lucyy/Desktop/coding/project02-docreview/doctor_review.db
```

### 基础命令格式：
```bash
cd /Users/lucyy/Desktop/coding/project02-docreview
sqlite3 doctor_review.db "<SQL查询>"
```

---

## 🔍 常用查询

### 1. 查看待审批用户
```bash
sqlite3 doctor_review.db -header -column \
  "SELECT phone_number, requested_at
   FROM user_whitelist
   WHERE approved = 0;"
```

### 2. 查看所有已批准用户
```bash
sqlite3 doctor_review.db -header -column \
  "SELECT phone_number, approved_at
   FROM user_whitelist
   WHERE approved = 1;"
```

### 3. 查看活跃用户（使用量排名）
```bash
sqlite3 doctor_review.db -header -column \
  "SELECT user_id, total_searches, today_usage, last_active_at
   FROM user_sessions
   ORDER BY total_searches DESC
   LIMIT 10;"
```

### 4. 查看今日搜索活动
```bash
sqlite3 doctor_review.db -header -column \
  "SELECT user_id, doctor_name, created_at
   FROM search_logs
   WHERE DATE(created_at) = DATE('now')
   ORDER BY created_at DESC;"
```

### 5. 查看热门医生（搜索次数排名）
```bash
sqlite3 doctor_review.db -header -column \
  "SELECT doctor_name, COUNT(*) as searches
   FROM search_logs
   GROUP BY doctor_name
   ORDER BY searches DESC
   LIMIT 10;"
```

### 6. 查看某个用户的搜索历史
```bash
sqlite3 doctor_review.db -header -column \
  "SELECT doctor_name, created_at, cache_hit, response_time_ms
   FROM search_logs
   WHERE user_id = '+60123456789'
   ORDER BY created_at DESC;"
```

### 7. 查看今日统计
```bash
sqlite3 doctor_review.db -header -column \
  "SELECT
     COUNT(*) as total_searches,
     SUM(cache_hit) as cache_hits,
     ROUND(AVG(response_time_ms)) as avg_response_ms,
     COUNT(DISTINCT user_id) as active_users
   FROM search_logs
   WHERE DATE(created_at) = DATE('now');"
```

### 8. 查看某个用户的配额使用情况
```bash
sqlite3 doctor_review.db -header -column \
  "SELECT user_id, today_usage, daily_quota,
          (daily_quota - today_usage) as remaining
   FROM user_sessions
   WHERE user_id = '+60123456789';"
```

---

## 🛠️ 管理操作

### 手动批准用户
```bash
sqlite3 doctor_review.db \
  "INSERT OR REPLACE INTO user_whitelist (phone_number, approved, approved_at)
   VALUES ('+60123456789', 1, CURRENT_TIMESTAMP);"
```

### 手动拒绝/删除用户
```bash
sqlite3 doctor_review.db \
  "DELETE FROM user_whitelist WHERE phone_number = '+60123456789';"
```

### 重置某个用户的今日配额
```bash
sqlite3 doctor_review.db \
  "UPDATE user_sessions
   SET today_usage = 0, quota_reset_at = CURRENT_DATE
   WHERE user_id = '+60123456789';"
```

### 修改某个用户的每日配额
```bash
sqlite3 doctor_review.db \
  "UPDATE user_sessions
   SET daily_quota = 100
   WHERE user_id = '+60123456789';"
```

---

## 📊 导出数据

### 导出今日搜索到 CSV
```bash
sqlite3 -header -csv doctor_review.db \
  "SELECT user_id, doctor_name, created_at, response_time_ms
   FROM search_logs
   WHERE DATE(created_at) = DATE('now');" \
  > today_searches.csv
```

### 导出所有用户列表
```bash
sqlite3 -header -csv doctor_review.db \
  "SELECT phone_number, approved, requested_at, approved_at
   FROM user_whitelist;" \
  > user_list.csv
```

---

## 🎯 快捷脚本

### 创建快捷命令别名（添加到 ~/.zshrc 或 ~/.bashrc）

```bash
# 添加到你的 shell 配置文件
alias docbot-db="cd /Users/lucyy/Desktop/coding/project02-docreview && sqlite3 doctor_review.db"
alias docbot-pending="sqlite3 /Users/lucyy/Desktop/coding/project02-docreview/doctor_review.db 'SELECT * FROM user_whitelist WHERE approved = 0'"
alias docbot-today="sqlite3 /Users/lucyy/Desktop/coding/project02-docreview/doctor_review.db -header -column 'SELECT user_id, doctor_name, created_at FROM search_logs WHERE DATE(created_at) = DATE(\"now\")'"
```

然后你就可以直接运行：
```bash
docbot-pending    # 查看待审批
docbot-today      # 查看今日活动
docbot-db         # 进入数据库交互模式
```

---

## 🔐 安全提醒

- 数据库包含用户电话号码，请妥善保管
- 不要公开分享数据库文件
- 定期备份数据库：`cp doctor_review.db doctor_review_backup_$(date +%Y%m%d).db`

---

**需要更多自定义查询？** 告诉我你想看什么数据！
