-- Supabase数据库初始化脚本
-- 在Supabase SQL Editor中执行

-- 创建hot_search_snapshots表
CREATE TABLE IF NOT EXISTS hot_search_snapshots (
    id BIGSERIAL PRIMARY KEY,
    platform VARCHAR(50) NOT NULL,
    rank INTEGER NOT NULL,
    title TEXT NOT NULL,
    hot_value BIGINT,
    url TEXT,
    description TEXT,
    crawled_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    published_at TIMESTAMP WITH TIME ZONE,
    author VARCHAR(255),
    view_count BIGINT,
    comment_count INTEGER,
    like_count INTEGER,
    share_count INTEGER,
    category VARCHAR(100),
    labels TEXT[],
    platform_specific JSONB,
    raw_data JSONB NOT NULL
);

-- 创建索引
CREATE INDEX IF NOT EXISTS idx_snapshots_platform ON hot_search_snapshots(platform);
CREATE INDEX IF NOT EXISTS idx_snapshots_crawled ON hot_search_snapshots(crawled_at);
-- 创建唯一约束（防止重复数据）
CREATE UNIQUE INDEX IF NOT EXISTS idx_unique_snapshot ON hot_search_snapshots(platform, title, crawled_at);

-- 创建hot_topics表
CREATE TABLE IF NOT EXISTS hot_topics (
    id BIGSERIAL PRIMARY KEY,
    platform VARCHAR(50) NOT NULL,
    title TEXT NOT NULL,
    topic_hash VARCHAR(64) NOT NULL UNIQUE,
    first_seen_at TIMESTAMP WITH TIME ZONE,
    last_seen_at TIMESTAMP WITH TIME ZONE,
    appearance_count INTEGER DEFAULT 1,
    max_rank INTEGER,
    max_hot_value BIGINT,
    latest_description TEXT,
    latest_url TEXT,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

-- 创建索引
CREATE INDEX IF NOT EXISTS idx_topics_platform ON hot_topics(platform);
CREATE INDEX IF NOT EXISTS idx_topics_last_seen ON hot_topics(last_seen_at);

-- 启用RLS（行级安全）
ALTER TABLE hot_search_snapshots ENABLE ROW LEVEL SECURITY;
ALTER TABLE hot_topics ENABLE ROW LEVEL SECURITY;

-- 创建访问策略（允许匿名读取和插入）
CREATE POLICY "Allow anonymous read" ON hot_search_snapshots
    FOR SELECT USING (true);

CREATE POLICY "Allow anonymous insert" ON hot_search_snapshots
    FOR INSERT WITH CHECK (true);

CREATE POLICY "Allow anonymous read" ON hot_topics
    FOR SELECT USING (true);

CREATE POLICY "Allow anonymous insert" ON hot_topics
    FOR INSERT WITH CHECK (true);

CREATE POLICY "Allow anonymous update" ON hot_topics
    FOR UPDATE USING (true);
