# -*- coding:utf-8 -*-
# AUTHOR: Sun
"""
@brief 调试入口
@details 包含 VCR 录制模式与正常启动模式的本地调试入口逻辑，
         通过配置项 [app] use_vcr 控制是否注入 VCR 种子任务。
"""

import vcr as _vcr  # type: ignore[import-untyped]
import httpx

import asyncio

from config import config, setup_logging
from data.request import SingleHttpxRequestData
from database import init_db
from main import main

if __name__ == '__main__':
    setup_logging()
    init_db(config.get('bangumi', 'database_url'))

    _vcr_instance = _vcr.VCR(
        cassette_library_dir='cassettes',
        record_mode='new_episodes'
    )

    seed = SingleHttpxRequestData(
        retry=config.getint('bangumi', 'retry'),
        request=httpx.Request(
            'GET',
            'https://api.bgm.tv/calendar',
            headers={'User-Agent': config.get('bangumi', 'user_agent')},
        )
    )

    with _vcr_instance.use_cassette('bangumi.yaml'):
        asyncio.run(main(seed))
