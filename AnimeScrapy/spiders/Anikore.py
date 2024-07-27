from datetime import datetime
from re import compile
from typing import Iterable

from pytz import timezone
from scrapy import Request, Spider
from scrapy.http import Response

from AnimeScrapy.items import ScoreItem, DetailItem, PictureItem

TZ = timezone('Asia/Shanghai')
GET_NAME = compile(r'「?(.*?)（.*?）」?')
URL_PATTERN = compile(r'https?://(.*?)/.*?')
ANIME_PATTERN = compile(r'https?://(.*?)/anime/(\d+)/')


class AnikoreSpider(Spider):
    name = "Anikore"
    allowed_domains = ["www.anikore.jp", "img.anikore.jp"]
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

        urls = []
        for i in response.xpath(
                r'//*[@id="page-top"]/section[4]/div/div[2]/div[contains(@class, "l-searchPageRanking_unit")]'):

            name = GET_NAME.findall(i.xpath(r'./h2/a/span[3]/span/following-sibling::text()[1]').get().strip())[0]
            if name not in response.meta['anime']:
                urls.append(i.xpath(r'./h2/a/@href').get())
        yield from response.follow_all(urls, callback=self.parse_detail, meta=response.meta)

    def parse_detail(self, response: Response):
        detail = DetailItem()
        name = response.xpath(r'//*[@id="page-top"]/section[4]/div/h1/text()').get().strip()
        detail['name'] = GET_NAME.findall(name)[0]
        detail['description'] = response.xpath(r'string(//*[@id="page-top"]/section[6]/blockquote)').get()

        time: str = response.xpath(r'//*[@id="page-top"]/section[7]/dl/div[2]/dd/a/text()').get()
        if time:
            try:
                detail['time'] = datetime.strptime(time, '%Y年%m月%d日').date()
            except ValueError:
                year, season = time.split('年')
                match season:
                    case '冬アニメ':
                        season = 'D'
                    case '春アニメ':
                        season = 'C'
                    case '夏アニメ':
                        season = 'X'
                    case '秋アニメ':
                        season = 'Q'
                    case _:
                        raise ValueError(f'{season} is not a valid season')
                detail['season'] = year[2:] + season

        detail['alias'] = []
        detail['tag'] = []
        detail['cast'] = []
        detail['web'], detail['webId'] = ANIME_PATTERN.findall(response.url)[0]

        picture_url: str = response.xpath(r'//*[@id="page-top"]/section[4]/div/div[1]/div/img/@data-src').get()
        picture_url = picture_url.split('?')[0]
        detail['picture'] = picture_url

        yield detail

        response.meta['picture'][picture_url] = (detail['name'],)
        yield response.follow(picture_url, callback=self.parse_picture, meta=response.meta)

    @staticmethod
    def parse_picture(response: Response):
        picture = PictureItem()
        picture['name'] = response.meta['picture'][response.url]
        picture['picture'] = response.body
        yield picture


if __name__ == '__main__':
    from scrapy.cmdline import execute
    execute('scrapy crawl Anikore'.split())
