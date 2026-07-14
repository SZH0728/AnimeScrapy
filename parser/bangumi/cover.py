# -*- coding:utf-8 -*-
# AUTHOR: Sun
"""
@brief 实现 Bangumi 封面图响应解析器
@details 从 HttpxResponseData 中提取图片字节，并通过 meta['db_id'] 关联数据库记录，
         产出 BangumiCoverStoreData 供后续存储器写入 subjects.cover_image 列。
"""

from logging import getLogger

from data.parse import BangumiCoverParseData
from data.request import RequestBaseData
from data.store import BangumiCoverStoreData, StoreBaseData
from parser.base import ParserBase

logger = getLogger(__name__)


class BangumiCoverParser(ParserBase[BangumiCoverParseData]):
    """
    @brief Bangumi 封面图解析器
    @details 从封面图 HTTP 响应中提取原始字节，结合 meta 中传递的 db_id，
             产出 BangumiCoverStoreData 供后续存储器写入数据库。
    """

    async def _do_parse(self, task: BangumiCoverParseData) -> BangumiCoverStoreData | None:
        """
        @brief 解析封面图响应，提取图片字节
        @param task 封面图响应解析输入，meta 中须包含 db_id
        @return BangumiCoverStoreData 落库数据包；meta 缺少 db_id 时返回 None
        """
        db_id = task.meta.get('db_id')

        if db_id is None:
            logger.warning(f"BangumiCoverParser meta 缺少 db_id，丢弃响应")
            return None

        results = BangumiCoverStoreData(db_id=db_id, image_bytes=task.response.content)

        logger.info(f"解析 {type(task).__name__} 产出 {results.db_id} 的后续任务")
        return results


if __name__ == '__main__':
    pass
