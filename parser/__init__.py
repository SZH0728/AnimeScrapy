# -*- coding:utf-8 -*-
# AUTHOR: Sun
"""
@brief parser 包统一导出入口
@details 导出 DISPATCH_REGISTRY 供外部注册解析数据类到解析器的映射。
         build_parsers() 一次性实例化所有 ParserBase 子类，
         返回值可直接用 ** 解包合并到 main.py 的 dispatch_registry。
"""

from base import HandlerBase
from data.base import TaskBaseData
from parser.base import ParserBase

# 解析数据类 → 解析器类 的全局注册表
DISPATCH_REGISTRY: dict[type[TaskBaseData], type[ParserBase]] = {
}


def build_parsers() -> dict[type[TaskBaseData], HandlerBase]:
    """
    @brief 实例化并返回所有解析器的映射字典
    @details 返回值可直接用 ** 解包合并到 main.py 的 dispatch_registry。
    @return 类型 → 实例的映射，包含所有已注册解析器
    """
    return {cls: parser_cls() for cls, parser_cls in DISPATCH_REGISTRY.items()}


__all__ = [
    'ParserBase',
    'DISPATCH_REGISTRY',
    'build_parsers',
]

if __name__ == '__main__':
    pass
