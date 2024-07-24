from datetime import datetime
from re import compile
from typing import Iterable

from scrapy import Request, Spider
from scrapy.http import Response

from AnimeScrapy.items import ScoreItem, DetailItem, PictureItem

URL_PATTERN = compile(r'https?://(.*?)/.*?')
ANIME_PATTERN = compile(r'https?://(.*?)/anime/(\d+)')


class AnidbSpider(Spider):
    name = "aniDB"
    allowed_domains = ["anidb.net", "cdn-us.anidb.net"]

    def start_requests(self) -> Iterable[Request]:
        return [Request(url='https://anidb.net/anime/season?view=smallgrid', callback=self.parse_list)]

    def parse(self, response: Response):
        pass

    def parse_list(self, response: Response):
        for i in response.xpath(r'//*[@id="layout-main"]/div[1]/div[2]/div[2]/div/div/div'):
            if i.xpath(r'./div[2]/div[contains(@class, "votes average")]/span[2]/span[1]'):
                score = ScoreItem()

                score['name'] = i.xpath(r'./div[2]/div[contains(@class, "wrap name")]/a/text()').get()
                score['score'] = float(i.xpath(
                    r'./div[2]/div[contains(@class, "votes average")]/span[2]/span[1]/text()'
                ).get())

                score['vote'] = int(i.xpath(
                    r'./div[2]/div[contains(@class, "votes average")]/span[2]/span[2]/text()'
                ).get().strip('()'))

                score['source'] = URL_PATTERN.findall(response.url)[0]

                yield score

        urls = []
        for i in response.xpath(r'//a[contains(@class, "name-colored")]'):
            name = i.xpath('./text()').get()
            if name not in response.meta['anime']:
                urls.append(i.attrib['href'])

        yield from response.follow_all(urls, callback=self.parse_detail, meta=response.meta)

    def parse_detail(self, response: Response):
        detail = DetailItem()

        detail['name'] = response.xpath(r'//*[@id="layout-main"]/h1/text()').get().replace('Anime: ', '')
        detail['translation'] = response.xpath(
            r'//*[@id="tab_1_pane"]/div/table/tbody/tr[2]/td/label/text()').get()

        name_box = [
            *response.xpath(r'//*[@id="tab_2_pane"]/div/table/tbody/tr/td/span/text()'),
            *response.xpath(r'//*[@id="tab_2_pane"]/div/table/tbody/tr/td/label/text()'),
            *response.xpath(r'//*[@id="tab_2_pane"]/div/table/tbody/tr/td/text()')
        ]
        name_box = [i.get().strip() for i in name_box if i]
        name_box = [i for i in name_box if i not in {'', '(', ')', detail['name'], detail['translation']}]

        detail['alias'] = name_box

        time = response.xpath(
            r'//*[@id="tab_1_pane"]/div/table/tbody/tr[contains(@class, "year")]/td/span[1]/@content').get()
        if time:
            detail['time'] = datetime.strptime(time, '%Y-%m-%d').date()
        else:
            self.logger.error(f'Could not find time for {detail["name"]}')

        detail['tag'] = [i.xpath(r'./a/span[1]/text()').get()
                         for i in response.xpath(
                r'//*[@id="tab_1_pane"]/div/table/tbody/tr[contains(@class, "tags")]/td/span')]

        detail['director'] = response.xpath(r'//*[@id="staffoverview"]/tbody/tr[2]/td[2]/a/span[2]/text()').get()
        detail['cast'] = [i.xpath(r'./td[1]/a/text()').get()
                          for i in response.xpath(r'//*[@id="castoverview"]/tbody/tr')]

        detail['description'] = response.xpath(
            r'string(//*[@id="layout-main"]/div[2]/div[@itemprop="description"])'
        ).get().strip()
        detail['web'], detail['webId'] = ANIME_PATTERN.findall(response.url)[0]

        picture_url = response.xpath(r'//*[@id="layout-main"]/div[2]/div[1]/div[2]/div[1]/div/picture/img/@src').get()
        detail['picture'] = picture_url

        yield detail

        # noinspection DuplicatedCode
        if detail['alias']:
            name_list = (detail['name'], detail['translation'], *detail['alias'])
        else:
            name_list = (detail['name'], detail['translation'])

        response.meta['picture'][picture_url] = name_list
        yield response.follow(url=picture_url, callback=self.parse_picture, meta=response.meta)

    @staticmethod
    def parse_picture(response: Response):
        picture = PictureItem()
        picture['name'] = response.meta['picture'][response.url]
        picture['picture'] = response.body
        yield picture


if __name__ == '__main__':
    from scrapy.cmdline import execute
    execute('scrapy crawl aniDB'.split())
