# SPDX-FileCopyrightText: 2023 Alexander Sosedkin <monk@unboiled.info>
# SPDX-License-Identifier: CC-PDDC

"""Test SlowServer testing helper with ClientSession limiting functionality."""

import asyncio
import multiprocessing
import time
import typing

import aiohttp

import pytest

import connections_counter
import slow_http_server


ServerCounter = typing.Tuple[slow_http_server.SlowServer,
                             connections_counter.ConnectionsCounter]
T = typing.TypeVar('T')
FixtureYielding = typing.Generator[T, None, None]


@pytest.fixture(name='server_counter', scope='module')
def fixture_server_counter() -> FixtureYielding[ServerCounter]:
    """Spin up a SlowServer to test against: fixture."""
    port = slow_http_server.find_port('127.0.0.1')
    c_counter = connections_counter.ConnectionsCounter()
    slow_server = slow_http_server.SlowServer('127.0.0.1', port,
                                              c_counter.increment,
                                              c_counter.decrement)
    process = multiprocessing.Process(target=slow_server.serve_forever)
    process.start()
    yield slow_server, c_counter
    process.terminate()
    process.join()


async def request(session: aiohttp.ClientSession, url: str
                  ) -> typing.Tuple[float, float]:
    """Issue a single request to a given URL."""
    async with session.get(url) as resp:
        assert resp.status == 200
        status_time = time.time()
        assert await resp.text() == ''.join(f'{i}\n' for i in range(10))
        end_time = time.time()
        return status_time, end_time


@pytest.mark.asyncio
async def test_single_request(server_counter: ServerCounter) -> None:
    """Issue a single request to SlowServer, time it."""
    server, conn_counter = server_counter
    conn_counter.reset()
    assert conn_counter.max == 0
    async with aiohttp.ClientSession() as session:
        init_time = time.time()
        status_time, end_time = await request(session, server.url)
        assert 0 < status_time - init_time < .1  # status arrives quickly
        assert 1 < end_time - init_time < 1.1  # response arrives in ~1s
    assert conn_counter.max == 1


@pytest.mark.asyncio
async def test_concurrent_requests(server_counter: ServerCounter) -> None:
    """Issue many requests to SlowServer, time them, check max connections."""
    server, conn_counter = server_counter
    async with aiohttp.ClientSession() as session:
        # warm up
        conn_counter.reset()
        assert conn_counter.max == 0
        await asyncio.gather(*[request(session, server.url)
                               for _ in range(30)])
        assert 10 <= conn_counter.max <= 30
        conn_counter.reset()
        assert conn_counter.max == 0

        # measure after warming up
        init_time = time.time()
        coros = [request(session, server.url) for _ in range(30)]
        times = await asyncio.gather(*coros)
        print(min(status_time - init_time for status_time, _ in times))
        print(max(status_time - init_time for status_time, _ in times))
        print(min(end_time - init_time for _, end_time in times))
        print(max(end_time - init_time for _, end_time in times))
        assert all(0 < status_time - init_time < .1  # status arrives quickly
                   for status_time, _ in times)
        assert all(1 < end_time - init_time < 1.1  # response arrives in ~1s
                   for _, end_time in times)
        assert conn_counter.max == 30
