# -*- coding:utf-8 -*-
# AUTHOR: Sun

from logging import getLogger
from dataclasses import dataclass
from asyncio import Queue, QueueFull, QueueEmpty, QueueShutDown
from time import sleep

logger = getLogger(__name__)


@dataclass
class Task(object):
    url: str
    path: str | None = None
    name: str | None = None
    format: str | None = None


@dataclass
class Package(object):
    task: Task
    data: bytes
    name: str
    format: str


class Bridge(object):
    def __init__(self):
        self._first: Queue[Task | None] = Queue()
        self._last: Queue[Package | None] = Queue()

        self.send = Send(self._first)
        self.receive = Receive(self._last)
        self.middle = Middle(self._last, self._first)


    def stop(self):
        while True:
            if not self._first.full():
                break

            sleep(10)

        try:
            self._first.put_nowait(None)
        except QueueShutDown:
            logger.warning('Queue has been shutdown', exc_info=True)


class Send[T]:
    def __init__(self, send: Queue[T]):
        self.__queue: Queue[T] = send

    async def send(self, msg: T) -> bool:
        try:
            await self.__queue.put(msg)
        except QueueShutDown:
            logger.warning(f'Queue has been shutdown', exc_info=True)
            return False

        return True

    def send_nowait(self, msg: T) -> bool:
        try:
            self.__queue.put_nowait(msg)
        except (QueueFull, QueueShutDown):
            logger.warning(f'Queue put error', exc_info=True)
            return False

        return True

    def is_send_full(self) -> bool:
        return self.__queue.full()

    def is_send_empty(self) -> bool:
        return self.__queue.empty()


class Receive[T]:
    def __init__(self, receive: Queue[T]):
        self.__queue: Queue[T] = receive

    async def receive(self) -> T | None:
        try:
            return await self.__queue.get()
        except QueueShutDown:
            logger.warning(f'Queue has been shutdown', exc_info=True)

        return None


    def receive_nowait(self) -> T | None:
        try:
            return self.__queue.get_nowait()
        except (QueueEmpty, QueueShutDown):
            logger.warning(f'Queue get error', exc_info=True)

        return None


    def is_receive_full(self) -> bool:
        return self.__queue.full()

    def is_receive_empty(self) -> bool:
        return self.__queue.empty()


class Middle[T, S](Send, Receive):
    def __init__(self, send: Queue[T], receive: Queue[S]):
        Send.__init__(self, send)
        Receive.__init__(self, receive)


if __name__ == '__main__':
    pass
