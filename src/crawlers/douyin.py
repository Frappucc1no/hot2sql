"""
抖音热榜爬虫

原始字段: word, hot_value, label, event_time, view_count, video_count
天然缺失: 描述、发布时间、作者
注意: 字段较少，raw_data仅保留核心字段
"""
import requests
from datetime import datetime

API_URL = "https://www.iesdouyin.com/web/api/v2/hotsearch/billboard/word/"


def fetch():
    resp = requests.get(API_URL, headers={'User-Agent': 'Mozilla/5.0'}, timeout=10)
    data = resp.json().get('word_list', [])

    result = []
    for i, item in enumerate(data):
        hot_value = item.get('hot_value', 0)
        view_count = item.get('view_count', 0)
        video_count = item.get('video_count', 0)
        label = item.get('label', 0)
        
        platform_fields = {
            'label': label,
            'video_count': video_count,
        }
        
        raw_data = {
            'word': item.get('word', ''),
            'hot_value': hot_value,
            'label': label,
        }
        
        result.append({
            'rank': item.get('position', i + 1),
            'title': item.get('word', ''),
            'title_source': 'word',
            'hot_value': hot_value,
            'hot_value_text': str(hot_value),
            'hot_value_source': 'hot_value',
            'description': None,
            'description_source': None,
            'url': f"https://www.douyin.com/search/{item.get('word', '')}",
            'published_at': None,
            'published_at_source': None,
            'author': None,
            'author_id': None,
            'author_source': None,
            'view_count': view_count if view_count else None,
            'like_count': None,
            'comment_count': None,
            'share_count': None,
            'favorite_count': None,
            'interaction_source': 'view_count' if view_count else None,
            'category': str(label) if label else None,
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
