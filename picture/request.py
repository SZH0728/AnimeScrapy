# -*- coding:utf-8 -*-
# AUTHOR: Sun

from logging import getLogger
from asyncio import Semaphore, create_task, gather
from asyncio import Task as CoroutineTask
from re import compile, Match

from httpx import AsyncClient, Response, HTTPError

from picture.bridge import Task, Package, Middle
from picture.config import Config, RequestConfig

logger = getLogger(__name__)
GET_MANE_FROM_URL = compile(r'/.*/(.*?)\.(.*)')


class ConcurrentControl(object):
    """
    @brief 并发控制类，用于控制请求的并发数量

    该类负责管理全局并发请求数量和每个域名的并发请求数量限制
    """

    def __init__(self, max_concurrent: int, max_concurrent_per_domain: int):
        """
        @brief 初始化并发控制器

        @param max_concurrent 全局最大并发请求数量
        @param max_concurrent_per_domain 每个域名的最大并发请求数量
        """
        self._max_concurrent: int = max_concurrent
        self._max_concurrent_per_domain: int = max_concurrent_per_domain

        self._concurrent_semaphore: Semaphore = Semaphore(max_concurrent)
        self._domain_semaphore: dict[str, Semaphore] = {}

    async def acquire(self, domain: str):
        """
        @brief 获取指定域名的并发许可

        @param domain 请求的目标域名
        """
        if domain not in self._domain_semaphore.keys():
            self._domain_semaphore[domain] = Semaphore(self._max_concurrent_per_domain)

        await self._concurrent_semaphore.acquire()
        domain_semaphore = self._domain_semaphore[domain]
        await domain_semaphore.acquire()

    async def release(self, domain: str):
        """
        @brief 释放指定域名的并发许可

        @param domain 请求的目标域名
        """
        domain_semaphore = self._domain_semaphore[domain]
        domain_semaphore.release()
        self._concurrent_semaphore.release()

    @property
    def max_concurrent(self) -> int:
        """
        @brief 获取全局最大并发数

        @return 全局最大并发请求数量
        """
        return self._max_concurrent

    @property
    def max_concurrent_per_domain(self) -> int:
        """
        @brief 获取每个域名的最大并发数

        @return 每个域名的最大并发请求数量
        """
        return self._max_concurrent_per_domain


class Requester(object):
    """
    @brief 请求处理器类，负责处理图片下载请求

    该类管理HTTP请求的发送、响应处理和并发控制
    """

    def __init__(self, queue: Middle[Package | None, Task | None], config: Config):
        """
        @brief 初始化请求处理器

        @param queue 任务队列，用于接收任务和发送结果
        @param config 配置对象，包含请求相关配置
        """
        self.config: RequestConfig = config.REQUEST
        self._queue: Middle[Package | None, Task | None] = queue

        self._concurrent_control: ConcurrentControl = ConcurrentControl(
            self.config.CONCURRENT_REQUESTS,
            self.config.CONCURRENT_REQUESTS_PER_DOMAIN
        )

    async def loop(self):
        """
        @brief 主循环函数，持续处理队列中的任务

        创建异步HTTP客户端，循环从队列中获取任务并处理，直到接收到停止信号
        """
        user_agent: dict[str, str] = self.config.DEFAULT_REQUEST_HEADERS
        user_agent['user-agent'] = self.config.USER_AGENT

        async with AsyncClient(headers=user_agent, timeout=self.config.MAX_DELAY, follow_redirects=True) as client:
            tasks: list[CoroutineTask] = []

            while True:
                task: Task | None = await self._queue.receive()

                if task is None:
                    logger.info('request loop stopped')
                    break

                tasks.append(create_task(self.coroutine(task, client)))

            logger.info('wait for all tasks to complete')
            await gather(*tasks)

        logger.debug('send stop signal to save')
        await self._queue.send(None)

    async def handle_request(self, task: Task, client: AsyncClient) -> Response | None:
        """
        @brief 处理HTTP请求

        @param task 请求任务对象，包含URL等信息
        @param client HTTP客户端实例

        @return 响应对象，如果请求失败则返回None
        """
        for i in range(self.config.MAX_RETRY):
            try:
                response: Response = await client.get(task.url)
                response.raise_for_status()
            except HTTPError as e:
                logger.warning(f'{task.url} failed because of {e}, retrying...', exc_info=True)
            else:
                return response

        logger.error(f'{task.url} failed after {self.config.MAX_RETRY} retries')
        return None

    @staticmethod
    async def handle_response(response: Response, task: Task) -> Package:
        """
        @brief 处理HTTP响应，提取文件名和格式信息

        @param response HTTP响应对象
        @param task 原始请求任务对象

        @return 包装好的数据包对象
        """
        group: Match[str] | None = GET_MANE_FROM_URL.match(response.url.path)

        name: str = group.group(1) if group else ''
        formate: str = group.group(2) if group else ''
        logger.info(f'{task.url} downloaded as {name}.{formate}')

        data: bytes = response.content

        package = Package(task, data, name, formate)
        return package

    async def coroutine(self, task: Task, client: AsyncClient):
        """
        @brief 协程函数，处理单个任务的完整流程

        包括获取并发许可、发送请求、处理响应和释放许可等步骤

        @param task 请求任务对象
        @param client HTTP客户端实例
        """
        await self._concurrent_control.acquire(task.url)
        response: Response | None = await self.handle_request(task, client)
        await self._concurrent_control.release(task.url)

        if response:
            logger.debug(f'{task.url} downloaded successfully')
            package: Package = await self.handle_response(response, task)

            await self._queue.send(package)



if __name__ == '__main__':
    pass
