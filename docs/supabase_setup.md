# Supabase 接入指引

## 一、注册和创建项目

### 1. 注册Supabase账号
1. 访问 https://supabase.com
2. 点击 "Start your project"
3. 使用GitHub账号登录（推荐，方便后续集成）

### 2. 创建新项目
1. 点击 "New Project"
2. 填写项目信息：
   - **Name**: hot2sql（或你喜欢的名字）
   - **Database Password**: 设置一个强密码（保存好，后面会用到）
   - **Region**: 选择离你最近的区域（如 Singapore）
3. 点击 "Create new project"
4. 等待项目创建完成（约1-2分钟）

---

## 二、获取连接信息

### 1. 获取API URL和Key
1. 进入项目Dashboard
2. 点击左侧菜单 "Project Settings" → "API"
3. 找到以下信息：
   - **URL**: `https://xxxxxxxxxxxx.supabase.co`（这是SUPABASE_URL）
   - **anon public**: `eyJ...`（这是SUPABASE_KEY）

### 2. 保存连接信息
创建 `.env` 文件：
```bash
SUPABASE_URL=https://your-project.supabase.co
SUPABASE_KEY=your-anon-key-here
```

---

## 三、创建数据库表

### 方法一：使用SQL Editor（推荐）

1. 在Supabase Dashboard中，点击左侧 "SQL Editor"
2. 点击 "New query"
3. 复制 `scripts/init_db.sql` 文件中的内容
4. 粘贴到SQL Editor中
5. 点击 "Run" 执行

### 方法二：使用Table Editor

#### 创建 hot_search_snapshots 表

1. 点击左侧 "Table Editor"
2. 点击 "Create a new table"
3. 填写表名：`hot_search_snapshots`
4. 添加以下列：

| 列名 | 类型 | 是否必填 | 默认值 |
|------|------|---------|--------|
| platform | varchar | 是 | - |
| rank | int8 | 是 | - |
| title | text | 是 | - |
| hot_value | int8 | 否 | - |
| url | text | 否 | - |
| description | text | 否 | - |
| crawled_at | timestamptz | 否 | now() |
| published_at | timestamptz | 否 | - |
| author | varchar | 否 | - |
| view_count | int8 | 否 | - |
| comment_count | int8 | 否 | - |
| like_count | int8 | 否 | - |
| share_count | int8 | 否 | - |
| category | varchar | 否 | - |
| labels | text[] | 否 | - |
| platform_specific | jsonb | 否 | - |
| raw_data | jsonb | 是 | - |

5. 点击 "Save"

#### 创建 hot_topics 表

1. 点击 "Create a new table"
2. 填写表名：`hot_topics`
3. 添加以下列：

| 列名 | 类型 | 是否必填 | 默认值 |
|------|------|---------|--------|
| platform | varchar | 是 | - |
| title | text | 是 | - |
| topic_hash | varchar | 是 | - |
| first_seen_at | timestamptz | 否 | - |
| last_seen_at | timestamptz | 否 | - |
| appearance_count | int8 | 否 | 1 |
| max_rank | int8 | 否 | - |
| max_hot_value | int8 | 否 | - |
| latest_description | text | 否 | - |
| latest_url | text | 否 | - |

4. 设置 `topic_hash` 为唯一（点击列设置 → Is Unique）
5. 点击 "Save"

---

## 四、配置GitHub Secrets

### 1. 打开GitHub仓库设置
1. 进入你的GitHub仓库
2. 点击 "Settings" → "Secrets and variables" → "Actions"
3. 点击 "New repository secret"

### 2. 添加Secrets

添加以下两个secrets：

**Name**: `SUPABASE_URL`  
**Value**: `https://your-project.supabase.co`

**Name**: `SUPABASE_KEY`  
**Value**: `your-anon-key-here`

---

## 五、本地测试

### 1. 安装依赖
```bash
cd hot2sql
pip install -r requirements.txt
```

### 2. 配置环境变量
```bash
cp .env.example .env
# 编辑.env文件，填入你的SUPABASE_URL和SUPABASE_KEY
```

### 3. 测试单个平台
```bash
python main.py baidu
```

### 4. 测试所有平台
```bash
python main.py
```

---

## 六、验证数据入库

### 1. 在Supabase Dashboard中查看
1. 点击左侧 "Table Editor"
2. 选择 `hot_search_snapshots` 或 `hot_topics`
3. 查看数据是否正确插入

### 2. 使用SQL查询
```sql
-- 查看最近的数据
SELECT * FROM hot_search_snapshots 
ORDER BY crawled_at DESC 
LIMIT 10;

-- 查看话题统计
SELECT platform, COUNT(*) as count 
FROM hot_topics 
GROUP BY platform;
```

---

## 七、常见问题

### Q1: 免费额度够用吗？
- 免费版：500MB空间，约能用3天
- 建议：测试阶段用免费版，生产环境升级到付费版

### Q2: 如何备份数据？
- Supabase自动每日备份
- 也可以手动导出：Table Editor → Export → CSV

### Q3: 数据重复怎么办？
- 已设置唯一约束 `platform + title + crawled_at`
- 重复数据会自动跳过

### Q4: 如何清理旧数据？
```sql
-- 删除7天前的数据
DELETE FROM hot_search_snapshots 
WHERE crawled_at < NOW() - INTERVAL '7 days';
```

---

## 八、下一步

1. ✅ 完成Supabase配置
2. ✅ 测试本地运行
3. ✅ 推送到GitHub
4. ✅ 检查GitHub Actions运行状态
5. 🔄 开始数据沉淀

---

**文档版本**: v1.0  
**更新日期**: 2026-02-11
