# -*- coding:utf-8 -*-
# AUTHOR: Sun

from frame.control import Control

from spider.bagumi import BagumiSpider


def main():
    control = Control()
    control.add(BagumiSpider)

    control.start()

if __name__ == '__main__':
    import logging

    logging.basicConfig(level=logging.DEBUG)

    logging.getLogger('httpcore').setLevel(logging.WARNING)
    logging.getLogger('httpx').setLevel(logging.WARNING)

    main()
