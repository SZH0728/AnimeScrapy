# -*- coding:utf-8 -*-
# AUTHOR: Sun

from threading import Thread
from asyncio import gather, run, sleep, create_task
from logging import getLogger

from frame.request import Requester
from frame.bridge import Bridge
from frame.handle import Spider, MethodDict, Handle
from frame.counter import AsyncCounter

logger = getLogger(__name__)


class Manager(object):
    def __init__(self, spider: Spider):
        self.bridge = Bridge()

        self.spider: Spider = spider
        methods: MethodDict = spider.construct()

        self.counter = AsyncCounter(len(self.spider.config.HANDLE.INIT_URL))

        self.handle = Handle(self.bridge.A, self.spider.config, self.counter, methods)
        self.request = Requester(self.bridge.B, self.spider.config)

    def loop(self):
        run(self.main())

    def start(self) -> Thread:
        thread: Thread = Thread(target=self.loop)
        thread.start()
        logger.info(f'Start spider: {self.spider.__class__.__name__}')
        return thread

    async def main(self):
        logger.debug(f'Starting spider: {self.spider.__class__.__name__} in thread ')

        try:
            handle_task = create_task(self.handle.loop())
            request_task = create_task(self.request.loop())

            while await self.counter.value() != 0:
                await sleep(1)

            await self.bridge.stop()

            await gather(handle_task, request_task)
        except Exception as e:
            logger.error(f'An error occurred: {e}', exc_info=True)


class Control(object):
    def __init__(self):
        self.managers: list[Manager] = []

    def add(self, spider: Spider):
        logger.info(f'Add spider: {spider.__class__.__name__}')
        self.managers.append(Manager(spider))

    def start(self):
        threads: list[Thread] = []

        logger.info('Starting spider...')
        for manager in self.managers:
            threads.append(manager.start())

        logger.info('Spider started, waiting...')
        for thread in threads:
            thread.join()

        logger.info('Spider finished')


if __name__ == '__main__':
    pass
