from os.path import dirname, abspath, join
from typing import Iterable
from datetime import date
from re import compile

from scrapy import Request, Spider, Selector
from scrapy.http import Response

from AnimeScrapy.items import ScoreItem, DetailItem, PictureItem

URL_PATTERN = compile(r'https?://(.*?)/.*?')
ANIME_PATTERN = compile(r'https?://(.*?)/subject/(\d+)')


class AnidbSpider(Spider):
    name = "aniDB"
    allowed_domains = ["anidb.net"]
    start_urls = ["https://anidb.net/anime/season?view=smallgrid"]

    def start_requests(self) -> Iterable[Request]:
        path = dirname(abspath(__file__))
        with open(join(path, 'anime.txt'), 'r') as f:
            anime = set(f.read().split())
        return [Request(url='https://anidb.net/anime/season?view=smallgrid',
                        callback=self.parse_list, meta={'anime': anime})]

    def parse(self, response: Response):
        pass

    def parse_list(self, response: Response):
        for i in response.xpath(r'//*[@id="layout-main"]/div[1]/div[2]/div[2]/div/div/div'):
            if not i.xpath(r'./div[2]/div[7]/span[2]/span[1]'):
                score_object = ScoreItem()

                score_object['name'] = i.xpath(r'./div[2]/div[2]/a/text()').get()
                score_object['score'] = i.xpath(r'./div[2]/div[7]/span[2]/span[1]/text()').get()
                score_object['vote'] = i.xpath(r'./div[2]/div[7]/span[2]/span[2]/text()').get().strip('()')
                score_object['source'] = URL_PATTERN.findall(response.url)[0]

                yield score_object

        for i in response.xpath(r'//*[@id="layout-main"]/div[1]/div[2]/div[2]/div/div/div'):
            name = i.xpath(r'./div[2]/div[2]/a/text()').get()
            if name not in response.meta['anime']:
                url = i.xpath(r'./div[2]/div[2]/a/@href').get()
                yield response.follow(url=url, callback=self.parse_detail, meta=response.meta)

    def parse_detail(self, response: Response):
        detail_object = DetailItem()

        detail_object['name'] = response.xpath(r'//*[@id="tab_1_pane"]/div/table/tbody/tr[3]/td/label/text()').get()
        detail_object['translation'] = response.xpath(
            r'//*[@id="tab_1_pane"]/div/table/tbody/tr[2]/td/label/text()').get()

        name_box = [
            *response.xpath(r'//*[@id="tab_2_pane"]/div/table/tbody/tr/td/span/text()'),
            *response.xpath(r'//*[@id="tab_2_pane"]/div/table/tbody/tr/td/label/text()'),
            *response.xpath(r'//*[@id="tab_2_pane"]/div/table/tbody/tr/td/text()')
        ]
        name_box = [i.get().strip() for i in name_box if i]
        name_box = [i for i in name_box if i not in {'', '(', ')', detail_object['name'], detail_object['translation']}]

        detail_object['alias'] = name_box

        time = response.xpath(
            r'//*[@id="tab_1_pane"]/div/table/tbody/tr[contains(@class, "g_odd year")]/td/span[1]/@content'
        ).get().split('-')
        detail_object['time'] = date(int(time[0]), int(time[1]), int(time[2]))

        tags = []
        for i in response.xpath(r'//*[@id="tab_1_pane"]/div/table/tbody/tr[contains(@class, "g_odd tags")]/td/span'):
            tags.append(i.xpath(r'./a/span[1]/text()').get())
        detail_object['tag'] = tags

        detail_object['director'] = response.xpath(r'//*[@id="staffoverview"]/tbody/tr[2]/td[2]/a/span[2]/text()')

        casts = []
        for i in response.xpath(r'//*[@id="castoverview"]/tbody/tr'):
            casts.append(i.xpath(r'./td[1]/a/text()').get())
        detail_object['cast'] = casts

        detail_object['description'] = response.xpath(r'string(//*[@id="layout-main"]/div[2]/div[2])').get().strip()
        detail_object['web'], detail_object['webId'] = ANIME_PATTERN.findall(response.url)[0]

        picture_url = response.xpath(r'//*[@id="layout-main"]/div[2]/div[1]/div[2]/div[1]/div/picture/img/@src').get()
        detail_object['picture'] = picture_url

        yield detail_object

        response.meta[picture_url] = detail_object['name']
        yield response.follow(url=picture_url, callback=self.parse_picture, meta=response.meta)

    def parse_picture(self, response: Response):
        picture_object = PictureItem()
        picture_object['name'] = response.meta[response.url]
        picture_object['picture'] = response.body
        yield picture_object
