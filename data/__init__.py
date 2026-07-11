# -*- coding:utf-8 -*-
# AUTHOR: Sun
"""
@brief data 包统一导出入口
@details 从各子模块 re-export 所有公有类，外部模块可通过
         `from data import XxxData` 完成单行导入，无需感知内部文件结构。
"""

from data.base import TaskBaseData
from data.parse import ExampleParseData, ParseBaseData
from data.request import (
    BatchHttpxRequestData,
    ExampleRequestData,
    MultiHttpxRequestData,
    RequestBaseData,
    SingleHttpxRequestData,
    ThrottledHttpxRequestData,
)
from data.response import ExampleResponseData, HttpxResponseData, ResponseBaseData
from data.site import ExampleSiteHandleData, SiteHandleBaseData
from data.store import ExampleStoreData, StoreBaseData

__all__ = [
    # base
    "TaskBaseData",
    # request
    "RequestBaseData",
    "ExampleRequestData",
    "MultiHttpxRequestData",
    "SingleHttpxRequestData",
    "BatchHttpxRequestData",
    "ThrottledHttpxRequestData",
    # response
    "ResponseBaseData",
    "ExampleResponseData",
    "HttpxResponseData",
    # site
    "SiteHandleBaseData",
    "ExampleSiteHandleData",
    # parse
    "ParseBaseData",
    "ExampleParseData",
    # store
    "StoreBaseData",
    "ExampleStoreData",
]
