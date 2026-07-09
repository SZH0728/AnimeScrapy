# -*- coding:utf-8 -*-
# AUTHOR: Sun
"""
@brief 定义总线数据包的根基类
@details 所有在异步事件总线上流通的数据包均继承自 TaskBaseData。
         Bus 的 dispatch_registry 以 type[TaskBaseData] 为键进行路由。
         此模块无任何项目内依赖，也不引入第三方库。
"""

from dataclasses import dataclass
from logging import getLogger

logger = getLogger(__name__)


@dataclass(frozen=True)
class TaskBaseData(object):
    """
    @brief 总线数据包根基类
    @details 纯标记基类，无任何字段。所有具体数据包均继承此类，
             Bus 通过 type(task) 精确匹配注册表进行分发。
    """


if __name__ == '__main__':
    pass
