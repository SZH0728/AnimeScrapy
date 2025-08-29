# -*- coding:utf-8 -*-
# AUTHOR: Sun

from pathlib import Path
from logging import getLogger

from picture.config import Config, SaveConfig
from picture.bridge import Receive, Package, Task

logger = getLogger(__name__)


class Save(object):
    def __init__(self, queue: Receive[Package | None], config: Config):
        self.config: SaveConfig = config.SAVE
        self._queue: Receive[Package | None] = queue

    async def loop(self):
        while True:
            package: Package | None = await self._queue.receive()

            if package is None:
                logger.info('Save loop stop')
                break

            logger.debug(f'Save file from {package.task.url}')
            self.handle_save(package)
            logger.debug(f'Save file successfully')


    def handle_save(self, package: Package):
        path = self.handle_path(package)
        path.parents[0].mkdir(parents=True, exist_ok=True)

        logger.debug(f'Save file to {path}')
        with path.open('wb') as f:
            f.write(package.data)

    def handle_path(self, package: Package) -> Path:
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
