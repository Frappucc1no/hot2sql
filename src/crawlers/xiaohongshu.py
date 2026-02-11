"""小红书热搜爬虫"""
import requests
from datetime import datetime

API_URL = 'https://edith.xiaohongshu.com/api/sns/v1/search/hot_list'
HEADERS = {
    'User-Agent': 'Mozilla/5.0 (iPhone; CPU iPhone OS 16_0 like Mac OS X) AppleWebKit/605.1.15 (KHTML, like Gecko) Mobile/15E148 MicroMessenger/8.0.7(0x18000733) NetType/WIFI Language/zh_CN',
    'referer': 'https://app.xhs.cn/',
    'accept': 'application/json, text/plain, */*',
    'accept-language': 'zh-CN,zh;q=0.9',
    'xy-direction': '22',
    'shield': 'XYAAAAAQAAAAEAAABTAAAAUzUWEe4xG1IYD9/c+qCLOlKGmTtFa+lG434Oe+FTRagxxoaz6rUWSZ3+juJYz8RZqct+oNMyZQxLEBaBEL+H3i0RhOBVGrauzVSARchIWFYwbwkV',
    'xy-platform-info': 'platform=iOS&version=8.7&build=8070515&deviceId=C323D3A5-6A27-4CE6-AA0E-51C9D4C26A24&bundle=com.xingin.discover',
    'xy-common-params': 'app_id=ECFAAF02&build=8070515&channel=AppStore&deviceId=C323D3A5-6A27-4CE6-AA0E-51C9D4C26A24&device_fingerprint=20230920120211bd7b71a80778509cf4211099ea911000010d2f20f6050264&device_fingerprint1=20230920120211bd7b71a80778509cf4211099ea911000010d2f20f6050264&device_model=phone&fid=1695182528-0-0-63b29d709954a1bb8c8733eb2fb58f29&gid=7dc4f3d168c355f1a886c54a898c6ef21fe7b9a847359afc77fc24ad&identifier_flag=0&lang=zh-Hans&launch_id=716882697&platform=iOS&project_id=ECFAAF&sid=session.1695189743787849952190&t=1695190591&teenager=0&tz=Asia/Shanghai&uis=light&version=8.7',
}


def parse_score(score_str):
    """解析热度值"""
    if not score_str:
        return 0
    try:
        if 'w' in score_str.lower():
            return int(float(score_str.lower().replace('w', '')) * 10000)
        elif '万' in score_str:
            return int(float(score_str.replace('万', '')) * 10000)
        elif '亿' in score_str:
            return int(float(score_str.replace('亿', '')) * 100000000)
        else:
            return int(float(score_str))
    except:
        return 0


def fetch():
    """获取小红书热搜数据"""
    resp = requests.get(API_URL, headers=HEADERS, timeout=10)
    data = resp.json()

    if data.get('code') != 0:
        return []

    items = data.get('data', {}).get('items', [])
    if not items:
        return []

    result = []
    for idx, item in enumerate(items, 1):
        result.append({
            'rank': idx,
            'title': item.get('title', ''),
            'word': item.get('title', ''),
            'score': item.get('score', ''),
            'hot_value': parse_score(item.get('score', '0')),
            'word_type': item.get('word_type', ''),
            'rank_change': item.get('rank_change', 0),
            'url': f"https://www.xiaohongshu.com/search_result?keyword={item.get('title', '')}&type=51",
            'raw_data': item,
        })
    return result


if __name__ == '__main__':
    data = fetch()
    print(f"获取到 {len(data)} 条数据")
    for item in data[:5]:
        print(f"{item['rank']}. {item['title']} - {item['score']}")
