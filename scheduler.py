# -*- coding:utf-8 -*-
# AUTHOR: SUN
from logging import getLogger
from multiprocessing import Process
from typing import Callable

from schedule import every, repeat
from scrapy.crawler import CrawlerProcess
from scrapy.utils.log import configure_logging
from scrapy.utils.project import get_project_settings

from AnimeScrapy.spiders import *
from dbmanager import Session, Detail

configure_logging(get_project_settings())
logger = getLogger(__name__)

SPIDER = (
    aniDB.AnidbSpider,
    Anikore.AnikoreSpider,
    Bangumi.BangumiSpider,
    MyAnimeList.MyanimelistSpider
)


def catch_exception(function: Callable):
    def wrapper(*args, **kwargs):
        try:
            result = function(*args, **kwargs)
        except Exception as e:
            logger.error(f'An error occurred in {function.__name__}: {e}', exc_info=True)
        else:
            return result

    return wrapper


def start_spider():
    settings = get_project_settings()
    crawler = CrawlerProcess(settings)
    for i in SPIDER:
        crawler.crawl(i)
    crawler.start()


@repeat(every().day.at("20:00", "Asia/Shanghai"))
@catch_exception
def spider():
    spider_process = Process(target=start_spider)
    spider_process.start()


@repeat(every().day.at("04:00", "Asia/Shanghai"))
@catch_exception
def anime():
    session = Session()
    result = session.query(Detail).filter(Detail.webId is not None)
    name = [
        *[i.name for i in result],
        *[i.translation for i in result],
        *[alia for i in result if i for alia in i.alias]
    ]
    name = [i for i in name if i]
    with open('anime.txt', 'w', encoding='utf-8') as f:
        f.write('\n'.join(name))


if __name__ == '__main__':
    from schedule import run_all

    run_all()
