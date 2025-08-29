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
    def __init__(self, config: Config):
        self.config: Config = config

        self._bridge: Bridge = Bridge()
        self._send: Send[Task | None] = self._bridge.send

        self._requester: Requester = Requester(self._bridge.middle, self.config)
        self._save: Save = Save(self._bridge.receive, self.config)

    async def loop(self):
        logger.debug('start loop...')
        try:
            request_loop = create_task(self._requester.loop())
            save_loop = create_task(self._save.loop())

            await gather(request_loop, save_loop)
        except Exception as e:
            logger.error(f'An error occurred in loop: {e}', exc_info=True)

    def main(self):
        self._send.send_nowait(None)
        logger.info(f"picture download starting...")
        run(self.loop())

    def add(self, task: Task):
        logger.debug(f"add task: {task.url}")
        self._send.send_nowait(task)

    def add_tasks(self, tasks: Iterable[Task]):
        logger.debug(f"add tasks: {len(tuple(task for task in tasks))}")
        for task in tasks:
            self._send.send_nowait(task)

if __name__ == '__main__':
    pass
