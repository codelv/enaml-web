"""
Copyright (c) 2017, Jairus Martin.

Distributed under the terms of the MIT License.

The full license is in the file COPYING.txt, distributed with this software.

Created on Apr 12, 2017

@author: jrm
"""
import tornado.ioloop
import tornado.web
from atom.api import Instance
from web.impl.lxml_app import LxmlApplication


class TornadoApplication(LxmlApplication):
    #: Tornado app to run
    app = Instance(tornado.web.Application)
    
    #: IOLoop to run in
    ioloop = Instance(tornado.ioloop.IOLoop)
    
    def _default_ioloop(self):
        return tornado.ioloop.IOLoop.current()
    
    def start(self):
        """ Start the application's main event loop.

        """
        self.app.listen(self.port)
        self.ioloop.start()

    def stop(self):
        """ Stop the application's main event loop.

        """
        self.ioloop.stop()

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
        self.ioloop.add_callback(callback, *args, **kwargs)
    
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
        self.ioloop.call_later(ms/1000.0, callback, *args, **kwargs)
    
    def write_to_websocket(self, websocket, message):
        """ Send message data to the websocket. Subclasses must implement this
        for data binding.

        Parameters
        -----------
        websocket :
            A websocket object for the given toolkit
        message : str or bytes
            Data to send to the websocket

        """
        websocket.write_message(message)
