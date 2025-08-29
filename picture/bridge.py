# -*- coding:utf-8 -*-
# AUTHOR: Sun

from logging import getLogger
from dataclasses import dataclass
from asyncio import Queue, QueueFull, QueueEmpty, QueueShutDown
from time import sleep

logger = getLogger(__name__)


@dataclass
class Task(object):
    """
    @brief 数据类，表示一个下载任务
    
    @details 包含下载任务所需的基本信息，如URL、保存路径、文件名和格式
    """
    #: 资源的URL地址
    url: str
    #: 文件保存路径（可选）
    path: str | None = None
    #: 文件名称（可选）
    name: str | None = None
    #: 文件格式（可选）
    format: str | None = None


@dataclass
class Package(object):
    """
    @brief 数据类，表示一个已完成的下载包
    
    @details 包含下载任务、下载的数据以及相关元信息
    """
    #: 关联的下载任务
    task: Task
    #: 下载的数据内容
    data: bytes
    #: 文件名称
    name: str
    #: 文件格式
    format: str


class Bridge(object):
    """
    @brief 桥接类，用于连接下载器和保存器
    
    @details 管理任务队列和数据队列，提供发送、接收功能
    """
    def __init__(self):
        """
        @brief 初始化桥接对象
        
        @details 创建任务队列和数据队列，并初始化相关的发送、接收和中间处理对象
        """
        self._first: Queue[Task | None] = Queue()
        self._last: Queue[Package | None] = Queue()

        self.send = Send(self._first)
        self.receive = Receive(self._last)
        self.middle = Middle(self._last, self._first)

    def stop(self):
        """
        @brief 停止桥接器
        
        @details 等待队列有空间后发送停止信号
        """
        while True:
            if not self._first.full():
                break

            sleep(10)

        try:
            self._first.put_nowait(None)
        except QueueShutDown:
            logger.warning('Queue has been shutdown', exc_info=True)


class Send[T]:
    """
    @brief 发送类，用于向队列发送数据
    
    @tparam T 队列中数据的类型
    """
    def __init__(self, send: Queue[T]):
        """
        @brief 初始化发送对象
        
        @param send 要发送数据的队列
        """
        self.__queue: Queue[T] = send

    async def send(self, msg: T) -> bool:
        """
        @brief 异步发送消息到队列
        
        @param msg 要发送的消息
        @return bool 发送是否成功
        """
        try:
            await self.__queue.put(msg)
        except QueueShutDown:
            logger.warning(f'Queue has been shutdown', exc_info=True)
            return False

        return True

    def send_nowait(self, msg: T) -> bool:
        """
        @brief 立即发送消息到队列（非阻塞）
        
        @param msg 要发送的消息
        @return bool 发送是否成功
        """
        try:
            self.__queue.put_nowait(msg)
        except (QueueFull, QueueShutDown):
            logger.warning(f'Queue put error', exc_info=True)
            return False

        return True

    def is_send_full(self) -> bool:
        """
        @brief 检查发送队列是否已满
        
        @return bool 队列是否已满
        """
        return self.__queue.full()

    def is_send_empty(self) -> bool:
        """
        @brief 检查发送队列是否为空
        
        @return bool 队列是否为空
        """
        return self.__queue.empty()


class Receive[T]:
    """
    @brief 接收类，用于从队列接收数据
    
    @tparam T 队列中数据的类型
    """
    def __init__(self, receive: Queue[T]):
        """
        @brief 初始化接收对象
        
        @param receive 要接收数据的队列
        """
        self.__queue: Queue[T] = receive

    async def receive(self) -> T | None:
        """
        @brief 异步从队列接收数据
        
        @return T | None 接收到的数据，如果队列关闭则返回None
        """
        try:
            return await self.__queue.get()
        except QueueShutDown:
            logger.warning(f'Queue has been shutdown', exc_info=True)

        return None

    def receive_nowait(self) -> T | None:
        """
        @brief 立即从队列接收数据（非阻塞）
        
        @return T | None 接收到的数据，如果队列为空或关闭则返回None
        """
        try:
            return self.__queue.get_nowait()
        except (QueueEmpty, QueueShutDown):
            logger.warning(f'Queue get error', exc_info=True)

        return None

    def is_receive_full(self) -> bool:
        """
        @brief 检查接收队列是否已满
        
        @return bool 队列是否已满
        """
        return self.__queue.full()

    def is_receive_empty(self) -> bool:
        """
        @brief 检查接收队列是否为空
        
        @return bool 队列是否为空
        """
        return self.__queue.empty()


class Middle[T, S](Send, Receive):
    """
    @brief 中间处理类，继承自发送和接收类
    
    @tparam T 发送数据的类型
    @tparam S 接收数据的类型
    """
    def __init__(self, send: Queue[T], receive: Queue[S]):
        """
        @brief 初始化中间处理对象
        
        @param send 发送队列
        @param receive 接收队列
        """
        Send.__init__(self, send)
        Receive.__init__(self, receive)


if __name__ == '__main__':
    pass
