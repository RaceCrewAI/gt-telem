"""
Utility functions for event handling.

This module provides helper functions to reduce code duplication
in event handler classes.
"""

import asyncio
from typing import Any, Callable, List


async def invoke_callbacks(callbacks: List[Callable], *args: Any) -> None:
    """
    Invoke a list of callbacks, handling both sync and async callbacks.

    This helper function checks each callback to determine if it's a coroutine
    function (async) or a regular function (sync), and invokes it appropriately.

    Parameters:
        callbacks: List of callback functions to invoke
        *args: Arguments to pass to each callback

    Example:
        await invoke_callbacks(self.on_lap_change, lap_number)
        await invoke_callbacks(self.on_race_start)
    """
    for callback in callbacks:
        if asyncio.iscoroutinefunction(callback):
            await callback(*args)
        else:
            callback(*args)
