"""爬虫模块"""
from .baidu import fetch as fetch_baidu
from .weibo import fetch as fetch_weibo
from .douyin import fetch as fetch_douyin
from .bilibili import fetch as fetch_bilibili
from .zhihu import fetch as fetch_zhihu
from .toutiao import fetch as fetch_toutiao
from .tieba import fetch as fetch_tieba
from .quark import fetch as fetch_quark
from .xiaohongshu import fetch as fetch_xiaohongshu

__all__ = [
    'fetch_baidu',
    'fetch_weibo',
    'fetch_douyin',
    'fetch_bilibili',
    'fetch_zhihu',
    'fetch_toutiao',
    'fetch_tieba',
    'fetch_quark',
    'fetch_xiaohongshu',
]
