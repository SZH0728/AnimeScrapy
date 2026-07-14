# -*- coding:utf-8 -*-
# AUTHOR: Sun
"""
@brief Bangumi 站点处理器实现
@details 提供两个站点处理器：
         BangumiApiGateway 处理 api.bgm.tv 域名的响应，根据 URL 路径路由至对应的
         解析输入数据包；BangumiCoverGateway 处理 lain.bgm.tv 域名的封面图响应，
         无路径分支，直接产出 BangumiCoverParseData。
"""

from logging import getLogger

from data.gateway import BangumiApiGatewayData, BangumiCoverGatewayData
from data.parse import (
    BangumiCalendarParseData,
    BangumiCoverParseData,
    BangumiSubjectDetailParseData,
)
from gateway.base import SiteGatewayBase

logger = getLogger(__name__)


class BangumiApiGateway(SiteGatewayBase[BangumiApiGatewayData]):
    """
    @brief api.bgm.tv 域名站点处理器
    @details 根据 URL 路径将响应路由至 BangumiCalendarParseData 或
             BangumiSubjectDetailParseData，未知路径则记录警告并返回 None。
    """

    async def _do_handle(self, task: BangumiApiGatewayData) -> BangumiCalendarParseData| BangumiSubjectDetailParseData | None:
        """
        @brief 按 URL 路径分发至对应解析输入数据包
        @param task 携带 api.bgm.tv 响应的数据包
        @return 对应的 ParseBaseData 子类实例，未知路径时返回 None
        """
        result: BangumiCalendarParseData| BangumiSubjectDetailParseData | None
        match task.response.url.path:
            case '/calendar':
                result = BangumiCalendarParseData(task=task.task, response=task.response)
                logger.info(f"站点 [{type(self).__name__}] URL [{task.response.url.path}] 命中类型 [{type(result).__name__}]")
                return result
            case path if path.startswith('/v0/subjects/'):
                result = BangumiSubjectDetailParseData(task=task.task, response=task.response)
                logger.info(f"站点 [{type(self).__name__}] URL [{task.response.url.path}] 命中类型 [{type(result).__name__}]")
                return result
            case _:
                logger.warning(f"BangumiApiGateway 未知路径 [{task.response.url}]")
                return None


class BangumiCoverGateway(SiteGatewayBase[BangumiCoverGatewayData]):
    """
    @brief lain.bgm.tv 封面图域名站点处理器
    @details 无路径分支，所有来自 lain.bgm.tv 的响应均产出 BangumiCoverParseData。
    """

    async def _do_handle(self, task: BangumiCoverGatewayData) -> BangumiCoverParseData:
        """
        @brief 直接产出封面图解析输入数据包
        @param task 携带 lain.bgm.tv 响应的数据包
        @return BangumiCoverParseData 实例
        """
        result = BangumiCoverParseData(task=task.task, response=task.response)
        logger.info(f"站点 [{type(self).__name__}] URL [{task.response.url.path}] 命中类型 [{type(result).__name__}]")
        return result


if __name__ == '__main__':
    pass
