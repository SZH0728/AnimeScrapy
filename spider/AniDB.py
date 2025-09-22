# -*- coding:utf-8 -*-
# AUTHOR: Sun

from datetime import date, datetime
from logging import getLogger
from enum import Enum

from httpx import Request, Response
from lxml import etree
from re import compile

from frame.handle import Spider
from database.model import Cache, SessionFactory
from database.data import CacheData, Season, DEFAULT_TZ


logger = getLogger(__name__)
ANIME_PATTERN = compile(r'/anime/(\d+)')


class NameType(Enum):
    UNKNOWN = 'Unknown'
    MAIN = 'Main Title'
    OFFICIAL = 'Official Title'
    SYNONYM = 'Synonym'


AniDBSpider = Spider()

AniDBSpider.config.REQUEST.USER_AGENT = 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/139.0.0.0 Safari/537.36'
AniDBSpider.config.REQUEST.DEFAULT_REQUEST_HEADERS = {
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
AniDBSpider.config.REQUEST.DOWNLOAD_DELAY = 300

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

    return [Request('GET', f'https://anidb.net/anime/season/{today.year}/{season}/?do=calendar&h=1')]

AniDBSpider.config.HANDLE.INIT_URL_FUNCTION = init_request


@AniDBSpider.route('anidb.net/anime/season/')
def handle_season(response: Response)  -> list[Request]:
    root = etree.HTML(response.text)

    following: list[str] = []
    for a_element in root.xpath(r'//div[@class="g_bubblewrap g_bubble container"]/div/div/a'):
        following.append(a_element.get('href'))

    return [Request('GET', 'https://anidb.net' + url) for url in following]


@AniDBSpider.route(r'anidb.net/anime/\d+', regex=True)
def handle_detail(response: Response):
    cache_object: CacheData = CacheData()

    root = etree.HTML(response.text)

    information_table = root.xpath(r'//div[@id="tabbed_pane"]')[0]

    name_dict: dict[str | None, str] = {}
    name_table = information_table.xpath(r'.//div[@id="tab_2_pane"]//tr')
    for tr_element in name_table:
        key: NameType = NameType.UNKNOWN
        if 'romaji' in tr_element.get('class'):
            key = NameType.MAIN
        elif 'official' in tr_element.get('class'):
            key = NameType.OFFICIAL
        elif 'syn' in tr_element.get('class'):
            key = NameType.SYNONYM

        if key == NameType.UNKNOWN:
            continue

        if key == NameType.SYNONYM:
            continue

        language: str | None = None
        if key == NameType.OFFICIAL:
            icon_element = tr_element.xpath(r'.//span[contains(@class, "i_icon") and position() = 1]/span')[0]
            language = icon_element.text.strip()

        name_string: str = ''
        if key == NameType.MAIN:
            name_string: str = tr_element.xpath(r'.//span[@itemprop="name"]')[0].text.strip()
        elif key == NameType.OFFICIAL or key == NameType.SYNONYM:
            name_string: str = tr_element.xpath(r'.//label')[0].text.strip()
        name_dict[language] = name_string

    if 'ja' in name_dict.keys():
        cache_object.name = name_dict['ja']
    else:
        cache_object.name = name_dict[None]

    cache_object.translation = None
    for language in ('zh-Hans', 'zh-Hant', 'en'):
        if language in name_dict.keys():
            cache_object.translation = name_dict[language]
            break

    cache_object.all_data = list(name_dict.values())
    logger.debug('name analysis successfully')

    cache_object.description = root.xpath(r'string(//div[@itemprop="description"])').strip()

    cache_object.tag = []
    detail_table: list = information_table.xpath(r'//div[@id="tab_1_pane"]//tr')
    for tr_element in detail_table:
        class_type: str = tr_element.get('class').strip()

        if 'year' in class_type:
            if tr_element.xpath(r'.//span[@itemprop="startDate"]'):
                time_element = tr_element.xpath(r'.//span[@itemprop="startDate"]')[0]
            elif tr_element.xpath(r'.//span[@itemprop="datePublished"]'):
                time_element = tr_element.xpath(r'.//span[@itemprop="datePublished"]')[0]
            else:
                logger.warning(f'time element not found in {response.url}')
                continue

            time: str = time_element.get('content').strip()
            release_date: date = datetime.strptime(time, '%Y-%m-%d').date()

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
            logger.debug('time analysis successfully')

        elif 'tags' in class_type:
            tag_elements: list = tr_element.xpath(r'.//span[@class="tagname"]')
            for tag_element in tag_elements:
                cache_object.tag.append(tag_element.text)

        elif 'rating' in class_type:
            if 'tmprating' in class_type:
                continue

            if not tr_element.xpath(r'.//*[@itemprop="ratingValue"]'):
                cache_object.score = 0
                cache_object.vote = 0
                continue

            score_element = tr_element.xpath(r'.//*[@itemprop="ratingValue"]')[0]
            vote_element = tr_element.xpath(r'.//span[@itemprop="ratingCount"]')[0]

            if score_element.text:
                cache_object.score = float(score_element.text)
            elif score_element.get('content'):
                cache_object.score = float(score_element.get('content'))
            else:
                cache_object.score = 0
            cache_object.vote = int(vote_element.get('content'))
            logger.debug('rating analysis successfully')
    logger.debug('base information analysis successfully')

    cache_object.date = datetime.now(tz=DEFAULT_TZ).date()

    cache_object.web = 3
    cache_object.webId = ANIME_PATTERN.match(response.url.path).group(1)

    cache_object.picture = root.xpath(r'//meta[@property="og:image"]')[0].get('content')

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
    control.add(AniDBSpider)

    control.start()
