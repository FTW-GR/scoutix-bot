#!/usr/bin/env python
"""
The main bot class module
"""
import asyncio
import functools
import signal

import pydle

import modules


class Bot(pydle.Client):
    """
    Main bot class
    This defines the event types on which the bot interacts.
    Interactions should live in modules and not here.
    """

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.cmd_char = "!"
        self.module_config = {}
        self.eventloop.add_signal_handler(
            signal.SIGINT,
            functools.partial(asyncio.ensure_future,
                              self.quit("Exiting. Process interrupted!"))
        )
        self.data = {}
        self._modules = None

    @property
    def modules(self):
        """
        Returns a list of instances of the configured module classes
        """
        if self._modules is None:
            configured_modules = self.module_config.keys()
            self._modules = [getattr(modules, f"{module}Module")(self)
                             for module in configured_modules]
        return self._modules

    async def on_connect(self, *args, **kwargs):
        """
        Executes when the bot connects to the network.
        """
        await super().on_connect(*args, **kwargs)
        for module in self.modules:
            try:
                await module.on_connect(*args, **kwargs)
            except AttributeError:
                pass

    async def on_message(self, *args, **kwargs):
        """
        Executes when the bot gets a message (either private or in channel)
        """
        await super().on_message(*args, **kwargs)
        for module in self.modules:
            try:
                await module.on_message(*args, **kwargs)
            except AttributeError:
                pass

    async def on_channel_message(self, *args, **kwargs):
        """
        Executes when the bot gets a message in channel
        """
        await super().on_channel_message(*args, **kwargs)
        for module in self.modules:
            try:
                await module.on_channel_message(*args, **kwargs)
            except AttributeError:
                pass
