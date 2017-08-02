'''
Copyright (c) 2017, Jairus Martin.

Distributed under the terms of the MIT License.

The full license is in the file COPYING.txt, distributed with this software.

Created on Aug 2, 2017

@author: jrm
'''
import markdown
from .lxml_raw import RawComponent
from web.components.md import ProxyMarkdown


class MarkdownComponent(RawComponent, ProxyMarkdown):
    """ A block for rendering Markdown source. """

    def init_widget(self):
        """ Create the markdown source """
        d = self.declaration
        super(MarkdownComponent, self).init_widget()
        if d.source:
            self.set_source(d.source)

    def _refresh_source(self):
        d = self.declaration
        md = d.source

        #: Parse md
        source = markdown.markdown(md)

        #: Parse source to html
        super(MarkdownComponent, self).set_source(source)

    def set_source(self, source):
        self._refresh_source()

    def set_safe_mode(self, mode):
        self._refresh_source()

    def set_output_format(self, format):
        self._refresh_source()

    def set_tab_length(self, length):
        self._refresh_source()