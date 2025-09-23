# -*- coding:utf-8 -*-
# AUTHOR: Sun

from logging import getLogger

from database.model import Web, SessionFactory

logger = getLogger(__name__)


class WebPriority(object):
    """
    @brief 网站优先级管理类

    该类用于管理和遍历按照优先级排序的网站列表，支持向前和向后遍历网站列表
    """
    def __init__(self):
        """
        @brief 初始化WebPriority对象

        从数据库中查询所有网站，并按优先级升序排列存储在内部列表中
        """
        logger.debug('Initialize WebPriority, selecting webs...')
        with SessionFactory() as session:
            self._webs: list[Web] = session.query(Web).order_by(Web.priority.asc()).all()
        logger.info(f'Selected {len(self._webs)} webs successfully')

        self._current: int = 0
        self.web_list: list[int] = [web.id for web in self._webs]

    @property
    def current_web_id(self) -> int:
        """
        @brief 获取当前网站的ID

        @return 当前网站的ID
        @retval int 当前网站的ID值
        """
        return self._webs[self._current].id

    @property
    def current_web_name(self):
        """
        @brief 获取当前网站的名称

        @return 当前网站的名称
        @retval str 当前网站的名称
        """
        return self._webs[self._current].name

    def next(self) -> bool:
        """
        @brief 移动到下一个网站

        将当前索引向前移动一位，如果已经到达列表末尾则不移动并返回False

        @return 是否成功移动到下一个网站
        @retval bool True表示成功移动，False表示已到达列表末尾
        """
        self._current += 1

        if self._current >= len(self._webs):
            self._current = len(self._webs) - 1
            return False

        return True

    def previous(self) -> bool:
        """
        @brief 移动到上一个网站

        将当前索引向后移动一位，如果已经到达列表开头则不移动并返回False

        @return 是否成功移动到上一个网站
        @retval bool True表示成功移动，False表示已到达列表开头
        """
        self._current -= 1

        if self._current < 0:
            self._current = 0
            return False

        return True


if __name__ == '__main__':
    pass
