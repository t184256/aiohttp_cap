# SPDX-FileCopyrightText: 2023 Alexander Sosedkin <monk@unboiled.info>
# SPDX-License-Identifier: CC-PDDC

"""
Test project, do not use.

Limits the amount of simultaneous connections for aiohttp.
If I were to use aio.http.TCPConnector, it'd be just

```
class CappedSession:
    def __init__(self, limit=None):
        conn = aiohttp.TCPConnector(limit=limit)
        self._session = aiohttp.ClientSession(connector=conn)

    async def __aenter__(self):
        await self._session.__aenter__()
        return self

    async def __aexit__(self, exc_t, exc_v, exc_tb):
        await self._session.__aexit__(exc_t, exc_v, exc_tb)

    def get(self, *a, **kwa):
        return self._session.get(*a, **kwa)
```

But I'm rolling my own high-level-interface limiter for learning purposes.
"""

import asyncio
import contextlib
import types
import typing

import aiohttp


T = typing.TypeVar('T')
AsyncYields = typing.AsyncGenerator[T, None]

P = typing.ParamSpec('P')


class CappedSession:
    """Analogous to aiohttp.ClientSession, but with a connection limit."""

    def __init__(self, limit: typing.Optional[int] = None) -> None:
        """
        Like aiohttp.ClientSession, but with a connection limit.

        :param int limit: maximum number of simultaneous connections
        """
        self.session = aiohttp.ClientSession()
        self.semaphore = (asyncio.Semaphore(limit)
                          if limit else contextlib.nullcontext())

    async def __aenter__(self) -> typing.Self:
        await self.session.__aenter__()
        return self

    async def __aexit__(self,
                        exc_type: typing.Optional[typing.Type[BaseException]],
                        exc: typing.Optional[BaseException],
                        traceback: typing.Optional[types.TracebackType],
                        ) -> None:
        await self.session.__aexit__(exc_type, exc, traceback)
        # returns nothing, so we also return nothing

    # kwa: Any is also how the actual .get() wraps .request() inside aiohttp
    def get(self, url: aiohttp.typedefs.StrOrURL, **kwa: typing.Any
            ) -> typing.AsyncContextManager[aiohttp.ClientResponse]:
        """Proxies aiohttp.ClientSession.get."""
        @contextlib.asynccontextmanager
        async def response() -> AsyncYields[aiohttp.ClientResponse]:
            # must be a typeshed bug,
            # one sure can async with on asyncio.Semaphore
            async with self.semaphore:  # type: ignore[attr-defined]
                async with self.session.get(url, **kwa) as resp:
                    yield resp
        return response()


__all__ = ['CappedSession']
