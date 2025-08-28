# -*- coding:utf-8 -*-
# AUTHOR: Sun

"""
@file counter.py
@brief 异步计数器实现
@details 提供线程安全的异步计数器功能，支持原子性的增加、减少和获取值操作
"""

from asyncio import Lock


class AsyncCounter:
    """
    @brief 异步计数器类
    @details 使用asyncio.Lock保证异步环境下的线程安全计数器操作
    """
    
    def __init__(self, init=0):
        """
        @brief 初始化异步计数器
        @param init 计数器初始值，默认为0
        """
        self._value: int = init
        self._lock: Lock = Lock()

    async def increment(self, value: int = 1) -> int:
        """
        @brief 原子性地增加计数器值
        @param value 要增加的数值，默认为1
        @return 增加后的计数器值
        """
        async with self._lock:
            self._value += value
            return self._value

    async def decrement(self, value: int = 1) -> int:
        """
        @brief 原子性地减少计数器值
        @param value 要减少的数值，默认为1
        @return 减少后的计数器值
        """
        async with self._lock:
            self._value -= value
            return self._value

    async def value(self) -> int:
        """
        @brief 获取当前计数器值
        @return 当前计数器的值
        """
        async with self._lock:
            return self._value


if __name__ == '__main__':
    pass