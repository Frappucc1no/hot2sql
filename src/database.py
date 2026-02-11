"""数据库模块"""
from supabase import create_client
from datetime import datetime
import hashlib
import json
from .config import SUPABASE_URL, SUPABASE_KEY


class HotSearchDB:
    """热榜数据库操作类"""

    def __init__(self):
        self.client = create_client(SUPABASE_URL, SUPABASE_KEY)

    def _generate_topic_hash(self, platform, title):
        """生成话题唯一标识"""
        key = f"{platform}:{title}"
        return hashlib.md5(key.encode()).hexdigest()

    def _transform_to_snapshot(self, platform, item, crawled_at):
        """转换数据为snapshot格式"""
        # 提取通用字段
        title = item.get('title') or item.get('word', '')
        hot_value = item.get('hot_value') or item.get('hot_score')
        description = item.get('description') or item.get('desc') or item.get('detail') or item.get('summary', '')
        url = item.get('url', '')

        # 提取时间
        published_at = item.get('published_at') or item.get('create_time') or item.get('pub_time') or item.get('publish_time') or item.get('created')
        if not published_at:
            published_at = None

        # 提取作者/来源
        author = item.get('author') or item.get('source', '')

        # 提取互动数据
        view_count = item.get('view_count') or item.get('views') or item.get('view_cnt', 0)
        comment_count = item.get('comment_count') or item.get('answer_count') or item.get('discuss_num') or item.get('replies') or item.get('cmt_cnt', 0)
        like_count = item.get('like_count') or item.get('likes') or item.get('follower_count') or item.get('article_like_cnt', 0)
        share_count = item.get('share_count') or item.get('shares') or item.get('share_cnt', 0)

        # 提取分类标签
        category = item.get('category', '')
        if isinstance(category, list) and category:
            category = category[0]

        labels = item.get('labels') or item.get('tags', [])
        if not isinstance(labels, list):
            labels = [labels] if labels else []

        # 构建snapshot
        snapshot = {
            'platform': platform,
            'rank': item.get('rank', 0),
            'title': title,
            'hot_value': hot_value,
            'url': url,
            'description': description,
            'crawled_at': crawled_at,
            'published_at': published_at,
            'author': author,
            'view_count': view_count,
            'comment_count': comment_count,
            'like_count': like_count,
            'share_count': share_count,
            'category': category,
            'labels': labels,
            'platform_specific': {k: v for k, v in item.items() if k not in ['rank', 'title', 'word', 'hot_value', 'hot_score', 'url', 'description', 'desc', 'detail', 'summary', 'raw_data']},
            'raw_data': item.get('raw_data', item),
        }

        return snapshot

    def insert_snapshot(self, platform, item, crawled_at):
        """插入单条snapshot数据"""
        snapshot = self._transform_to_snapshot(platform, item, crawled_at)

        try:
            result = self.client.table('hot_search_snapshots').insert(snapshot).execute()
            return result.data[0] if result.data else None
        except Exception as e:
            print(f"插入snapshot失败: {e}")
            return None

    def insert_snapshots_batch(self, platform, items, crawled_at):
        """批量插入snapshot数据"""
        snapshots = [self._transform_to_snapshot(platform, item, crawled_at) for item in items]

        try:
            result = self.client.table('hot_search_snapshots').insert(snapshots).execute()
            return result.data
        except Exception as e:
            print(f"批量插入snapshot失败: {e}")
            return []

    def upsert_topic(self, platform, item, crawled_at):
        """插入或更新topic数据"""
        title = item.get('title') or item.get('word', '')
        topic_hash = self._generate_topic_hash(platform, title)

        topic_data = {
            'platform': platform,
            'title': title,
            'topic_hash': topic_hash,
            'first_seen_at': crawled_at,
            'last_seen_at': crawled_at,
            'appearance_count': 1,
            'max_rank': item.get('rank', 0),
            'max_hot_value': item.get('hot_value') or item.get('hot_score', 0),
            'latest_description': item.get('description') or item.get('desc') or item.get('detail') or item.get('summary', ''),
            'latest_url': item.get('url', ''),
        }

        try:
            # 先尝试插入
            result = self.client.table('hot_topics').insert(topic_data).execute()
            return result.data[0] if result.data else None
        except Exception as e:
            # 如果已存在则更新
            if 'duplicate' in str(e).lower():
                try:
                    # 获取现有数据
                    existing = self.client.table('hot_topics').select('*').eq('topic_hash', topic_hash).execute()
                    if existing.data:
                        existing_data = existing.data[0]
                        update_data = {
                            'last_seen_at': crawled_at,
                            'appearance_count': existing_data['appearance_count'] + 1,
                            'max_rank': min(existing_data['max_rank'], item.get('rank', 0)),
                            'max_hot_value': max(existing_data['max_hot_value'], item.get('hot_value') or item.get('hot_score', 0)),
                            'latest_description': item.get('description') or item.get('desc') or item.get('detail') or item.get('summary', ''),
                            'latest_url': item.get('url', ''),
                        }
                        result = self.client.table('hot_topics').update(update_data).eq('topic_hash', topic_hash).execute()
                        return result.data[0] if result.data else None
                except Exception as e2:
                    print(f"更新topic失败: {e2}")
            return None

    def process_platform_data(self, platform, items, crawled_at):
        """处理单个平台的数据"""
        # 批量插入snapshots
        snapshots = self.insert_snapshots_batch(platform, items, crawled_at)
        print(f"[{platform}] 插入 {len(snapshots)} 条snapshots")

        # 更新topics
        topic_count = 0
        for item in items:
            topic = self.upsert_topic(platform, item, crawled_at)
            if topic:
                topic_count += 1

        print(f"[{platform}] 更新 {topic_count} 条topics")
        return len(snapshots), topic_count
