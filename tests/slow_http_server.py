#!/usr/bin/env python3

# SPDX-FileCopyrightText: 2023 Alexander Sosedkin <monk@unboiled.info>
# SPDX-License-Identifier: CC-PDDC

import http.server
import socket
import time


def find_port(address='127.0.0.1'):
    # race-condition-prone, but still better than just random
    s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    s.bind((address, 0))
    s.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
    _, port = s.getsockname()
    s.close()
    return port


class SlowServer(http.server.ThreadingHTTPServer):
    def __init__(self, address='127.0.0.1', port=8000,
                 callback_start=None, callback_stop=None):
        class SlowHTTPRequestHandler(http.server.BaseHTTPRequestHandler):
            protocol_version = "HTTP/1.1"

            def do_HEAD(self):
                self.send_response(http.server.HTTPStatus.OK)
                self.send_header('Content-Length', 2 * 10)
                self.end_headers()

            def do_GET(self):
                self.do_HEAD()
                if callback_start:
                    callback_start()
                for i in range(10):
                    time.sleep(.1)
                    self.wfile.write(str(i).encode() + b'\n')
                    self.wfile.flush()
                if callback_stop:
                    callback_stop()

        self.url = f'http://{address}:{port}'
        super().__init__((address, port), SlowHTTPRequestHandler)


if __name__ == '__main__':
    SlowServer().serve_forever()
