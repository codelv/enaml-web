"""
Copyright (c) 2017, Jairus Martin.

Distributed under the terms of the MIT License.

The full license is in the file LICENSE.text, distributed with this software.

Created on Aug 2, 2017

@author: jrm
"""
from atom.api import set_default
from lxml import etree
from .lxml_toolkit_object import WebComponent
from web.components.raw import ProxyRawNode


class RawComponent(WebComponent, ProxyRawNode):
    """ A block for rendering raw html source. """
    
    def init_widget(self):
        """ Initialize the widget with the source. """
        d = self.declaration
        if d.source:
            self.set_source(d.source)
        else:
            super(RawComponent, self).init_widget()

    def set_source(self, source):
        """ Set the source by parsing the source and inserting it into the 
        component. 
        """
        self.widget.clear()
        html = etree.HTML(source)
        self.widget.extend(html[0])

        # Clear removes everything so it must be reinitialized
        super(RawComponent, self).init_widget()
