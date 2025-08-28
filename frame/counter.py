# -*- coding:utf-8 -*-
# AUTHOR: Sun

from asyncio import Lock


class AsyncCounter:
    def __init__(self, init=0):
        self._value: int = init
        self._lock: Lock = Lock()

    async def increment(self, value: int = 1) -> int:
        async with self._lock:
            self._value += value
            return self._value

    async def decrement(self, value: int = 1) -> int:
        async with self._lock:
            self._value -= value
            return self._value

    async def value(self)  -> int:
        async with self._lock:
            return self._value


if __name__ == '__main__':
    pass
