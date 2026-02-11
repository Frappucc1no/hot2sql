"""B站热门爬虫"""
import requests
from datetime import datetime

API_URL = "https://api.bilibili.com/x/web-interface/ranking/v2?rid=0&type=all"


def fetch():
    """获取B站热门数据"""
    resp = requests.get(API_URL, headers={'User-Agent': 'Mozilla/5.0', 'Referer': 'https://www.bilibili.com'}, timeout=10)
    video_list = resp.json().get('data', {}).get('list', [])

    result = []
    for idx, video in enumerate(video_list, 1):
        stat = video.get('stat', {})
        owner = video.get('owner', {})

        result.append({
            'rank': idx,
            'title': video.get('title'),
            'bvid': video.get('bvid'),
            'region': video.get('tname'),
            'description': video.get('desc'),
            'author': owner.get('name'),
            'author_id': owner.get('mid'),
            'views': stat.get('view', 0),
            'danmaku': stat.get('danmaku', 0),
            'replies': stat.get('reply', 0),
            'likes': stat.get('like', 0),
            'coins': stat.get('coin', 0),
            'favorites': stat.get('favorite', 0),
            'shares': stat.get('share', 0),
            'score': video.get('score', 0),
            'pub_time': datetime.fromtimestamp(video.get('pubdate', 0)).strftime('%Y-%m-%d %H:%M:%S'),
            'duration': video.get('duration', 0),
            'cover_url': video.get('pic'),
            'video_url': f"https://www.bilibili.com/video/{video.get('bvid')}",
            'raw_data': video,
        })
    return result


if __name__ == '__main__':
    data = fetch()
    print(f"获取到 {len(data)} 条数据")
    for item in data[:5]:
        print(f"{item['rank']}. {item['title']} - {item['author']}")
