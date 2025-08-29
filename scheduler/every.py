# -*- coding:utf-8 -*-
# AUTHOR: Sun

"""
@file every.py
@brief 时间规则构建器
@details 时间规则构建器，用于指定任务的执行时间
"""

from dataclasses import dataclass, field


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

if __name__ == '__main__':
    pass
