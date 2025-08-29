# -*- coding:utf-8 -*-
# AUTHOR: Sun

from dataclasses import dataclass, field


@dataclass
class RequestConfig(object):
    """请求配置类，用于配置HTTP请求相关参数"""

    # 用户代理字符串，用于模拟浏览器请求
    USER_AGENT: str = ''

    # 默认请求头字典，可以添加通用的请求头信息
    DEFAULT_REQUEST_HEADERS: dict[str, str] = field(default_factory=dict)

    CONCURRENT_REQUESTS: int = 32

    CONCURRENT_REQUESTS_PER_DOMAIN: int = 16

    # 最大重试次数，当请求失败时的重试上限
    MAX_RETRY: int = 5

    # 最大延迟时间（秒），请求延迟的上限值
    MAX_DELAY: int = 60


@dataclass
class SaveConfig(object):
    DEFAULT_PATH: str = ''

    DEFAULT_FORMATE: str = ''


@dataclass
class Config(object):
    REQUEST: RequestConfig = field(default_factory=RequestConfig)
    SAVE: SaveConfig = field(default_factory=SaveConfig)


if __name__ == '__main__':
    pass
