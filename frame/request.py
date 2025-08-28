# -*- coding:utf-8 -*-
# AUTHOR: Sun

from logging import getLogger
from asyncio import sleep

from httpx import Request, Response, AsyncClient, HTTPError

from frame.bridge import Client
from frame.config import Config, RequestConfig

logger = getLogger(__name__)


class Requester(object):
    def __init__(self, client: Client[Response | None, Request | None], config: Config):
        self.config: RequestConfig = config.REQUEST
        self._channel: Client[Response | None, Request | None] = client

    async def loop(self):
        user_agent: dict[str, str] = self.config.DEFAULT_REQUEST_HEADERS
        user_agent['user-agent'] = self.config.USER_AGENT

        async with AsyncClient(headers=user_agent, timeout=self.config.DOWNLOAD_DELAY) as client:
            while True:
                request: Request | None = await self._channel.get()

                if request is None:
                    logger.info('receive close signal, stopping program')
                    break

                logger.debug(f'requesting {request.url} ...')
                response: Response | None = await self.handle_request(request, client)
                await  self.handle_response(response, request.url)

                logger.debug(f'sleeping for {self.config.DOWNLOAD_DELAY} seconds...')
                await sleep(self.config.DOWNLOAD_DELAY)

    async def handle_request(self, request: Request, client: AsyncClient) -> Response | None:
        for i in range(self.config.MAX_RETRY):
            try:
                response: Response = await client.send(request)
                response.raise_for_status()
            except HTTPError as e:
                logger.warning(f'{request.url} failed because of {e}, retrying...', exc_info=True)
            else:
                return  response

        return None

    async def handle_response(self, response: Response | None, url: str):
        if response is None:
            logger.error(f'{url} failed to the maximum number of retries')
        elif isinstance(response, Response):
            logger.debug(f'{url} succeeded')
            await self._channel.put(response)
        else:
            raise TypeError(f'response must be a Response or None, {type(response)} given')



if __name__ == '__main__':
    pass
