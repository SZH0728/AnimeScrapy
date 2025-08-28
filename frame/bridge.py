# -*- coding:utf-8 -*-
# AUTHOR: Sun

"""
@file bridge.py
@brief 异步队列桥接模块
@details 提供一个基于异步队列的双向通信桥接实现，用于在两个客户端之间进行异步数据传输
"""

from asyncio import Queue, QueueFull, QueueEmpty, QueueShutDown
from asyncio import sleep
from logging import getLogger

logger = getLogger(__name__)


QUEUE_MAX_WAIT_TIME = 120

class Bridge[T, S]:
    """
    @brief 异步队列桥接类
    @details 创建一个连接两个客户端的双向通信桥接，使用泛型支持不同类型的数据传输
    """
    def __init__(self):
        """
        @brief 初始化桥接对象
        @details 创建两个异步队列用于双向通信，并初始化两个客户端
        """
        self._channel_A_to_B: Queue[T | None] = Queue()
        self._channel_B_to_A: Queue[S | None] = Queue()

        self.A = Client(self._channel_A_to_B, self._channel_B_to_A)
        self.B = Client(self._channel_B_to_A, self._channel_A_to_B)

    async def stop(self):
        """
        @brief 停止桥接通信
        @details 向两个通信通道发送停止信号(None)，通知客户端停止接收数据
        """
        for i in (self._channel_A_to_B, self._channel_B_to_A):
            try:
                await i.put(None)
            except QueueShutDown:
                logger.warning(f'Queue has been shutdown', exc_info=True)


class Client[T, S]:
    """
    @brief 客户端通信类
    @details 提供向通道发送数据和从通道接收数据的方法，支持同步和异步操作
    """
    def __init__(self, send_channel: Queue[T], receive_channel: Queue[S]):
        """
        @brief 初始化客户端
        @param send_channel 发送数据的通道
        @param receive_channel 接收数据的通道
        """
        self._send_channel = send_channel
        self._receive_channel = receive_channel

    def put_nowait(self, msg: T) -> bool:
        """
        @brief 立即发送消息
        @details 尝试立即将消息放入发送队列，如果队列已满或已关闭则返回False
        @param msg 要发送的消息
        @return 发送成功返回True，失败返回False
        """
        try:
            self._send_channel.put_nowait(msg)
        except (QueueFull, QueueShutDown):
            logger.warning(f'Queue put error', exc_info=True)
            return False

        return True

    async def put(self, msg: T) -> bool:
        """
        @brief 异步发送消息
        @details 等待队列有空间后发送消息，如果等待超时则返回False
        @param msg 要发送的消息
        @return 发送成功返回True，失败返回False
        """
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
        """
        @brief 立即获取消息
        @details 尝试立即从接收队列获取消息，如果队列为空或已关闭则返回None
        @return 成功获取消息则返回消息内容，否则返回None
        """
        try:
            return self._receive_channel.get_nowait()
        except (QueueEmpty, QueueShutDown):
            logger.warning(f'Queue get error', exc_info=True)
            return None

    async def get(self) -> S | None:
        """
        @brief 异步获取消息
        @details 等待队列有数据后获取消息，如果等待超时则返回None
        @return 成功获取消息则返回消息内容，否则返回None
        """
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
        """
        @brief 检查接收队列是否为空
        @return 接收队列为空返回True，否则返回False
        """
        return self._receive_channel.empty()

    def receive_is_full(self) -> bool:
        """
        @brief 检查接收队列是否已满
        @return 接收队列已满返回True，否则返回False
        """
        return self._receive_channel.full()

    def send_is_empty(self) -> bool:
        """
        @brief 检查发送队列是否为空
        @return 发送队列为空返回True，否则返回False
        """
        return self._send_channel.empty()

    def send_is_full(self) -> bool:
        """
        @brief 检查发送队列是否已满
        @return 发送队列已满返回True，否则返回False
        """
        return self._send_channel.full()


if __name__ == '__main__':
    pass