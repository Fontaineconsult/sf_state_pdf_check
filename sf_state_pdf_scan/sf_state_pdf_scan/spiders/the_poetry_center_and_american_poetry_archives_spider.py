
import os

import scrapy
import re
from scrapy.linkextractors import LinkExtractor
from pydispatch import dispatcher
from scrapy import signals

from ..box_handler import get_box_contents


class ThePoetryCenterAndAmericanPoetryArchivesSpider(scrapy.Spider):
    name = 'the_poetry_center_and_american_poetry_archives_spider'
    start_urls = ['https://poetry.sfsu.edu']
    output_folder = r'C:\Users\913678186\Box\ATI\PDF Accessibility\SF State Website PDF Scans\poetry-sfsu-edu'


    @classmethod
    def from_crawler(cls, crawler, *args, **kwargs):
        spider = super(ThePoetryCenterAndAmericanPoetryArchivesSpider, cls).from_crawler(crawler, *args, **kwargs)
        crawler.signals.connect(spider.spider_closed, signal=signals.spider_closed)
        return spider

    def __init__(self):

        self.matched_links = []  # Store matched links
        self.pdf_links = []  # Store PDF links
    

    def parse(self, response):

        # Regular expression pattern for URLs within access.sfsu.edu domain
        access_url_pattern = re.compile(r'https://poetry.sfsu.edu/.*')
        # Pattern specifically for box.com links
        box_url_pattern = re.compile(r'https?://sfsu.box.com/s/.*')

        pdf_pattern = re.compile(r'.*\.pdf$', re.IGNORECASE)  # Pattern to match .pdf files

        # Extract URLs from href attributes
        extracted_links = response.css('a::attr(href)').getall()

        # Filter links and delegate accordingly

        for link in extracted_links:
            absolute_url = response.urljoin(link)

            # Check for access.sfsu.edu links
            if access_url_pattern.match(absolute_url):
                if pdf_pattern.match(absolute_url):
                    self.pdf_links.append((absolute_url, response.url))
                else:
                    yield response.follow(absolute_url, self.parse)

            # Special handling for box.com links
            elif box_url_pattern.match(absolute_url):
                history = response.meta.get('history', [])
                history.append(response.url)

                yield response.follow(absolute_url, self.parse_box_link, meta={'history': history})

    def parse_box_link(self, response):
        # Implement special handling for box.com links here
        # For example, extracting direct download URLs, if available

        pdf = get_box_contents(response.url)
        if pdf:

            self.pdf_links.append((pdf, response.meta.get('history', [])[0] ))

        print('Handling a Box.com link:', response.url)
        # Add any specific logic for Box.com links

    def spider_closed(self, spider):
        # Ensure the output folder exists
        os.makedirs(self.output_folder, exist_ok=True)

        # Define the output file path
        output_file_path = os.path.join(self.output_folder, 'scanned_pdfs.txt')

        # Open the file and write each PDF link
        with open(output_file_path, 'w', encoding='utf-8') as file:
            for link in self.pdf_links:
                file.write(f"{link[0]} {link[1]}\n")

        print("PDF LINKS saved to", self.output_folder)
