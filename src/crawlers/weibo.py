"""微博热搜爬虫"""
import re
import requests
from datetime import datetime
from urllib.parse import quote

API_URL = "https://m.weibo.cn/api/container/getIndex?containerid=106003type%3D25%26t%3D3%26disable_hot%3D1%26filter_type%3Drealtimehot"

COOKIE = 'WEIBOCN_FROM=1110006030; SUB=_2AkMe1h3tf8NxqwFRmvsXxG7ia4h2wwrEieKoiuw2JRM3HRl-yT9kqnc9tRB6NVYzAmxCM1izZSWe9-xcPQmmL_NGEnIl; SUBP=0033WrSXqPxfM72-Ws9jqgMF55529P9D9WhR9EPgz3BDPWy-YHwFuiIb; MLOGIN=0; _T_WM=38152265571; XSRF-TOKEN=86baeb; M_WEIBOCN_PARAMS=luicode%3D10000011%26lfid%3D102803%26launchid%3D10000360-page_H5%26fid%3D106003type%253D25%2526t%253D3%2526disable_hot%253D1%2526filter_type%253Drealtimehot%26uicode%3D10000011'

HOT_VALUE_REGEX = re.compile(r'(?P<value>\d+)', re.IGNORECASE)


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
        hot_match = HOT_VALUE_REGEX.search(str(desc_extr))
        hot_value = int(hot_match.group('value')) if hot_match else 0

        result.append({
            'rank': rank,
            'title': desc,
            'hot_value': hot_value,
            'category': '',
            'description': '',
            'url': f"https://s.weibo.com/weibo?q={quote(desc)}",
            'subject_label': '',
            'label_name': '',
            'onboard_time': '',
            'start_time': '',
            'updated_time': '',
            'realpos': 0,
            'is_new': 0,
            'is_ad': False,
            'raw_data': item,
        })
    return result


if __name__ == '__main__':
    data = fetch()
    print(f"获取到 {len(data)} 条数据")
    for item in data[:5]:
        print(f"{item['rank']}. {item['title']} - {item['hot_value']}")
