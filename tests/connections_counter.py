# SPDX-FileCopyrightText: 2023 Alexander Sosedkin <monk@unboiled.info>
# SPDX-License-Identifier: CC-PDDC

"""Testing helper: connection counter that works across processes/threads."""

import multiprocessing
import threading


class ConnectionsCounter:
    """
    Connection counter that works across processes/threads.

    Interface:
        .current.value
        .max.value
        increment()
        decrement()
        reset()
    """

    def __init__(self):
        """Initialize a counter."""
        self.current = multiprocessing.Value('I', 0)
        self.max = multiprocessing.Value('I', 0)
        self._lock = threading.Lock()

    def increment(self):
        """Increment a counter."""
        with self._lock:
            self.current.value += 1
            if self.current.value > self.max.value:
                self.max.value = self.current.value

    def decrement(self):
        """Decrement a counter."""
        with self._lock:
            self.current.value -= 1

    def reset(self):
        """Reset a counter, together with max value."""
        with self._lock:
            self.current.value = self.max.value = 0
