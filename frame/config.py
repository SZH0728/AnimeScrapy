# -*- coding:utf-8 -*-
# AUTHOR: Sun

from dataclasses import dataclass, field

from httpx import Request


@dataclass
class RequestConfig(object):
    INTERVAL: int = 1
    MAX_RETRY: int = 5


@dataclass
class HandleConfig(object):
    INIT_URL: list[Request] = field(default_factory=list)


@dataclass
class Config(object):
    REQUEST = RequestConfig()
    HANDLE = HandleConfig()



if __name__ == '__main__':
    pass
