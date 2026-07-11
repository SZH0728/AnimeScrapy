# -*- coding:utf-8 -*-
# AUTHOR: Sun
"""
@brief scheduler 包统一导出入口
@details 导出 SiteScheduleConfig 供外部构造站点调度配置。
         SCHEDULE_REGISTRY 是全局站点配置注册表，
         main.py 从此处导入并传入 Scheduler 构造函数。
"""

from scheduler.base import Scheduler, SiteScheduleConfig

SCHEDULE_REGISTRY: tuple[SiteScheduleConfig, ...] = tuple()

if __name__ == '__main__':
    pass
