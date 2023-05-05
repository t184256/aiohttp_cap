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

import aiohttp


class CappedSession:
    """Analogous to aiohttp.ClientSession, but with a connection limit."""

    def __init__(self, limit=None):
        """
        Like aiohttp.ClientSession, but with a connection limit.

        :param int limit: maximum number of simultaneous connections
        """
        self.session = aiohttp.ClientSession()
        self.semaphore = (asyncio.Semaphore(limit)
                          if limit else contextlib.nullcontext())

    async def __aenter__(self):

        await self.session.__aenter__()
        return self

    async def __aexit__(self, exc_t, exc_v, exc_tb):
        await self.session.__aexit__(exc_t, exc_v, exc_tb)

    def get(self, *a, **kwa):
        """Proxies aiohttp.ClientSession.get."""
        @contextlib.asynccontextmanager
        async def response():
            async with self.semaphore:
                async with self.session.get(*a, **kwa) as resp:
                    yield resp
        return response()


__all__ = ['CappedSession']
