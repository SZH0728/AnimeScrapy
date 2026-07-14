# -*- coding:utf-8 -*-
# AUTHOR: Sun
"""
@brief BangumiCoverStorage：封面图字节存储器
@details 接收 BangumiCoverStoreData，将图片字节 UPDATE 到 subjects.cover_image 列。
         通过 db_id 精确定位数据库行，UPDATE 操作幂等，链路终止后返回 None。
"""

from logging import getLogger

from sqlalchemy import update

from data.store import BangumiCoverStoreData
from database import Subject, get_session
from storage.base import StorageBase

logger = getLogger(__name__)


class BangumiCoverStorage(StorageBase[BangumiCoverStoreData]):
    """
    @brief Bangumi 封面图字节存储器
    @details 将封面图原始字节写入 subjects.cover_image 列。
             使用 UPDATE WHERE id = db_id 精确定位行，操作幂等，重复写入不报错。
    """

    async def _do_store(self, task: BangumiCoverStoreData) -> None:
        """
        @brief 将封面图字节更新到 subjects 表
        @param task 封面图落库数据包，含 db_id 与 image_bytes
        @return None（链路终止）
        """
        async with get_session() as session:
            await session.execute(
                update(Subject)
                .where(Subject.id == task.db_id)
                .values(cover_image=task.image_bytes)
            )

            await session.commit()

        logger.info(f"写入 1 条 {type(task).__name__} 数据")


if __name__ == '__main__':
    pass
