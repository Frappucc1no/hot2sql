"""
头条热搜爬虫
版本: v2.0.0
更新时间: 2026-02-12

原始字段: Title, HotValue, ClusterId, QueryWord, Url, Label, LabelDesc, InterestCategory, Image
天然缺失: 描述、发布时间、作者、互动数据
注意: HotValue是字符串类型，需转换为整数
"""
import requests
from datetime import datetime

API_URL = "https://www.toutiao.com/hot-event/hot-board/"

CRAWLER_VERSION = "2.0.0"


def fetch():
    resp = requests.get(API_URL, params={'origin': 'toutiao_pc'}, headers={'User-Agent': 'Mozilla/5.0'}, timeout=10)
    data = resp.json().get('data', [])

    result = []
    for idx, item in enumerate(data, 1):
        hot_value_str = item.get('HotValue', '0').replace(',', '')
        hot_value = int(hot_value_str) if hot_value_str else 0
        
        platform_fields = {
            'ClusterId': item.get('ClusterId', 0),
            'Label': item.get('Label', ''),
            'LabelDesc': item.get('LabelDesc', ''),
            'InterestCategory': item.get('InterestCategory', []),
        }
        
        raw_data = {
            'ClusterId': item.get('ClusterId', 0),
            'Title': item.get('Title', ''),
            'HotValue': hot_value_str,
            'QueryWord': item.get('QueryWord', ''),
        }
        
        interest_category = item.get('InterestCategory', [])
        category = interest_category[0] if interest_category else None
        
        result.append({
            'rank': idx,
            'title': item.get('Title', ''),
            'title_source': 'Title',
            'hot_value': hot_value,
            'hot_value_text': hot_value_str,
            'hot_value_source': 'HotValue',
            'description': None,
            'description_source': None,
            'url': item.get('Url', ''),
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
            'category': category,
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
