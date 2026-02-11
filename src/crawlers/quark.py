"""夸克热榜爬虫"""
import requests
import re
from datetime import datetime

API_URL = "https://iflow.quark.cn/iflow/api/v1/article/aggregation"


def clean_html(html):
    """清理HTML标签"""
    if not html:
        return ''
    text = re.sub(r'<!--\{(img|video):\d+\}-->', '', html)
    text = re.sub(r'<[^>]+>', '', text)
    text = text.replace('&nbsp;', ' ').replace('&lt;', '<').replace('&gt;', '>')
    text = text.replace('&amp;', '&').replace('&quot;', '"')
    return re.sub(r'\s+', ' ', text).strip()


def fetch():
    """获取夸克热榜数据"""
    resp = requests.get(API_URL, params={'aggregation_id': '16665090098771297825', 'count': 50}, headers={'User-Agent': 'Mozilla/5.0'}, timeout=10)
    data = resp.json().get('data', {}).get('articles', [])

    result = []
    for idx, item in enumerate(data, 1):
        summary = item.get('summary', '')
        summary = re.sub(r'[，；,;。]?(查看)?((更多)|(详情))(>>)?', '。', summary).replace('>>', '。')

        publish_time = item.get('publish_time', 0)
        publish_time_readable = ''
        if publish_time:
            try:
                publish_time_readable = datetime.fromtimestamp(publish_time / 1000).strftime('%Y-%m-%d %H:%M:%S')
            except:
                pass

        result.append({
            'rank': idx,
            'title': item.get('title', ''),
            'summary': summary,
            'content': clean_html(item.get('content', '')),
            'source': item.get('source_name', ''),
            'origin_source': item.get('origin_src_name', ''),
            'category': item.get('category', []),
            'tags': item.get('tags', []),
            'like_count': item.get('article_like_cnt', 0),
            'comment_count': item.get('cmt_cnt', 0),
            'view_count': item.get('view_cnt', 0),
            'publish_time': publish_time_readable,
            'url': f"https://123.quark.cn/detail?item_id={item.get('id', '')}",
            'raw_data': item,
        })
    return result


if __name__ == '__main__':
    data = fetch()
    print(f"获取到 {len(data)} 条数据")
    for item in data[:5]:
        print(f"{item['rank']}. {item['title']} - {item['source']}")
