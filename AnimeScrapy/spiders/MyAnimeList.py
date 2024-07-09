import scrapy


class MyanimelistSpider(scrapy.Spider):
    name = "MyAnimeList"
    allowed_domains = ["myanimelist.net"]
    start_urls = ["https://myanimelist.net/anime/season"]

    def parse(self, response):
        pass
