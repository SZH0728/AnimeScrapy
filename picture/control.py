# -*- coding:utf-8 -*-
# AUTHOR: Sun

from typing import Iterable
from logging import getLogger
from asyncio import gather, run, create_task

from picture.config import Config
from picture.request import Requester
from picture.save import Save
from picture.bridge import Task, Bridge, Send

logger = getLogger(__name__)


class Control(object):
    """
    @brief 控制模块主类，负责协调图片下载请求和保存过程
    """

    def __init__(self, config: Config):
        """
        @brief 初始化Control实例

        @param config 配置对象，包含下载相关配置信息
        """
        self.config: Config = config

        self._bridge: Bridge = Bridge()
        self._send: Send[Task | None] = self._bridge.send

        self._requester: Requester = Requester(self._bridge.middle, self.config)
        self._save: Save = Save(self._bridge.receive, self.config)

    async def loop(self):
        """
        @brief 异步运行主循环，同时执行请求和保存任务

        @details 启动请求器和保存器的异步任务，并等待它们完成
        """
        logger.debug('start loop...')
        try:
            request_loop = create_task(self._requester.loop())
            save_loop = create_task(self._save.loop())

            await gather(request_loop, save_loop)
        except Exception as e:
            logger.error(f'An error occurred in loop: {e}', exc_info=True)

    def main(self):
        """
        @brief 主函数入口，启动图片下载流程

        @details 运行主循环
        """
        self._send.send_nowait(None)
        logger.info(f"picture download starting...")
        run(self.loop())

    def add(self, task: Task):
        """
        @brief 添加单个下载任务

        @param task 需要添加的下载任务
        """
        logger.debug(f"add task: {task.url}")
        self._send.send_nowait(task)

    def add_tasks(self, tasks: Iterable[Task]):
        """
        @brief 批量添加下载任务

        @param tasks 需要添加的下载任务集合
        """
        logger.debug(f"add tasks: {len(tuple(task for task in tasks))}")
        for task in tasks:
            self._send.send_nowait(task)

if __name__ == '__main__':
    pass
