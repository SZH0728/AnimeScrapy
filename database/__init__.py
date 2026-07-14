# -*- coding:utf-8 -*-
# AUTHOR: Sun
"""
@brief database 包公共接口
@details 重导出 models 与 session 子模块的所有公共符号，
         保证 `from database import ...` 的用法与原 database.py 完全兼容。
"""

from database.models import Base, Rating, SeasonType, Subject
from database.session import get_session, init_db

__all__ = [
    'Base',
    'SeasonType',
    'Subject',
    'Rating',
    'init_db',
    'get_session',
]
