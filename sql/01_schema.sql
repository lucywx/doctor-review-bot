-- Doctor Review Aggregation Bot - Database Schema
-- Created: 2025-10-08

-- ===========================================
-- 1. Main Tables
-- ===========================================

-- Doctors Table (Master data)
CREATE TABLE IF NOT EXISTS doctors (
    id SERIAL PRIMARY KEY,
    doctor_id VARCHAR(255) UNIQUE NOT NULL,
    name VARCHAR(255) NOT NULL,
    specialty VARCHAR(100),
    hospital_name VARCHAR(255),
    location VARCHAR(255),

    -- Aggregated statistics
    total_reviews INTEGER DEFAULT 0,
    positive_reviews INTEGER DEFAULT 0,
    negative_reviews INTEGER DEFAULT 0,
    neutral_reviews INTEGER DEFAULT 0,
    average_rating DECIMAL(2,1),

    -- External IDs
    google_place_id VARCHAR(255),
    facebook_page_id VARCHAR(255),
    official_website TEXT,

    -- Metadata
    metadata JSONB,
    created_at TIMESTAMP DEFAULT NOW(),
    updated_at TIMESTAMP DEFAULT NOW()
);

-- Doctor Reviews Cache Table (按照你的要求设计)
CREATE TABLE IF NOT EXISTS doctor_reviews (
    id SERIAL PRIMARY KEY,

    -- Doctor identification
    doctor_id VARCHAR(255) NOT NULL,
    doctor_name VARCHAR(255) NOT NULL,
    doctor_specialty VARCHAR(100),
    hospital_name VARCHAR(255),
    location VARCHAR(255),

    -- Data source
    source VARCHAR(50) NOT NULL,  -- google_maps, facebook, hospital_website
    url TEXT NOT NULL,

    -- Review content
    snippet TEXT NOT NULL,
    sentiment VARCHAR(20),  -- positive, negative, neutral
    rating DECIMAL(2,1),
    review_date DATE,
    author_name VARCHAR(255),

    -- Cache management
    hash VARCHAR(64) UNIQUE NOT NULL,
    fetched_at TIMESTAMP NOT NULL DEFAULT NOW(),
    valid_until TIMESTAMP NOT NULL,

    -- Display policy
    display_policy VARCHAR(50) DEFAULT 'normal',  -- normal, featured, hidden

    -- Extended metadata
    metadata JSONB,
    created_at TIMESTAMP DEFAULT NOW(),
    updated_at TIMESTAMP DEFAULT NOW(),

    -- Foreign key
    CONSTRAINT fk_doctor FOREIGN KEY (doctor_id) REFERENCES doctors(doctor_id) ON DELETE CASCADE
);

-- Search Logs Table
CREATE TABLE IF NOT EXISTS search_logs (
    id SERIAL PRIMARY KEY,

    -- User information
    user_id VARCHAR(100),
    session_id VARCHAR(100),

    -- Search information
    doctor_name VARCHAR(255) NOT NULL,
    doctor_id VARCHAR(255),
    location VARCHAR(255),

    -- Performance metrics
    cache_hit BOOLEAN DEFAULT FALSE,
    response_time_ms INTEGER,
    sources_used TEXT[],
    results_count INTEGER,

    -- Cost tracking
    api_calls_count INTEGER DEFAULT 0,
    estimated_cost_usd DECIMAL(10,4),

    -- Error information
    error_message TEXT,

    -- Timestamp
    created_at TIMESTAMP DEFAULT NOW()
);

-- User Sessions Table
CREATE TABLE IF NOT EXISTS user_sessions (
    id SERIAL PRIMARY KEY,

    -- User identification
    user_id VARCHAR(100) UNIQUE NOT NULL,
    phone_number_hash VARCHAR(64),

    -- Access control
    is_active BOOLEAN DEFAULT TRUE,
    role VARCHAR(20) DEFAULT 'user',

    -- Quota management
    daily_quota INTEGER DEFAULT 10,
    today_usage INTEGER DEFAULT 0,
    total_searches INTEGER DEFAULT 0,

    -- Timestamps
    first_seen_at TIMESTAMP DEFAULT NOW(),
    last_active_at TIMESTAMP DEFAULT NOW(),
    quota_reset_at DATE DEFAULT CURRENT_DATE,

    -- Metadata
    metadata JSONB
);

-- ===========================================
-- 2. Indexes for Performance
-- ===========================================

-- Doctors table indexes
CREATE INDEX IF NOT EXISTS idx_doctor_id_main ON doctors(doctor_id);
CREATE INDEX IF NOT EXISTS idx_doctor_name ON doctors(name);
CREATE INDEX IF NOT EXISTS idx_hospital ON doctors(hospital_name);
CREATE INDEX IF NOT EXISTS idx_location ON doctors(location);

-- Doctor Reviews indexes
CREATE INDEX IF NOT EXISTS idx_dr_doctor_id ON doctor_reviews(doctor_id);
CREATE INDEX IF NOT EXISTS idx_dr_doctor_name ON doctor_reviews(doctor_name);
CREATE INDEX IF NOT EXISTS idx_dr_valid_until ON doctor_reviews(valid_until);
CREATE INDEX IF NOT EXISTS idx_dr_source ON doctor_reviews(source);
CREATE INDEX IF NOT EXISTS idx_dr_sentiment ON doctor_reviews(sentiment);
CREATE INDEX IF NOT EXISTS idx_dr_hash ON doctor_reviews(hash);
CREATE INDEX IF NOT EXISTS idx_dr_display_policy ON doctor_reviews(display_policy);

-- Composite index for cache queries
CREATE INDEX IF NOT EXISTS idx_dr_doctor_valid ON doctor_reviews(doctor_id, valid_until);
CREATE INDEX IF NOT EXISTS idx_dr_sentiment_display ON doctor_reviews(sentiment, display_policy);

-- Search Logs indexes
CREATE INDEX IF NOT EXISTS idx_sl_user_id ON search_logs(user_id);
CREATE INDEX IF NOT EXISTS idx_sl_doctor_name ON search_logs(doctor_name);
CREATE INDEX IF NOT EXISTS idx_sl_created_at ON search_logs(created_at);
CREATE INDEX IF NOT EXISTS idx_sl_cache_hit ON search_logs(cache_hit);

-- User Sessions indexes
CREATE INDEX IF NOT EXISTS idx_us_user_id ON user_sessions(user_id);
CREATE INDEX IF NOT EXISTS idx_us_is_active ON user_sessions(is_active);
CREATE INDEX IF NOT EXISTS idx_us_quota_reset ON user_sessions(quota_reset_at);

-- JSONB indexes (for metadata queries)
CREATE INDEX IF NOT EXISTS idx_doctors_metadata ON doctors USING GIN (metadata);
CREATE INDEX IF NOT EXISTS idx_reviews_metadata ON doctor_reviews USING GIN (metadata);

-- ===========================================
-- 3. Functions and Triggers
-- ===========================================

-- Function to update updated_at timestamp
CREATE OR REPLACE FUNCTION update_updated_at_column()
RETURNS TRIGGER AS $$
BEGIN
    NEW.updated_at = NOW();
    RETURN NEW;
END;
$$ LANGUAGE plpgsql;

-- Triggers for updated_at (drop if exists, then create)
DROP TRIGGER IF EXISTS update_doctors_updated_at ON doctors;
CREATE TRIGGER update_doctors_updated_at
    BEFORE UPDATE ON doctors
    FOR EACH ROW
    EXECUTE FUNCTION update_updated_at_column();

DROP TRIGGER IF EXISTS update_doctor_reviews_updated_at ON doctor_reviews;
CREATE TRIGGER update_doctor_reviews_updated_at
    BEFORE UPDATE ON doctor_reviews
    FOR EACH ROW
    EXECUTE FUNCTION update_updated_at_column();

-- Function to cleanup expired reviews
CREATE OR REPLACE FUNCTION cleanup_expired_reviews()
RETURNS void AS $$
BEGIN
    DELETE FROM doctor_reviews
    WHERE valid_until < NOW() - INTERVAL '30 days';
END;
$$ LANGUAGE plpgsql;

-- Function to reset daily user quotas
CREATE OR REPLACE FUNCTION reset_daily_quotas()
RETURNS void AS $$
BEGIN
    UPDATE user_sessions
    SET today_usage = 0,
        quota_reset_at = CURRENT_DATE
    WHERE quota_reset_at < CURRENT_DATE;
END;
$$ LANGUAGE plpgsql;

-- ===========================================
-- 4. Initial Data (Optional)
-- ===========================================

-- Insert test doctor
INSERT INTO doctors (doctor_id, name, specialty, hospital_name, location)
VALUES
    ('test_doctor_001', '测试医生', '心内科', '测试医院', '北京')
ON CONFLICT (doctor_id) DO NOTHING;

-- ===========================================
-- 5. Comments
-- ===========================================

COMMENT ON TABLE doctors IS '医生主表，存储医生基本信息';
COMMENT ON TABLE doctor_reviews IS '医生评价缓存表，存储多源聚合的评价数据';
COMMENT ON TABLE search_logs IS '搜索日志表，用于分析和成本追踪';
COMMENT ON TABLE user_sessions IS '用户会话表，管理访问控制和配额';

COMMENT ON COLUMN doctor_reviews.hash IS '内容去重 hash (SHA256)';
COMMENT ON COLUMN doctor_reviews.valid_until IS '缓存有效期，超过此时间需重新抓取';
COMMENT ON COLUMN doctor_reviews.display_policy IS 'normal=正常显示, featured=优先展示, hidden=隐藏';
