import scrapy
from scrapy.crawler import CrawlerProcess
from scrapy.utils.project import get_project_settings
from scrapy import spiderloader
from scrapy import signals
from pydispatch import dispatcher


if __name__ == '__main__':
    # Get project settings
    settings = get_project_settings()
    process = CrawlerProcess(settings)

    # Load all spiders from the configured spider folder
    spider_loader = spiderloader.SpiderLoader.from_settings(settings)
    all_spiders = spider_loader.list()  # list of spider names

    # Turn the list into an iterator so we can get one spider at a time
    spider_iter = iter(all_spiders)

    def run_next_spider():
        """
        Get the next spider name from spider_iter.
        If there is none left, do nothing (Scrapy will eventually stop).
        """
        try:
            spider_name = next(spider_iter)
        except StopIteration:
            return  # No more spiders to run
        process.crawl(spider_name)  # Schedule the next spider to crawl

    def spider_closed(spider):
        """
        This function is triggered by the spider_closed signal
        each time a spider finishes.
        """
        run_next_spider()

    # Connect the spider_closed signal to our handler
    dispatcher.connect(spider_closed, signal=signals.spider_closed)

    # Start running the first spider
    run_next_spider()

    # Begin the crawling process
    process.start()