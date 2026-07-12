# -*- coding:utf-8 -*-
# AUTHOR: Sun
"""
@brief 存储模块包初始化，暴露注册表与工厂方法
@details DISPATCH_REGISTRY 映射存储数据类型到存储器类，
         build_storages() 工厂方法根据注册表实例化所有存储器。
         新增具体存储后端时，只需在 DISPATCH_REGISTRY 中追加一行映射。
"""

from data.store import StoreBaseData
from data.base import TaskBaseData
from base import HandlerBase
from storage.base import StorageBase

# 存储数据类型 → 存储器类的调度注册表
DISPATCH_REGISTRY: dict[type[StoreBaseData], type[StorageBase]] = {}


def build_storages() -> dict[type[TaskBaseData], HandlerBase]:
    """
    @brief 根据注册表实例化所有已注册的存储器
    @return 存储数据类型到存储器实例的映射字典
    """
    return {data_cls: handler_cls() for data_cls, handler_cls in DISPATCH_REGISTRY.items()}


if __name__ == '__main__':
    pass
