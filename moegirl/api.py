import aiohttp
import asyncio
import json
from typing import Any, Mapping
from .error import MoegirlUpstreamError, MoegirlTimeoutError, MoegirlRateLimitedError
class MoegirlClient:
    def __init__(
        self,
        *,
        api_base: str,
        user_agent: str,
        timeout: float,
        max_retries: int,
        fallback_api_base: str | None = None,
    ) -> None:
        self.api_base = api_base
        self.user_agent = user_agent
        self.timeout = timeout
        self.max_retries = max_retries
        self.fallback_api_base = fallback_api_base
        self._session: aiohttp.ClientSession | None = None
    async def _ensure_session(self) -> aiohttp.ClientSession:
        if not self._session or self._session.closed:
            self._session = aiohttp.ClientSession(
                headers={"User-Agent": self.user_agent},
                timeout=aiohttp.ClientTimeout(total=self.timeout),
            )
        return self._session
    async def __aenter__(self) -> MoegirlClient:
        await self._ensure_session()
        return self
    async def __aexit__(self, *exc: object) -> None:
        await self.aclose()
    async def aclose(self) -> None:
        session,self._session=self._session,None
        if session is not None and not session.closed:
           await session.close()
    async def _get_from_api(self, endpoint: str, params: Mapping[str, str | int] ) -> Any:
        """向萌娘百科发一次请求"""
        session = await self._ensure_session()
        attempts = 0
        while True:
            try:
                async with session.get(endpoint, params=params) as resp:
                    status = resp.status
                    body = await resp.text()
            except asyncio.TimeoutError as exc:
                raise MoegirlTimeoutError(f"萌娘百科请求 {endpoint} 超时：{self.timeout}秒") from exc
            except aiohttp.ClientConnectionError as exc:
                raise
            except aiohttp.ClientError as exc:
                raise MoegirlUpstreamError(f"萌娘百科请求 {endpoint} 失败：{exc}") from exc
            if status == 429:
                if attempts >= self.max_retries:
                    raise MoegirlRateLimitedError(f"萌娘百科请求 {endpoint} 被限速：{self.max_retries}次")
                attempts += 1
                await asyncio.sleep(1)
                continue
            if status >= 500:
                raise MoegirlUpstreamError(f"萌娘百科请求 {endpoint} 失败：{status}")
            try:
                payload = json.loads(body)
            except ValueError as exc:
                raise MoegirlUpstreamError(f"{endpoint} 返回了非 JSON 内容（HTTP {status}）：{body[:120]!r}") from exc
            return payload
