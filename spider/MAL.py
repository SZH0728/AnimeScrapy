# -*- coding:utf-8 -*-
# AUTHOR: Sun

from datetime import date, datetime
from logging import getLogger
from re import compile

from httpx import Request, Response
from lxml import etree

from frame.handle import Spider
from database.model import Cache, SessionFactory
from database.data import CacheData, Season, DEFAULT_TZ


logger = getLogger(__name__)
TEST_DATE_FORMATE = compile(r'.+\s+\d{1,2},\s+\d{4}')
ANIME_PATTERN = compile(r'/anime/(\d+)/.*')

MALSpider = Spider()

MALSpider.config.REQUEST.USER_AGENT = 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/139.0.0.0 Safari/537.36'
MALSpider.config.REQUEST.DEFAULT_REQUEST_HEADERS = headers = {
    'accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.7',
    'accept-language': 'zh-CN,zh;q=0.9,en;q=0.8,zh-TW;q=0.7',
    'dnt': '1',
    'priority': 'u=0, i',
    'sec-ch-ua': '"Not;A=Brand";v="99", "Google Chrome";v="139", "Chromium";v="139"',
    'sec-ch-ua-mobile': '?0',
    'sec-ch-ua-platform': '"Windows"',
    'sec-fetch-dest': 'document',
    'sec-fetch-mode': 'navigate',
    'sec-fetch-site': 'cross-site',
    'sec-fetch-user': '?1',
    'upgrade-insecure-requests': '1',
}
MALSpider.config.REQUEST.DOWNLOAD_DELAY = 5

MALSpider.config.HANDLE.INIT_URL = Request('GET', 'https://myanimelist.net/anime/season')

@MALSpider.route('myanimelist.net/anime/season')
def handle_season(response: Response) -> list[Request]:
    root = etree.HTML(response.text)

    following: list[str] = []
    for a_element in root.xpath(r'//div[contains(@class, " seasonal-anime ")]//h2/a'):
        following.append(a_element.get('href'))

    return  [Request('GET', url) for url in following]


@MALSpider.route(r'myanimelist.net/anime/\d+/.+', regex=True)
def handle_detail(response: Response):
    cache_object: CacheData = CacheData()

    root = etree.HTML(response.text)

    name_bar = root.xpath(r'//div[@itemprop="name"]')[0]
    info_list = root.xpath(r'//div[@class="leftside"]')[0]

    name_title: str = name_bar.xpath(r'.//strong')[0].text.strip()
    name_translation: str = name_bar.xpath(r'./p')[0].text.strip() if name_bar.xpath(r'./p') else None

    name_list: list[str] = []
    name_element_list: list = info_list.xpath(r'./div[preceding-sibling::h2[text()="Alternative Titles"] and following-sibling::h2[text()="Information"]]')
    if name_element_list and name_element_list[-1].get('class') == 'js-alternative-titles hide':
        last_name_element = name_element_list.pop()
        name_element_list.extend(last_name_element.xpath(r'./div'))
    for name_element in name_element_list:
        language: str = name_element.xpath(r'./span')[0].text.strip()
        name: str = name_element.xpath('./span/following-sibling::text()')[0].strip()

        if 'Japanese' in language:
            cache_object.name = name

        name_list.append(name)

    cache_object.name = cache_object.name if cache_object.name else name_title
    cache_object.translation = name_translation
    cache_object.all_data = [cache_object.name, cache_object.translation]
    cache_object.all_data.extend(name_list)
    cache_object.all_data = list(set(i for i in cache_object.all_data if i))
    logger.debug('name analysis successfully')

    information_element_list: list = info_list.xpath(r'./div[preceding-sibling::h2[text()="Information"] and following-sibling::h2[text()="Statistics"]]')
    for information_element in information_element_list:
        key: str = information_element.xpath('./span')[0].text.strip()
        value: str = information_element.xpath('./span/following-sibling::text()')[0].strip()

        if 'Aired' in key:
            time_string: str = value.split(' to ')[0].strip()

            if TEST_DATE_FORMATE.match(time_string):
                release_date: date = datetime.strptime(time_string, '%b %d, %Y').date()
            else:
                release_date: date = datetime.strptime(time_string, '%b %Y').date()

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

            cache_object.time = release_date

            break
    logger.debug('time analysis successfully')

    cache_object.tag = []

    description_element = root.xpath(r'//p[@itemprop="description"]')[0]
    cache_object.description = description_element.xpath('string(.)')
    logger.debug('base information analysis successfully')

    rating_element = info_list.xpath(r'./div[@itemprop="aggregateRating"]')
    if rating_element:
        rating_element = rating_element[0]
        cache_object.score = float(rating_element.xpath(r'./span[@itemprop="ratingValue"]/text()')[0])
        cache_object.vote = int(rating_element.xpath(r'./span[@itemprop="ratingCount"]/text()')[0])
        logger.debug('rating analysis successfully')
    else:
        cache_object.score = 0
        cache_object.vote = 0
        logger.info(f'{cache_object.name} has no rating')
    cache_object.date = datetime.now(DEFAULT_TZ).date()

    cache_object.web = 4
    cache_object.webId = int(ANIME_PATTERN.match(response.url.path).group(1))

    cache_object.picture = root.xpath(r'//img[@itemprop="image"]')[0].get('data-src')

    cache: Cache = cache_object.to_orm()

    with SessionFactory() as session:
        session.add(cache)
        session.commit()
    logger.info(f'{cache_object.name} add successfully')


if __name__ == '__main__':
    import logging

    logging.basicConfig(level=logging.DEBUG)

    logging.getLogger('httpcore').setLevel(logging.WARNING)
    logging.getLogger('httpx').setLevel(logging.WARNING)

    from frame.control import Control

    control = Control()
    control.add(MALSpider)

    control.start()
