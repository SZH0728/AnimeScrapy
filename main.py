# -*- coding:utf-8 -*-
# AUTHOR: Sun

from os import name, getenv

from pytz import timezone

from scheduler.schedule import Schedule, RunType, Every
from spider.main import main
from summarize.collect import Collect
from picture.control import Control, Config, Task

tz = timezone('Asia/Shanghai')
schedule: Schedule = Schedule(tz)

@schedule.repeat(Every().hour(2))
def task():
    main()

    collect = Collect()
    pictures: list[tuple[str, str]] = collect.main()

    config: Config = Config()
    config.REQUEST.DEFAULT_REQUEST_HEADERS = {
        'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,image/apng,*/*;q=0.8',
        'Accept-Language': 'zh-CN,zh;q=0.9,en-US;q=0.8,en;q=0.7',
        'Accept-Encoding': 'gzip, deflate, br',
        'Connection': 'keep-alive',
        'Upgrade-Insecure-Requests': '1',
        'Cache-Control': 'max-age=0'
    }
    config.REQUEST.USER_AGENT = 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/123.0.0.0 Safari/537.36'

    if name == 'nt':
        config.SAVE.DEFAULT_PATH = r'./examples'
    elif name == 'posix':
        # TODO: environment variable
        config.SAVE.DEFAULT_PATH = getenv('PICTURE_PATH')

    control: Control = Control(config)
    control.add_tasks([Task(url=url, name=uid) for uid, url in pictures])
    control.main()

if __name__ == '__main__':
    schedule.loop(RunType.BLOCK)
