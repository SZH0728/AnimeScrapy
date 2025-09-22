# -*- coding:utf-8 -*-
# AUTHOR: Sun

from datetime import date, datetime
from logging import getLogger

from httpx import Request, Response
from lxml import etree
from re import compile

from frame.handle import Spider
from database.model import Cache, SessionFactory
from database.data import CacheData, Season, DEFAULT_TZ


logger = getLogger(__name__)
ANIME_ID_PATTERN = compile(r'/anime/(\d+)')
ANIME_QUERY_ID_PATTERN = compile(r'[&?]aid=(\d+)')

AniDBAPISpider = Spider()

AniDBAPISpider.config.REQUEST.USER_AGENT = 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/139.0.0.0 Safari/537.36'
AniDBAPISpider.config.REQUEST.DEFAULT_REQUEST_HEADERS = {
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
AniDBAPISpider.config.REQUEST.DOWNLOAD_DELAY = 300

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

AniDBAPISpider.config.HANDLE.INIT_URL_FUNCTION = init_request


@AniDBAPISpider.route('anidb.net/anime/season/')
def handle_season(response: Response)  -> list[Request]:
    root = etree.HTML(response.text)

    following: list[str] = []
    for a_element in root.xpath(r'//div[@class="g_bubblewrap g_bubble container"]/div/div/a'):
        following.append(a_element.get('href'))

    url_template: str = 'http://api.anidb.net:9001/httpapi?client=animescrapy&clientver=1&protover=1&request=anime&aid={}'
    return [Request('GET', url_template.format(ANIME_ID_PATTERN.match(url).group(1))) for url in following]

@AniDBAPISpider.route('api.anidb.net/httpapi')
def handle_detail(response: Response):
    cache_object: CacheData = CacheData()

    root = etree.fromstring(response.content)

    title_dict: dict[str, str] = {}
    for title in root.xpath(r'./titles/title'):
        title_dict[title.get('{http://www.w3.org/XML/1998/namespace}lang')] = title.text.strip()

    if 'ja' in title_dict.keys():
        cache_object.name = title_dict['ja']
    else:
        cache_object.name = root.xpath('./titles/title[@type="main"]')[0].text.strip()

    cache_object.translation = None
    for language in ('zh-Hans', 'zh-Hant', 'en'):
        if language in title_dict.keys():
            cache_object.translation = title_dict[language]
            break

    cache_object.all_data = list(title_dict.values())
    logger.debug('name analysis successfully')

    time: str = root.xpath('./startdate')[0].text.strip()
    key: int = len(time.split('-'))
    if key == 3:
        release_date: date = datetime.strptime(time, '%Y-%m-%d').date()
    elif key == 2:
        release_date: date = datetime.strptime(time, '%Y-%m').date()
    elif key == 1:
        release_date: date = datetime.strptime(time, '%Y').date()
    else:
        raise ValueError(f'Invalid date: {time}')

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

    description = root.xpath('./description')
    if description:
        cache_object.description = description[0].text.strip()
    else:
        cache_object.description = ''
    cache_object.tag = []
    for tag in root.xpath('./tags/tag/name'):
        cache_object.tag.append(tag.text.strip())
    logger.debug('base information analysis successfully')

    rating = root.xpath('./ratings/permanent')
    if rating:
        cache_object.score = float(rating[0].text.strip())
        cache_object.vote = int(rating[0].get('count').strip())
        logger.debug('rating analysis successfully')
    else:
        cache_object.score = 0
        cache_object.vote = 0
        logger.debug('no rating data found')

    cache_object.date = datetime.now(tz=DEFAULT_TZ).date()

    cache_object.web = 3
    cache_object.webId = ANIME_QUERY_ID_PATTERN.search(response.url.query.decode('utf-8')).group(1)

    picture = root.xpath(r'./picture')[0].text.strip()
    cache_object.picture = f'https://cdn-eu.anidb.net/images/main/{picture}'

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
    control.add(AniDBAPISpider)

    control.start()
