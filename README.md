# Disclaimer

This project is written purely for learning purposes.
Don't use it, use the limits in `aiohttp.TCPConnector` instead.

# Goals

* Write a toy pooling library
  to limit the amount of established async HTTP connections
  (functionality analogous to limit= and limit_per_host= in aiohttp,
   but implemented externally)
* Learn what are the industry standard practices for testing asyncio code.
* Implement unit test and integration tests for my toy library.
* Add static typing and a CI job that checks types.
