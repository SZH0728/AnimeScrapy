import scrapy


class BangumiSpider(scrapy.Spider):
    name = "Bangumi"
    allowed_domains = ["bangumi.tv"]
    start_urls = ["https://bangumi.tv/calendar"]

    def parse(self, response):
        pass
