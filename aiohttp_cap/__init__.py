# SPDX-FileCopyrightText: 2023 Alexander Sosedkin <monk@unboiled.info>
# SPDX-License-Identifier: CC-PDDC

import aiohttp
import asyncio
import contextlib


# If I were to use aio.http.TCPConnector, it'd be just
#class CappedSession:
#    def __init__(self, limit=None):
#        conn = aiohttp.TCPConnector(limit=limit)
#        self._session = aiohttp.ClientSession(connector=conn)
#
#    async def __aenter__(self):
#        await self._session.__aenter__()
#        return self
#
#    async def __aexit__(self, exc_t, exc_v, exc_tb):
#        await self._session.__aexit__(exc_t, exc_v, exc_tb)
#
#    def get(self, *a, **kwa):
#        return self._session.get(*a, **kwa)


# But I'm rolling my own high-level-interface limiter for learning purposes.


class CappedSession:
    def __init__(self, limit=None):
        self.session = aiohttp.ClientSession()
        self.semaphore = (asyncio.Semaphore(limit)
                          if limit else contextlib.nullcontext())

    async def __aenter__(self):
        await self.session.__aenter__()
        return self

    async def __aexit__(self, exc_t, exc_v, exc_tb):
        await self.session.__aexit__(exc_t, exc_v, exc_tb)

    def get(self, *a, **kwa):
        @contextlib.asynccontextmanager
        async def response():
            async with self.semaphore:
                async with self.session.get(*a, **kwa) as resp:
                    yield resp
        return response()
