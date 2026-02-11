"""抖音热榜爬虫"""
import requests
from datetime import datetime

API_URL = "https://www.iesdouyin.com/web/api/v2/hotsearch/billboard/word/"


def fetch():
    """获取抖音热榜数据"""
    resp = requests.get(API_URL, headers={'User-Agent': 'Mozilla/5.0'}, timeout=10)
    data = resp.json().get('word_list', [])

    result = []
    for i, item in enumerate(data):
        hot_value = item.get('hot_value', 0)
        view_count = item.get('view_count', 0)
        event_time = item.get('event_time', 0)

        result.append({
            'rank': item.get('position', i + 1),
            'word': item.get('word', ''),
            'hot_value': hot_value,
            'view_count': view_count,
            'video_count': item.get('video_count', 0),
            'label': item.get('label', ''),
            'event_time': datetime.fromtimestamp(event_time).strftime('%Y-%m-%d %H:%M:%S') if event_time else '',
            'url': f"https://www.douyin.com/search/{item.get('word', '')}",
            'raw_data': item,
        })
    return result


if __name__ == '__main__':
    data = fetch()
    print(f"获取到 {len(data)} 条数据")
    for item in data[:5]:
        print(f"{item['rank']}. {item['word']} - {item['hot_value']}")
