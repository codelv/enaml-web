"""
Copyright (c) 2017, Jairus Martin.

Distributed under the terms of the MIT License.

The full license is in the file COPYING.txt, distributed with this software.

Created on Apr 12, 2017

@author: jrm
"""
import sys
import json
from atom.api import Instance
from twisted.internet import reactor, endpoints
from twisted.web import server
from twisted.python import log
from web.impl.lxml_app import LxmlApplication


class UtfEncoder(json.JSONEncoder):
    def default(self, obj):
        if isinstance(obj, bytes):
            return obj.decode('utf-8')
        return super(UtfEncoder, self).default(obj)


class TwistedApplication(LxmlApplication):
    #: Twisted site to run
    site = Instance(server.Site)
    
    #: Endpoint to host the site on
    endpoint = Instance(endpoints._TCPServerEndpoint)
    
    #: Log location
    log = Instance(object, factory=lambda: sys.stdout)
    
    def _default_endpoint(self):
        """ By default return a TCP4ServerEndpoint
            on the given port and interface if none is passed
        """
        return endpoints.TCP4ServerEndpoint(reactor, self.port,
                                            interface=self.interface)
        
    def start(self):
        """ Start the application's main event loop.

        """
        if self.log:
            log.startLogging(self.log)
        self.endpoint.listen(self.site)
        reactor.run()
    
    def stop(self):
        """ Stop the application's main event loop.

        """
        reactor.stop()

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
        reactor.callFromThread(callback, *args, **kwargs)
    
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
        reactor.callLater(ms/1000.0, callback, *args, **kwargs)
    
    def write_to_websocket(self, websocket, message):
        """ Send message data to a twisted websocket.

        Parameters
        -----------
        websocket :
            A websocket object for the given toolkit
        message : dict, str or bytes
            Data to send to the websocket

        """
        if isinstance(message, dict):
            message = json.dumps(message, cls=UtfEncoder).encode('utf-8')
        websocket.sendMessage(message)
