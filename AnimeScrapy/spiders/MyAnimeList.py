from typing import Iterable
from datetime import date
from re import compile

from scrapy import Request, Spider, Selector
from scrapy.http import Response

from AnimeScrapy.items import ScoreItem, DetailItem, PictureItem

URL_PATTERN = compile(r'https?://(.*?)/.*?')
ANIME_PATTERN = compile(r'https?://(.*?)/anime/(\d+)')

class MyanimelistSpider(Spider):
    name = "MyAnimeList"
    allowed_domains = ["myanimelist.net"]

    def start_requests(self) -> Iterable[Request]:
        return [Request(url='https://myanimelist.net/anime/season', callback=self.parse_list)]

    def parse(self, response):
        pass

    def parse_list(self, response: Response):
        for i in response.xpath(r'//*[@id="content"]/div[3]/div[contains(@class, "seasonal-anime-list")]/div[contains(@class, "seasonal-anime")]'):
            score_object = ScoreItem()

            score_object['name'] = i.xpath(r'./div[1]/div[1]/span[4]/text()').get()
            score_object['score'] = float(i.xpath(r'./div[1]/div[1]/span[2]/text()').get())
            score_object['vote'] = int(i.xpath(r'./div[1]/div[1]/span[1]/text()').get())
            score_object['source'] = URL_PATTERN.findall(response.url)[0]

            yield score_object

        # urls = []
        # for i in response.xpath(
        #     r'//*[@id="content"]/div[3]/div[contains(@class, "seasonal-anime-list")]/div[contains(@class, "seasonal-anime")]'):
        #     name = i.xpath(r'./div[1]/div[1]/span[4]/text()').get()
        #     if name not in response.meta:
        #         urls.append(i.xpath(r'./div[1]/div[1]/div/h2/a/@href').get())

        # yield from response.follow_all(urls, callback=self.parse_detail, meta=response.meta)

    def parse_detail(self, response: Response):
        pass
        # title_sign = [False, False]
        # for i in response.xpath(r'//*[@id="content"]/table/tbody/tr/td[1]/div/*'):
