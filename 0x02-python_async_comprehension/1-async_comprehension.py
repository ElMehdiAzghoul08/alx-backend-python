#!/usr/bin/env python3
"""Module"""


from typing import List
import asyncio

async_generator = __import__('0-async_generator').async_generator


async def async_comprehension() -> List[float]:
    "async_comprehension"
    return [number async for number in async_generator()]
