# -*- coding:utf-8 -*-
# AUTHOR: Sun

from time import sleep
import logging

from httpx import Request, Response

from frame.control import Control
from frame.handle import Spider

logging.basicConfig(level=logging.DEBUG)

logging.getLogger('httpcore').setLevel(logging.WARNING)
logging.getLogger('httpx').setLevel(logging.WARNING)

spider = Spider()
spider.config.HANDLE.INIT_URL = [Request('GET', 'http://127.0.0.1:5000/')]


@spider.route('127.0.0.1/')
def handle_index(response: Response):
    print(response.text)
    sleep(2)
    return [Request('GET', f'http://127.0.0.1:5000/{number}') for number in range(10)]

@spider.route(r'127.0.0.1/\d+', regex=True)
def handle_number(response: Response):
    print(response.text)
    return 123


control = Control()
control.add(spider)
control.start()

if __name__ == '__main__':
    pass
