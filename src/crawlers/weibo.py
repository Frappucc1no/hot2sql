"""
微博热搜爬虫

原始字段: desc, desc_extr, pic, icon, card_type, itemid, scheme, actionlog
天然缺失: 描述、发布时间、作者、互动数据
注意: 需要Cookie认证，pic字段用于过滤真实热搜
"""
import re
import requests
from datetime import datetime
from urllib.parse import quote

API_URL = "https://m.weibo.cn/api/container/getIndex?containerid=106003type%3D25%26t%3D3%26disable_hot%3D1%26filter_type%3Drealtimehot"


def fetch():
    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
        'Cookie': COOKIE,
    }
    resp = requests.get(API_URL, headers=headers, timeout=10)
    data = resp.json().get('data', {})
    card_group = data.get('cards', [{}])[0].get('card_group', [])

    result = []
    rank = 0
    for item in card_group:
        pic = item.get('pic', '')
        if not re.match(r'.*img_search_\d+.*', pic):
            continue

        rank += 1
        if rank > 50:
            break

        desc = item.get('desc', '')
        desc_extr = item.get('desc_extr', 0)
        hot_value = int(desc_extr) if desc_extr else 0
        
        platform_fields = {
            'pic': pic,
            'card_type': item.get('card_type', 0),
            'itemid': item.get('itemid', ''),
        }
        
        raw_data = {
            'pic': pic,
            'desc': desc,
            'desc_extr': desc_extr,
            'scheme': item.get('scheme', ''),
            'card_type': item.get('card_type', 0),
        }
        
        result.append({
            'rank': rank,
            'title': desc,
            'title_source': 'desc',
            'hot_value': hot_value,
            'hot_value_text': str(desc_extr),
            'hot_value_source': 'desc_extr',
            'description': None,
            'description_source': None,
            'url': f"https://s.weibo.com/weibo?q={quote(desc)}",
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
        print(f"{item['rank']}. {item['title']} - {item['hot_value']}")
