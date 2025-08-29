# -*- coding:utf-8 -*-
# AUTHOR: Sun

from json import loads
from datetime import date, datetime
from logging import getLogger

from httpx import Request, Response

from frame.handle import Spider
from database.model import Cache, Session
from database.data import CacheData, Season, DEFAULT_TZ


looger = getLogger(__name__)
BagumiSpider = Spider()

BagumiSpider.config.REQUEST.USER_AGENT = 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/123.0.0.0 Safari/537.36'
BagumiSpider.config.REQUEST.DEFAULT_REQUEST_HEADERS = {
    'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,image/apng,*/*;q=0.8',
    'Accept-Language': 'zh-CN,zh;q=0.9,en-US;q=0.8,en;q=0.7',
    'Accept-Encoding': 'gzip, deflate, br',
    'Connection': 'keep-alive',
    'Upgrade-Insecure-Requests': '1',
    'Cache-Control': 'max-age=0'
}
BagumiSpider.config.REQUEST.DOWNLOAD_DELAY = 3

BagumiSpider.config.HANDLE.INIT_URL = Request('GET', 'https://api.bgm.tv/calendar')

@BagumiSpider.route('api.bgm.tv/calendar')
def handle_calender(response: Response):
    data = loads(response.content)
    uid: list[int] = []

    for week_item in data:
        for item in week_item['items']:
            uid.append(item['id'])

    return [Request('GET', f'https://api.bgm.tv/v0/subjects/{i}') for i in uid][:3]


@BagumiSpider.route(r'api.bgm.tv/v0/subjects/\d+', regex=True)
def handle_subject(response: Response):
    cache_object = CacheData()

    data = loads(response.content)

    cache_object.name = data['name']
    cache_object.translation = data['name_cn']
    cache_object.all_data = [cache_object.name, cache_object.translation]
    for item in data['infobox']:
        if item['key'] == '别名':
            for value in item['value']:
                cache_object.all_data.append(value['v'])

            break
    logger.debug('name analysis successfully')

    release_date: tuple[int, ...] = tuple(int(i) for i in data['date'].split('-'))
    cache_object.year = release_date[0]
    if 1 <= release_date[1] <= 3:
        cache_object.season = Season.WINTER
    elif 4 <= release_date[1] <= 6:
        cache_object.season = Season.SPRING
    elif 7 <= release_date[1] <= 9:
        cache_object.season = Season.SUMMER
    elif 10 <= release_date[1] <= 12:
        cache_object.season = Season.AUTUMN
    else:
        raise ValueError(f'Invalid date: {release_date}')
    logger.debug('time analysis successfully')

    cache_object.time = date(*release_date)
    cache_object.tag = data['meta_tags']
    cache_object.description = data['summary']
    logger.debug('base information analysis successfully')

    rating = data['rating']
    cache_object.score = rating['score']
    cache_object.vote = rating['total']
    cache_object.date = datetime.now(DEFAULT_TZ).date()
    logger.debug('rating analysis successfully')

    cache_object.web = 1
    cache_object.webId = data['id']

    cache_object.picture = data['images']['large']

    cache: Cache = cache_object.to_orm()

    with Session() as session:
        session.add(cache)
        session.commit()
    logger.info(f'{cache_object.name} add successfully')

if __name__ == '__main__':
    import logging

    logging.basicConfig(level=logging.DEBUG)

    logging.getLogger('httpcore').setLevel(logging.WARNING)
    logging.getLogger('httpx').setLevel(logging.WARNING)

    from frame.control import Control, logger

    control = Control()
    control.add(BagumiSpider)

    control.start()
