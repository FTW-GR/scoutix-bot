"""
Contains classes to be (re)used in various places
"""

import asyncio


class Timer:  # pylint: disable=too-few-public-methods
    """
    Executes a callback function after a specified timeout
    """

    def __init__(self, timeout, callback):
        self._timeout = timeout
        self._callback = callback
        self._task = asyncio.ensure_future(self._job())

    async def _job(self):
        """
        Runs the defined callback after timeout has passed
        """
        await asyncio.sleep(self._timeout)
        await self._callback()

    def cancel(self):
        """
        Cancels a future execution
        """
        self._task.cancel()
