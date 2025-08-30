# -*- coding:utf-8 -*-
# AUTHOR: Sun

from logging import getLogger

from database.model import Web, SessionFactory

logger = getLogger(__name__)


class WebPriority(object):
    def __init__(self):
        logger.debug('Initialize WebPriority, selecting webs...')
        with SessionFactory() as session:
            self._webs: list[Web] = session.query(Web).order_by(Web.priority.asc()).all()
        logger.info(f'Selected {len(self._webs)} webs successfully')

        self._current: int = 0

    @property
    def current_web_id(self) -> int:
        return self._webs[self._current].id

    @property
    def current_web_name(self):
        return self._webs[self._current].name

    def next(self) -> bool:
        self._current += 1

        if self._current >= len(self._webs):
            self._current = len(self._webs) - 1
            return False

        return True

    def previous(self) -> bool:
        self._current -= 1

        if self._current < 0:
            self._current = 0
            return False

        return True


if __name__ == '__main__':
    pass
