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
    def __init__(self, max_concurrent: int, max_concurrent_per_domain: int):
        self._max_concurrent: int = max_concurrent
        self._max_concurrent_per_domain: int = max_concurrent_per_domain

        self._concurrent_semaphore: Semaphore = Semaphore(max_concurrent)
        self._domain_semaphore: dict[str, Semaphore] = {}

    async def acquire(self, domain: str):
        if domain not in self._domain_semaphore.keys():
            self._domain_semaphore[domain] = Semaphore(self._max_concurrent_per_domain)

        await self._concurrent_semaphore.acquire()
        domain_semaphore = self._domain_semaphore[domain]
        await domain_semaphore.acquire()

    async def release(self, domain: str):
        domain_semaphore = self._domain_semaphore[domain]
        domain_semaphore.release()
        self._concurrent_semaphore.release()

    @property
    def max_concurrent(self) -> int:
        return self._max_concurrent

    @property
    def max_concurrent_per_domain(self) -> int:
        return self._max_concurrent_per_domain


class Requester(object):
    def __init__(self, queue: Middle[Package | None, Task | None], config: Config):
        self.config: RequestConfig = config.REQUEST
        self._queue: Middle[Package | None, Task | None] = queue

        self._concurrent_control: ConcurrentControl = ConcurrentControl(
            self.config.CONCURRENT_REQUESTS,
            self.config.CONCURRENT_REQUESTS_PER_DOMAIN
        )
    async def loop(self):
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
        group: Match[str] | None = GET_MANE_FROM_URL.match(response.url.path)

        name: str = group.group(1) if group else ''
        formate: str = group.group(2) if group else ''
        logger.info(f'{task.url} downloaded as {name}.{formate}')

        data: bytes = response.content

        package = Package(task, data, name, formate)
        return package

    async def coroutine(self, task: Task, client: AsyncClient):
        await self._concurrent_control.acquire(task.url)
        response: Response | None = await self.handle_request(task, client)
        await self._concurrent_control.release(task.url)

        if response:
            logger.debug(f'{task.url} downloaded successfully')
            package: Package = await self.handle_response(response, task)

            await self._queue.send(package)



if __name__ == '__main__':
    pass
