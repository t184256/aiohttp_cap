# SPDX-FileCopyrightText: 2023 Alexander Sosedkin <monk@unboiled.info>
# SPDX-License-Identifier: CC-PDDC

"""Unit-test CappedSession."""

import asyncio
import unittest.mock

import pytest

import aiohttp_cap


@pytest.mark.asyncio
async def test_mocked():
    """Test CappedSession against a mocked ClientSession.get."""
    with unittest.mock.patch('aiohttp.ClientSession.get') as mock:
        async with aiohttp_cap.CappedSession(limit=3) as session:
            async def fake_request(session, index, duration):
                async with session.get(f'http://nonex/{index}') as mock:
                    await asyncio.sleep(duration)
                    await mock.end(index)

            await fake_request(session, 0, 0)
            # pylint: disable=unnecessary-dunder-call
            mock().__aenter__.assert_called_with()
            mock().__aexit__.assert_called_with(None, None, None)
            mock.assert_has_calls([
                # #0 begins...
                unittest.mock.call('http://nonex/0'),
                unittest.mock.call().__aenter__(),
                # ... and completes
                unittest.mock.call().__aenter__().end(0),
                unittest.mock.call().__aexit__(None, None, None),
            ])
            mock.reset_mock()

            durations = [0.7, 0.4, 0.2, 0.3, 0.2]
            # 0000000
            # 1111
            # 22
            #   333
            #     44
            await asyncio.gather(*[fake_request(session, i, duration)
                                   for i, duration in enumerate(durations)])
            print(mock.mock_calls)
            mock.assert_has_calls([
                # 0.0: #1-#3 begin at once
                unittest.mock.call('http://nonex/0'),
                unittest.mock.call().__aenter__(),
                unittest.mock.call('http://nonex/1'),
                unittest.mock.call().__aenter__(),
                unittest.mock.call('http://nonex/2'),
                unittest.mock.call().__aenter__(),
                # 0.2: #2 finishes, #3 begins
                unittest.mock.call().__aenter__().end(2),
                unittest.mock.call().__aexit__(None, None, None),
                unittest.mock.call('http://nonex/3'),
                unittest.mock.call().__aenter__(),
                # 0.4: #1 finishes, #4 begins
                unittest.mock.call().__aenter__().end(1),
                unittest.mock.call().__aexit__(None, None, None),
                unittest.mock.call('http://nonex/4'),
                unittest.mock.call().__aenter__(),
                # 0.5: #3 finishes
                unittest.mock.call().__aenter__().end(3),
                unittest.mock.call().__aexit__(None, None, None),
                # 0.6: #4 finishes
                unittest.mock.call().__aenter__().end(4),
                unittest.mock.call().__aexit__(None, None, None),
                # 0.7: #0 finishes
                unittest.mock.call().__aenter__().end(0),
                unittest.mock.call().__aexit__(None, None, None),
            ])
