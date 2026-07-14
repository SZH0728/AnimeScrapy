# -*- coding:utf-8 -*-
# AUTHOR: Sun
"""
@brief 定义站点处理器输入数据包
@details SiteGatewayBaseData 是纯路由标记基类，字段为空。
         具体站点子类通过双继承同时获得路由标识（来自 SiteGatewayBaseData）
         和数据字段（来自 ResponseBaseData 或其子类）。
"""

from dataclasses import dataclass
from logging import getLogger

from data.base import TaskBaseData
from data.response import HttpxResponseData, ResponseBaseData

logger = getLogger(__name__)


@dataclass(frozen=True)
class SiteGatewayBaseData(TaskBaseData):
    """
    @brief 站点处理器输入数据包根基类
    @details 纯路由标记类，无任何字段。Bus 据此类型路由到对应 SiteGatewayBase。
             具体站点子类通过双继承获得实际数据字段，无需在此基类中定义。
    """


@dataclass(frozen=True)
class ExampleSiteGatewayData(SiteGatewayBaseData, ResponseBaseData):
    """
    @brief SiteGatewayBaseData 双继承示例
    @details 示范标准双继承写法：
               - SiteGatewayBaseData 提供总线路由标识
               - ResponseBaseData 提供 task 字段
             实际站点子类通常将第二个父类替换为 HttpxResponseData 以携带响应体。
    """


@dataclass(frozen=True)
class HttpxSiteGatewayData(SiteGatewayBaseData, HttpxResponseData):
    """
    @brief httpx 站点处理器输入数据包
    @details 双继承：SiteGatewayBaseData 提供总线路由标识，HttpxResponseData 提供
             task 和 response 字段。由 HttpxSiteRouter 包装后投入总线，
             由具体站点的 SiteGatewayBase 子类据此类型消费。
    """


@dataclass(frozen=True)
class BangumiApiGatewayData(HttpxSiteGatewayData):
    """
    @brief api.bgm.tv 域名路由标记
    @details 由 HttpxSiteRouter 在匹配到 api.bgm.tv 时产出，
             路由到 BangumiApiGateway 处理器。
             字段全部由继承链提供，无额外字段。
    """


@dataclass(frozen=True)
class BangumiCoverGatewayData(HttpxSiteGatewayData):
    """
    @brief lain.bgm.tv 封面图域名路由标记
    @details 由 HttpxSiteRouter 在匹配到 lain.bgm.tv 时产出，
             路由到 BangumiCoverGateway 处理器。
             字段全部由继承链提供，无额外字段。
    """


if __name__ == '__main__':
    pass
