# -*- coding:utf-8 -*-
# AUTHOR: Sun

"""
@file schedule.py
@brief 调度模块，用于定时执行任务
@details 提供基于时间规则的任务调度功能，支持按小时、星期、日期、月份等维度设置任务执行时间
"""

from typing import Callable
from dataclasses import dataclass, field
from logging import getLogger
from enum import Enum
from datetime import datetime, tzinfo
from time import sleep
from threading import Thread

logger = getLogger(__name__)


class RunType(Enum):
    """
    @brief 运行类型枚举
    @details 定义任务的运行方式
    """
    BLOCK = 1          #: 阻塞模式运行
    THREAD = 2         #: 线程模式运行
    THREAD_JOIN = 4    #: 线程模式运行并等待结束


@dataclass
class Time(object):
    """
    @brief 时间配置类
    @details 用于存储任务执行的时间规则配置
    """
    hour: tuple[int, ...] = field(default=tuple)        #: 小时配置 (0-23)
    weekday: tuple[int, ...] = field(default=tuple)     #: 星期配置 (1-7, 1为周一)
    monthday: tuple[int, ...] = field(default=tuple)    #: 日期配置 (1-31)
    month: tuple[int, ...] = field(default=tuple)       #: 月份配置 (1-12)


class Every(object):
    """
    @brief 时间规则构建器
    @details 提供链式调用方式构建时间规则，用于指定任务的执行时间
    """
    def __init__(self):
        """
        @brief 初始化Every对象
        """
        self._time = Time()

    def hour(self, *args: int) -> 'Every':
        """
        @brief 设置小时规则
        @param args 小时值列表 (0-23)
        @return Every 返回自身，支持链式调用
        @exception TypeError 当传入的参数不是整数时抛出
        @exception ValueError 当小时值不在有效范围时抛出
        """
        hours = []

        for i in args:
            if not isinstance(i, int):
                raise TypeError(f'{i} is not a valid hour.')

            if 0 <= i <= 23:
                hours.append(i)

            elif i == 24:
                hours.append(0)

            else:
                raise ValueError(f'{i} is not a valid hour.')

        hours.sort()
        self._time.hour = tuple(hours)
        return self

    def weekday(self, *args: int) -> 'Every':
        """
        @brief 设置星期规则
        @param args 星期值列表 (1-7, 1为周一)
        @return Every 返回自身，支持链式调用
        @exception TypeError 当传入的参数不是整数时抛出
        @exception ValueError 当星期值不在有效范围时抛出
        """
        weekdays = []

        for i in args:
            if not isinstance(i, int):
                raise TypeError(f'{i} is not a valid weekday.')

            if 1 <= i <= 7:
                weekdays.append(i)

            else:
                raise ValueError(f'{i} is not a valid weekday.')

        weekdays.sort()
        self._time.weekday = tuple(weekdays)
        return self

    def monthday(self, *args: int) -> 'Every':
        """
        @brief 设置日期规则
        @param args 日期值列表 (1-31)
        @return Every 返回自身，支持链式调用
        @exception TypeError 当传入的参数不是整数时抛出
        @exception ValueError 当日期值不在有效范围时抛出
        """
        monthdays = []

        for i in args:
            if not isinstance(i, int):
                raise TypeError(f'{i} is not a valid monthday.')

            if 1 <= i <= 31:
                monthdays.append(i)

            else:
                raise ValueError(f'{i} is not a valid monthday.')

        monthdays.sort()
        self._time.monthday = tuple(monthdays)
        return self

    def month(self, *args: int) -> 'Every':
        """
        @brief 设置月份规则
        @param args 月份值列表 (1-12)
        @return Every 返回自身，支持链式调用
        @exception TypeError 当传入的参数不是整数时抛出
        @exception ValueError 当月份值不在有效范围时抛出
        """
        months = []

        for i in args:
            if not isinstance(i, int):
                raise TypeError(f'{i} is not a valid month.')

            if 1 <= i <= 12:
                months.append(i)

            else:
                raise ValueError(f'{i} is not a valid month.')

        months.sort()
        self._time.month = tuple(months)
        return self

    @property
    def monday(self) -> 'Every':
        """
        @brief 添加周一到执行规则
        @return Every 返回自身，支持链式调用
        """
        weekdays = list(self._time.weekday)
        weekdays.append(1)
        self._time.weekday = tuple(weekdays)
        return self

    @property
    def tuesday(self) -> 'Every':
        """
        @brief 添加周二到执行规则
        @return Every 返回自身，支持链式调用
        """
        weekdays = list(self._time.weekday)
        weekdays.append(2)
        self._time.weekday = tuple(weekdays)
        return self

    @property
    def wednesday(self) -> 'Every':
        """
        @brief 添加周三到执行规则
        @return Every 返回自身，支持链式调用
        """
        weekdays = list(self._time.weekday)
        weekdays.append(3)
        self._time.weekday = tuple(weekdays)
        return self

    @property
    def thursday(self) -> 'Every':
        """
        @brief 添加周四到执行规则
        @return Every 返回自身，支持链式调用
        """
        weekdays = list(self._time.weekday)
        weekdays.append(4)
        self._time.weekday = tuple(weekdays)
        return self

    @property
    def friday(self) -> 'Every':
        """
        @brief 添加周五到执行规则
        @return Every 返回自身，支持链式调用
        """
        weekdays = list(self._time.weekday)
        weekdays.append(5)
        self._time.weekday = tuple(weekdays)
        return self

    @property
    def saturday(self) -> 'Every':
        """
        @brief 添加周六到执行规则
        @return Every 返回自身，支持链式调用
        """
        weekdays = list(self._time.weekday)
        weekdays.append(6)
        self._time.weekday = tuple(weekdays)
        return self

    @property
    def sunday(self) -> 'Every':
        """
        @brief 添加周日到执行规则
        @return Every 返回自身，支持链式调用
        """
        weekdays = list(self._time.weekday)
        weekdays.append(7)
        self._time.weekday = tuple(weekdays)
        return self

    @property
    def time(self) -> Time:
        """
        @brief 获取时间规则配置
        @return Time 时间规则配置对象
        """
        return self._time


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
