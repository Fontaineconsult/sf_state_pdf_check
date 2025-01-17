import scrapy
from scrapy.crawler import CrawlerProcess
from scrapy.utils.project import get_project_settings
from scrapy import spiderloader

if __name__ == '__main__':
    # Get project settings
    settings = get_project_settings()
    process = CrawlerProcess(settings)

    # Import all spiders from the spiders module

    spider_loader = spiderloader.SpiderLoader.from_settings(settings)

    # Schedule a crawl for each spider
    for spider_name in spider_loader.list():

        if spider_name == 'j_paul_leonard_library_spider':
            print("STARTING", spider_name)
            process.crawl(spider_name)

    # Start the crawl process
    process.start()