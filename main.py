# -*- coding:utf-8 -*-
# AUTHOR: Sun
"""
@brief 框架程序入口
@details 装配所有模块，合并 dispatch_registry，构建 Bus 与 Scheduler 并启动。
         本文件不包含任何业务逻辑，仅做依赖注入与配置组装。
"""

import asyncio
from logging import getLogger

from config import config, setup_logging
from database import init_db
from base import HandlerBase
from data.base import TaskBaseData
from scheduler.base import Scheduler
from scheduler import SCHEDULE_REGISTRY
from requester import build_http_requesters
from router import build_httpx_site_router
from gateway import build_site_handlers
from parser import build_parsers
from storage import build_storages
from bus import Bus, BusConfig

logger = getLogger(__name__)


async def main(debug_seed: TaskBaseData | None = None) -> None:
    """
    @brief 装配所有处理器并启动事件总线
    @details 按阶段顺序调用各模块工厂方法，合并为单一 dispatch_registry，
             构造 BusConfig 与 Bus，再由 Bus.run() 与 Scheduler 并发运行。
    """
    dispatch_registry: dict[type[TaskBaseData], HandlerBase] = {
        **build_http_requesters(),    # Single/Batch/ThrottledHttpxRequestData → 请求器实例
        **build_httpx_site_router(),  # HttpxResponseData → HttpxSiteRouter 实例
        **build_site_handlers(),      # 各站点 GatewayData → 站点处理器实例
        **build_parsers(),            # 各解析数据类 → 解析器实例
        **build_storages(),           # 各存储数据类 → 存储器实例
    }

    bus_config: BusConfig = BusConfig(
        dispatch_registry=dispatch_registry,
        max_concurrent_tasks=config.getint('bus', 'max_concurrent_tasks'),
    )
    bus: Bus = Bus(bus_config)
    scheduler: Scheduler = Scheduler(list(SCHEDULE_REGISTRY))

    if debug_seed:
        await bus.put(debug_seed)

    logger.info("框架启动，开始运行事件总线")
    await bus.run(scheduler)


if __name__ == '__main__':
    setup_logging()
    init_db(config.get('bangumi', 'database_url'))
    asyncio.run(main())
