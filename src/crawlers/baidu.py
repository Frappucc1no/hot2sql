"""
百度热搜爬虫

原始字段: word, hotScore, desc, url, img, hotTag, hotChange, index, query, appUrl, rawUrl, indexUrl, hotTagImg, show
天然缺失: 发布时间、作者、互动数据
"""
import requests
from datetime import datetime

API_URL = "https://top.baidu.com/api/board?platform=pc&tab=realtime"


def fetch():
    resp = requests.get(API_URL, headers={'User-Agent': 'Mozilla/5.0'}, timeout=10)
    data = resp.json().get('data', {}).get('cards', [{}])[0].get('content', [])

    result = []
    for idx, item in enumerate(data, 1):
        hot_score_str = item.get('hotScore', '0')
        hot_value = int(hot_score_str) if hot_score_str else 0
        
        platform_fields = {
            'img': item.get('img', ''),
            'hotTag': item.get('hotTag', ''),
            'hotChange': item.get('hotChange', ''),
            'index': item.get('index', 0),
        }
        
        raw_data = {
            'word': item.get('word', ''),
            'hotScore': hot_score_str,
            'desc': item.get('desc', ''),
            'url': item.get('url', ''),
            'img': item.get('img', ''),
            'hotTag': item.get('hotTag', ''),
            'hotChange': item.get('hotChange', ''),
        }
        
        result.append({
            'rank': idx,
            'title': item.get('word', ''),
            'title_source': 'word',
            'hot_value': hot_value,
            'hot_value_text': hot_score_str,
            'hot_value_source': 'hotScore',
            'description': item.get('desc', ''),
            'description_source': 'desc',
            'url': item.get('url', ''),
            'published_at': None,
            'published_at_source': None,
            'author': None,
            'author_id': None,
            'author_source': None,
            'view_count': None,
            'like_count': None,
            'comment_count': None,
            'share_count': None,
            'favorite_count': None,
            'interaction_source': None,
            'category': item.get('hotTag', ''),
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
