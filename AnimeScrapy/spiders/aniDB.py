import scrapy


class AnidbSpider(scrapy.Spider):
    name = "aniDB"
    allowed_domains = ["anidb.net"]
    start_urls = ["https://anidb.net/anime/season?view=smallgrid"]

    def parse(self, response):
        pass
