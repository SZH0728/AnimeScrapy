# -*- coding:utf-8 -*-
# AUTHOR: Sun

from datetime import date, datetime
from logging import getLogger

from httpx import Request, Response
from lxml import etree
from re import compile

from frame.handle import Spider
from database.model import SessionFactory
from database.data import CacheData, Season, DEFAULT_TZ

logger = getLogger(__name__)
TEST_DATE_FORMATE = compile(r'\d+年\d+月\d+日')
ANIME_PATTERN = compile(r'/anime/(\d+)/')
NAME_PATTERN = compile(r'(.+)（.*）')

AnikoreSpider = Spider()

AnikoreSpider.config.REQUEST.USER_AGENT = 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/139.0.0.0 Safari/537.36'
AnikoreSpider.config.REQUEST.DEFAULT_REQUEST_HEADERS = {
    'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.7',
    'Accept-Language': 'zh-CN,zh;q=0.9,en;q=0.8,zh-TW;q=0.7',
    'Connection': 'keep-alive',
    'DNT': '1',
    'Sec-Fetch-Dest': 'document',
    'Sec-Fetch-Mode': 'navigate',
    'Sec-Fetch-Site': 'same-origin',
    'Sec-Fetch-User': '?1',
    'Upgrade-Insecure-Requests': '1',
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/139.0.0.0 Safari/537.36',
    'sec-ch-ua': '"Not;A=Brand";v="99", "Google Chrome";v="139", "Chromium";v="139"',
    'sec-ch-ua-mobile': '?0',
    'sec-ch-ua-platform': '"Windows"',
}

AnikoreSpider.config.REQUEST.DOWNLOAD_DELAY = 300


def init_request() -> list[Request]:
    today: date = datetime.now(DEFAULT_TZ).date()

    season: str = ''
    if 1 <= today.month <= 3:
        season = 'winter'
    elif 4 <= today.month <= 6:
        season = 'spring'
    elif 7 <= today.month <= 9:
        season = 'summer'
    elif 10 <= today.month <= 12:
        season = 'autumn'

    return [Request('GET', f'https://www.anikore.jp/chronicle/{today.year}/{season}/')]


AnikoreSpider.config.HANDLE.INIT_URL_FUNCTION = init_request


def handle_anime(anime_element) -> CacheData:
    cache_object = CacheData()

    name_string: str = anime_element.xpath(r'.//span[@class="l-searchPageRanking_unit_title_rankName"]/following-sibling::text()')[0].strip()
    if NAME_PATTERN.match(name_string):
        cache_object.name = NAME_PATTERN.match(name_string).groups(1)[0]
    else:
        cache_object.name = name_string
    cache_object.translation = None
    cache_object.all_data = [cache_object.name]
    logger.debug('name analysis successfully')

    time_string: str = anime_element.xpath(r'.//div[@class="l-searchPageRanking_unit_mainBlock_chronicle"]')[
        0].text.strip()
    if TEST_DATE_FORMATE.match(time_string):
        release_date: date = datetime.strptime(time_string, '%Y年%m月%d日').date()
    else:
        year: int = int(time_string[:4])
        month: int = 0

        if time_string[5:6] == '冬':
            month = 1
        elif time_string[5:6] == '春':
            month = 4
        elif time_string[5:6] == '夏':
            month = 7
        elif time_string[5:6] == '秋':
            month = 10

        release_date: date = date(year, month, 1)

    cache_object.year = release_date.year
    if 1 <= release_date.month <= 3:
        cache_object.season = Season.WINTER
    elif 4 <= release_date.month <= 6:
        cache_object.season = Season.SPRING
    elif 7 <= release_date.month <= 9:
        cache_object.season = Season.SUMMER
    elif 10 <= release_date.month <= 12:
        cache_object.season = Season.AUTUMN
    else:
        raise ValueError(f'Invalid date: {release_date}')
    logger.debug('time analysis successfully')

    cache_object.time = release_date
    cache_object.tag = []
    cache_object.description = anime_element.xpath(r'string(.//div[@class="l-searchPageRanking_unit_excerpt"])').strip()

    cache_object.score = float(
        anime_element.xpath(r'.//div[@class="l-searchPageRanking_unit_mainBlock_starPoint"]/strong')[0].text)
    cache_object.vote = int(
        anime_element.xpath(r'.//div[@class="l-searchPageRanking_unit_mainBlock_starPoint"]/span')[0].text)
    cache_object.date = datetime.now(DEFAULT_TZ).date()
    logger.debug('rating analysis successfully')

    cache_object.web = 2
    href = anime_element.xpath(r'./h2/a')[0].get('href')
    cache_object.webId = int(ANIME_PATTERN.match(href).group(1))

    cache_object.picture = anime_element.xpath(r'.//a/img')[0].get('src')

    return cache_object


def handle_anime_list(root) -> list[CacheData]:
    cache_list: list[CacheData] = []

    for anime_element in root.xpath(r'//div[@class="l-searchPageRanking_list"]/div[@class="l-searchPageRanking_unit"]'):
        cache_list.append(handle_anime(anime_element))

    return cache_list


@AnikoreSpider.route(r'www.anikore.jp/chronicle/\d+/.+/$', regex=True)
def handle_chronicle(response: Response) -> list[Request]:
    root = etree.HTML(response.text)

    cache_list: list[CacheData] = handle_anime_list(root)

    with SessionFactory() as session:
        session.add_all([cache_object.to_orm() for cache_object in cache_list])
        session.commit()
    logger.info(f'{len(cache_list)} add successfully')

    url_list: list[str] = []
    url_list_element: list = root.xpath(r'//section[@class="l-searchPaginate"]/span[preceding-sibling::span[@class="current"] and position() < last()]')
    for url_element in url_list_element:
        url_list.append(url_element.xpath(r'./a')[0].get('href'))

    return [Request('GET', 'https://www.anikore.jp' + url) for url in url_list]


@AnikoreSpider.route(r'www.anikore.jp/chronicle/\d+/.+/page:\d+', regex=True)
def handle_following_chronicle(response: Response):
    root = etree.HTML(response.text)

    cache_list: list[CacheData] = handle_anime_list(root)

    with SessionFactory() as session:
        session.add_all([cache_object.to_orm() for cache_object in cache_list])
        session.commit()
    logger.info(f'{len(cache_list)} add successfully')


if __name__ == '__main__':
    import logging

    logging.basicConfig(level=logging.DEBUG)

    logging.getLogger('httpcore').setLevel(logging.WARNING)
    logging.getLogger('httpx').setLevel(logging.WARNING)

    from frame.control import Control

    control = Control()
    control.add(AnikoreSpider)

    control.start()
