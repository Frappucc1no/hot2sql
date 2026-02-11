"""头条热搜爬虫"""
import requests

API_URL = "https://www.toutiao.com/hot-event/hot-board/"


def fetch():
    """获取头条热搜数据"""
    resp = requests.get(API_URL, params={'origin': 'toutiao_pc'}, headers={'User-Agent': 'Mozilla/5.0'}, timeout=10)
    data = resp.json().get('data', [])

    result = []
    for idx, item in enumerate(data, 1):
        result.append({
            'rank': idx,
            'title': item.get('Title', ''),
            'hot_value': int(item.get('HotValue', '0').replace(',', '')),
            'label_desc': item.get('LabelDesc', ''),
            'interest_category': item.get('InterestCategory', []),
            'url': item.get('Url', ''),
            'raw_data': item,
        })
    return result


if __name__ == '__main__':
    data = fetch()
    print(f"获取到 {len(data)} 条数据")
    for item in data[:5]:
        print(f"{item['rank']}. {item['title']} - {item['hot_value']}")
