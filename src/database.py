"""
数据库模块 v2.0.0
更新时间: 2026-02-12

三表设计：
- crawl_sessions: 爬取任务表
- hot_search_snapshots: 快照表
- hot_topics: 话题表
"""
from supabase import create_client
from datetime import datetime
import hashlib
import json
import uuid
from .config import SUPABASE_URL, SUPABASE_KEY

CRAWLER_VERSION = "2.0.0"


class HotSearchDB:
    """热榜数据库操作类 v2.0.0"""

    def __init__(self):
        self.client = create_client(SUPABASE_URL, SUPABASE_KEY)

    def _generate_session_id(self, platform):
        """生成唯一批次ID"""
        timestamp = datetime.now().strftime('%Y%m%d%H%M%S')
        uuid8 = uuid.uuid4().hex[:8]
        return f"{platform}_{timestamp}_{uuid8}"

    def _generate_topic_hash(self, platform, title):
        """生成话题唯一标识"""
        key = f"{platform}:{title}"
        return hashlib.md5(key.encode()).hexdigest()

    def _calculate_quality_flags(self, item):
        """计算数据质量标记"""
        return {
            'has_hot_value': item.get('hot_value') is not None and item.get('hot_value') > 0,
            'has_description': item.get('description') is not None and len(str(item.get('description', ''))) > 0,
            'has_published_at': item.get('published_at') is not None,
            'has_author': item.get('author') is not None and len(str(item.get('author', ''))) > 0,
            'has_interaction': any([
                item.get('view_count'),
                item.get('like_count'),
                item.get('comment_count'),
                item.get('share_count'),
                item.get('favorite_count'),
            ]),
        }

    def _transform_to_snapshot(self, platform, item, session_id, crawled_at):
        """转换数据为snapshot格式"""
        quality_flags = self._calculate_quality_flags(item)
        
        snapshot = {
            'session_id': session_id,
            'platform': platform,
            'rank': item.get('rank', 0),
            'title': item.get('title', ''),
            'title_source': item.get('title_source', ''),
            'hot_value': item.get('hot_value'),
            'hot_value_text': item.get('hot_value_text'),
            'hot_value_source': item.get('hot_value_source'),
            'description': item.get('description'),
            'description_source': item.get('description_source'),
            'url': item.get('url'),
            'published_at': item.get('published_at'),
            'published_at_source': item.get('published_at_source'),
            'author': item.get('author'),
            'author_id': item.get('author_id'),
            'author_source': item.get('author_source'),
            'view_count': item.get('view_count'),
            'like_count': item.get('like_count'),
            'comment_count': item.get('comment_count'),
            'share_count': item.get('share_count'),
            'favorite_count': item.get('favorite_count'),
            'interaction_source': item.get('interaction_source'),
            'category': item.get('category'),
            'tags': item.get('tags', []),
            'has_hot_value': quality_flags['has_hot_value'],
            'has_description': quality_flags['has_description'],
            'has_published_at': quality_flags['has_published_at'],
            'has_author': quality_flags['has_author'],
            'has_interaction': quality_flags['has_interaction'],
            'platform_fields': item.get('platform_fields', {}),
            'raw_data': item.get('raw_data', {}),
            'crawled_at': crawled_at,
        }

        return snapshot

    def create_session(self, platform):
        """创建爬取任务记录"""
        session_id = self._generate_session_id(platform)
        session_data = {
            'session_id': session_id,
            'platform': platform,
            'crawler_version': CRAWLER_VERSION,
            'started_at': datetime.now().isoformat(),
            'status': 'running',
        }

        try:
            result = self.client.table('crawl_sessions').insert(session_data).execute()
            return session_id, result.data[0] if result.data else None
        except Exception as e:
            print(f"创建session失败: {e}")
            return session_id, None

    def update_session(self, session_id, status, items_count=0, error_message=None):
        """更新爬取任务状态"""
        update_data = {
            'status': status,
            'finished_at': datetime.now().isoformat(),
            'items_count': items_count,
        }
        if error_message:
            update_data['error_message'] = error_message

        try:
            result = self.client.table('crawl_sessions').update(update_data).eq('session_id', session_id).execute()
            return result.data[0] if result.data else None
        except Exception as e:
            print(f"更新session失败: {e}")
            return None

    def insert_snapshots_batch(self, platform, items, session_id, crawled_at):
        """批量插入snapshot数据"""
        snapshots = [self._transform_to_snapshot(platform, item, session_id, crawled_at) for item in items]

        try:
            result = self.client.table('hot_search_snapshots').insert(snapshots).execute()
            return result.data
        except Exception as e:
            print(f"批量插入snapshot失败: {e}")
            return []

    def upsert_topic(self, platform, item, crawled_at, snapshot_id=None):
        """插入或更新topic数据"""
        title = item.get('title', '')
        topic_hash = self._generate_topic_hash(platform, title)
        rank = item.get('rank', 0)
        hot_value = item.get('hot_value') or 0

        try:
            existing = self.client.table('hot_topics').select('*').eq('topic_hash', topic_hash).execute()
            
            if existing.data:
                existing_data = existing.data[0]
                current_count = existing_data.get('appearance_count', 1)
                current_total = existing_data.get('total_snapshots', 1)
                current_max_rank = existing_data.get('max_rank', rank)
                current_min_rank = existing_data.get('min_rank', rank)
                current_max_hot = existing_data.get('max_hot_value', 0)
                current_avg_hot = existing_data.get('avg_hot_value', 0)
                rank_history = existing_data.get('rank_history', [])
                hot_history = existing_data.get('hot_history', [])
                
                rank_history.append({'time': crawled_at, 'rank': rank})
                hot_history.append({'time': crawled_at, 'hot_value': hot_value})
                
                new_total = current_total + 1
                new_avg_hot = ((current_avg_hot * current_total) + hot_value) // new_total if hot_value else current_avg_hot
                
                update_data = {
                    'last_seen_at': crawled_at,
                    'appearance_count': current_count + 1,
                    'total_snapshots': new_total,
                    'max_rank': min(current_max_rank, rank),
                    'min_rank': max(current_min_rank, rank),
                    'max_hot_value': max(current_max_hot, hot_value),
                    'avg_hot_value': new_avg_hot,
                    'rank_history': rank_history[-100:],
                    'hot_history': hot_history[-100:],
                    'latest_description': item.get('description'),
                    'latest_url': item.get('url'),
                    'latest_snapshot_id': snapshot_id,
                }
                
                result = self.client.table('hot_topics').update(update_data).eq('topic_hash', topic_hash).execute()
                return result.data[0] if result.data else None
            else:
                topic_data = {
                    'topic_hash': topic_hash,
                    'platform': platform,
                    'title': title,
                    'first_seen_at': crawled_at,
                    'last_seen_at': crawled_at,
                    'appearance_count': 1,
                    'total_snapshots': 1,
                    'max_rank': rank,
                    'min_rank': rank,
                    'max_hot_value': hot_value if hot_value else None,
                    'avg_hot_value': hot_value if hot_value else None,
                    'rank_history': [{'time': crawled_at, 'rank': rank}],
                    'hot_history': [{'time': crawled_at, 'hot_value': hot_value}] if hot_value else [],
                    'latest_description': item.get('description'),
                    'latest_url': item.get('url'),
                    'latest_snapshot_id': snapshot_id,
                    'is_merged': False,
                }
                
                result = self.client.table('hot_topics').insert(topic_data).execute()
                return result.data[0] if result.data else None

        except Exception as e:
            print(f"更新topic失败: {e}")
            return None

    def process_platform_data(self, platform, items, crawled_at):
        """处理单个平台的数据（新版三表逻辑）"""
        session_id, session = self.create_session(platform)
        if not session:
            print(f"[{platform}] 创建session失败")
            return 0, 0, False

        try:
            snapshots = self.insert_snapshots_batch(platform, items, session_id, crawled_at)
            snapshot_count = len(snapshots)
            print(f"[{platform}] 插入 {snapshot_count} 条snapshots")

            topic_count = 0
            for idx, item in enumerate(items):
                snapshot_id = snapshots[idx].get('id') if idx < len(snapshots) else None
                topic = self.upsert_topic(platform, item, crawled_at, snapshot_id)
                if topic:
                    topic_count += 1

            print(f"[{platform}] 更新 {topic_count} 条topics")

            self.update_session(session_id, 'success', snapshot_count)

            return snapshot_count, topic_count, True

        except Exception as e:
            self.update_session(session_id, 'failed', 0, str(e))
            print(f"[{platform}] 处理数据失败: {e}")
            return 0, 0, False
