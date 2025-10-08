-- Doctor Review Aggregation Bot - SQLite Schema
-- Created: 2025-10-08

-- ===========================================
-- 1. Main Tables
-- ===========================================

-- Doctors Table (Master data)
CREATE TABLE IF NOT EXISTS doctors (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    doctor_id TEXT UNIQUE NOT NULL,
    name TEXT NOT NULL,
    specialty TEXT,
    hospital_name TEXT,
    location TEXT,

    -- Aggregated statistics
    total_reviews INTEGER DEFAULT 0,
    positive_reviews INTEGER DEFAULT 0,
    negative_reviews INTEGER DEFAULT 0,
    neutral_reviews INTEGER DEFAULT 0,
    average_rating REAL,

    -- External IDs
    google_place_id TEXT,
    facebook_page_id TEXT,
    official_website TEXT,

    -- Metadata
    metadata TEXT,  -- JSON as TEXT in SQLite
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Doctor Reviews Cache Table
CREATE TABLE IF NOT EXISTS doctor_reviews (
    id INTEGER PRIMARY KEY AUTOINCREMENT,

    -- Doctor identification
    doctor_id TEXT NOT NULL,
    doctor_name TEXT NOT NULL,
    doctor_specialty TEXT,
    hospital_name TEXT,
    location TEXT,

    -- Data source
    source TEXT NOT NULL,  -- google_maps, facebook, hospital_website
    url TEXT NOT NULL,

    -- Review content
    snippet TEXT NOT NULL,
    sentiment TEXT,  -- positive, negative, neutral
    rating REAL,
    review_date DATE,
    author_name TEXT,

    -- Cache management
    hash TEXT UNIQUE NOT NULL,
    fetched_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    valid_until TIMESTAMP NOT NULL,

    -- Display policy
    display_policy TEXT DEFAULT 'normal',  -- normal, featured, hidden

    -- Extended metadata
    metadata TEXT,  -- JSON as TEXT
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,

    -- Foreign key
    FOREIGN KEY (doctor_id) REFERENCES doctors(doctor_id) ON DELETE CASCADE
);

-- Search Logs Table
CREATE TABLE IF NOT EXISTS search_logs (
    id INTEGER PRIMARY KEY AUTOINCREMENT,

    -- User information
    user_id TEXT,
    session_id TEXT,

    -- Search information
    doctor_name TEXT NOT NULL,
    doctor_id TEXT,
    location TEXT,

    -- Performance metrics
    cache_hit INTEGER DEFAULT 0,  -- Boolean as INTEGER
    response_time_ms INTEGER,
    sources_used TEXT,  -- JSON array as TEXT
    results_count INTEGER,

    -- Cost tracking
    api_calls_count INTEGER DEFAULT 0,
    estimated_cost_usd REAL,

    -- Error information
    error_message TEXT,

    -- Timestamp
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- User Sessions Table
CREATE TABLE IF NOT EXISTS user_sessions (
    id INTEGER PRIMARY KEY AUTOINCREMENT,

    -- User identification
    user_id TEXT UNIQUE NOT NULL,
    phone_number_hash TEXT,

    -- Access control
    is_active INTEGER DEFAULT 1,  -- Boolean as INTEGER
    role TEXT DEFAULT 'user',

    -- Quota management
    daily_quota INTEGER DEFAULT 50,
    today_usage INTEGER DEFAULT 0,
    total_searches INTEGER DEFAULT 0,

    -- Timestamps
    first_seen_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    last_active_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    quota_reset_at DATE DEFAULT CURRENT_DATE,

    -- Metadata
    metadata TEXT  -- JSON as TEXT
);

-- ===========================================
-- 2. Indexes for Performance
-- ===========================================

CREATE INDEX IF NOT EXISTS idx_doctor_id_main ON doctors(doctor_id);
CREATE INDEX IF NOT EXISTS idx_doctor_name ON doctors(name);
CREATE INDEX IF NOT EXISTS idx_hospital ON doctors(hospital_name);

CREATE INDEX IF NOT EXISTS idx_dr_doctor_id ON doctor_reviews(doctor_id);
CREATE INDEX IF NOT EXISTS idx_dr_doctor_name ON doctor_reviews(doctor_name);
CREATE INDEX IF NOT EXISTS idx_dr_valid_until ON doctor_reviews(valid_until);
CREATE INDEX IF NOT EXISTS idx_dr_source ON doctor_reviews(source);
CREATE INDEX IF NOT EXISTS idx_dr_sentiment ON doctor_reviews(sentiment);
CREATE INDEX IF NOT EXISTS idx_dr_hash ON doctor_reviews(hash);

CREATE INDEX IF NOT EXISTS idx_sl_user_id ON search_logs(user_id);
CREATE INDEX IF NOT EXISTS idx_sl_doctor_name ON search_logs(doctor_name);
CREATE INDEX IF NOT EXISTS idx_sl_created_at ON search_logs(created_at);

CREATE INDEX IF NOT EXISTS idx_us_user_id ON user_sessions(user_id);
CREATE INDEX IF NOT EXISTS idx_us_is_active ON user_sessions(is_active);

-- ===========================================
-- 3. Test Data
-- ===========================================

INSERT OR IGNORE INTO doctors (doctor_id, name, specialty, hospital_name, location)
VALUES ('test_doctor_001', '测试医生', '心内科', '测试医院', '北京');
