# -*- coding:utf-8 -*-
# AUTHOR: Sun
"""
@brief 实现三种 HTTP 请求策略的具体请求器
@details 包含 SingleHttpRequester（单条请求）、BatchHttpRequester（并发批次）、
         ThrottledHttpRequester（节流顺序）三个 RequesterBase 子类。
         每个子类仅处理对应的一种请求数据包类型，通过 _do_request() 完成
         请求执行、异常捕获及重试递减，httpx.AsyncClient 在每次调用内创建销毁。
"""

import asyncio
from dataclasses import replace
from logging import getLogger

from httpx import AsyncClient, Request, Response, HTTPError

from data.request import (
    RequestBaseData,
    MultiHttpxRequestData,
    SingleHttpxRequestData,
    BatchHttpxRequestData,
    ThrottledHttpxRequestData,
)
from data.response import HttpxResponseData
from requester.base import RequesterBase

logger = getLogger(__name__)


class HttpRequesterMixin(object):
    """
    @brief HTTP 请求器工具 Mixin
    @details 提供三个请求器共用的无状态工具方法：响应包装、单条重试判断、批量重试追加。
             所有方法均为 @staticmethod，不携带任何实例状态。
    """

    @staticmethod
    def _handle_response(task: RequestBaseData, response: Response) -> HttpxResponseData | None:
        """
        @brief 将 httpx.Response 包装为 HttpxResponseData，并从请求任务复制 meta
        @param task 发起本次请求的任务数据包
        @param response httpx 响应对象
        @return 成功时返回 HttpxResponseData（meta 从 task.meta 复制）；404 时返回 None（资源不存在，链路终止）
        @throws httpx.HTTPStatusError 当响应状态为非 404 的错误码时由 raise_for_status() 抛出
        """
        if response.status_code == 404:
            return None

        response.raise_for_status()
        return HttpxResponseData(task=task, response=response, meta=task.meta)

    @staticmethod
    def _retry_single[T: RequestBaseData](task: T, exc: Exception) -> T | None:
        """
        @brief 单条请求的重试判断：retry > 1 时递减返回，否则记录日志后丢弃
        @param task 发生异常的请求任务
        @param exc 捕获到的异常
        @return 递减 retry 后的新任务；retry 耗尽时返回 None
        """
        if task.retry > 1:
            logger.warning(f'{type(task).__name__} 请求失败，剩余重试 {task.retry - 1} 次：{exc}')
            return replace(task, retry=task.retry - 1)

        logger.warning(f'{type(task).__name__} 请求失败且重试耗尽，任务已丢弃：{exc}')
        return None

    @staticmethod
    def _retry_batch[T: MultiHttpxRequestData](task: T, failed: list[Request]) -> None | T:
        """
        @brief 批量请求的重试追加：有失败时追加重试任务或记录丢弃日志
        @param task 原始批量请求任务
        @param failed 本轮失败的请求列表
        @return 无失败或 retry 耗尽时返回 None；有失败且 retry > 1 时返回递减后的新批次任务
        """
        if not failed:
            return None

        if task.retry > 1:
            return replace(task, requests=failed, retry=task.retry - 1)

        logger.warning(f'{type(task).__name__} {len(failed)} 条请求失败且重试耗尽，已丢弃')
        return None


class SingleHttpRequester(RequesterBase[SingleHttpxRequestData], HttpRequesterMixin):
    """
    @brief 单条 HTTP 请求器
    @details 每次 handle() 发送一条 httpx.Request，成功返回 HttpxResponseData，
             失败时递减 retry 并返回重试任务；retry 耗尽则记录 warning 后返回 None。
    """

    async def _do_request(self, task: SingleHttpxRequestData) -> HttpxResponseData | SingleHttpxRequestData | None:
        """
        @brief 执行单条 HTTP 请求
        @param task 携带单条 httpx.Request 的请求数据包
        @return HttpxResponseData 请求成功；SingleHttpxRequestData retry 递减重试；None 耗尽重试
        """
        try:
            async with AsyncClient() as client:
                response = await client.send(task.request)

            result = self._handle_response(task, response)
            if result is not None:
                logger.info(f"请求成功 [{task.request.url}]")
            return result
        except HTTPError as e:
            logger.warning(f'{task.request.url} 请求失败：{e}')
            return self._retry_single(task, e)


class BatchHttpRequester(RequesterBase[BatchHttpxRequestData], HttpRequesterMixin):
    """
    @brief 并发批次 HTTP 请求器
    @details 用 asyncio.Semaphore 控制本批次最大并发数，asyncio.gather 并发执行所有请求。
             失败子集在 retry > 1 时构造新的 BatchHttpxRequestData 投回总线重试。
    """

    async def _do_request(self, task: BatchHttpxRequestData) -> list[HttpxResponseData | BatchHttpxRequestData | None]:
        """
        @brief 并发执行批次中所有 HTTP 请求
        @param task 携带多条 httpx.Request 及并发控制参数的批次请求数据包
        @return 成功响应列表，retry > 1 时末尾追加重试任务
        """
        results: list[HttpxResponseData | BatchHttpxRequestData | None] = []
        failed_requests: list[Request] = []
        semaphore = asyncio.Semaphore(task.max_concurrent)

        async with AsyncClient() as client:
            raw_results = await asyncio.gather(
                *[self._send(request, client, semaphore) for request in task.requests],
                return_exceptions=True,
            )

        for request, result in zip(task.requests, raw_results):
            if isinstance(result, HTTPError):
                logger.warning(f'{request.url} 请求失败：{result}')
                failed_requests.append(request)
            elif isinstance(result, BaseException):
                raise result
            else:
                results.append(self._handle_response(task, result))

        success_count = sum(1 for r in results if r is not None)
        logger.info(
            f"批量请求完成，共 {len(task.requests)} 条，"
            f"成功 {success_count} 条，失败 {len(failed_requests)} 条"
        )
        results.append(self._retry_batch(task, failed_requests))
        return results

    @staticmethod
    async def _send(request: Request, client: AsyncClient, semaphore: asyncio.Semaphore) -> Response:
        """
        @brief 在 Semaphore 许可下发送单条请求
        @param request 待发送的 httpx.Request
        @param client 当前批次共享的 AsyncClient
        @param semaphore 控制最大并发数的信号量
        @return httpx 响应对象
        """
        async with semaphore:
            return await client.send(request)


class ThrottledHttpRequester(RequesterBase[ThrottledHttpxRequestData], HttpRequesterMixin):
    """
    @brief 节流顺序 HTTP 请求器
    @details 按列表顺序依次发送请求，每条完成后等待 task.interval 秒（末条不等待）。
             interval 语义为"上一条请求完成后开始计时"。
             失败子集在 retry > 1 时构造新的 ThrottledHttpxRequestData 投回总线重试。
    """

    async def _do_request(self, task: ThrottledHttpxRequestData) -> list[HttpxResponseData | ThrottledHttpxRequestData | None]:
        """
        @brief 节流顺序执行所有 HTTP 请求
        @param task 携带多条 httpx.Request 及节流间隔的请求数据包
        @return 成功响应列表，retry > 1 时末尾追加重试任务
        """
        results: list[HttpxResponseData | ThrottledHttpxRequestData | None] = []
        failed_requests: list[Request] = []
        last_index = len(task.requests) - 1

        async with AsyncClient() as client:
            for i, request in enumerate(task.requests):
                try:
                    response = await client.send(request)
                    results.append(self._handle_response(task, response))
                except HTTPError as e:
                    logger.warning(f'{request.url} 请求失败：{e}')
                    failed_requests.append(request)

                # interval 语义：上一条完成后计时，末条不等待
                if i < last_index:
                    await asyncio.sleep(task.interval)

        success_count = sum(1 for r in results if r is not None)
        logger.info(
            f"节流请求完成，共 {len(task.requests)} 条，"
            f"成功 {success_count} 条，失败 {len(failed_requests)} 条"
        )
        results.append(self._retry_batch(task, failed_requests))
        return results


if __name__ == '__main__':
    pass
