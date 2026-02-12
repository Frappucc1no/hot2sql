# hot2sql

[![Python](https://img.shields.io/badge/Python-3.10+-blue.svg)](https://www.python.org/)
[![License](https://img.shields.io/badge/License-MIT-green.svg)](LICENSE)
[![GitHub Actions](https://img.shields.io/badge/GitHub%20Actions-Automated-brightgreen.svg)](https://github.com/features/actions)

多平台热搜数据自动采集系统，支持 9 大中文互联网平台，基于 Supabase 存储。

## ✨ 特性

- 🚀 **多平台支持** - 百度、微博、抖音、B站、知乎、头条、贴吧、夸克、小红书
- 🔄 **自动化采集** - GitHub Actions 定时运行，无需服务器
- 📊 **三表架构** - 爬取任务追溯、快照存储、话题追踪
- 🏷️ **质量标记** - 自动标记数据完整性，便于后续处理
- 📦 **开箱即用** - 一键部署到 Supabase

## 📋 支持平台

| 平台 | 标识 | 数据量 | 热度值 | 描述 | 作者 | 时间 |
|------|------|--------|--------|------|------|------|
| 百度热搜 | `baidu` | 50条 | ✅ | ✅ | ❌ | ❌ |
| 微博热搜 | `weibo` | 50条 | ✅ | ❌ | ❌ | ❌ |
| B站热门 | `bilibili` | 50条 | ❌ | ✅ | ✅ | ✅ |
| 抖音热榜 | `douyin` | 50条 | ✅ | ❌ | ❌ | ❌ |
| 知乎热榜 | `zhihu` | 30条 | ✅ | ✅ | ❌ | ✅ |
| 小红书热搜 | `xiaohongshu` | 20条 | ✅ | ❌ | ❌ | ❌ |
| 头条热搜 | `toutiao` | 50条 | ✅ | ❌ | ❌ | ❌ |
| 贴吧话题榜 | `tieba` | 30条 | ✅ | ✅ | ❌ | ✅ |
| 夸克热榜 | `quark` | 50条 | ❌ | ✅ | ✅ | ✅ |

## 🚀 快速开始

### 1. 克隆项目

```bash
git clone https://github.com/Frappucc1no/hot2sql.git
cd hot2sql
```

### 2. 安装依赖

```bash
pip install -r requirements.txt
```

### 3. 配置 Supabase

#### 创建项目
1. 访问 [Supabase](https://supabase.com) 注册账号
2. 创建新项目
3. 获取 Project URL 和 anon key

#### 配置环境变量

```bash
cp .env.example .env
```

编辑 `.env` 文件：

```env
SUPABASE_URL=https://your-project.supabase.co
SUPABASE_KEY=your-anon-key
```

#### 初始化数据库

在 Supabase SQL Editor 中执行：

```sql
-- 复制 scripts/init_db.sql 的内容执行
```

### 4. 本地测试

```bash
# 测试单个平台
python main.py baidu

# 测试所有平台
python main.py
```

### 5. 配置 GitHub Actions 自动采集

1. 推送代码到 GitHub
2. 进入仓库 **Settings → Secrets and variables → Actions**
3. 添加 Repository secrets：
   - `SUPABASE_URL`
   - `SUPABASE_KEY`
4. Actions 将自动每 30 分钟采集一次

## 📊 数据库架构

### crawl_sessions（爬取任务表）

追溯每次爬取的元信息，便于问题排查。

| 字段 | 类型 | 说明 |
|------|------|------|
| session_id | varchar | 唯一批次ID |
| platform | varchar | 平台标识 |
| crawler_version | varchar | 爬虫版本 |
| started_at | timestamptz | 开始时间 |
| finished_at | timestamptz | 结束时间 |
| status | varchar | 状态：running/success/failed |
| items_count | int | 抓取条数 |

### hot_search_snapshots（快照表）

存储每次爬取的完整快照，是一道数据的核心表。

| 字段 | 类型 | 说明 |
|------|------|------|
| session_id | varchar | 关联爬取批次 |
| platform | varchar | 平台标识 |
| rank | int | 排名 |
| title | text | 标题（统一命名） |
| title_source | varchar | 原始标题字段名 |
| hot_value | bigint | 热度值（已解析） |
| hot_value_text | text | 热度原始文本 |
| description | text | 描述 |
| author | varchar | 作者 |
| published_at | timestamptz | 发布时间 |
| has_hot_value | boolean | 是否有热度 |
| has_description | boolean | 是否有描述 |
| platform_fields | jsonb | 平台特有字段 |
| raw_data | jsonb | 精简后的原始数据 |

### hot_topics（话题表）

追踪话题的历史出现情况，支持趋势分析。

| 字段 | 类型 | 说明 |
|------|------|------|
| topic_hash | varchar | 唯一标识 |
| platform | varchar | 平台标识 |
| title | text | 标题 |
| first_seen_at | timestamptz | 首次出现 |
| last_seen_at | timestamptz | 最后出现 |
| appearance_count | int | 出现次数 |
| max_rank | int | 最高排名 |
| max_hot_value | bigint | 最高热度 |
| rank_history | jsonb | 排名历史 |

## 🔧 配置说明

### 爬取频率

编辑 `.github/workflows/main.yml`：

```yaml
schedule:
  - cron: '7,37 * * * *'  # 每小时的第7分和第37分
```

### 平台选择

在 GitHub Actions matrix 中启用/禁用平台：

```yaml
strategy:
  matrix:
    platform: [baidu, weibo, bilibili, douyin, zhihu, xiaohongshu, toutiao, tieba, quark]
```

## 📁 项目结构

```
hot2sql/
├── src/
│   ├── version.py           # 版本管理（单一来源）
│   ├── config.py            # 配置
│   ├── database.py          # 数据库操作
│   └── crawlers/            # 爬虫模块
│       ├── baidu.py
│       ├── weibo.py
│       └── ...
├── scripts/
│   └── init_db.sql          # 数据库初始化
├── .github/workflows/
│   └── main.yml             # GitHub Actions
├── ARCHITECTURE.md          # 架构文档
├── main.py                  # 主入口
└── requirements.txt
```

## 🔍 数据查询示例

```sql
-- 查询今日百度热搜 Top 10
SELECT rank, title, hot_value, description
FROM hot_search_snapshots
WHERE platform = 'baidu'
  AND crawled_at >= CURRENT_DATE
ORDER BY rank
LIMIT 10;

-- 查询最近7天出现次数最多的话题
SELECT platform, title, appearance_count, max_hot_value
FROM hot_topics
WHERE last_seen_at >= NOW() - INTERVAL '7 days'
ORDER BY appearance_count DESC
LIMIT 20;

-- 查询缺少描述的快照（需要LLM补充）
SELECT platform, title, crawled_at
FROM hot_search_snapshots
WHERE has_description = FALSE
ORDER BY crawled_at DESC;
```

## 🗺️ 路线图

- [ ] 二道数据：LLM 增强（分类、情感、摘要）
- [ ] 二道数据：跨平台事件聚合
- [ ] 二道数据：向量化和语义检索
- [ ] API 接口：RESTful API
- [ ] 可视化：Web Dashboard

## 🤝 贡献

欢迎提交 Issue 和 Pull Request！

1. Fork 本仓库
2. 创建特性分支 (`git checkout -b feature/AmazingFeature`)
3. 提交更改 (`git commit -m 'Add some AmazingFeature'`)
4. 推送到分支 (`git push origin feature/AmazingFeature`)
5. 创建 Pull Request

## 📄 许可证

本项目采用 MIT 许可证 - 详见 [LICENSE](LICENSE) 文件

## 🙏 致谢

- [Supabase](https://supabase.com) - 开源的 Firebase 替代方案
- 各平台提供的公开 API

---

⭐ 如果这个项目对你有帮助，请给一个 Star！
