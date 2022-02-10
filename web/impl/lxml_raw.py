"""
Copyright (c) 2017, Jairus Martin.

Distributed under the terms of the MIT License.

The full license is in the file LICENSE.text, distributed with this software.

Created on Aug 2, 2017

@author: jrm
"""
from atom.api import set_default
from lxml.etree import HTML
from web.components.raw import ProxyRawNode
from .lxml_toolkit_object import WebComponent


class RawComponent(WebComponent, ProxyRawNode):
    """A block for rendering raw html source."""

    def init_widget(self):
        """Initialize the widget with the source."""
        d = self.declaration
        if d.source:
            self.set_source(d.source)
        else:
            super().init_widget()

    def set_source(self, source: str):
        """Set the source by parsing the source and inserting it into the
        component.
        """
        widget = self.widget
        assert widget is not None
        widget.clear()
        html = HTML(source)
        widget.extend(html[0])

        # Clear removes everything so it must be reinitialized
        super().init_widget()
