"""
B站热门爬虫

原始字段: title, bvid, aid, desc, pic, tname, pubdate, duration, owner, stat
天然缺失: 热度值（可用播放量替代）
注意: stat包含完整互动数据，owner包含作者信息
"""
import requests
from datetime import datetime

API_URL = "https://api.bilibili.com/x/web-interface/ranking/v2?rid=0&type=all"


def fetch():
    resp = requests.get(API_URL, headers={'User-Agent': 'Mozilla/5.0', 'Referer': 'https://www.bilibili.com'}, timeout=10)
    video_list = resp.json().get('data', {}).get('list', [])

    result = []
    for idx, video in enumerate(video_list[:50], 1):
        stat = video.get('stat', {})
        owner = video.get('owner', {})
        
        pubdate = video.get('pubdate', 0)
        published_at = None
        if pubdate:
            try:
                published_at = datetime.fromtimestamp(pubdate).isoformat()
            except:
                pass
        
        platform_fields = {
            'bvid': video.get('bvid', ''),
            'aid': video.get('aid', 0),
            'pic': video.get('pic', ''),
            'tname': video.get('tname', ''),
            'duration': video.get('duration', 0),
            'stat': {
                'danmaku': stat.get('danmaku', 0),
                'coin': stat.get('coin', 0),
                'his_rank': stat.get('his_rank', 0),
            },
        }
        
        raw_data = {
            'aid': video.get('aid', 0),
            'bvid': video.get('bvid', ''),
            'pic': video.get('pic', ''),
            'title': video.get('title', ''),
            'desc': video.get('desc', ''),
            'stat': {
                'view': stat.get('view', 0),
                'like': stat.get('like', 0),
                'coin': stat.get('coin', 0),
                'reply': stat.get('reply', 0),
                'share': stat.get('share', 0),
                'favorite': stat.get('favorite', 0),
            },
            'owner': {
                'mid': owner.get('mid', 0),
                'name': owner.get('name', ''),
            },
            'tname': video.get('tname', ''),
            'pubdate': pubdate,
            'duration': video.get('duration', 0),
        }
        
        result.append({
            'rank': idx,
            'title': video.get('title', ''),
            'title_source': 'title',
            'hot_value': None,
            'hot_value_text': None,
            'hot_value_source': None,
            'description': video.get('desc', ''),
            'description_source': 'desc',
            'url': f"https://www.bilibili.com/video/{video.get('bvid')}",
            'published_at': published_at,
            'published_at_source': 'pubdate',
            'author': owner.get('name', ''),
            'author_id': str(owner.get('mid', '')),
            'author_source': 'owner.name',
            'view_count': stat.get('view', 0),
            'like_count': stat.get('like', 0),
            'comment_count': stat.get('reply', 0),
            'share_count': stat.get('share', 0),
            'favorite_count': stat.get('favorite', 0),
            'interaction_source': 'stat',
            'category': video.get('tname', ''),
            'tags': [],
            'platform_fields': platform_fields,
            'raw_data': raw_data,
        })
    return result


if __name__ == '__main__':
    data = fetch()
    print(f"获取到 {len(data)} 条数据")
    for item in data[:5]:
        print(f"{item['rank']}. {item['title']} - {item['author']}")
