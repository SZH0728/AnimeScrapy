# -*- coding:utf-8 -*-
# AUTHOR: Sun

from typing import Callable, Iterable
from dataclasses import dataclass, field

from httpx import Request


@dataclass
class RequestConfig(object):
    """请求配置类，用于配置HTTP请求相关参数"""
    
    # 用户代理字符串，用于模拟浏览器请求
    USER_AGENT: str = ''
    
    # 默认请求头字典，可以添加通用的请求头信息
    DEFAULT_REQUEST_HEADERS: dict[str, str] = field(default_factory=dict)

    # 下载延迟时间（秒），用于控制请求间隔
    DOWNLOAD_DELAY: int = 1
    
    # 最大重试次数，当请求失败时的重试上限
    MAX_RETRY: int = 5
    
    # 最大延迟时间（秒），请求延迟的上限值
    MAX_DELAY: int = 60


@dataclass
class HandleConfig(object):
    """处理器配置类，用于配置数据处理相关参数"""

    # 初始URL，程序启动时需要处理的请求
    INIT_URL: Request | None = None
    
    # 初始URL列表，程序启动时需要处理的请求列表
    INIT_URLS: list[Request] = field(default_factory=list)

    # 初始URL处理函数，返回一个请求列表
    INIT_URL_FUNCTION: Callable[[], Iterable[Request]] | None = None


@dataclass
class Config(object):
    """主配置类，整合所有配置项"""
    
    # 请求配置实例
    REQUEST: RequestConfig = field(default_factory=RequestConfig)
    
    # 处理器配置实例
    HANDLE: HandleConfig = field(default_factory=HandleConfig)


if __name__ == '__main__':
    pass