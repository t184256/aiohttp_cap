#!/usr/bin/env python3

# SPDX-FileCopyrightText: 2023 Alexander Sosedkin <monk@unboiled.info>
# SPDX-License-Identifier: CC-PDDC

"""Testing helper: a slow HTTP server."""

import http.server
import socket
import time


def find_port(address='127.0.0.1'):
    """
    Find a free port to listen on.

    Race-condition-prone, but still better than just random.
    """
    sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    sock.bind((address, 0))
    sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
    _, port = sock.getsockname()
    sock.close()
    return port


class SlowServer(http.server.ThreadingHTTPServer):
    """Deliberately slow http server used for testing purposes."""

    def __init__(self, address='127.0.0.1', port=8000,
                 callback_start=None, callback_stop=None):
        """
        Initialize a SlowServer.

        :param str address: address to listen at
        :param int port: port to listen at
        :param callback_start: callback to invoke before serving the data
        :param callback_stop: callback to invoke after serving the data
        """
        class SlowHTTPRequestHandler(http.server.BaseHTTPRequestHandler):
            """HTTPRequestHandler that trickles data byte-by-byte."""

            protocol_version = "HTTP/1.1"

            def do_HEAD(self):  # pylint: disable=invalid-name
                """Fairly normal HEAD HTTP method implementation."""
                self.send_response(http.server.HTTPStatus.OK)
                self.send_header('Content-Length', 2 * 10)
                self.end_headers()

            def do_GET(self):  # pylint: disable=invalid-name
                """Slow GET HTTP method implementation, offers callbacks."""
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


__all__ = ['find_port', 'SlowServer']
