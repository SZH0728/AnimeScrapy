# -*- coding:utf-8 -*-
# AUTHOR: Sun

from asyncio import Queue, QueueFull, QueueEmpty, QueueShutDown
from asyncio import sleep
from logging import getLogger

logger = getLogger(__name__)


QUEUE_MAX_WAIT_TIME = 120

class Bridge[T, S]:
    def __init__(self):
        self._channel_A_to_B: Queue[T | None] = Queue()
        self._channel_B_to_A: Queue[S | None] = Queue()

        self.A = Client(self._channel_A_to_B, self._channel_B_to_A)
        self.B = Client(self._channel_B_to_A, self._channel_A_to_B)

    async def stop(self):
        for i in (self._channel_A_to_B, self._channel_B_to_A):
            try:
                await i.put(None)
            except QueueShutDown:
                logger.warning(f'Queue has been shutdown', exc_info=True)


class Client[T, S]:
    def __init__(self, send_channel: Queue[T], receive_channel: Queue[S]):
        self._send_channel = send_channel
        self._receive_channel = receive_channel

    def put_nowait(self, msg: T) -> bool:
        try:
            self._send_channel.put_nowait(msg)
        except (QueueFull, QueueShutDown):
            logger.warning(f'Queue put error', exc_info=True)
            return False

        return True

    async def put(self, msg: T) -> bool:
        for i in range(QUEUE_MAX_WAIT_TIME):
            if not self._send_channel.full():
                break
            await sleep(1)
        else:
            return False

        try:
            self._send_channel.put_nowait(msg)
        except QueueShutDown:
            logger.warning(f'Queue has been shutdown', exc_info=True)
            return False

        return True

    def get_nowait(self) -> S | None:
        try:
            return self._receive_channel.get_nowait()
        except (QueueEmpty, QueueShutDown):
            logger.warning(f'Queue get error', exc_info=True)
            return None

    async def get(self) -> S | None:
        for i in range(QUEUE_MAX_WAIT_TIME):
            if not self._receive_channel.empty():
                break
            await sleep(1)
        else:
            return None

        try:
            return self._receive_channel.get_nowait()
        except QueueShutDown:
            logger.warning(f'Queue has been shutdown', exc_info=True)
            return None

    def receive_is_empty(self) -> bool:
        return self._receive_channel.empty()

    def receive_is_full(self) -> bool:
        return self._receive_channel.full()

    def send_is_empty(self) -> bool:
        return self._send_channel.empty()

    def send_is_full(self) -> bool:
        return self._send_channel.full()


if __name__ == '__main__':
    pass
