# -*- coding:utf-8 -*-
# AUTHOR: Sun

from asyncio import Queue, QueueShutDown, sleep


class Bridge[T, S]:
    def __init__(self):
        self._channel_A_to_B: Queue[T | None] = Queue()
        self._channel_B_to_A: Queue[S | None] = Queue()

        self.A = Client(self._channel_A_to_B, self._channel_B_to_A)
        self.B = Client(self._channel_B_to_A, self._channel_A_to_B)

    async def stop(self):
        await self._channel_A_to_B.put(None)
        await self._channel_B_to_A.put(None)


class Client[T, S]:
    def __init__(self, send_channel: Queue[T], receive_channel: Queue[S]):
        self._send_channel = send_channel
        self._receive_channel = receive_channel

    def put(self, msg: T) -> bool:
        try:
            self._send_channel.put_nowait(msg)
        except QueueShutDown:
            return False

        return True

    async def get(self) -> S | None:
        for i in range(120):
            if not self._receive_channel.empty():
                break
            await sleep(1)
        else:
            return None

        return self._receive_channel.get_nowait()

    def is_empty(self) -> bool:
        return self._receive_channel.empty()


if __name__ == '__main__':
    pass
