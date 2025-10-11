-- User whitelist table for approval system (PostgreSQL)
CREATE TABLE IF NOT EXISTS user_whitelist (
    phone_number VARCHAR(20) PRIMARY KEY,
    approved SMALLINT DEFAULT 0,  -- 0 = pending, 1 = approved
    requested_at TIMESTAMP DEFAULT NOW(),
    approved_at TIMESTAMP,
    notes TEXT
);

-- Index for quick approval lookups
CREATE INDEX IF NOT EXISTS idx_user_whitelist_approved ON user_whitelist(approved);
