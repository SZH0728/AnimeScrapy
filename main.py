# -*- coding:utf-8 -*-
# AUTHOR: Sun
"""
@brief 框架程序入口
@details 装配所有模块，合并 dispatch_registry，构建 Bus 与 Scheduler 并启动。
         本文件不包含任何业务逻辑，仅做依赖注入与配置组装。
"""

import asyncio
import sys
from logging import getLogger, Formatter, DEBUG, INFO, ERROR, WARNING, StreamHandler
from logging.handlers import TimedRotatingFileHandler
from pathlib import Path

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

MAX_CONCURRENT_TASKS: int = 20  # 最大并发子协程数，对应 Bus 内部信号量上限


def setup_logging(log_dir: str = 'logs') -> None:
    """
    @brief 初始化日志配置
    @details 根据操作系统自动切换策略：
             Windows/macOS 使用开发模式（控制台 DEBUG），
             Linux 使用生产模式（纯文件，INFO 留 7 天，ERROR 永不删除）。
             两种模式均压制 httpx / hpack / asyncio 的 DEBUG 噪音。
    @param log_dir 生产模式下日志文件存放目录，默认 logs/
    """
    _FMT = '%(asctime)s [%(levelname)-8s] %(name)s - %(message)s'

    root = getLogger()
    root.setLevel(DEBUG)

    if sys.platform in ('win32', 'darwin'):
        handler = StreamHandler()
        handler.setLevel(DEBUG)
        handler.setFormatter(Formatter(_FMT, datefmt='%H:%M:%S'))
        root.addHandler(handler)
    else:
        Path(log_dir).mkdir(parents=True, exist_ok=True)
        fmt = Formatter(_FMT, datefmt='%Y-%m-%d %H:%M:%S')

        info_h = TimedRotatingFileHandler(
            f'{log_dir}/info.log', when='midnight', backupCount=7, encoding='utf-8',
        )
        info_h.setLevel(INFO)
        info_h.setFormatter(fmt)

        # backupCount=0 使轮转时不删除旧文件，error 日志永久保留
        error_h = TimedRotatingFileHandler(
            f'{log_dir}/error.log', when='midnight', backupCount=0, encoding='utf-8',
        )
        error_h.setLevel(ERROR)
        error_h.setFormatter(fmt)

        root.addHandler(info_h)
        root.addHandler(error_h)

    for lib in ('httpx', 'hpack', 'asyncio'):
        getLogger(lib).setLevel(WARNING)


async def main() -> None:
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
        max_concurrent_tasks=MAX_CONCURRENT_TASKS,
    )
    bus: Bus = Bus(bus_config)
    scheduler: Scheduler = Scheduler(list(SCHEDULE_REGISTRY))

    logger.info("框架启动，开始运行事件总线")
    await bus.run(scheduler)


if __name__ == '__main__':
    setup_logging()
    asyncio.run(main())
