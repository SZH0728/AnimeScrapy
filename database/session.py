# -*- coding:utf-8 -*-
# AUTHOR: Sun
"""
@brief 数据库引擎与会话模块
@details 以模块级单例 session_factory 暴露异步会话工厂，仿照 config.py 的延迟初始化模式。
         init_db() 由 main.py 在 asyncio.run() 之前唯一调用，初始化后各 Storage 类
         通过 get_session() 上下文管理器获取 AsyncSession，禁止直接导入 session_factory 变量。
"""

from contextlib import asynccontextmanager
from logging import getLogger
from typing import AsyncGenerator

from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker, create_async_engine

logger = getLogger(__name__)

session_factory: async_sessionmaker[AsyncSession] | None = None


def init_db(database_url: str) -> None:
    """
    @brief 初始化异步数据库连接池
    @details 创建 asyncpg 引擎与 async_sessionmaker，赋值给模块级 session_factory。
             由 main.py 在 asyncio.run() 之前唯一调用，之后所有 Storage 通过
             get_session() 获取 AsyncSession，无需重复初始化。
    @param database_url asyncpg 连接字符串，格式：
                        postgresql+asyncpg://user:password@host:port/dbname
    """
    engine = create_async_engine(database_url)
    global session_factory
    session_factory = async_sessionmaker(engine, expire_on_commit=False)


@asynccontextmanager
async def get_session() -> AsyncGenerator[AsyncSession, None]:
    """
    @brief 获取一个异步数据库会话的上下文管理器
    @details 在运行时读取 session_factory，保证读取的是 init_db() 初始化后的值。
             Storage 类应通过此函数获取 AsyncSession，禁止直接导入 session_factory 变量
             （直接导入会在模块加载时捕获 None 值，init_db() 的更新对其不可见）。
    @return AsyncSession 实例
    @throws RuntimeError session_factory 尚未通过 init_db() 初始化时
    """
    if session_factory is None:
        raise RuntimeError("数据库未初始化，请先调用 init_db()")

    async with session_factory() as session:
        yield session


if __name__ == '__main__':
    pass
