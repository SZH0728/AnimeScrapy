# Define here the models for your spider middleware
#
# See documentation in:
# https://docs.scrapy.org/en/latest/topics/spider-middleware.html

from datetime import date, datetime
from os.path import abspath, join, dirname, normpath
from typing import Iterable

from pytz import timezone
from scrapy import Spider, Request
from scrapy.exceptions import IgnoreRequest
import scrapy.http.response
# useful for handling different item types with a single interface
from itemadapter import is_item, ItemAdapter

from AnimeScrapy.items import DetailItem, ScoreItem

TZ = timezone('Asia/Shanghai')


class DetailItemSpiderMiddleware(object):
    def process_spider_output(self, response: scrapy.http.response, result, spider: Spider):
        for i in result:
            if is_item(i) and isinstance(i, DetailItem):
                adapter = ItemAdapter(i)

                if not adapter.get('time'):
                    yield adapter.item
                    continue

                time: date = adapter.get('time')

                year = str(time.year)[2:]
                month = time.month

                if 1 <= month <= 3:
                    month = 'D'
                elif 4 <= month <= 6:
                    month = 'C'
                elif 7 <= month <= 9:
                    month = 'X'
                elif 10 <= month <= 12:
                    month = 'Q'

                adapter['season'] = f'{year}{month}'

                yield adapter.item
            else:
                yield i


class ScoreItemSpiderMiddleware(object):
    def process_spider_output(self, response: scrapy.http.response, result, spider: Spider):
        for i in result:
            if is_item(i) and isinstance(i, ScoreItem):
                adapter = ItemAdapter(i)
                now = datetime.now(TZ)
                adapter['date'] = now.date()
                adapter['score'] = float(adapter['score'])
                adapter['vote'] = int(adapter['vote'])
                yield adapter.item
            else:
                yield i


class MetaDataSpiderMiddleware(object):
    def process_start_requests(self, start_requests: Iterable[Request], spider: Spider):
        current_dir = dirname(abspath(__file__))
        parent_dir = normpath(join(current_dir, '..'))
        path = join(parent_dir, 'anime.txt')
        with open(path, 'r', encoding='utf-8') as f:
            anime = f.read().split()

        for i in start_requests:
            i.meta['anime'] = set(anime)
            yield i


class FilterDetailRequestDownloaderMiddleware(object):
    def process_request(self, request: Request, spider: Spider):
        if 'bangumi.tv' in request.url:
            return None
        if 'anime' not in request.url:
            return None

        now = datetime.now(TZ).date()
        if now.month in {1, 4, 7, 10} and now.day == 1:
            raise IgnoreRequest('Ignore the detail request for the first day of the season')
        return None
