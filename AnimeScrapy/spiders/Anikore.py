from typing import Iterable
from datetime import date, datetime
from re import compile

from pytz import timezone
from scrapy import Request, Spider, Selector
from scrapy.http import Response

from AnimeScrapy.items import ScoreItem, DetailItem, PictureItem

TZ = timezone('Asia/Shanghai')
GET_NAME = compile(r'(.*?)（.*?）')
URL_PATTERN = compile(r'https?://(.*?)/.*?')


class AnikoreSpider(Spider):
    name = "Anikore"
    allowed_domains = ["www.anikore.jp"]
    start_urls = ["https://www.anikore.jp/chronicle/<year>/<season>"]

    def start_requests(self) -> Iterable[Request]:
        today = datetime.now(TZ)
        year = today.year
        month = today.month

        if 1 <= month <= 3:
            season = 'winter'
        elif 4 <= month <= 6:
            season = 'spring'
        elif 7 <= month <= 9:
            season = 'summer'
        else:
            season = 'autumn'

        return [Request(url=f'https://www.anikore.jp/chronicle/{year}/{season}/ac:all/', callback=self.parse_list)]

    def parse(self, response: Response):
        pass

    def parse_list(self, response: Response):
        for i in response.xpath(
                r'//*[@id="page-top"]/section[4]/div/div[2]/div[contains(@class, "l-searchPageRanking_unit")]'):
            score_object = ScoreItem()

            name = GET_NAME.findall(i.xpath(r'./h2/a/span[3]/span/following-sibling::text()[1]').get().strip())
            score_object['name'] = name[0]
            score_object['score'] = float(i.xpath(r'./div[1]/div[3]/strong/text()').get())
            score_object['vote'] = int(i.xpath(r'./div[1]/div[3]/span/text()').get())
            score_object['source'] = URL_PATTERN.findall(response.url)[0]

            yield score_object

        next_url = response.xpath(r'//*[@id="page-top"]/section[5]/span[5]/a/@href').get()
        if next_url:
            yield response.follow(next_url, callback=self.parse_list, meta=response.meta)

