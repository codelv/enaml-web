"""
Copyright (c) 2017, Jairus Martin.

Distributed under the terms of the MIT License.

The full license is in the file LICENSE.text, distributed with this software.

Created on Aug 2, 2017

@author: jrm
"""
import markdown
from .lxml_raw import RawComponent
from web.components.md import ProxyMarkdown


class MarkdownComponent(RawComponent, ProxyMarkdown):
    """ A block for rendering Markdown source. """

    def _refresh_source(self):
        d = self.declaration

        #: Parse md and put in a root node
        source = markdown.markdown(
            d.source,
            tab_length=d.tab_length,
            safe_mode=d.safe_mode,
            output_format=d.output_format,
            extensions=d.extensions,
            extension_configs=d.extension_configs
        )
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

    def set_extensions(self, extensions):
        self._refresh_source()

    def set_extension_configs(self, config):
        self._refresh_source()
