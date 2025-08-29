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

    # 并发请求数量，同时发起的请求数上限
    CONCURRENT_REQUESTS: int = 32

    # 每个域名的并发请求数量限制
    CONCURRENT_REQUESTS_PER_DOMAIN: int = 16

    # 最大重试次数，当请求失败时的重试上限
    MAX_RETRY: int = 5

    # 最大延迟时间（秒），请求延迟的上限值
    MAX_DELAY: int = 60


@dataclass
class SaveConfig(object):
    """保存配置类，用于配置文件保存相关参数"""

    # 默认保存路径
    DEFAULT_PATH: str = ''

    # 默认文件格式
    DEFAULT_FORMATE: str = ''


@dataclass
class Config(object):
    """主配置类，整合所有配置项"""

    # 请求相关配置实例
    REQUEST: RequestConfig = field(default_factory=RequestConfig)

    # 保存相关配置实例
    SAVE: SaveConfig = field(default_factory=SaveConfig)


if __name__ == '__main__':
    pass
