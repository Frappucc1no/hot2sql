"""
夸克热榜爬虫
版本: v2.0.0
更新时间: 2026-02-12

原始字段: 149个字段，精简后保留13个核心字段
保留字段: id, title, summary, content, source_name, publish_time, category, tags, like_cnt, cmt_cnt, view_cnt, wm_author
天然缺失: 热度值
注意: publish_time是毫秒级时间戳；字段最丰富，包含完整分类、标签、互动数据
"""
import requests
import re
from datetime import datetime

API_URL = "https://iflow.quark.cn/iflow/api/v1/article/aggregation"

CRAWLER_VERSION = "2.0.0"


def clean_html(html):
    if not html:
        return ''
    text = re.sub(r'<!--\{(img|video):\d+\}-->', '', html)
    text = re.sub(r'<[^>]+>', '', text)
    text = text.replace('&nbsp;', ' ').replace('&lt;', '<').replace('&gt;', '>')
    text = text.replace('&amp;', '&').replace('&quot;', '"')
    return re.sub(r'\s+', ' ', text).strip()


def fetch():
    resp = requests.get(API_URL, params={'aggregation_id': '16665090098771297825', 'count': 50}, headers={'User-Agent': 'Mozilla/5.0'}, timeout=10)
    data = resp.json().get('data', {}).get('articles', [])

    result = []
    for idx, item in enumerate(data, 1):
        summary = item.get('summary', '')
        summary = re.sub(r'[，；,;。]?(查看)?((更多)|(详情))(>>)?', '。', summary).replace('>>', '。')

        publish_time = item.get('publish_time', 0)
        published_at = None
        if publish_time:
            try:
                published_at = datetime.fromtimestamp(publish_time / 1000).isoformat()
            except:
                pass
        
        wm_author = item.get('wm_author', {})
        author_name = wm_author.get('name', '') if isinstance(wm_author, dict) else ''
        author_id = str(wm_author.get('user_id', '')) if isinstance(wm_author, dict) else ''
        
        category = item.get('category', [])
        category_str = category[0] if category else None
        
        tags = item.get('tags', [])
        
        platform_fields = {
            'id': item.get('id', ''),
            'origin_src_name': item.get('origin_src_name', ''),
        }
        
        raw_data = {
            'id': item.get('id', ''),
            'title': item.get('title', ''),
            'summary': summary,
            'content': clean_html(item.get('content', '')),
            'source_name': item.get('source_name', ''),
            'publish_time': publish_time,
            'category': category,
            'tags': tags,
            'like_cnt': item.get('article_like_cnt', 0),
            'cmt_cnt': item.get('cmt_cnt', 0),
            'view_cnt': item.get('view_cnt', 0),
            'wm_author': {
                'name': author_name,
            } if author_name else {},
        }
        
        like_cnt = item.get('article_like_cnt', 0)
        cmt_cnt = item.get('cmt_cnt', 0)
        view_cnt = item.get('view_cnt', 0)
        
        result.append({
            'rank': idx,
            'title': item.get('title', ''),
            'title_source': 'title',
            'hot_value': None,
            'hot_value_text': None,
            'hot_value_source': None,
            'description': summary,
            'description_source': 'summary',
            'url': f"https://123.quark.cn/detail?item_id={item.get('id', '')}",
            'published_at': published_at,
            'published_at_source': 'publish_time',
            'author': item.get('source_name', '') or author_name,
            'author_id': author_id,
            'author_source': 'source_name',
            'view_count': view_cnt if view_cnt else None,
            'like_count': like_cnt if like_cnt else None,
            'comment_count': cmt_cnt if cmt_cnt else None,
            'share_count': None,
            'favorite_count': None,
            'interaction_source': 'article_like_cnt/cmt_cnt/view_cnt',
            'category': category_str,
            'tags': tags,
            'platform_fields': platform_fields,
            'raw_data': raw_data,
        })
    return result


if __name__ == '__main__':
    data = fetch()
    print(f"获取到 {len(data)} 条数据")
    for item in data[:5]:
        print(f"{item['rank']}. {item['title']} - {item['author']}")
