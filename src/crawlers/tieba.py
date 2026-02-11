"""百度贴吧话题榜爬虫"""
import requests
from datetime import datetime

API_URL = "https://tieba.baidu.com/hottopic/browse/topicList"


def fetch():
    """获取贴吧话题榜数据"""
    resp = requests.get(API_URL, headers={'User-Agent': 'Mozilla/5.0'}, timeout=10)
    bang_topic = resp.json().get('data', {}).get('bang_topic', {})
    data = bang_topic.get('topic_list', []) if isinstance(bang_topic, dict) else bang_topic

    tag_map = {0: '', 1: '热', 2: '新', 3: '爆', 4: '荐', 5: '精', 6: '置顶'}

    result = []
    for idx, item in enumerate(data, 1):
        tag_code = item.get('tag', 0)
        create_time = item.get('create_time', 0)
        create_time_readable = ''
        if create_time:
            try:
                create_time_readable = datetime.fromtimestamp(create_time).strftime('%Y-%m-%d %H:%M:%S')
            except:
                pass

        result.append({
            'rank': idx,
            'title': item.get('topic_name', ''),
            'description': item.get('topic_desc', ''),
            'abstract': item.get('abstract', ''),
            'discuss_num': item.get('discuss_num', 0),
            'hot_value': item.get('discuss_num', 0),
            'tag': tag_map.get(tag_code, ''),
            'is_video_topic': item.get('is_video_topic', '0') == '1',
            'content_num': item.get('content_num', 0),
            'create_time': create_time_readable,
            'url': item.get('topic_url', ''),
            'raw_data': item,
        })
    return result


if __name__ == '__main__':
    data = fetch()
    print(f"获取到 {len(data)} 条数据")
    for item in data[:5]:
        print(f"{item['rank']}. {item['title']} - {item['discuss_num']}")
