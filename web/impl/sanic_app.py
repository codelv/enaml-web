"""
Copyright (c) 2018, Jairus Martin.

Distributed under the terms of the MIT License.

The full license is in the file COPYING.txt, distributed with this software.

Created on May 20, 2018

@author: jrm
"""
import sys
import uvloop
import asyncio
from sanic import Sanic
from functools import partial
from atom.api import Instance
from web.impl.lxml_app import LxmlApplication


class SanicApplication(LxmlApplication):
    """ An application based on MagicStack's uvloop
    
    """
    #: Sanic app
    app = Instance(Sanic)

    #: The event loop
    loop = Instance(asyncio.AbstractEventLoop)

    def start(self, **kwargs):
        """ Start the application's main event loop.

        """
        async def set_loop():
            self.loop = self._default_loop()
        self.loop = self.app.add_task(set_loop)
        self.app.run(host=self.interface,
                     port=self.port,
                     debug=self.debug, **kwargs)

    def _default_loop(self):
        if self.app.loop:
            return self.app.loop
        asyncio.set_event_loop_policy(uvloop.EventLoopPolicy())
        return asyncio.get_event_loop()

    def stop(self):
        """ Stop the application's main event loop.

        """
        self.loop.stop()

    def deferred_call(self, callback, *args, **kwargs):
        """ Invoke a callable on the next cycle of the main event loop
        thread.

        Parameters
        ----------
        callback : callable
            The callable object to execute at some point in the future.

        *args, **kwargs
            Any additional positional and keyword arguments to pass to
            the callback.

        """
        if kwargs:
            callback = partial(callback, **kwargs)
        self.loop.call_soon_threadsafe(callback, *args)

    def timed_call(self, ms, callback, *args, **kwargs):
        """ Invoke a callable on the main event loop thread at a
        specified time in the future.

        Parameters
        ----------
        ms : int
            The time to delay, in milliseconds, before executing the
            callable.

        callback : callable
            The callable object to execute at some point in the future.

        *args, **kwargs
            Any additional positional and keyword arguments to pass to
            the callback.

        """
        if kwargs:
            callback = partial(callback, **kwargs)
        self.loop.call_later(ms/1000.0, callback, *args)

    def write_to_websocket(self, websocket, message):
        """ Send message data to a twisted websocket.

        Parameters
        -----------
        websocket :
            A websocket object for the given toolkit
        message : dict, str or bytes
            Data to send to the websocket

        """
        #: TODO
        raise NotImplementedError