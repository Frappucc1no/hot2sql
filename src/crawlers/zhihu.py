"""
知乎热榜爬虫

原始字段: title, excerpt, detail_text, url, created, answer_count, follower_count, comment_count, id
天然缺失: 作者
注意: 热度值是文本格式如"1675 万热度"，需解析
"""
import requests
import re
from datetime import datetime

API_URL = "https://api.zhihu.com/topstory/hot-lists/total?limit=30"


def parse_hot_value(detail_text):
    if not detail_text:
        return 0, None
    match = re.search(r'(\d+(?:\.\d+)?)\s*万', detail_text)
    if match:
        return int(float(match.group(1)) * 10000), detail_text
    match = re.search(r'(\d+(?:\.\d+)?)\s*亿', detail_text)
    if match:
        return int(float(match.group(1)) * 100000000), detail_text
    match = re.search(r'(\d+)', detail_text)
    if match:
        return int(match.group(1)), detail_text
    return 0, detail_text


def fetch():
    resp = requests.get(API_URL, headers={'User-Agent': 'Mozilla/5.0'}, timeout=10)
    data = resp.json().get('data', [])

    result = []
    for idx, item in enumerate(data, 1):
        target = item.get('target', {})
        
        created = target.get('created', 0)
        published_at = None
        if created:
            try:
                published_at = datetime.fromtimestamp(created).isoformat()
            except:
                pass
        
        detail_text = item.get('detail_text', '')
        hot_value, hot_value_text = parse_hot_value(detail_text)
        
        platform_fields = {
            'id': item.get('id', ''),
            'question_id': target.get('id', ''),
        }
        
        raw_data = {
            'id': item.get('id', ''),
            'title': target.get('title', ''),
            'url': target.get('url', ''),
            'excerpt': target.get('excerpt', ''),
            'answer_count': target.get('answer_count', 0),
            'follower_count': target.get('follower_count', 0),
            'created': created,
        }
        
        result.append({
            'rank': idx,
            'title': target.get('title', ''),
            'title_source': 'title',
            'hot_value': hot_value,
            'hot_value_text': hot_value_text,
            'hot_value_source': 'detail_text',
            'description': target.get('excerpt', ''),
            'description_source': 'excerpt',
            'url': target.get('url', '').replace('api.', 'www.').replace('questions', 'question'),
            'published_at': published_at,
            'published_at_source': 'created',
            'author': None,
            'author_id': None,
            'author_source': None,
            'view_count': None,
            'like_count': None,
            'comment_count': target.get('comment_count', 0) if target.get('comment_count', 0) else None,
            'share_count': None,
            'favorite_count': target.get('follower_count', 0) if target.get('follower_count', 0) else None,
            'interaction_source': 'target',
            'category': None,
            'tags': [],
            'platform_fields': platform_fields,
            'raw_data': raw_data,
        })
    return result


if __name__ == '__main__':
    data = fetch()
    print(f"获取到 {len(data)} 条数据")
    for item in data[:5]:
        print(f"{item['rank']}. {item['title']} - {item['hot_value_text']}")
