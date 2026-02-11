"""微博热搜爬虫"""
import requests
from datetime import datetime

API_URL = "https://weibo.com/ajax/statuses/hot_band"


def timestamp_to_readable(ts):
    """时间戳转可读格式"""
    if not ts:
        return ''
    try:
        return datetime.fromtimestamp(int(ts)).strftime('%Y-%m-%d %H:%M:%S')
    except:
        return ''


def fetch():
    """获取微博热搜数据"""
    resp = requests.get(API_URL, headers={'User-Agent': 'Mozilla/5.0'}, timeout=10)
    band_list = resp.json().get('data', {}).get('band_list', [])

    result = []
    for idx, item in enumerate(band_list[:50], 1):
        if item.get('promotion') or item.get('is_ad'):
            continue

        onboard_time = item.get('onboard_time', 0)
        start_time = item.get('start_time', 0)
        updated_time = item.get('updated_time', '')

        result.append({
            'rank': idx,
            'title': item.get('word', ''),
            'hot_value': item.get('num', 0),
            'category': item.get('category', ''),
            'description': item.get('note', ''),
            'url': f"https://s.weibo.com/weibo?q={item.get('word_scheme', item.get('word', ''))}",
            'subject_label': item.get('subject_label', ''),
            'label_name': item.get('label_name', ''),
            'onboard_time': timestamp_to_readable(onboard_time),
            'start_time': timestamp_to_readable(start_time) if start_time else '',
            'updated_time': timestamp_to_readable(int(updated_time)) if updated_time else '',
            'realpos': item.get('realpos', 0),
            'is_new': item.get('is_new', 0),
            'is_ad': False,
            'raw_data': item,
        })
    return result


if __name__ == '__main__':
    data = fetch()
    print(f"获取到 {len(data)} 条数据")
    for item in data[:5]:
        print(f"{item['rank']}. {item['title']} - {item['hot_value']}")
