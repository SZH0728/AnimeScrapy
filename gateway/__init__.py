# -*- coding:utf-8 -*-
# AUTHOR: Sun
"""
@brief gateway 包统一导出入口
@details 导出 DISPATCH_REGISTRY 供外部注册站点数据类到处理器的映射。
         build_site_handlers() 一次性实例化所有 SiteGatewayBase 子类，
         返回值可直接用 ** 解包合并到 main.py 的 dispatch_registry。
"""

from base import HandlerBase
from data.base import TaskBaseData
from gateway.base import SiteGatewayBase

# 站点数据类 → 站点处理器类 的全局注册表
DISPATCH_REGISTRY: dict[type[TaskBaseData], type[SiteGatewayBase]] = {
}


def build_site_handlers() -> dict[type[TaskBaseData], HandlerBase]:
    """
    @brief 实例化并返回所有站点处理器的映射字典
    @details 返回值可直接用 ** 解包合并到 main.py 的 dispatch_registry。
    @return 类型 → 实例的映射，包含所有已注册站点处理器
    """
    return {cls: handler_cls() for cls, handler_cls in DISPATCH_REGISTRY.items()}


__all__ = [
    'SiteGatewayBase',
    'DISPATCH_REGISTRY',
    'build_site_handlers',
]

if __name__ == '__main__':
    pass
