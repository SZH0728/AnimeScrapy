# -*- coding:utf-8 -*-
# AUTHOR: Sun
"""
@brief 调度器核心模块
@details Scheduler 是一个独立的异步协程，与 Bus 主循环并行运行。
         按预设的每日时间节点向 Bus 队列注入种子任务，
         使框架以"常驻守护进程 + 定时注入"方式运行，无需重启进程即可定时触发新一轮采集。
"""

import asyncio
from dataclasses import dataclass, field
from datetime import date, datetime, time, timedelta
from logging import getLogger
from typing import TYPE_CHECKING

from data.base import TaskBaseData

if TYPE_CHECKING:
    from bus import Bus

logger = getLogger(__name__)


@dataclass(frozen=True)
class SiteScheduleConfig(object):
    """
    @brief 单个站点的定时调度配置
    @details 指定该站点的每日触发时刻列表与每次触发时注入的种子任务列表。
             frozen=True 防止配置在运行时被意外修改。
             seed_tasks 因 TaskBaseData 不可哈希，使用 field(hash=False) 排除在 __hash__ 之外。
    """
    site_name: str                                    # 站点标识，仅用于日志
    seed_tasks: tuple[TaskBaseData] = field(hash=False)  # 触发时直接注入队列的种子任务
    trigger_times: tuple[time]                           # 每日触发时刻，如 [time(8, 0), time(20, 0)]


@dataclass
class _TriggerSlot(object):
    """
    @brief 内部触发槽，对应一个 SiteScheduleConfig × trigger_time 组合
    @details 非 frozen，因 next_dt 字段在每次触发后需要向前推进。
             不对外暴露，仅供 Scheduler 内部使用。
    """
    config: SiteScheduleConfig  # 所属站点配置
    trigger_time: time          # 原始触发时刻，保留用于日志
    next_datetime: datetime     # 下次触发的绝对时刻，每次触发后推进一天


class Scheduler(object):
    """
    @brief 定时种子任务调度器
    @details 与 Bus._dispatch() 通过 asyncio.gather 并行运行。
             内部维护触发槽列表，每次取最近的槽休眠等待，触发后向总线注入种子任务，
             再将该槽的 next_dt 推进一天，确保时刻对齐不漂移。
    """

    def __init__(self, configs: list[SiteScheduleConfig]) -> None:
        """
        @brief 初始化调度器，将所有站点配置展开为独立的触发槽
        @details 每个 config × trigger_time 组合对应一个 _TriggerSlot。
                 初始 next_dt 为今日该时刻（若已过则顺延至明日）。
                 不在此处存储 Bus 引用，Bus 在 run() 调用时注入。
        @param configs 所有站点的调度配置列表
        """
        slots: list[_TriggerSlot] = []
        now: datetime = datetime.now()
        today: date = now.date()

        for config in configs:
            for trigger_time in config.trigger_times:
                candidate: datetime = datetime.combine(today, trigger_time)

                if candidate <= now:
                    candidate += timedelta(days=1)

                slots.append(_TriggerSlot(
                    config=config,
                    trigger_time=trigger_time,
                    next_datetime=candidate,
                ))

        self._slots: tuple[_TriggerSlot, ...] = tuple(slots)

    async def run(self, bus: Bus) -> None:
        """
        @brief 调度器主协程，永不终止
        @details 由 Bus.run() 通过 asyncio.gather 与 _dispatch() 并行启动。
                 每次循环找出最近的触发槽，休眠至触发时刻，注入任务后推进 next_dt。
                 next_dt 基于自身累加而非 datetime.now()，防止长期运行后时刻漂移。
        @param bus 事件总线实例，由 Bus.run() 在运行时注入
        """
        if not self._slots:
            return

        while True:
            slot: _TriggerSlot = min(self._slots, key=lambda s: s.next_datetime)
            sleep_secs: float = (slot.next_datetime - datetime.now()).total_seconds()

            if sleep_secs > 0:
                await asyncio.sleep(sleep_secs)

            for task in slot.config.seed_tasks:
                await bus.put(task)
            logger.info(f"站点 [{slot.config.site_name}] 注入 {len(slot.config.seed_tasks)} 个种子任务")

            slot.next_datetime += timedelta(days=1)
            # 跳过积压的触发点，中间触发次数直接丢弃
            while slot.next_datetime <= datetime.now():
                slot.next_datetime += timedelta(days=1)


if __name__ == '__main__':
    pass
