# Admin Data Guide - What User Data You Can See

## 📊 Available Data Overview

Your database contains **5 main tables** with user and usage data:

---

## 1. **User Whitelist** (Approval System)
**Table**: `user_whitelist`

### What you can see:
- Phone number (WhatsApp number)
- Approval status (pending/approved)
- Request timestamp
- Approval timestamp
- Admin notes

### View pending approvals:
```bash
sqlite3 doctor_review.db "SELECT * FROM user_whitelist WHERE approved = 0;"
```

### View all approved users:
```bash
sqlite3 doctor_review.db "SELECT * FROM user_whitelist WHERE approved = 1;"
```

---

## 2. **User Sessions** (Quota & Usage)
**Table**: `user_sessions`

### What you can see:
- `user_id` - User identifier (usually phone number)
- `total_searches` - Lifetime search count
- `today_usage` - Today's search count
- `daily_quota` - Daily limit (default: 50)
- `first_seen_at` - First time using bot
- `last_active_at` - Last activity time
- `role` - User role (user/admin)

### View active users:
```bash
sqlite3 doctor_review.db -header -column \
  "SELECT user_id, total_searches, today_usage, last_active_at
   FROM user_sessions
   ORDER BY last_active_at DESC
   LIMIT 10;"
```

### View power users (most searches):
```bash
sqlite3 doctor_review.db -header -column \
  "SELECT user_id, total_searches, today_usage
   FROM user_sessions
   ORDER BY total_searches DESC
   LIMIT 10;"
```

**Current Stats**:
- Total users: 13
- Active today: Check with query above

---

## 3. **Search Logs** (Search Activity)
**Table**: `search_logs`

### What you can see:
- `user_id` - Who searched
- `doctor_name` - What they searched
- `cache_hit` - Was it cached? (1=yes, 0=no)
- `response_time_ms` - How fast
- `results_count` - Number of reviews found
- `api_calls_count` - API calls made
- `estimated_cost_usd` - Estimated cost
- `created_at` - When

### View recent searches:
```bash
sqlite3 doctor_review.db -header -column \
  "SELECT user_id, doctor_name, cache_hit, response_time_ms, created_at
   FROM search_logs
   ORDER BY created_at DESC
   LIMIT 10;"
```

### View popular doctors:
```bash
sqlite3 doctor_review.db -header -column \
  "SELECT doctor_name, COUNT(*) as searches
   FROM search_logs
   GROUP BY doctor_name
   ORDER BY searches DESC
   LIMIT 10;"
```

### Daily statistics:
```bash
sqlite3 doctor_review.db -header -column \
  "SELECT
     COUNT(*) as total_searches,
     SUM(cache_hit) as cache_hits,
     ROUND(AVG(response_time_ms)) as avg_response_ms,
     SUM(estimated_cost_usd) as total_cost
   FROM search_logs
   WHERE DATE(created_at) = DATE('now');"
```

**Current Stats**:
- Total searches: 3
- Pending approvals: 1

---

## 4. **Doctor Reviews** (Cached Data)
**Table**: `doctor_reviews`

### What you can see:
- `doctor_name` - Doctor's name
- `source` - Where review came from (Facebook, Google Maps, etc.)
- `snippet` - Review text
- `sentiment` - positive/negative/neutral
- `rating` - Star rating
- `url` - Source URL
- `author_name` - Reviewer name
- `valid_until` - Cache expiry date

### View cached reviews for a doctor:
```bash
sqlite3 doctor_review.db -header -column \
  "SELECT doctor_name, source, snippet, sentiment
   FROM doctor_reviews
   WHERE doctor_name LIKE '%李%'
   LIMIT 5;"
```

### View cache statistics:
```bash
sqlite3 doctor_review.db -header -column \
  "SELECT
     COUNT(*) as total_cached,
     COUNT(DISTINCT doctor_id) as unique_doctors,
     SUM(CASE WHEN valid_until > datetime('now') THEN 1 ELSE 0 END) as still_valid
   FROM doctor_reviews;"
```

---

## 5. **Doctors** (Doctor Profiles)
**Table**: `doctors`

### What you can see:
- Doctor basic info (name, specialty, hospital, location)
- Review statistics (total, positive, negative)
- External IDs (Google, Facebook)

### View doctor profiles:
```bash
sqlite3 doctor_review.db -header -column \
  "SELECT name, total_reviews, positive_reviews, negative_reviews
   FROM doctors
   ORDER BY total_reviews DESC;"
```

---

## 🔐 Privacy & Security

### What you CAN see:
✅ Phone numbers (WhatsApp IDs) - needed for bot communication
✅ Search queries (doctor names)
✅ Usage patterns (when, how often)
✅ Cached review content (public data)

### What you CANNOT see:
❌ WhatsApp message content (except feedback messages)
❌ User personal info (beyond phone number)
❌ Private conversations

### Data Retention:
- **User sessions**: Kept permanently (unless manually deleted)
- **Search logs**: Kept permanently (for analytics)
- **Cached reviews**: 7 days TTL (auto-expire)
- **User whitelist**: Kept permanently

---

## 📱 Quick Commands You'll Use Most

### 1. Check pending approvals:
```bash
sqlite3 doctor_review.db -header -column \
  "SELECT phone_number, requested_at FROM user_whitelist WHERE approved = 0;"
```

### 2. View today's activity:
```bash
sqlite3 doctor_review.db -header -column \
  "SELECT user_id, doctor_name, created_at
   FROM search_logs
   WHERE DATE(created_at) = DATE('now');"
```

### 3. Check user quota usage:
```bash
sqlite3 doctor_review.db -header -column \
  "SELECT user_id, today_usage, daily_quota
   FROM user_sessions
   ORDER BY today_usage DESC;"
```

### 4. View feedback messages:
Check your WhatsApp - feedback is sent directly to your admin number!

---

## 📊 Via WhatsApp (Admin Commands)

You can also manage users directly via WhatsApp:

```
pending          - View users waiting for approval
approve +60xxx   - Approve a user
reject +60xxx    - Reject a user
```

Users can send you feedback:
```
Feedback <message>  - Forwarded to you instantly
```

---

## 🛠️ Advanced Queries

### Export to CSV:
```bash
sqlite3 -header -csv doctor_review.db \
  "SELECT * FROM search_logs WHERE DATE(created_at) = DATE('now');" \
  > today_searches.csv
```

### Monthly cost report:
```bash
sqlite3 doctor_review.db -header -column \
  "SELECT
     strftime('%Y-%m', created_at) as month,
     COUNT(*) as searches,
     SUM(api_calls_count) as api_calls,
     SUM(estimated_cost_usd) as total_cost
   FROM search_logs
   GROUP BY month
   ORDER BY month DESC;"
```

---

## 🔍 Database Location

```
/Users/lucyy/Desktop/coding/project02-docreview/doctor_review.db
```

Access via:
```bash
sqlite3 /Users/lucyy/Desktop/coding/project02-docreview/doctor_review.db
```

---

**Need more custom queries?** Let me know what data you want to see!
