"""
百度贴吧话题榜爬虫

原始字段: topic_name, topic_desc, abstract, topic_id, discuss_num, content_num, create_time, tag, is_video_topic, topic_pic, topic_url
天然缺失: 作者
注意: tag是数字，需映射为文本；discuss_num可作为热度值
"""
import requests
from datetime import datetime

API_URL = "https://tieba.baidu.com/hottopic/browse/topicList"

TAG_MAP = {0: '', 1: '热', 2: '新', 3: '爆', 4: '荐', 5: '精', 6: '置顶'}


def fetch():
    resp = requests.get(API_URL, headers={'User-Agent': 'Mozilla/5.0'}, timeout=10)
    bang_topic = resp.json().get('data', {}).get('bang_topic', {})
    data = bang_topic.get('topic_list', []) if isinstance(bang_topic, dict) else bang_topic

    result = []
    for idx, item in enumerate(data, 1):
        tag_code = item.get('tag', 0)
        create_time = item.get('create_time', 0)
        published_at = None
        if create_time:
            try:
                published_at = datetime.fromtimestamp(create_time).isoformat()
            except:
                pass
        
        discuss_num = item.get('discuss_num', 0)
        
        platform_fields = {
            'topic_id': item.get('topic_id', 0),
            'tag_code': tag_code,
            'tag_text': TAG_MAP.get(tag_code, ''),
            'is_video_topic': item.get('is_video_topic', '0') == '1',
            'content_num': item.get('content_num', 0),
            'topic_pic': item.get('topic_pic', ''),
        }
        
        raw_data = {
            'topic_id': item.get('topic_id', 0),
            'topic_name': item.get('topic_name', ''),
            'topic_desc': item.get('topic_desc', ''),
            'discuss_num': discuss_num,
            'create_time': create_time,
            'topic_pic': item.get('topic_pic', ''),
        }
        
        result.append({
            'rank': idx,
            'title': item.get('topic_name', ''),
            'title_source': 'topic_name',
            'hot_value': discuss_num,
            'hot_value_text': str(discuss_num),
            'hot_value_source': 'discuss_num',
            'description': item.get('topic_desc', ''),
            'description_source': 'topic_desc',
            'url': item.get('topic_url', ''),
            'published_at': published_at,
            'published_at_source': 'create_time',
            'author': None,
            'author_id': None,
            'author_source': None,
            'view_count': None,
            'like_count': None,
            'comment_count': item.get('content_num', 0) if item.get('content_num', 0) else None,
            'share_count': None,
            'favorite_count': None,
            'interaction_source': 'content_num' if item.get('content_num', 0) else None,
            'category': TAG_MAP.get(tag_code, ''),
            'tags': [],
            'platform_fields': platform_fields,
            'raw_data': raw_data,
        })
    return result


if __name__ == '__main__':
    data = fetch()
    print(f"获取到 {len(data)} 条数据")
    for item in data[:5]:
        print(f"{item['rank']}. {item['title']} - {item['hot_value']}")
