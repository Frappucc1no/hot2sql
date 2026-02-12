-- Supabase数据库初始化脚本 v2.0.0
-- 在Supabase SQL Editor中执行
-- 更新时间: 2026-02-12

-- ============================================
-- 第一步：删除旧表（如果存在）
-- ============================================
DROP TABLE IF EXISTS hot_search_snapshots CASCADE;
DROP TABLE IF EXISTS hot_topics CASCADE;
DROP TABLE IF EXISTS crawl_sessions CASCADE;

-- ============================================
-- 第二步：创建 crawl_sessions 表（爬取任务表）
-- ============================================
CREATE TABLE crawl_sessions (
    id BIGSERIAL PRIMARY KEY,
    session_id VARCHAR(64) NOT NULL UNIQUE,
    platform VARCHAR(50) NOT NULL,
    crawler_version VARCHAR(20) NOT NULL DEFAULT '2.0.0',
    started_at TIMESTAMP WITH TIME ZONE NOT NULL,
    finished_at TIMESTAMP WITH TIME ZONE,
    status VARCHAR(20) NOT NULL DEFAULT 'running',
    items_count INTEGER DEFAULT 0,
    error_message TEXT,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

CREATE INDEX idx_sessions_platform ON crawl_sessions(platform);
CREATE INDEX idx_sessions_started ON crawl_sessions(started_at);
CREATE INDEX idx_sessions_status ON crawl_sessions(status);

COMMENT ON TABLE crawl_sessions IS '爬取任务表：追溯每次爬取的元信息';
COMMENT ON COLUMN crawl_sessions.session_id IS '唯一批次ID，格式：{platform}_{timestamp}_{uuid8}';
COMMENT ON COLUMN crawl_sessions.crawler_version IS '爬虫版本号';
COMMENT ON COLUMN crawl_sessions.status IS 'running/success/failed';

-- ============================================
-- 第三步：创建 hot_search_snapshots 表（快照表）
-- ============================================
CREATE TABLE hot_search_snapshots (
    -- 主键
    id BIGSERIAL PRIMARY KEY,
    
    -- 关联字段
    session_id VARCHAR(64) NOT NULL,
    platform VARCHAR(50) NOT NULL,
    rank INTEGER NOT NULL,
    
    -- 标题字段（统一命名 + 来源追踪）
    title TEXT NOT NULL,
    title_source VARCHAR(50) NOT NULL,
    
    -- 热度字段
    hot_value BIGINT,
    hot_value_text TEXT,
    hot_value_source VARCHAR(50),
    
    -- 内容字段
    description TEXT,
    description_source VARCHAR(50),
    url TEXT,
    
    -- 时间字段
    published_at TIMESTAMP WITH TIME ZONE,
    published_at_source VARCHAR(50),
    
    -- 作者字段
    author VARCHAR(255),
    author_id VARCHAR(255),
    author_source VARCHAR(50),
    
    -- 互动数据
    view_count BIGINT,
    like_count BIGINT,
    comment_count BIGINT,
    share_count BIGINT,
    favorite_count BIGINT,
    interaction_source VARCHAR(50),
    
    -- 分类标签
    category VARCHAR(100),
    tags TEXT[],
    
    -- 数据质量标记
    has_hot_value BOOLEAN NOT NULL DEFAULT FALSE,
    has_description BOOLEAN NOT NULL DEFAULT FALSE,
    has_published_at BOOLEAN NOT NULL DEFAULT FALSE,
    has_author BOOLEAN NOT NULL DEFAULT FALSE,
    has_interaction BOOLEAN NOT NULL DEFAULT FALSE,
    
    -- 平台特有字段（保留原始命名）
    platform_fields JSONB DEFAULT '{}',
    
    -- 精简后的原始数据
    raw_data JSONB NOT NULL,
    
    -- 元数据
    crawled_at TIMESTAMP WITH TIME ZONE NOT NULL,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

-- 索引
CREATE INDEX idx_snapshots_session ON hot_search_snapshots(session_id);
CREATE INDEX idx_snapshots_platform_time ON hot_search_snapshots(platform, crawled_at);
CREATE INDEX idx_snapshots_platform_rank ON hot_search_snapshots(platform, rank);
CREATE INDEX idx_snapshots_needs_enrichment ON hot_search_snapshots(has_description) WHERE has_description = FALSE;

-- 唯一约束
CREATE UNIQUE INDEX idx_unique_snapshot ON hot_search_snapshots(platform, title, session_id);

-- 外键约束
ALTER TABLE hot_search_snapshots 
ADD CONSTRAINT fk_snapshots_session 
FOREIGN KEY (session_id) REFERENCES crawl_sessions(session_id) ON DELETE CASCADE;

COMMENT ON TABLE hot_search_snapshots IS '快照表：存储每次爬取的完整快照，是一道数据的核心表';
COMMENT ON COLUMN hot_search_snapshots.title_source IS '原始标题字段名（word/desc/title等）';
COMMENT ON COLUMN hot_search_snapshots.hot_value_text IS '热度原始文本（如"907.3w"）';
COMMENT ON COLUMN hot_search_snapshots.platform_fields IS '平台特有字段，保留原始命名';

-- ============================================
-- 第四步：创建 hot_topics 表（话题表）
-- ============================================
CREATE TABLE hot_topics (
    id BIGSERIAL PRIMARY KEY,
    topic_hash VARCHAR(64) NOT NULL UNIQUE,
    event_hash VARCHAR(64),
    platform VARCHAR(50) NOT NULL,
    title TEXT NOT NULL,
    title_normalized TEXT,
    
    -- 出现统计
    first_seen_at TIMESTAMP WITH TIME ZONE NOT NULL,
    last_seen_at TIMESTAMP WITH TIME ZONE NOT NULL,
    appearance_count INTEGER NOT NULL DEFAULT 1,
    total_snapshots INTEGER NOT NULL DEFAULT 1,
    
    -- 排名统计
    max_rank INTEGER NOT NULL,
    min_rank INTEGER NOT NULL,
    rank_history JSONB DEFAULT '[]',
    
    -- 热度统计
    max_hot_value BIGINT,
    avg_hot_value BIGINT,
    hot_history JSONB DEFAULT '[]',
    
    -- 最新信息
    latest_description TEXT,
    latest_url TEXT,
    latest_snapshot_id BIGINT,
    
    -- 合并标记（二道数据用）
    is_merged BOOLEAN NOT NULL DEFAULT FALSE,
    merged_to_event_id BIGINT,
    
    -- 元数据
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

-- 索引
CREATE INDEX idx_topics_platform ON hot_topics(platform);
CREATE INDEX idx_topics_last_seen ON hot_topics(last_seen_at);
CREATE INDEX idx_topics_event_hash ON hot_topics(event_hash) WHERE event_hash IS NOT NULL;
CREATE INDEX idx_topics_not_merged ON hot_topics(is_merged) WHERE is_merged = FALSE;

COMMENT ON TABLE hot_topics IS '话题表：追踪话题的历史出现情况，支持趋势分析';
COMMENT ON COLUMN hot_topics.topic_hash IS '唯一标识（platform:title的MD5）';
COMMENT ON COLUMN hot_topics.event_hash IS '跨平台事件ID（二道数据填充）';
COMMENT ON COLUMN hot_topics.title_normalized IS '标准化标题（二道数据填充）';
COMMENT ON COLUMN hot_topics.is_merged IS '是否已合并到跨平台事件';

-- ============================================
-- 第五步：启用RLS（行级安全）
-- ============================================
ALTER TABLE crawl_sessions ENABLE ROW LEVEL SECURITY;
ALTER TABLE hot_search_snapshots ENABLE ROW LEVEL SECURITY;
ALTER TABLE hot_topics ENABLE ROW LEVEL SECURITY;

-- ============================================
-- 第六步：创建访问策略
-- ============================================

-- crawl_sessions 策略
CREATE POLICY "Allow anonymous read sessions" ON crawl_sessions
    FOR SELECT USING (true);

CREATE POLICY "Allow anonymous insert sessions" ON crawl_sessions
    FOR INSERT WITH CHECK (true);

CREATE POLICY "Allow anonymous update sessions" ON crawl_sessions
    FOR UPDATE USING (true);

-- hot_search_snapshots 策略
CREATE POLICY "Allow anonymous read snapshots" ON hot_search_snapshots
    FOR SELECT USING (true);

CREATE POLICY "Allow anonymous insert snapshots" ON hot_search_snapshots
    FOR INSERT WITH CHECK (true);

-- hot_topics 策略
CREATE POLICY "Allow anonymous read topics" ON hot_topics
    FOR SELECT USING (true);

CREATE POLICY "Allow anonymous insert topics" ON hot_topics
    FOR INSERT WITH CHECK (true);

CREATE POLICY "Allow anonymous update topics" ON hot_topics
    FOR UPDATE USING (true);

-- ============================================
-- 第七步：创建更新时间触发器
-- ============================================
CREATE OR REPLACE FUNCTION update_updated_at_column()
RETURNS TRIGGER AS $$
BEGIN
    NEW.updated_at = NOW();
    RETURN NEW;
END;
$$ language 'plpgsql';

CREATE TRIGGER update_hot_topics_updated_at 
    BEFORE UPDATE ON hot_topics 
    FOR EACH ROW 
    EXECUTE FUNCTION update_updated_at_column();

-- ============================================
-- 完成提示
-- ============================================
-- 执行完成后，请验证表结构：
-- SELECT table_name FROM information_schema.tables WHERE table_schema = 'public';
