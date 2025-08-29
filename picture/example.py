# -*- coding:utf-8 -*-
# AUTHOR: Sun

import logging
from json import load

from picture.config import Config
from picture.control import Control
from picture.bridge import Task

logging.basicConfig(level=logging.DEBUG)

logging.getLogger('httpcore').setLevel(logging.WARNING)
logging.getLogger('httpx').setLevel(logging.WARNING)


config = Config()
config.REQUEST.DEFAULT_REQUEST_HEADERS = {
    'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,image/apng,*/*;q=0.8',
    'Accept-Language': 'zh-CN,zh;q=0.9,en-US;q=0.8,en;q=0.7',
    'Accept-Encoding': 'gzip, deflate, br',
    'Connection': 'keep-alive',
    'Upgrade-Insecure-Requests': '1',
    'Cache-Control': 'max-age=0'
}
config.REQUEST.USER_AGENT = 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/123.0.0.0 Safari/537.36'

config.SAVE.DEFAULT_PATH = r'./examples'

control = Control(config)

with open('example.json', encoding='utf-8') as f:
    data = load(f)

pictures: list[Task] = []
for i in data:
    for item in i['items']:
        pictures.append(Task(item['images']['small']))

control.add_tasks(pictures)
control.main()


if __name__ == '__main__':
    pass
