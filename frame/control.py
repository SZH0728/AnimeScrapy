# -*- coding:utf-8 -*-
# AUTHOR: Sun

"""
@file control.py
@brief 爬虫控制器模块
@details 爬虫控制器模块，负责启动多个爬虫实例并等待它们完成
"""

from threading import Thread
from asyncio import gather, run, sleep, create_task
from logging import getLogger

from frame.request import Requester
from frame.bridge import Bridge
from frame.handle import Spider, MethodDict, Handle
from frame.counter import AsyncCounter

logger = getLogger(__name__)


class Manager(object):
    """
    @brief 管理单个爬虫的执行
    
    Manager类负责初始化和运行单个爬虫实例，包括创建请求处理器、
    处理器和它们之间的通信桥梁，并协调整个爬取过程
    """
    
    def __init__(self, spider: Spider):
        """!
        @brief 初始化Manager实例
        
        @param spider 爬虫实例
        """
        self.bridge = Bridge()

        self.spider: Spider = spider
        methods: MethodDict = spider.construct()

        if self.spider.config.HANDLE.INIT_URL:
            self.spider.config.HANDLE.INIT_URLS.append(self.spider.config.HANDLE.INIT_URL)

        self.counter = AsyncCounter(len(self.spider.config.HANDLE.INIT_URLS))

        self.handle = Handle(self.bridge.A, self.spider.config, self.counter, methods)
        self.request = Requester(self.bridge.B, self.spider.config)

    def loop(self):
        """!
        @brief 运行主事件循环
        
        在新的线程中启动asyncio事件循环来执行爬虫任务
        """
        run(self.main())

    def start(self) -> Thread:
        """!
        @brief 启动爬虫管理器
        
        @return Thread 启动的线程对象
        """
        thread: Thread = Thread(target=self.loop)
        thread.start()
        logger.info(f'Start spider: {self.spider.__class__.__name__}')
        return thread

    async def main(self):
        """!
        @brief 主异步处理函数
        
        协调处理任务和请求任务的执行，监控计数器直到所有任务完成
        """
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
    """!
    @brief 爬虫控制器
    
    Control类用于管理多个爬虫实例，可以同时运行多个不同的爬虫，
    并等待所有爬虫完成任务
    """
    
    def __init__(self):
        """!
        @brief 初始化控制器
        """
        self.managers: list[Manager] = []

    def add(self, spider: Spider):
        """!
        @brief 添加爬虫到控制器
        
        @param spider 爬虫实例
        """
        logger.info(f'Add spider: {spider.__class__.__name__}')
        self.managers.append(Manager(spider))

    def start(self):
        """!
        @brief 启动所有已添加的爬虫
        
        依次启动所有已添加的爬虫，并等待它们全部完成
        """
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
