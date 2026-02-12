# 热搜数据采集系统架构文档

> 版本: v2.0.0  
> 更新时间: 2026-02-12  
> 状态: 设计确认中

---

## 一、项目概述

### 1.1 项目定位

本项目是一个**多平台热搜词条采集与数据挖掘系统**，核心采集对象是各平台的"热搜词条"——通常是简短的短语或一句话，反映当下公众关注焦点。

### 1.2 数据分层架构

```
┌─────────────────────────────────────────────────────────────────┐
│                    一道数据（原始层）                             │
│  hot_search_snapshots / hot_topics / crawl_sessions            │
│  - 忠实录入爬虫原始响应                                          │
│  - 不补充、不推断、不清洗                                        │
│  - 完整保留原始数据                                              │
└─────────────────────────────────────────────────────────────────┘
                              │
                              ▼
┌─────────────────────────────────────────────────────────────────┐
│                    二道数据（清洗层）                             │
│  hot_events / event_timeline                                    │
│  - LLM 增强：分类、情感、关键词、实体、摘要                       │
│  - 联网搜索补充背景信息                                          │
│  - 向量化：embedding                                             │
│  - 标准化：热度归一化、标题清洗                                   │
│  - 跨平台聚合：相似事件合并                                       │
└─────────────────────────────────────────────────────────────────┘
                              │
                              ▼
┌─────────────────────────────────────────────────────────────────┐
│                    三道数据（消费层）                             │
│  聚合视图、API 接口、前端展示                                    │
└─────────────────────────────────────────────────────────────────┘
```

### 1.3 版本管理

| 版本 | 说明 | 状态 |
|------|------|------|
| v1.0.0 | 初始版本，基础爬虫 + 两张表 | 已废弃 |
| v2.0.0 | 重构版本，三表设计 + 统一字段 + 版本控制 | 设计确认中 |

---

## 二、一道数据设计（原始层）

### 2.1 设计原则

1. **忠实录入**：原始是什么就存什么，不补充、不推断
2. **统一命名**：入库时统一字段名，保留原始字段名到 `*_source` 字段
3. **完整保留**：raw_data 精简后保留，不丢弃关键信息
4. **质量标记**：标记哪些字段是"天然缺失"vs"有值"
5. **版本追溯**：每次爬取记录版本号，便于升级追溯

### 2.2 各平台原始字段详细分析

---

#### 2.2.1 百度热搜 (baidu)

**API地址**：`https://top.baidu.com/board?tab=realtime`

**爬取条数**：50条

**原始返回字段**：

| 字段名 | 类型 | 说明 | 示例值 |
|--------|------|------|--------|
| word | string | 标题 | "世界上最难建的铁路要完成了" |
| hotScore | string | 热度值（字符串） | "7808762" |
| desc | string | 描述 | "云南省大瑞铁路保山至瑞丽段..." |
| url | string | 链接 | "https://www.baidu.com/s?wd=..." |
| img | string | 图片URL | "https://fyb-2.cdn.bcebos.com/..." |
| hotTag | string | 热度标签 | "3" |
| hotChange | string | 热度变化 | "same" / "rise" / "fall" |
| index | number | 索引 | 0, 1, 2... |
| query | string | 查询词 | 同word |
| appUrl | string | APP链接 | - |
| rawUrl | string | 原始链接 | - |
| indexUrl | string | 索引链接 | - |
| hotTagImg | string | 热度标签图片 | - |
| show | array | 展示信息 | [] |

**注意事项**：
- hotScore 是字符串类型，需转换为整数
- hotTag 为数字字符串，含义：0=普通，1=热，2=沸，3=爆
- hotChange 表示排名变化趋势
- 无发布时间、作者、互动数据

**数据示例**：
```json
{
  "word": "世界上最难建的铁路要完成了",
  "hotScore": "7808762",
  "desc": "云南省大瑞铁路保山至瑞丽段即将在"十五五"期间建成通车...",
  "url": "https://www.baidu.com/s?wd=...",
  "img": "https://fyb-2.cdn.bcebos.com/...",
  "hotTag": "3",
  "hotChange": "same",
  "index": 0
}
```

---

#### 2.2.2 微博热搜 (weibo)

**API地址**：`https://m.weibo.cn/api/container/getIndex?containerid=106003type%3D25%26t%3D3%26disable_hot%3D1%26filter_type%3Drealtimehot`

**爬取条数**：50条

**原始返回字段**：

| 字段名 | 类型 | 说明 | 示例值 |
|--------|------|------|--------|
| desc | string | 标题 | "车厘子卖家赌涨价压货" |
| desc_extr | number | 热度值 | 1106646 |
| pic | string | 图片标识 | "https://simg.s.weibo.com/wb_search_img_search_1.png" |
| icon | string | 图标 | - |
| card_type | number | 卡片类型 | 4 |
| itemid | string | 项目ID | - |
| scheme | string | 跳转链接 | "https://m.weibo.cn/search?..." |
| actionlog | object | 日志信息 | - |

**注意事项**：
- 需要Cookie认证才能访问
- pic 字段用于过滤：`img_search_\d+` 才是真实热搜，其他是推广
- 无描述、发布时间、作者、互动数据
- desc_extr 是热度值，纯数字

**数据示例**：
```json
{
  "desc": "车厘子卖家赌涨价压货",
  "desc_extr": 1106646,
  "pic": "https://simg.s.weibo.com/wb_search_img_search_1.png",
  "card_type": 4,
  "scheme": "https://m.weibo.cn/search?..."
}
```

---

#### 2.2.3 B站热门 (bilibili)

**API地址**：`https://api.bilibili.com/x/web-interface/ranking/v2?rid=0&type=all`

**爬取条数**：50条

**原始返回字段**：

| 字段名 | 类型 | 说明 | 示例值 |
|--------|------|------|--------|
| title | string | 标题 | "霍乱：地图上的幽灵与一场科学叛变" |
| bvid | string | 视频ID | "BV1S8cMzZEor" |
| aid | number | 视频AV号 | 116039983630325 |
| desc | string | 描述 | "人类用放血、汞丸、白兰地对抗霍乱..." |
| pic | string | 封面图 | "http://i0.hdslb.com/bfs/archive/..." |
| tname | string | 分区名 | "科学科普" |
| pubdate | number | 发布时间戳 | 1770629961 |
| duration | number | 时长(秒) | 440 |
| owner | object | 作者信息 | {"mid": 1208823126, "name": "大圆镜科普"} |
| stat | object | 统计数据 | 见下表 |

**stat 字段详情**：

| 字段名 | 类型 | 说明 | 示例值 |
|--------|------|------|--------|
| view | number | 播放量 | 3938569 |
| like | number | 点赞数 | 269220 |
| coin | number | 投币数 | 14157 |
| share | number | 分享数 | 2578 |
| reply | number | 评论数 | 3122 |
| danmaku | number | 弹幕数 | 2830 |
| favorite | number | 收藏数 | 37979 |
| his_rank | number | 历史最高排名 | 9 |

**注意事项**：
- 无热度值，可用播放量替代
- pubdate 是 Unix 时间戳
- owner.name 是作者名，owner.mid 是作者ID
- stat 包含完整的互动数据

**数据示例**：
```json
{
  "title": "霍乱：地图上的幽灵与一场科学叛变",
  "bvid": "BV1S8cMzZEor",
  "desc": "人类用放血、汞丸、白兰地对抗霍乱近百年...",
  "tname": "科学科普",
  "pubdate": 1770629961,
  "duration": 440,
  "owner": {
    "mid": 1208823126,
    "name": "大圆镜科普"
  },
  "stat": {
    "view": 3938569,
    "like": 269220,
    "coin": 14157,
    "reply": 3122,
    "share": 2578,
    "favorite": 37979
  }
}
```

---

#### 2.2.4 抖音热榜 (douyin)

**API地址**：`https://www.douyin.com/hot/search`

**爬取条数**：50条

**原始返回字段**：

| 字段名 | 类型 | 说明 | 示例值 |
|--------|------|------|--------|
| word | string | 标题 | "我年少你飘渺" |
| hot_value | number | 热度值 | 9183638 |
| label | number | 标签类型 | 0, 1, 9... |
| event_time | string | 事件时间 | 可能为空 |
| view_count | number | 浏览数 | 可能为0 |
| video_count | number | 视频数 | 可能为0 |

**注意事项**：
- 无描述、发布时间、作者
- label 是数字类型，含义待确认
- 字段较少，raw_data 仅3个字段

**数据示例**：
```json
{
  "word": "我年少你飘渺",
  "hot_value": 9183638,
  "label": 9
}
```

---

#### 2.2.5 知乎热榜 (zhihu)

**API地址**：`https://www.zhihu.com/api/v3/feed/topstory/hot-lists/total`

**爬取条数**：30条

**原始返回字段**：

| 字段名 | 类型 | 说明 | 示例值 |
|--------|------|------|--------|
| title | string | 标题 | "如何看待「长征十号甲」可回收火箭一级成功溅落？" |
| excerpt | string | 摘要 | "2月11日，长征十号运载火箭的一级箭体..." |
| detail_text | string | 热度文本 | "1675 万热度" |
| url | string | 链接 | "https://www.zhihu.com/question/..." |
| created | number | 创建时间戳 | 1770779682 |
| answer_count | number | 回答数 | 363 |
| follower_count | number | 关注数 | 1009 |
| comment_count | number | 评论数 | 0 |
| id | string | 问题ID | "0_1770897121.445489" |

**注意事项**：
- 热度值是文本格式，如"1675 万热度"，需解析
- created 是 Unix 时间戳
- 无作者字段
- 有完整的互动数据（回答、关注、评论）

**数据示例**：
```json
{
  "title": "如何看待「长征十号甲」可回收火箭一级成功溅落？",
  "excerpt": "2月11日，长征十号运载火箭的一级箭体已按照预定程序完成受控操作...",
  "detail_text": "1675 万热度",
  "created": 1770779682,
  "answer_count": 363,
  "follower_count": 1009,
  "comment_count": 0
}
```

---

#### 2.2.6 小红书热搜 (xiaohongshu)

**API地址**：`https://www.xiaohongshu.com/hot/search/hotList`

**爬取条数**：20条

**原始返回字段**：

| 字段名 | 类型 | 说明 | 示例值 |
|--------|------|------|--------|
| title | string | 标题 | "用万能旅行拍照姿势美美出片" |
| id | string | ID | "dora_2178732" |
| score | string | 热度文本 | "907.3w" |
| word_type | string | 类型标签 | "热" / "新" / "无" |
| rank_change | number | 排名变化 | 0, 1, -1... |
| icon | string | 图标 | - |
| type | string | 类型 | "normal" |
| title_img | string | 标题图片 | 可能为空 |

**注意事项**：
- 无描述、发布时间、作者、互动数据
- score 是文本格式，如"907.3w"，需解析
- word_type 表示热搜类型
- 字段较少

**数据示例**：
```json
{
  "title": "用万能旅行拍照姿势美美出片",
  "id": "dora_2178732",
  "score": "907.3w",
  "word_type": "热",
  "rank_change": 0
}
```

---

#### 2.2.7 头条热搜 (toutiao)

**API地址**：`https://www.toutiao.com/hot-event/hot-board/`

**爬取条数**：50条

**原始返回字段**：

| 字段名 | 类型 | 说明 | 示例值 |
|--------|------|------|--------|
| Title | string | 标题 | "网友建议"永不发车"列车全国推广" |
| HotValue | string | 热度值（字符串） | "10954925" |
| ClusterId | number | 聚合ID | 7605100018558566436 |
| QueryWord | string | 查询词 | 同Title |
| Url | string | 链接 | "https://www.toutiao.com/trending/..." |
| Label | string | 标签 | 可能为空 |
| LabelDesc | string | 标签描述 | 可能为空 |
| InterestCategory | array | 兴趣分类 | [] |
| Image | object | 图片信息 | - |

**注意事项**：
- HotValue 是字符串类型，需转换为整数
- 无描述、发布时间、作者、互动数据
- InterestCategory 可能为空数组

**数据示例**：
```json
{
  "Title": "网友建议"永不发车"列车全国推广",
  "HotValue": "10954925",
  "ClusterId": 7605100018558566436,
  "QueryWord": "网友建议"永不发车"列车全国推广",
  "Url": "https://www.toutiao.com/trending/...",
  "InterestCategory": []
}
```

---

#### 2.2.8 贴吧话题榜 (tieba)

**API地址**：`https://tieba.baidu.com/hottopic/browse/topiclist`

**爬取条数**：30条

**原始返回字段**：

| 字段名 | 类型 | 说明 | 示例值 |
|--------|------|------|--------|
| topic_name | string | 标题 | "取消丝袜?乘务员改穿裤装" |
| topic_desc | string | 描述 | "00后女乘客察觉裙装与丝袜不便..." |
| abstract | string | 摘要 | 同topic_desc |
| topic_id | number | 话题ID | 28350619 |
| discuss_num | number | 讨论数 | 2467680 |
| content_num | number | 内容数 | 0 |
| create_time | number | 创建时间戳 | 1770891666 |
| tag | number | 标签 | 2 (对应"新") |
| is_video_topic | string | 是否视频话题 | "0" |
| topic_pic | string | 话题图片 | - |
| topic_url | string | 话题链接 | - |

**注意事项**：
- create_time 是 Unix 时间戳
- tag 是数字，需映射为文本（1=热，2=新等）
- discuss_num 可作为热度值
- 无作者字段

**数据示例**：
```json
{
  "topic_name": "取消丝袜?乘务员改穿裤装",
  "topic_desc": "00后女乘客察觉裙装与丝袜不便，手写信建议高铁乘务员改穿裤装。",
  "topic_id": 28350619,
  "discuss_num": 2467680,
  "create_time": 1770891666,
  "tag": 2
}
```

---

#### 2.2.9 夸克热榜 (quark)

**API地址**：`https://quark.sm.cn/api/rest?method=hotlist.index`

**爬取条数**：50条

**原始返回字段**（精简后保留）：

| 字段名 | 类型 | 说明 | 示例值 |
|--------|------|------|--------|
| title | string | 标题 | "两艘美国海军舰艇发生碰撞" |
| summary | string | 摘要 | "据报道，两艘美国海军舰艇..." |
| content | string | 正文 | "<p>[环球网快讯]...</p>" |
| source_name | string | 来源 | "环球网" |
| publish_time | number | 发布时间戳 | 1770896578000 |
| category | array | 分类 | ["军事", "国际军情"] |
| tags | array | 标签 | ["舰艇", "美国海军", ...] |
| like_cnt | number | 点赞数 | 5 |
| cmt_cnt | number | 评论数 | 4 |
| view_cnt | number | 浏览数 | 0 |
| wm_author | object | 作者信息 | {"name": "环球网", ...} |

**注意事项**：
- 原始返回有149个字段，需大幅精简
- publish_time 是毫秒级时间戳
- 无热度值
- 字段最丰富，包含完整的分类、标签、互动数据

**数据示例**：
```json
{
  "title": "两艘美国海军舰艇发生碰撞",
  "summary": "据报道，两艘美国海军舰艇在南美附近海域发生碰撞...",
  "content": "<p>[环球网快讯]美国《华尔街日报》12日最新消息称...</p>",
  "source_name": "环球网",
  "publish_time": 1770896578000,
  "category": ["军事", "国际军情"],
  "tags": ["舰艇", "美国海军", "美国军事"],
  "like_cnt": 5,
  "cmt_cnt": 4,
  "wm_author": {
    "name": "环球网",
    "desc": "环球网官方平台。"
  }
}
```

---

### 2.3 字段对比汇总表

| 平台 | 标题字段 | 热度字段 | 描述字段 | 时间字段 | 作者字段 | 互动数据 | 分类标签 |
|------|----------|----------|----------|----------|----------|----------|----------|
| 百度 | word | hot_score | desc | ❌ | ❌ | ❌ | hot_tag |
| 微博 | desc | desc_extr | ❌ | ❌ | ❌ | ❌ | ❌ |
| B站 | title | ❌ | desc | pubdate | owner | views/likes/coins... | tname |
| 抖音 | word | hot_value | ❌ | ❌ | ❌ | view/video_count | label |
| 知乎 | title | detail_text | excerpt | created | ❌ | answer/follower/comment | ❌ |
| 小红书 | title | score | ❌ | ❌ | ❌ | ❌ | word_type |
| 头条 | Title | HotValue | ❌ | ❌ | ❌ | ❌ | InterestCategory |
| 贴吧 | topic_name | discuss_num | topic_desc | create_time | ❌ | discuss/content_num | tag |
| 夸克 | title | ❌ | summary/content | publish_time | source | like/comment/view | category/tags |

### 2.4 天然缺失字段（非爬取遗漏）

| 平台 | 天然缺失的字段 |
|------|----------------|
| 百度 | 发布时间、作者、互动数据 |
| 微博 | 描述、发布时间、作者、互动数据 |
| B站 | 热度值 |
| 抖音 | 描述、发布时间、作者 |
| 知乎 | 热度值（是文本）、作者 |
| 小红书 | 描述、发布时间、作者、互动数据 |
| 头条 | 描述、发布时间、作者、互动数据 |
| 贴吧 | 作者 |
| 夸克 | 热度值 |

### 2.5 热度值类型差异

| 类型 | 平台 | 示例 | 处理方式 |
|------|------|------|----------|
| 纯数字 | 百度、微博、抖音、头条、贴吧 | 7808405 | 直接存储 |
| 文本描述 | 知乎、小红书 | "1675 万热度"、"907.3w" | 存原文 + 解析后数字 |
| 无热度 | B站、夸克 | - | 标记 has_hot_value=false |

---

## 三、表结构设计

### 3.1 crawl_sessions（爬取任务表）

**用途**：追溯每次爬取的元信息，支持问题排查和数据回溯。

| 字段 | 类型 | 必填 | 说明 |
|------|------|------|------|
| id | BIGSERIAL | ✅ | 主键 |
| session_id | VARCHAR(64) | ✅ | 唯一批次ID，格式：`{platform}_{timestamp}_{uuid8}` |
| platform | VARCHAR(50) | ✅ | 平台标识 |
| crawler_version | VARCHAR(20) | ✅ | 爬虫版本号 |
| started_at | TIMESTAMP | ✅ | 开始时间 |
| finished_at | TIMESTAMP | ❌ | 结束时间 |
| status | VARCHAR(20) | ✅ | running/success/failed |
| items_count | INTEGER | ❌ | 抓取条数 |
| error_message | TEXT | ❌ | 错误信息 |
| created_at | TIMESTAMP | ✅ | 创建时间 |

**索引**：
- `idx_sessions_platform` ON (platform)
- `idx_sessions_started` ON (started_at)
- `UNIQUE` ON (session_id)

---

### 3.2 hot_search_snapshots（快照表）

**用途**：存储每次爬取的完整快照，是一道数据的核心表。

| 字段 | 类型 | 必填 | 说明 |
|------|------|------|------|
| **通用字段** |
| id | BIGSERIAL | ✅ | 主键 |
| session_id | VARCHAR(64) | ✅ | 关联爬取批次 |
| platform | VARCHAR(50) | ✅ | 平台标识 |
| rank | INTEGER | ✅ | 排名 |
| title | TEXT | ✅ | 标题（统一命名） |
| title_source | VARCHAR(50) | ✅ | 原始标题字段名（word/desc/title等） |
| crawled_at | TIMESTAMP | ✅ | 爬取时间 |
| **热度字段** |
| hot_value | BIGINT | ❌ | 热度值（数字，已解析） |
| hot_value_text | TEXT | ❌ | 热度原始文本（"907.3w"） |
| hot_value_source | VARCHAR(50) | ❌ | 热度来源字段名 |
| **内容字段** |
| description | TEXT | ❌ | 描述/摘要 |
| description_source | VARCHAR(50) | ❌ | 描述来源字段名 |
| url | TEXT | ❌ | 链接 |
| **时间字段** |
| published_at | TIMESTAMP | ❌ | 发布时间 |
| published_at_source | VARCHAR(50) | ❌ | 时间来源字段名 |
| **作者字段** |
| author | VARCHAR(255) | ❌ | 作者名 |
| author_id | VARCHAR(255) | ❌ | 作者ID |
| author_source | VARCHAR(50) | ❌ | 作者来源字段名 |
| **互动数据** |
| view_count | BIGINT | ❌ | 浏览量 |
| like_count | BIGINT | ❌ | 点赞数 |
| comment_count | BIGINT | ❌ | 评论数 |
| share_count | BIGINT | ❌ | 分享数 |
| favorite_count | BIGINT | ❌ | 收藏数 |
| interaction_source | VARCHAR(50) | ❌ | 互动数据来源字段名 |
| **分类标签** |
| category | VARCHAR(100) | ❌ | 分类 |
| tags | TEXT[] | ❌ | 标签数组 |
| **数据质量标记** |
| has_hot_value | BOOLEAN | ✅ | 是否有热度 |
| has_description | BOOLEAN | ✅ | 是否有描述 |
| has_published_at | BOOLEAN | ✅ | 是否有时间 |
| has_author | BOOLEAN | ✅ | 是否有作者 |
| has_interaction | BOOLEAN | ✅ | 是否有互动数据 |
| **平台特有** |
| platform_fields | JSONB | ✅ | 平台特有字段（保留原始命名） |
| raw_data | JSONB | ✅ | 精简后的原始数据 |
| **元数据** |
| created_at | TIMESTAMP | ✅ | 入库时间 |

**索引**：
- `idx_snapshots_session` ON (session_id)
- `idx_snapshots_platform_time` ON (platform, crawled_at)
- `idx_snapshots_needs_enrichment` ON (has_description) WHERE has_description = FALSE

**唯一约束**：
- `UNIQUE` ON (platform, title, session_id)

---

### 3.3 hot_topics（话题表）

**用途**：追踪话题的历史出现情况，支持趋势分析。

| 字段 | 类型 | 必填 | 说明 |
|------|------|------|------|
| id | BIGSERIAL | ✅ | 主键 |
| topic_hash | VARCHAR(64) | ✅ | 唯一标识（platform:title的MD5） |
| event_hash | VARCHAR(64) | ❌ | 跨平台事件ID（二道数据填充） |
| platform | VARCHAR(50) | ✅ | 平台标识 |
| title | TEXT | ✅ | 标题 |
| title_normalized | TEXT | ❌ | 标准化标题（二道数据填充） |
| first_seen_at | TIMESTAMP | ✅ | 首次出现时间 |
| last_seen_at | TIMESTAMP | ✅ | 最后出现时间 |
| appearance_count | INTEGER | ✅ | 出现次数 |
| total_snapshots | INTEGER | ✅ | 关联快照数 |
| max_rank | INTEGER | ✅ | 最高排名（数字越小越高） |
| min_rank | INTEGER | ✅ | 最低排名 |
| max_hot_value | BIGINT | ❌ | 最高热度 |
| avg_hot_value | BIGINT | ❌ | 平均热度 |
| rank_history | JSONB | ❌ | 排名历史 |
| hot_history | JSONB | ❌ | 热度历史 |
| latest_description | TEXT | ❌ | 最新描述 |
| latest_url | TEXT | ❌ | 最新链接 |
| latest_snapshot_id | BIGINT | ❌ | 最新快照ID |
| is_merged | BOOLEAN | ✅ | 是否已合并到跨平台事件 |
| merged_to_event_id | BIGINT | ❌ | 合并到的事件ID |
| created_at | TIMESTAMP | ✅ | 创建时间 |
| updated_at | TIMESTAMP | ✅ | 更新时间 |

**索引**：
- `idx_topics_platform` ON (platform)
- `idx_topics_last_seen` ON (last_seen_at)
- `idx_topics_event_hash` ON (event_hash) WHERE event_hash IS NOT NULL
- `idx_topics_not_merged` ON (is_merged) WHERE is_merged = FALSE

**唯一约束**：
- `UNIQUE` ON (topic_hash)

---

### 3.4 raw_data 精简策略

#### 3.4.1 精简原则

- 保留有业务价值的字段
- 丢弃空值、默认值、内部标识字段
- 保留必要的追溯信息

#### 3.4.2 各平台精简后保留字段

| 平台 | 保留字段 |
|------|----------|
| 百度 | img, url, word, hotTag, hotScore, hotChange |
| 微博 | pic, desc, desc_extr, scheme, card_type |
| B站 | aid, bvid, pic, title, desc, stat, owner, tname, pubdate, duration |
| 抖音 | word, hot_value, label |
| 知乎 | id, title, url, excerpt, answer_count, follower_count, created |
| 小红书 | id, title, score, word_type, rank_change |
| 头条 | ClusterId, Title, HotValue, QueryWord, Image.url |
| 贴吧 | topic_id, topic_name, topic_desc, discuss_num, create_time, topic_pic |
| 夸克 | id, title, summary, content, source_name, publish_time, category, tags, like_cnt, cmt_cnt, view_cnt, wm_author.name |

#### 3.4.3 精简效果

| 平台 | 原始字段数 | 精简后字段数 | 压缩比 |
|------|-----------|-------------|--------|
| 夸克 | 149 | 13 | 91% |
| B站 | 30 | 10 | 67% |
| 其他 | 10-15 | 5-8 | ~50% |

---

## 四、数据量估算

### 4.1 当前配置

- 爬取频率：每30分钟一次（48次/天）
- 平台数量：9个
- 每次记录数：约380条

### 4.2 数据量估算

| 周期 | 记录数 | 数据量（优化前） | 数据量（优化后） |
|------|--------|-----------------|-----------------|
| 每次爬取 | 380 | 572 KB | 343 KB |
| 每天 | 18,240 | 26.82 MB | 16.09 MB |
| 每周 | 127,680 | 187.77 MB | 112.66 MB |
| 每月 | 547,200 | 804.60 MB | 482.76 MB |

### 4.3 Supabase 免费额度分析

| 配置 | 额度 | 可运行时间 |
|------|------|-----------|
| 当前配置（每30分钟） | 500 MB | ~19天（优化前）/ ~31天（优化后） |
| 降低频率（每1小时） | 500 MB | ~38天（优化前）/ ~62天（优化后） |
| 降低频率（每2小时） | 500 MB | ~76天（优化前）/ ~124天（优化后） |

### 4.4 成本优化建议

1. **降低爬取频率**：从每30分钟改为每1-2小时
2. **精简 raw_data**：按上述策略精简
3. **定期归档**：超过30天的数据归档到冷存储
4. **按需爬取**：部分低价值平台降低频率

---

## 五、版本管理规范

### 5.1 版本号规则

采用语义化版本：`MAJOR.MINOR.PATCH`

- **MAJOR**：重大架构变更（如表结构重构）
- **MINOR**：功能新增（如新增平台、新增字段）
- **PATCH**：Bug修复、小优化

### 5.2 版本记录位置

| 位置 | 内容 |
|------|------|
| 本文档 | 架构版本、表结构版本 |
| crawl_sessions.crawler_version | 爬虫版本 |
| 爬虫文件头部注释 | 爬虫版本历史 |
| Git tags | 代码版本 |

### 5.3 版本升级流程

1. 更新本文档版本号
2. 更新爬虫文件头部版本注释
3. 执行数据库迁移脚本
4. 更新 crawl_sessions.crawler_version
5. 创建 Git tag

---

## 六、二道数据规划（预告）

### 6.1 设计目标

- 统一热度评分（归一化）
- 补充缺失信息（LLM + 联网搜索）
- 跨平台事件聚合
- 向量化支持语义检索

### 6.2 预计表结构

- `hot_events`：跨平台事件表
- `event_timeline`：事件时间线
- `event_entities`：事件实体表

### 6.3 LLM 处理流程

```
一道数据 → 判断是否需要补充 → LLM增强 → 向量化 → 入库二道数据
                ↓
         联网搜索（可选）
```

---

## 七、附录

### 7.1 平台标识

| 平台 | 标识 | 爬取条数 |
|------|------|----------|
| 百度热搜 | baidu | 50 |
| 微博热搜 | weibo | 50 |
| B站热门 | bilibili | 50 |
| 抖音热榜 | douyin | 50 |
| 知乎热榜 | zhihu | 30 |
| 小红书热搜 | xiaohongshu | 20 |
| 头条热搜 | toutiao | 50 |
| 贴吧话题榜 | tieba | 30 |
| 夸克热榜 | quark | 50 |

### 7.2 热度归一化基准（二道数据用）

| 平台 | 基准值 | 说明 |
|------|--------|------|
| 百度 | 10,000,000 | 热度值范围约 500万-1000万 |
| 微博 | 2,000,000 | 热度值范围约 50万-200万 |
| 抖音 | 15,000,000 | 热度值范围约 500万-1500万 |
| 头条 | 50,000,000 | 热度值范围约 1000万-5000万 |
| 贴吧 | 5,000,000 | 讨论数范围约 50万-500万 |
| 知乎 | 20,000,000 | 按热度文本解析 |
| 小红书 | 10,000,000 | 按score解析 |

### 7.3 变更历史

| 版本 | 日期 | 变更内容 |
|------|------|----------|
| v1.0.0 | 2026-02-11 | 初始版本 |
| v2.0.0 | 2026-02-12 | 重构：三表设计、统一字段、版本控制、raw_data精简、各平台详细字段文档 |
