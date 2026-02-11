"""百度热搜爬虫"""
import requests
from datetime import datetime

API_URL = "https://top.baidu.com/api/board?platform=pc&tab=realtime"


def fetch():
    """获取百度热搜数据"""
    resp = requests.get(API_URL, headers={'User-Agent': 'Mozilla/5.0'}, timeout=10)
    data = resp.json().get('data', {}).get('cards', [{}])[0].get('content', [])

    result = []
    for idx, item in enumerate(data, 1):
        result.append({
            'rank': idx,
            'word': item.get('word', ''),
            'hot_score': int(item.get('hotScore', 0)),
            'desc': item.get('desc', ''),
            'url': item.get('url', ''),
            'hot_tag': item.get('hotTag', ''),
            'is_top': item.get('isTop', False),
            'hot_change': item.get('hotChange', ''),
            'raw_data': item,
        })
    return result


if __name__ == '__main__':
    data = fetch()
    print(f"获取到 {len(data)} 条数据")
    for item in data[:5]:
        print(f"{item['rank']}. {item['word']} - {item['hot_score']}")
