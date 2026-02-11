"""知乎热榜爬虫"""
import requests
from datetime import datetime

API_URL = "https://api.zhihu.com/topstory/hot-lists/total?limit=30"


def fetch():
    """获取知乎热榜数据"""
    resp = requests.get(API_URL, headers={'User-Agent': 'Mozilla/5.0'}, timeout=10)
    data = resp.json().get('data', [])

    result = []
    for idx, item in enumerate(data, 1):
        target = item.get('target', {})

        created = target.get('created', 0)
        created_readable = ''
        if created:
            try:
                created_readable = datetime.fromtimestamp(created).strftime('%Y-%m-%d %H:%M:%S')
            except:
                pass

        result.append({
            'rank': idx,
            'title': target.get('title', ''),
            'detail': target.get('excerpt', ''),
            'hot_value_desc': item.get('detail_text', ''),
            'answer_count': target.get('answer_count', 0),
            'follower_count': target.get('follower_count', 0),
            'comment_count': target.get('comment_count', 0),
            'created': created_readable,
            'url': target.get('url', '').replace('api.', 'www.').replace('questions', 'question'),
            'raw_data': item,
        })
    return result


if __name__ == '__main__':
    data = fetch()
    print(f"获取到 {len(data)} 条数据")
    for item in data[:5]:
        print(f"{item['rank']}. {item['title']} - {item['hot_value_desc']}")
