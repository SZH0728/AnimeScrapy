from typing import Iterable
from re import compile
from datetime import date as date

from scrapy import Spider, Request, Selector
from scrapy.http import Response

from AnimeScrapy.items import DetailItem, ScoreItem, PictureItem

DATE_PATTERN = compile(r'(\d{4})年(\d{1,2})月(\d{1,2})日')
DATE_PATTERN_BACKUP = compile(r'(\d{4})-(\d{1,2})-(\d{1,2})')
URL_PATTERN = compile(r'https?://(.*?)/subject/(\d+)')


class BangumiSpider(Spider):
    name = "Bangumi"
    allowed_domains = [
        "bangumi.tv",
        # "lain.bgm.tv",
    ]

    def start_requests(self) -> Iterable[Request]:
        return [Request(url='https://bangumi.tv/calendar', callback=self.parse_calendar)]

    def parse(self, response: Response):
        pass

    def parse_calendar(self, response: Response):
        """从日历页面解析出详情页链接."""
        urls = [
            item.xpath('./div/div/p[1]/a/@href').get()
            for item in response.xpath('//*[@id="colunmSingle"]/div/ul/li/dl/dd/ul/li')
        ]
        yield from response.follow_all(urls, callback=self.parse_detail, meta=response.meta)

    def parse_detail(self, response: Response):
        """从详情页解析动画信息."""
        if response.xpath(r'//*[@id="colunmNotice"]/img'):
            return None

        detail = DetailItem()
        detail['name'] = response.xpath(r'//*[@id="headerSubject"]/h1/a/text()')[0].get()

        description = response.xpath(r'//*[@id="subject_summary"]/text()')
        detail['description'] = '\n'.join([i.get().strip() for i in description])

        detail['cast'] = [i.xpath(r'./div/div/span/a/text()').get()
                          for i in response.xpath(r'//*[@id="browserItemList"]/li')]

        detail['tag'] = [i.xpath(r'./span/text()').get()
                         for i in response.xpath(r'//*[@id="subject_detail"]/div[3]/div/a')]

        alias = []
        info: list[Selector] = response.xpath(r'//*[@id="infobox"]/li')
        for i in info:
            match i.xpath(r'./span/text()').get():
                case '中文名: ':
                    detail['translation'] = i.xpath(r'./text()').get()
                case '放送开始: ' | '上映年度：':
                    day = DATE_PATTERN.findall(i.xpath(r'./text()').get())
                    if not day:
                        day = DATE_PATTERN_BACKUP.findall(i.xpath(r'./text()').get())

                    if day:
                        day = day[0]
                        detail['time'] = date(int(day[0]), int(day[1]), int(day[2]))
                    else:
                        self.logger.error(f'An error occurred while parsing date: {i.extract()}')
                case '导演: ':
                    detail['director'] = i.xpath(r'./a/text()').get()
                case '别名: ':
                    alias.append(i.xpath(r'./text()').get())

        detail['alias'] = alias
        detail['web'], detail['webId'] = URL_PATTERN.findall(response.url)[0]
        # web = 'https://bangumi.tv'+response.xpath(r'//*[@id="headerSubject"]/h1/a/@href')[0].get()
        # detail['web'], detail['webId'] = URL_PATTERN.findall(web)[0]

        picture_url = response.xpath('//*[@id="bangumiInfo"]/div/div[1]/a/img/@src').get()
        if picture_url:
            detail['picture'] = f'https:{picture_url}' if not picture_url.startswith('http') else picture_url
            response.meta[picture_url] = detail['name']
        else:
            detail['picture'] = None

        yield detail

        score = ScoreItem()
        score['name'] = detail['name']
        score['score'] = float(
            response.xpath(r'//*[@id="panelInterestWrapper"]/div[1]/div/a/div/div[2]/span[1]/text()').get()
        )
        score['vote'] = int(response.xpath(r'//*[@id="ChartWarpper"]/div/small/span/text()').get())
        score['source'] = detail['web']

        yield score

        if detail['name'] not in response.meta['anime'] and picture_url:
            yield response.follow(picture_url, callback=self.parse_picture, meta=response.meta)

    @staticmethod
    def parse_picture(response: Response):
        item = PictureItem()
        item['name'] = response.meta[response.url]
        item['picture'] = response.body


if __name__ == '__main__':
    from scrapy.cmdline import execute
    execute('scrapy crawl Bangumi'.split())
