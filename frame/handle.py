# -*- coding:utf-8 -*-
# AUTHOR: Sun

from typing import Callable, Iterable
from dataclasses import dataclass, field
from re import compile, Pattern
from logging import getLogger

from httpx import Request, Response

from frame.config import Config
from frame.bridge import Client
from frame.counter import AsyncCounter

logger = getLogger(__name__)


@dataclass
class Methods(object):
    FIX: dict[str, Callable[[Response], Request | Iterable[Request] | None]] = field(default_factory=dict)
    REGEX: dict[str, Callable[[Response], Request | Iterable[Request] | None]] = field(default_factory=dict)


class Spider(object):
    def __init__(self):
        self._methods = Methods()
        self.config = Config()

    def route(self, url: str, regex: bool = False):
        def decorator(func: Callable[[Response], Request | Iterable[Request] | None]):
            if regex:
                self._methods.REGEX[url] = func
            else:
                self._methods.FIX[url] = func
            return func

        return decorator

    def construct(self) -> 'MethodDict':
        return MethodDict(self._methods)


class MethodDict(object):
    def __init__(self, methods: Methods):
        self._fix_path: dict[str, Callable[[Response], Request | Iterable[Request] | None]] = methods.FIX
        self._regex_path: list[tuple[Pattern, Callable[[Response], Request | Iterable[Request] | None]]] = []
        for regex, func in methods.REGEX.items():
            self._regex_path.append((compile(regex), func))

    def handle(self, response: Response) -> list[Request]:
        url: str = f'{response.url.host}{response.url.path}'

        if url in self._fix_path.keys():
            method = self._fix_path[url]
            logger.debug(f'{url} match fix path: {url}, handle with {method.__name__}')
            return self.handle_method(response, method)

        for regex, method in self._regex_path:
            if regex.match(url):
                logger.debug(f'{url} match regex: {regex}, handle with {method.__name__}')
                return self.handle_method(response, method)

        logger.warning(f'{url} not match any route, dropped')
        return []

    @staticmethod
    def handle_method(response: Response, method: Callable[[Response], Request | Iterable[Request] | None]) -> list[Request]:
        result: Request | Iterable[Request] | None = method(response)

        if result is None:
            return []

        elif isinstance(result, Request):
            return [result]

        elif isinstance(result, Iterable):
            return list(result)

        else:
            raise TypeError(f'{method.__name__} return type error')


class Handle(object):
    def __init__(self, client: Client[Request | None, Response | None], config: Config, counter: AsyncCounter, methods: MethodDict):
        self.config = config.HANDLE

        self._channel = client
        self._counter = counter

        self._methods =  methods

    async def loop(self):
        init_requests = self.config.INIT_URL
        for request in init_requests:
            self._channel.put(request)

        while True:
            response: Response | None = await self._channel.get()

            if response is None:
                logger.info('receive close signal, stopping program')
                break

            logger.debug(f'handle response: {response.url}')
            requests: list[Request] = self.handle_response(response)

            logger.debug(f'add requests: {requests}')
            if len(requests):
                await self._counter.increment(len(requests))

            for request in requests:
                self._channel.put(request)

            await self._counter.decrement()

    def handle_response(self, response: Response) -> list[Request]:
        try:
            requests: list[Request] = self._methods.handle(response)
        except Exception as e:
            logger.error(f'Error occur when handle response: {e}')
        else:
            return requests

        return []


if __name__ == '__main__':
    pass
