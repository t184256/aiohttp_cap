# SPDX-FileCopyrightText: 2023 Alexander Sosedkin <monk@unboiled.info>
# SPDX-License-Identifier: CC-PDDC

import aiohttp
import asyncio
import time


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
# Session acquiring is intentionally folded into Response to make life harder.

class Response:
    def __init__(self, semaphore, *a, **kwa):
        self.semaphore = semaphore
        self.a, self.kwa = a, kwa

    async def __aenter__(self):
        # acquire a rate-limiting semaphore
        if self.semaphore is not None:
            await self.semaphore.acquire()
        # beginning of async with aiohttp.ClientSession() as self.sess:
        self.sess = await aiohttp.ClientSession().__aenter__()
        # beginning of async with self.sess.get(...) as self.response:
        self.response = self.sess.get(*self.a, **self.kwa)
        return await self.response.__aenter__()

    async def __aexit__(self, exc_t, exc_v, exc_tb):
        # end of async with self.sess.get(...)
        r1 = await self.response.__aexit__(exc_t, exc_v, exc_tb)
        # end of async with aiohttp.ClientSession()
        r2 = await self.sess.__aexit__(exc_t, exc_v, exc_tb)
        # release a rate-limiting semaphore
        if self.semaphore is not None:
            self.semaphore.release()
        return r1 or r2  # not sure this is fully correct


class CappedSession:
    def __init__(self, limit=None):
        self.semaphore = asyncio.Semaphore(limit) if limit else None

    async def __aenter__(self):
        return self

    async def __aexit__(self, exc_t, exc_v, exc_tb):
        pass

    def get(self, *a, **kwa):
        return Response(self.semaphore, *a, **kwa)
