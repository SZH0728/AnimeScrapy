# -*- coding:utf-8 -*-
# AUTHOR: SUN
from multiprocessing import Process

from schedule import every, repeat
from scrapy.crawler import CrawlerProcess
from scrapy.utils.project import get_project_settings

from dbmanager import Session, Detail
from AnimeScrapy.spiders import *


SPIDER = (
    aniDB.AnidbSpider,
    Anikore.AnikoreSpider,
    Bangumi.BangumiSpider,
    MyAnimeList.MyanimelistSpider
)


def start_spider():
    settings = get_project_settings()
    crawler = CrawlerProcess(settings)
    for i in SPIDER:
        crawler.crawl(i)
    crawler.start()


@repeat(every().day.at("20:00", "Asia/Shanghai"))
def spider():
    spider_process = Process(target=start_spider)
    spider_process.start()


@repeat(every().day.at("04:00", "Asia/Shanghai"))
def anime():
    session = Session()
    result = session.query(Detail).filter(Detail.webId != None)
    name = [
        *[i.name for i in result],
        *[i.translation for i in result],
        *[alia for i in result for alia in i.alias]
    ]
    name = [i for i in name if i]
    with open('anime.txt', 'w', encoding='utf-8') as f:
        f.write('\n'.join(name))


if __name__ == '__main__':
    from schedule import run_all
    run_all()
