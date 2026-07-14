# -*- coding:utf-8 -*-
# AUTHOR: Sun
"""
@brief 实现基于 httpx 响应的站点路由器
@details HttpxSiteRouter 是目前唯一注册进 dispatch_registry 的路由实例。
         构造时将注册表拆分为精确字典和正则列表两个内部结构，
         _do_route() 通过 httpx.URL.host 提取域名后调用 _match() 完成路由，
         匹配优先级严格遵守：精确 > 正则（按注册顺序首个命中）。
"""

from re import Pattern, fullmatch
from logging import getLogger

from data.response import HttpxResponseData
from data.gateway import HttpxSiteGatewayData
from router.base import SiteRouterBase

logger = getLogger(__name__)


class HttpxSiteRouter(SiteRouterBase[HttpxResponseData]):
    """
    @brief httpx 响应数据包的站点路由器
    @details 处理 HttpxResponseData，根据响应 URL 的域名将其包装为对应站点的
             HttpxSiteGatewayData 子类后投回总线。
             注册表支持 str 精确键（O(1)）和 re.Pattern 正则键（顺序遍历）。
    """

    def __init__(self, registry: dict[str | Pattern[str], type[HttpxSiteGatewayData]]) -> None:
        """
        @brief 初始化路由器，拆分注册表为精确字典与正则列表
        @param registry 域名 → 站点数据类 的映射，键可为纯字符串或编译后的正则
        """
        self._exact: dict[str, type[HttpxSiteGatewayData]] = {}
        self._patterns: list[tuple[Pattern[str], type[HttpxSiteGatewayData]]] = []

        for key, cls in registry.items():
            if isinstance(key, str):
                self._exact[key] = cls
            else:
                self._patterns.append((key, cls))

    async def _do_route(self, task: HttpxResponseData) -> HttpxSiteGatewayData | None:
        """
        @brief 提取域名并路由到对应站点数据包类
        @param task httpx 响应数据包
        @return 命中时返回包装后的站点数据包；未命中时记录 warning 并返回 None
        """
        domain: str = task.response.url.host
        target_cls: type[HttpxSiteGatewayData] | None = self._match(domain)

        if target_cls is None:
            logger.warning(f'域名 [{domain}] 未在 HTTPX_DOMAIN_REGISTRY 中注册，任务已丢弃')
            return None

        result = self._wrap(task, target_cls)
        logger.info(f"响应 [{domain}] 路由至站点 [{target_cls.__name__}]")
        return result

    def _match(self, domain: str) -> type[HttpxSiteGatewayData] | None:
        """
        @brief 统一匹配入口，精确优先，未命中再尝试正则
        @param domain 从响应 URL 提取的纯主机名（不含端口）
        @return 命中的站点数据类；全未命中返回 None
        """
        return self._match_exact(domain) or self._match_pattern(domain)

    def _match_exact(self, domain: str) -> type[HttpxSiteGatewayData] | None:
        """
        @brief O(1) 精确域名匹配
        @param domain 主机名字符串
        @return 注册表中对应的站点数据类；未命中返回 None
        """
        return self._exact.get(domain)

    def _match_pattern(self, domain: str) -> type[HttpxSiteGatewayData] | None:
        """
        @brief 按注册顺序遍历正则键，返回第一个命中的站点数据类
        @param domain 主机名字符串
        @return 首个命中的站点数据类；全未命中返回 None
        """
        for pattern, cls in self._patterns:
            if fullmatch(pattern, domain):
                return cls
        return None

    @staticmethod
    def _wrap(task: HttpxResponseData, target_cls: type[HttpxSiteGatewayData], ) -> HttpxSiteGatewayData:
        """
        @brief 将 HttpxResponseData 包装为目标站点数据类实例
        @param task 原始 httpx 响应数据包
        @param target_cls 命中的站点数据类（须与 HttpxSiteGatewayData 签名一致）
        @return 包装后的站点数据包实例
        """
        return target_cls(task=task.task, response=task.response, meta=task.meta)


if __name__ == '__main__':
    pass
