# -*- coding:utf-8 -*-
# AUTHOR: Sun
"""
@brief router 包统一导出入口
@details 导出 HTTPX_DOMAIN_REGISTRY 供外部注册站点域名映射。
         build_httpx_site_router() 一次性实例化 HttpxSiteRouter，
         返回值可直接用 ** 解包合并到 main.py 的 dispatch_registry。
"""

from re import Pattern

from base import HandlerBase
from data.base import TaskBaseData
from data.response import HttpxResponseData
from data.gateway import HttpxSiteGatewayData
from router.base import SiteRouterBase
from router.httpx_router import HttpxSiteRouter

# 域名 → 站点数据类 的全局注册表
# 键类型：str（精确匹配，优先级高）或 re.Pattern（正则匹配，按注册顺序首个命中）
HTTPX_DOMAIN_REGISTRY: dict[str | Pattern[str], type[HttpxSiteGatewayData]] = {
}


def build_httpx_site_router() -> dict[type[TaskBaseData], HandlerBase]:
    """
    @brief 实例化并返回 httpx 站点路由器的映射字典
    @details 返回值可直接用 ** 解包合并到 main.py 的 dispatch_registry。
    @return 类型 → 实例的映射，包含 HttpxSiteRouter 处理 HttpxResponseData
    """
    return {HttpxResponseData: HttpxSiteRouter(HTTPX_DOMAIN_REGISTRY)}


__all__ = [
    'SiteRouterBase',
    'HttpxSiteRouter',
    'HTTPX_DOMAIN_REGISTRY',
    'build_httpx_site_router',
]

if __name__ == '__main__':
    pass
