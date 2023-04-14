# SPDX-FileCopyrightText: 2023 Alexander Sosedkin <monk@unboiled.info>
# SPDX-License-Identifier: CC-PDDC

import aiohttp
import asyncio
import multiprocessing
import time

import pytest

import connections_counter
import slow_http_server


@pytest.fixture(scope='module')
def server_fixture():
    port = slow_http_server.find_port('127.0.0.1')
    c_counter = connections_counter.ConnectionsCounter()
    slow_server = slow_http_server.SlowServer('127.0.0.1', port,
                                              c_counter.increment,
                                              c_counter.decrement)
    slow_server.connections_counter = c_counter
    p = multiprocessing.Process(target=slow_server.serve_forever)
    p.start()
    yield slow_server
    p.terminate()
    p.join()


async def request(session, url):
    async with session.get(url) as resp:
        assert resp.status == 200
        status_time = time.time()
        assert await resp.text() == ''.join(f'{i}\n' for i in range(10))
        end_time = time.time()
        return status_time, end_time


@pytest.mark.asyncio
async def test_single_request(server_fixture):
    server_fixture.connections_counter.reset()
    assert server_fixture.connections_counter.max.value == 0
    async with aiohttp.ClientSession() as session:
        init_time = time.time()
        status_time, end_time = await request(session, server_fixture.url)
        assert 0 < status_time - init_time < .1  # status arrives quickly
        assert 1 < end_time - init_time < 1.1  # response arrives in ~1s
    assert server_fixture.connections_counter.max.value == 1


@pytest.mark.asyncio
async def test_concurrent_requests(server_fixture):
    async with aiohttp.ClientSession() as session:
        # warm up
        server_fixture.connections_counter.reset()
        assert server_fixture.connections_counter.max.value == 0
        await asyncio.gather(*[request(session, server_fixture.url)
                               for _ in range(30)])
        assert 10 <= server_fixture.connections_counter.max.value <= 30
        server_fixture.connections_counter.reset()
        assert server_fixture.connections_counter.max.value == 0

        # measure after warming up
        init_time = time.time()
        coros = [request(session, server_fixture.url) for _ in range(30)]
        times = await asyncio.gather(*coros)
        print(min(status_time - init_time for status_time, _ in times))
        print(max(status_time - init_time for status_time, _ in times))
        print(min(end_time - init_time for _, end_time in times))
        print(max(end_time - init_time for _, end_time in times))
        assert all(0 < status_time - init_time < .1  # status arrives quickly
                   for status_time, _ in times)
        assert all(1 < end_time - init_time < 1.1  # response arrives in ~1s
                   for _, end_time in times)
        assert server_fixture.connections_counter.max.value == 30
