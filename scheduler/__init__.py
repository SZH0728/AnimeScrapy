# -*- coding:utf-8 -*-
# AUTHOR: Sun
"""
@brief scheduler 包统一导出入口
@details 导出 SiteScheduleConfig 供外部构造站点调度配置。
         SCHEDULE_REGISTRY 是全局站点配置注册表，
         main.py 从此处导入并传入 Scheduler 构造函数。
"""

from datetime import time

import httpx

from config import config
from data.request import SingleHttpxRequestData
from scheduler.base import Scheduler, SiteScheduleConfig

SCHEDULE_REGISTRY: tuple[SiteScheduleConfig, ...] = (
    SiteScheduleConfig(
        site_name='bangumi',
        trigger_times=(time(
            config.getint('bangumi', 'trigger_hour'),
            config.getint('bangumi', 'trigger_minute'),
        ),),
        seed_tasks=(
            SingleHttpxRequestData(
                retry=config.getint('bangumi', 'retry'),
                request=httpx.Request(
                    'GET',
                    'https://api.bgm.tv/calendar',
                    headers={'User-Agent': config.get('bangumi', 'user_agent')},
                ),
            ),
        ),
    ),
)

if __name__ == '__main__':
    pass
