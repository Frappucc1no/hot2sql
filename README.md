# hot2sql

多平台热榜数据自动采集与入库系统

## 项目简介

hot2sql 是一个自动化采集多个中文互联网平台热榜数据并入库的系统，支持以下9个平台：

- 百度热搜
- 微博热搜
- 抖音热榜
- B站热门
- 知乎热榜
- 头条热搜
- 贴吧话题榜
- 夸克热榜
- 小红书热搜

## 项目结构

```
hot2sql/
├── src/
│   ├── __init__.py
│   ├── config.py          # 配置文件
│   ├── database.py        # 数据库操作模块
│   └── crawlers/          # 爬虫模块
│       ├── __init__.py
│       ├── baidu.py
│       ├── weibo.py
│       ├── douyin.py
│       ├── bilibili.py
│       ├── zhihu.py
│       ├── toutiao.py
│       ├── tieba.py
│       ├── quark.py
│       └── xiaohongshu.py
├── scripts/
│   └── init_db.sql        # 数据库初始化脚本
├── docs/
│   └── supabase_setup.md  # Supabase接入指引
├── .github/
│   └── workflows/
│       └── crawl.yml      # GitHub Actions工作流
├── main.py                # 主入口
├── requirements.txt       # 依赖列表
├── .env.example           # 环境变量示例
└── README.md              # 项目说明
```

## 快速开始

### 1. 克隆项目
```bash
git clone https://github.com/yourusername/hot2sql.git
cd hot2sql
```

### 2. 安装依赖
```bash
pip install -r requirements.txt
```

### 3. 配置Supabase

#### 3.1 创建Supabase项目
1. 访问 https://supabase.com 并注册
2. 创建新项目
3. 获取项目URL和API Key

#### 3.2 配置环境变量
```bash
cp .env.example .env
# 编辑.env文件，填入你的SUPABASE_URL和SUPABASE_KEY
```

#### 3.3 初始化数据库
在Supabase SQL Editor中执行 `scripts/init_db.sql`

详细步骤请参考 [docs/supabase_setup.md](docs/supabase_setup.md)

### 4. 本地测试

测试单个平台：
```bash
python main.py baidu
```

测试所有平台：
```bash
python main.py
```

### 5. 配置GitHub Actions

1. 推送代码到GitHub
2. 在仓库Settings → Secrets中添加：
   - `SUPABASE_URL`
   - `SUPABASE_KEY`
3. GitHub Actions会自动每30分钟运行一次

## 数据库设计

### hot_search_snapshots 表
存储每次爬取的原始数据

| 字段 | 类型 | 说明 |
|------|------|------|
| platform | varchar | 平台名称 |
| rank | int | 排名 |
| title | text | 标题 |
| hot_value | bigint | 热度值 |
| url | text | 链接 |
| description | text | 描述 |
| crawled_at | timestamptz | 爬取时间 |
| raw_data | jsonb | 原始API数据 |

### hot_topics 表
聚合同一话题，记录出现次数和时间范围

| 字段 | 类型 | 说明 |
|------|------|------|
| platform | varchar | 平台名称 |
| title | text | 标题 |
| topic_hash | varchar | 话题唯一标识 |
| first_seen_at | timestamptz | 首次出现时间 |
| last_seen_at | timestamptz | 最后出现时间 |
| appearance_count | int | 出现次数 |

## 定时任务

GitHub Actions配置每30分钟自动爬取一次：

```yaml
schedule:
  - cron: '*/30 * * * *'
```

## 后续开发

- [ ] LLM向量化分析
- [ ] 实体抽取
- [ ] 情感分析
- [ ] 热度趋势预测
- [ ] Web可视化界面

## License

MIT
