"""主入口脚本"""
import sys
import os
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from datetime import datetime
from src.database import HotSearchDB
from src.crawlers import (
    fetch_baidu, fetch_weibo, fetch_douyin,
    fetch_bilibili, fetch_zhihu, fetch_toutiao,
    fetch_tieba, fetch_quark, fetch_xiaohongshu
)

# 平台映射
PLATFORM_FETCHERS = {
    'baidu': fetch_baidu,
    'weibo': fetch_weibo,
    'douyin': fetch_douyin,
    'bilibili': fetch_bilibili,
    'zhihu': fetch_zhihu,
    'toutiao': fetch_toutiao,
    'tieba': fetch_tieba,
    'quark': fetch_quark,
    'xiaohongshu': fetch_xiaohongshu,
}


def crawl_platform(platform):
    """爬取单个平台数据"""
    print(f"\n{'='*50}")
    print(f"开始爬取: {platform}")
    print(f"{'='*50}")

    try:
        # 获取数据
        fetcher = PLATFORM_FETCHERS.get(platform)
        if not fetcher:
            print(f"未知平台: {platform}")
            return 0, 0

        items = fetcher()
        if not items:
            print(f"[{platform}] 未获取到数据")
            return 0, 0

        print(f"[{platform}] 获取到 {len(items)} 条数据")

        # 入库
        db = HotSearchDB()
        crawled_at = datetime.now().isoformat()
        snapshot_count, topic_count = db.process_platform_data(platform, items, crawled_at)

        print(f"[{platform}] 处理完成: {snapshot_count} snapshots, {topic_count} topics")
        return snapshot_count, topic_count

    except Exception as e:
        print(f"[{platform}] 爬取失败: {e}")
        import traceback
        traceback.print_exc()
        return 0, 0


def crawl_all():
    """爬取所有平台"""
    print("\n" + "="*60)
    print("开始爬取所有平台热榜数据")
    print("="*60)

    total_snapshots = 0
    total_topics = 0

    for platform in PLATFORM_FETCHERS.keys():
        snapshot_count, topic_count = crawl_platform(platform)
        total_snapshots += snapshot_count
        total_topics += topic_count

    print("\n" + "="*60)
    print(f"总计: {total_snapshots} snapshots, {total_topics} topics")
    print("="*60)


if __name__ == '__main__':
    if len(sys.argv) > 1:
        # 指定平台爬取
        platform = sys.argv[1]
        if platform in PLATFORM_FETCHERS:
            crawl_platform(platform)
        else:
            print(f"未知平台: {platform}")
            print(f"可用平台: {', '.join(PLATFORM_FETCHERS.keys())}")
    else:
        # 爬取所有平台
        crawl_all()
