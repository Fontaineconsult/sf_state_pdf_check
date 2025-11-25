import scrapy
from scrapy.crawler import CrawlerProcess
from scrapy.utils.project import get_project_settings




def run_spider_by_name(spider_name):
    """Run a Scrapy spider by its name."""
    # Get project settings
    settings = get_project_settings()
    process = CrawlerProcess(settings)

    # Schedule the spider to crawl
    process.crawl(spider_name)

    # Start the crawling process
    process.start()





if __name__ == '__main__':
    run_spider_by_name("disability_programs_and_resource_center_spider")

    # # Get project settings
    # settings = get_project_settings()
    # process = CrawlerProcess(settings)
    #
    # # Provide the spider name you want to run
    # spider_name = 'disability_programs_and_resource_center_spider'  # Replace with your actual spider name
    #
    # # Schedule the spider to crawl
    # process.crawl(spider_name)
    #
    # # Start the crawling process
    # process.start()