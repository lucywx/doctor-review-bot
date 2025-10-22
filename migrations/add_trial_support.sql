-- Add trial support to user_sessions table
-- Migration: Add trial fields for new user trial system

-- Add trial-related columns to user_sessions table
ALTER TABLE user_sessions 
ADD COLUMN IF NOT EXISTS trial_start_date DATE,
ADD COLUMN IF NOT EXISTS trial_end_date DATE;

-- Add index for trial queries
CREATE INDEX IF NOT EXISTS idx_us_trial_end ON user_sessions(trial_end_date);
CREATE INDEX IF NOT EXISTS idx_us_role ON user_sessions(role);

-- Update existing users to have 'user' role if NULL
UPDATE user_sessions 
SET role = 'user' 
WHERE role IS NULL;

-- Add comments
COMMENT ON COLUMN user_sessions.trial_start_date IS 'Trial period start date';
COMMENT ON COLUMN user_sessions.trial_end_date IS 'Trial period end date';
COMMENT ON COLUMN user_sessions.role IS 'User role: trial_user, user, admin';
