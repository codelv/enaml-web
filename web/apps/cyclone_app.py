"""
Copyright (c) 2017, Jairus Martin.

Distributed under the terms of the MIT License.

The full license is in the file COPYING.txt, distributed with this software.

Created on Apr 12, 2017

@author: jrm
"""
import cyclone.web
from atom.api import Instance
from web.impl.twisted_app import TwistedApplication, log, reactor


class CycloneApplication(TwistedApplication):

    #: Pass in cyclone web application
    app = Instance(cyclone.web.Application)
    
    def start(self):
        """ Start the application's main event loop.

        """
        if self.log:
            log.startLogging(self.log)
        reactor.listenTCP(self.port, self.app, interface=self.interface)
        reactor.run()
