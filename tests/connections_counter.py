# SPDX-FileCopyrightText: 2023 Alexander Sosedkin <monk@unboiled.info>
# SPDX-License-Identifier: CC-PDDC

"""Testing helper: connection counter that works across processes/threads."""

import multiprocessing
import threading


class ConnectionsCounter:
    """Connection counter that works across processes/threads."""

    def __init__(self) -> None:
        """Initialize a counter."""
        self._current = multiprocessing.Value('I', 0)
        self._max = multiprocessing.Value('I', 0)
        self._lock = threading.Lock()

    def increment(self) -> None:
        """Increment a counter, together with max value as well if needed."""
        with self._lock:
            # https://github.com/python/typeshed/issues/8799
            self._current.value += 1  # type: ignore[attr-defined]
            if (self._current.value >  # type: ignore[attr-defined]
                    self._max.value):  # type: ignore[attr-defined]
                self._max.value = (  # type: ignore[attr-defined]
                    self._current.value  # type: ignore[attr-defined]
                )

    def decrement(self) -> None:
        """Decrement a counter."""
        with self._lock:
            self._current.value -= 1  # type: ignore[attr-defined]

    def reset(self) -> None:
        """Reset a counter, together with max value."""
        with self._lock:
            self._current.value = 0  # type: ignore[attr-defined]
            self._max.value = 0  # type: ignore[attr-defined]

    @property
    def current(self) -> int:
        """Return the current counter value."""
        with self._lock:
            val: int
            val = self._current.value  # type: ignore[attr-defined]
            return val

    @property
    def max(self) -> int:
        """Return the max observed counter value since reset."""
        with self._lock:
            val: int
            val = self._max.value  # type: ignore[attr-defined]
            return val
