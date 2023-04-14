# SPDX-FileCopyrightText: 2023 Alexander Sosedkin <monk@unboiled.info>
# SPDX-License-Identifier: CC-PDDC

import aiohttp
import asyncio
import time


class CappedSession:
    def __init__(self, limit=None):
        # TODO: implement this myself
        conn = aiohttp.TCPConnector(limit=limit)
        self._session = aiohttp.ClientSession(connector=conn)
        pass

    async def __aenter__(self):
        await self._session.__aenter__()
        return self

    async def __aexit__(self, exc_t, exc_v, exc_tb):
        await self._session.__aexit__(exc_t, exc_v, exc_tb)

    def get(self, *a, **kwa):
        return self._session.get(*a, **kwa)
