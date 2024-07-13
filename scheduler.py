# -*- coding:utf-8 -*-
# AUTHOR: SUN
from schedule import every, repeat, run_all
from scrapy.crawler import CrawlerProcess
from scrapy.utils.project import get_project_settings

from dbmanager import Session, Detail


SPIDER = ('aniDB', 'Anikore', 'Bangumi', 'MyAnimeList')


# @repeat(every().day.at("22:00", "Asia/Shanghai"))
# def spider():
#     settings = get_project_settings()
#     process = CrawlerProcess(settings)
#     for i in SPIDER:
#         process.crawl(i)
#     process.start()


@repeat(every().day.at("04:00", "Asia/Shanghai"))
def anime():
    session = Session()
    result = session.query(Detail).filter(Detail.webId != None)
    name = [
        *[i.name for i in result],
        *[i.translation for i in result],
        *[alia for i in result for alia in i.alias]
    ]
    with open('anime.txt', 'w') as f:
        f.write('\n'.join(name))


if __name__ == '__main__':
    run_all()
