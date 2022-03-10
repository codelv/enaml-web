"""
Copyright (c) 2017, Jairus Martin.

Distributed under the terms of the MIT License.

The full license is in the file LICENSE.text, distributed with this software.

Created on Aug 2, 2017

@author: jrm
"""
from __future__ import annotations

import markdown
from web.components.md import ProxyMarkdown
from .lxml_raw import RawComponent, SourceType


class MarkdownComponent(RawComponent, ProxyMarkdown):
    """A block for rendering Markdown source."""

    def _refresh_source(self):
        d = self.declaration
        assert d is not None
        source = d.source
        if isinstance(source, str):
            source = markdown.markdown(
                source,
                tab_length=d.tab_length,
                safe_mode=d.safe_mode,
                output_format=d.output_format,
                extensions=d.extensions,
                extension_configs=d.extension_configs,
            )

        #: Parse md and put in a root node
        super().set_source(source)

    def set_source(self, source: SourceType):
        self._refresh_source()

    def set_safe_mode(self, mode: bool):
        self._refresh_source()

    def set_output_format(self, format: str):
        self._refresh_source()

    def set_tab_length(self, length: int):
        self._refresh_source()

    def set_extensions(self, extensions: list[str]):
        self._refresh_source()

    def set_extension_configs(self, config: dict[str, dict]):
        self._refresh_source()
