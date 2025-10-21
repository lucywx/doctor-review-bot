-- Update admin user quota to 500/month
-- Run this on Railway database

UPDATE user_sessions
SET daily_quota = 500, role = 'admin'
WHERE user_id = '+60173745939';

-- Verify the update
SELECT user_id, role, daily_quota, today_usage
FROM user_sessions
WHERE user_id = '+60173745939';
