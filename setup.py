# SPDX-FileCopyrightText: 2023 Alexander Sosedkin <monk@unboiled.info>
# SPDX-License-Identifier: CC-PDDC

from setuptools import setup

setup(
    name='aiohttp_cap',
    version='0.0.1',
    url='https://github.com/t184256/aiohttp_cap',
    author='Alexander Sosedkin',
    author_email='monk@unboiled.info',
    description="learning project, do not use",
    packages=[
        'aiohttp_cap',
    ],
    install_requires=[
        'aiohttp'
    ],
    tests_require=[
        'pytest', 'pytest-asyncio'
    ],
)
