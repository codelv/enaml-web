"""
Copyright (c) 2017, Jairus Martin.

Distributed under the terms of the MIT License.

The full license is in the file COPYING.txt, distributed with this software.

Created on Apr 17, 2017

@author: jrm
"""
from atom.api import Value
from enaml.application import Application, ProxyResolver
from web.impl import lxml_components


class WebApplication(Application):
    """ Base enaml web application that uses the widgets defined in 
    `web.components.html`

    """

    #: Database
    database = Value()
    
    def __init__(self, *args, **kwargs):
        """ Initialize a WebApplication.

        """
        super(WebApplication, self).__init__(*args, **kwargs)
        self.resolver = ProxyResolver(factories=lxml_components.FACTORIES)
        
