# -*- coding:utf-8 -*-
# AUTHOR: Sun

from pathlib import Path
from logging import getLogger

from picture.config import Config, SaveConfig
from picture.bridge import Receive, Package, Task

logger = getLogger(__name__)


class Save(object):
    """
    @brief 用于保存图片数据到本地文件系统
    """

    def __init__(self, queue: Receive[Package | None], config: Config):
        """
        @brief 初始化 Save 实例

        @param queue 接收 Package 数据的队列
        @param config 配置对象，包含保存相关的配置信息
        """
        self.config: SaveConfig = config.SAVE
        self._queue: Receive[Package | None] = queue

    async def loop(self):
        """
        @brief 持续从队列中接收并保存图片数据，直到接收到 None 为止

        该方法会持续运行，从 `self._queue` 中接收 `Package` 对象，
        并调用 handle_save 方法将数据保存到文件系统中。
        当接收到 `None` 时，循环结束并记录日志。
        """
        while True:
            package: Package | None = await self._queue.receive()

            if package is None:
                logger.info('Save loop stop')
                break

            logger.debug(f'Save file from {package.task.url}')
            self.handle_save(package)
            logger.debug(f'Save file successfully')

    def handle_save(self, package: Package):
        """
        @brief 将 Package 中的数据保存到文件系统中

        @param package 包含待保存数据和元信息的 Package 对象
        """
        path = self.handle_path(package)
        path.parents[0].mkdir(parents=True, exist_ok=True)

        logger.debug(f'Save file to {path}')
        with path.open('wb') as f:
            f.write(package.data)

    def handle_path(self, package: Package) -> Path:
        """
        @brief 根据 Package 中的信息生成文件保存路径

        @param package 包含任务信息和数据的 Package 对象
        @return 生成的文件路径
        """
        task: Task = package.task

        path = task.path if task.path else self.config.DEFAULT_PATH
        name = task.name if task.name else package.name
        formate = task.format if task.format else ''
        formate = formate if formate else self.config.DEFAULT_FORMATE
        formate = formate if formate else package.format

        file_name = f'{name}.{formate}' if formate else name

        return Path(path) / file_name


if __name__ == '__main__':
    pass
