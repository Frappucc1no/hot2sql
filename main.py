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
    """爬取单个平台数据，返回 (snapshot_count, topic_count, success)"""
    print(f"\n{'='*50}")
    print(f"开始爬取: {platform}")
    print(f"{'='*50}")

    try:
        fetcher = PLATFORM_FETCHERS.get(platform)
        if not fetcher:
            print(f"未知平台: {platform}")
            return 0, 0, False

        items = fetcher()
        if not items:
            print(f"[{platform}] 未获取到数据")
            return 0, 0, False

        print(f"[{platform}] 获取到 {len(items)} 条数据")

        db = HotSearchDB()
        crawled_at = datetime.now().isoformat()
        snapshot_count, topic_count = db.process_platform_data(platform, items, crawled_at)

        print(f"[{platform}] 处理完成: {snapshot_count} snapshots, {topic_count} topics")
        return snapshot_count, topic_count, True

    except Exception as e:
        print(f"[{platform}] 爬取失败: {e}")
        import traceback
        traceback.print_exc()
        return 0, 0, False


def crawl_all():
    """爬取所有平台"""
    print("\n" + "="*60)
    print("开始爬取所有平台热榜数据")
    print("="*60)

    total_snapshots = 0
    total_topics = 0
    failed_platforms = []

    for platform in PLATFORM_FETCHERS.keys():
        snapshot_count, topic_count, success = crawl_platform(platform)
        total_snapshots += snapshot_count
        total_topics += topic_count
        if not success:
            failed_platforms.append(platform)

    print("\n" + "="*60)
    print(f"总计: {total_snapshots} snapshots, {total_topics} topics")
    if failed_platforms:
        print(f"失败平台: {', '.join(failed_platforms)}")
    print("="*60)

    return len(failed_platforms) == 0


if __name__ == '__main__':
    if len(sys.argv) > 1:
        platform = sys.argv[1]
        if platform in PLATFORM_FETCHERS:
            snapshot_count, topic_count, success = crawl_platform(platform)
            if not success:
                sys.exit(1)
        else:
            print(f"未知平台: {platform}")
            print(f"可用平台: {', '.join(PLATFORM_FETCHERS.keys())}")
            sys.exit(1)
    else:
        all_success = crawl_all()
        if not all_success:
            sys.exit(1)
