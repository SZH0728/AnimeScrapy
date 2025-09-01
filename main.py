# -*- coding:utf-8 -*-
# AUTHOR: Sun

from os import name, getenv
import logging

from pytz import timezone

from frame.control import Control as SpiderControl
from scheduler.schedule import Schedule, RunType, Every
from summarize.collect import Collect
from picture.control import Control as PictureControl
from picture.control import Config, Task

from spider.Bagumi import BagumiSpider
from spider.MAL import MALSpider
from spider.AniDB import AniDBSpider

tz = timezone('Asia/Shanghai')
schedule: Schedule = Schedule(tz)

formatter = logging.Formatter('%(asctime)s [%(levelname)s] %(filename)s:%(lineno)d %(funcName)s() [Thread-%(thread)d]: %(message)s')

console = logging.StreamHandler()
console.setLevel(logging.DEBUG)
console.setFormatter(formatter)

if name == 'nt':
    file = logging.FileHandler('log.txt', encoding='utf-8')
elif name == 'posix':
    file = logging.FileHandler(getenv('LOG_PATH'), encoding='utf-8')
else:
    raise Exception('Unknown OS')
file.setLevel(logging.WARNING)
file.setFormatter(formatter)

logging.basicConfig(handlers=[console, file], level=logging.DEBUG)
logging.getLogger('httpcore').setLevel(logging.WARNING)
logging.getLogger('httpx').setLevel(logging.WARNING)


@schedule.repeat(Every().hour(2))
def task():
    spider_control: SpiderControl = SpiderControl()

    spider_control.add(BagumiSpider)
    spider_control.add(MALSpider)
    spider_control.add(AniDBSpider)

    spider_control.start()

    collect = Collect()
    pictures: list[tuple[str, str]] = collect.main()

    config: Config = Config()
    config.REQUEST.USER_AGENT = 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/123.0.0.0 Safari/537.36'

    if name == 'nt':
        config.SAVE.DEFAULT_PATH = r'./examples'
    elif name == 'posix':
        # TODO: environment variable
        config.SAVE.DEFAULT_PATH = getenv('PICTURE_PATH')
    else:
        raise Exception('Unknown OS')

    picture_control: PictureControl = PictureControl(config)
    picture_control.add_tasks([Task(url=url, name=uid) for uid, url in pictures])
    picture_control.main()

if __name__ == '__main__':
    #TODO: 切换调试与部署模式

    schedule.loop(RunType.BLOCK)
    # from time import sleep
    #
    # task()
    # sleep(3600)
