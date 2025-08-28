# -*- coding:utf-8 -*-
# AUTHOR: Sun

from logging import getLogger
from asyncio import sleep

from httpx import Request, Response, AsyncClient, HTTPError

from frame.bridge import Client
from frame.config import Config

logger = getLogger(__name__)


class Requester(object):
    def __init__(self, client: Client[Response | None, Request | None], config: Config):
        self.config = config.REQUEST
        self._channel = client

    async def loop(self):
        async with AsyncClient() as client:
            while True:
                request: Request | None = await self._channel.get()

                if request is None:
                    logger.info('receive close signal, stopping program')
                    break

                logger.debug(f'requesting {request.url}...')
                response: Response | None = await self.handle_request(request, client)

                if isinstance(response, Response):
                    logger.debug(f'{request.url} succeeded')
                    self._channel.put(response)
                else:
                    logger.error(f'{request.url} failed to the maximum number of retries')

                logger.debug(f'sleeping for {self.config.INTERVAL} seconds...')
                await sleep(self.config.INTERVAL)

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


if __name__ == '__main__':
    pass
