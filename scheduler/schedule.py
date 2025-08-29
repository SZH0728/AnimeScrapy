# -*- coding:utf-8 -*-
# AUTHOR: Sun

"""
@file schedule.py
@brief 调度模块，用于定时执行任务
@details 提供基于时间规则的任务调度功能，支持按小时、星期、日期、月份等维度设置任务执行时间
"""

from typing import Callable
from logging import getLogger
from enum import Enum
from datetime import datetime, tzinfo
from time import sleep
from threading import Thread

from scheduler.every import Time, Every

logger = getLogger(__name__)


class RunType(Enum):
    """
    @brief 运行类型枚举
    @details 定义任务的运行方式
    """
    BLOCK = 1          #: 阻塞模式运行
    THREAD = 2         #: 线程模式运行
    THREAD_JOIN = 4    #: 线程模式运行并等待结束


class Schedule(object):
    """
    @brief 任务调度器
    @details 管理和执行按时间规则调度的任务
    """
    def __init__(self, timezone: tzinfo):
        """
        @brief 初始化调度器
        @param timezone 时区信息
        """
        self._jobs: list[tuple[Time, Callable]] = []
        self.timezone = timezone

    def repeat(self, every: Every):
        """
        @brief 添加重复执行的任务
        @param every 时间规则
        @return decorator 装饰器函数
        """
        def decorator(func: Callable) -> Callable:
            self._jobs.append((every.time, func))
            return func
        return decorator

    def find(self, datetime_object: datetime) -> list[Callable]:
        """
        @brief 查找在指定时间应该执行的任务
        @param datetime_object 时间对象
        @return list[Callable] 应该在该时间执行的任务列表
        """
        hour: int = datetime_object.hour
        weekday: int = datetime_object.weekday() + 1
        monthday: int = datetime_object.day
        month: int = datetime_object.month

        functions: list[Callable] = []
        for time, func in self._jobs:
            if hour in time.hour and weekday in time.weekday and monthday in time.monthday and month in time.month:
                functions.append(func)

        return functions

    def now(self, timezone: tzinfo | None = None) -> datetime:
        """
        @brief 获取当前时间
        @param timezone 时区信息，如果为None则使用调度器默认时区
        @return datetime 当前时间
        """
        if timezone:
            return datetime.now(tz=timezone)
        else:
            return datetime.now(tz=self.timezone)

    def run_tick(self, timezone: tzinfo | None = None) -> list[Thread]:
        """
        @brief 执行一次任务调度（线程模式）
        @param timezone 时区信息，如果为None则使用调度器默认时区
        @return list[Thread] 创建的线程列表
        """
        now = self.now(timezone)
        functions = self.find(now)

        return [self.thread(func) for func in functions]

    def run_block_tick(self, timezone: tzinfo | None = None):
        """
        @brief 执行一次任务调度（阻塞模式）
        @param timezone 时区信息，如果为None则使用调度器默认时区
        @return list[Thread] 创建的线程列表
        """
        now = self.now(timezone)
        functions = self.find(now)

        for i in functions:
            try:
                i()
            except Exception as e:
                logger.error(f'An error occurred in {i.__name__}: {e}', exc_info=True)

    def run_join_tick(self, timezone: tzinfo | None = None):
        """
        @brief 执行一次任务调度（线程模式并等待完成）
        @param timezone 时区信息，如果为None则使用调度器默认时区
        """
        threads: list[Thread] = self.run_tick(timezone)
        for i in threads:
            i.join()

    def loop(self, type_: RunType, timezone: tzinfo | None = None):
        """
        @brief 循环执行任务调度
        @param type_ 运行类型
        @param timezone 时区信息，如果为None则使用调度器默认时区
        """
        while True:
            if type_ == RunType.BLOCK:
                self.run_block_tick(timezone)
            elif type_ == RunType.THREAD_JOIN:
                self.run_join_tick(timezone)
            elif type_ == RunType.THREAD:
                self.run_tick(timezone)

            sleep(3600)

    @staticmethod
    def thread(func: Callable) -> Thread:
        """
        @brief 在独立线程中执行函数
        @param func 要执行的函数
        @return Thread 创建的线程对象
        """
        def function():
            try:
                func()
            except Exception as e:
                logger.error(f'An error occurred in {func.__name__}: {e}', exc_info=True)

        thread = Thread(target=function)
        thread.start()
        return thread


if __name__ == '__main__':
    pass
