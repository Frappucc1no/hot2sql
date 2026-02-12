"""
配置文件
"""
import os
from dotenv import load_dotenv
from .version import __version__

load_dotenv()

SUPABASE_URL = os.getenv('SUPABASE_URL')
SUPABASE_KEY = os.getenv('SUPABASE_KEY')

PLATFORMS = {
    'baidu': '百度热搜',
    'weibo': '微博热搜',
    'douyin': '抖音热榜',
    'bilibili': 'B站热门',
    'zhihu': '知乎热榜',
    'toutiao': '头条热搜',
    'tieba': '贴吧话题榜',
    'quark': '夸克热榜',
    'xiaohongshu': '小红书热搜',
}

CRAWL_INTERVAL = 30

CRAWLER_VERSION = __version__
