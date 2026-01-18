
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent))

import os
from scrapy.crawler import CrawlerProcess
from scrapy.utils.project import get_project_settings
from scrapy import spiderloader, signals
from pydispatch import dispatcher


from set_env import get_project_path

COMPLETED_FILE = get_project_path('completed_spiders')

def load_completed():
    if not os.path.exists(COMPLETED_FILE):
        return set()
    with open(COMPLETED_FILE) as f:
        return {line.strip() for line in f if line.strip()}

def mark_completed(spider_name):
    # open/close on each call so it's flushed immediately
    with open(COMPLETED_FILE, 'a') as f:
        f.write(spider_name + '\n')



def run_all_spiders():

    settings = get_project_settings()
    process = CrawlerProcess(settings)

    loader = spiderloader.SpiderLoader.from_settings(settings)
    all_spiders = list(reversed(loader.list()))
    completed = load_completed()
    to_run = [name for name in all_spiders if name not in completed]

    if not to_run:
        print("All spiders have already completed. Exiting.")
        exit()

    def on_spider_closed(spider, reason):
        if reason == 'finished':
            mark_completed(spider.name)
            print(f"Completed spider: {spider.name}")
        else:
            print(f"Spider '{spider.name}' closed (reason: {reason})")

    dispatcher.connect(on_spider_closed, signal=signals.spider_closed)

    # Schedule ALL spiders before starting the reactor
    for name in to_run:
        print(f"Scheduling spider: {name}")
        process.crawl(name)

    print(f"\nStarting {len(to_run)} spiders concurrently...")
    process.start()



if __name__ == '__main__':
    run_all_spiders()