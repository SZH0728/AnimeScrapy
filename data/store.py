# -*- coding:utf-8 -*-
# AUTHOR: Sun
"""
@brief 定义存储数据包
@details StoreBaseData 是所有落库数据包的根基类，字段为空。
         具体存储子类继承此类并自定义所需字段。
"""

from dataclasses import dataclass
from logging import getLogger

from data.base import TaskBaseData

logger = getLogger(__name__)


@dataclass(frozen=True)
class StoreBaseData(TaskBaseData):
    """
    @brief 存储数据包根基类
    @details 纯标记基类，无任何字段。Bus 据此类型路由到对应 Storage。
             各站点存储子类继承此类并定义自身所需的结构化字段。
    """


@dataclass(frozen=True)
class ExampleStoreData(StoreBaseData):
    """
    @brief StoreBaseData 继承示例
    @details 展示最简继承写法，不添加任何字段。
             实际存储子类应在此基础上添加具体的业务字段。
    """


if __name__ == '__main__':
    pass
