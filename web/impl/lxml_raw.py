"""
Copyright (c) 2017, Jairus Martin.

Distributed under the terms of the MIT License.

The full license is in the file LICENSE.text, distributed with this software.

Created on Aug 2, 2017

@author: jrm
"""
from typing import Optional, Union
from lxml.etree import HTML
from lxml.etree import _Element as Element
from web.components.raw import ProxyRawNode, SourceType
from .lxml_toolkit_object import WebComponent


class RawComponent(WebComponent, ProxyRawNode):
    """A block for rendering raw html source."""

    def init_widget(self):
        """Initialize the widget with the source."""
        d = self.declaration
        source = d.source
        if source is not None and len(source):
            self.set_source(source)
        else:
            super().init_widget()

    def set_source(self, source: SourceType):
        """Set the source by parsing the source and inserting it into the
        component.
        """
        widget = self.widget
        assert widget is not None
        widget.clear()
        if isinstance(source, Element):
            widget.append(source)
        elif isinstance(source, list):
            widget.extend(source)
        elif isinstance(source, str):
            html = HTML(source)
            if html is not None:
                widget.extend(html[0])
        # else source is None

        # Clear removes everything so it must be reinitialized
        super().init_widget()
