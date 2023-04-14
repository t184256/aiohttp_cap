# SPDX-FileCopyrightText: 2023 Alexander Sosedkin <monk@unboiled.info>
# SPDX-License-Identifier: CC-PDDC

import multiprocessing
import threading

class ConnectionsCounter:
    def __init__(self):
        self.current = multiprocessing.Value('I', 0)
        self.max = multiprocessing.Value('I', 0)
        self._lock = threading.Lock()

    def increment(self):
        with self._lock:
            self.current.value += 1
            if self.current.value > self.max.value:
                self.max.value = self.current.value

    def decrement(self):
        with self._lock:
            self.current.value -= 1

    def reset(self):
        with self._lock:
            self.current.value = self.max.value = 0


