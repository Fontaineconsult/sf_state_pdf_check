
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent))

import os
from scrapy.crawler import CrawlerRunner
from scrapy.utils.project import get_project_settings
from scrapy import spiderloader
from twisted.internet import reactor, defer

from set_env import get_project_path

COMPLETED_FILE = get_project_path('completed_spiders')
BATCH_SIZE = 4  # Number of spiders to run concurrently

def load_completed():
    if not os.path.exists(COMPLETED_FILE):
        return set()
    with open(COMPLETED_FILE) as f:
        return {line.strip() for line in f if line.strip()}

def mark_completed(spider_name):
    # open/close on each call so it's flushed immediately
    with open(COMPLETED_FILE, 'a') as f:
        f.write(spider_name + '\n')


@defer.inlineCallbacks
def crawl_batched(runner, spiders, batch_size):
    """Run spiders in batches for controlled concurrency."""
    for i in range(0, len(spiders), batch_size):
        batch = spiders[i:i + batch_size]
        batch_num = (i // batch_size) + 1
        total_batches = (len(spiders) + batch_size - 1) // batch_size

        print(f"\n=== Batch {batch_num}/{total_batches}: {batch} ===")

        # Schedule all spiders in this batch
        deferreds = []
        for name in batch:
            print(f"  Starting: {name}")
            d = runner.crawl(name)
            d.addCallback(lambda _, n=name: mark_completed(n))
            deferreds.append(d)

        # Wait for entire batch to complete
        yield defer.DeferredList(deferreds)
        print(f"=== Batch {batch_num} complete ===")

    reactor.stop()


def run_all_spiders():

    settings = get_project_settings()
    runner = CrawlerRunner(settings)

    loader = spiderloader.SpiderLoader.from_settings(settings)
    all_spiders = list(reversed(loader.list()))
    completed = load_completed()
    to_run = [name for name in all_spiders if name not in completed]

    if not to_run:
        print("All spiders have already completed. Exiting.")
        exit()

    print(f"Running {len(to_run)} spiders in batches of {BATCH_SIZE}...")
    crawl_batched(runner, to_run, BATCH_SIZE)
    reactor.run()



if __name__ == '__main__':
    run_all_spiders()