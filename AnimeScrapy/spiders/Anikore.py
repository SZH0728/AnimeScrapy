import scrapy


class AnikoreSpider(scrapy.Spider):
    name = "Anikore"
    allowed_domains = ["www.anikore.jp"]
    start_urls = ["https://www.anikore.jp/chronicle/<year>/<season>"]

    def parse(self, response):
        pass
