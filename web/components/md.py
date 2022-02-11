"""
Copyright (c) 2017, Jairus Martin.

Distributed under the terms of the MIT License.

The full license is in the file LICENSE.text, distributed with this software.

Created on Aug 2, 2017

@author: jrm
"""

from typing import Optional
from atom.api import Typed, ForwardTyped, Enum, Int, Bool, List, Dict, observe
from enaml.core.declarative import d_
from .html import Tag, ChangeDict
from .raw import Raw, ProxyRawNode


class ProxyMarkdown(ProxyRawNode):
    #: Reference to the declaration
    declaration = ForwardTyped(lambda: Markdown)

    def set_safe_mode(self, mode: bool):
        raise NotImplementedError

    def set_output_format(self, output_format: str):
        raise NotImplementedError

    def set_tab_length(self, length: int):
        raise NotImplementedError

    def set_extensions(self, extensions: list[str]):
        raise NotImplementedError

    def set_extensions_config(self, config: dict[str, dict]):
        raise NotImplementedError


class Markdown(Raw):
    """A block for rendering Markdown source."""

    #: Extensions to use when rendering
    extensions = d_(
        List(
            default=[
                "markdown.extensions.codehilite",
                "markdown.extensions.fenced_code",
                "markdown.extensions.tables",
            ]
        )
    ).tag(attr=False)

    #: Configuration for them
    extension_configs = d_(
        Dict(
            default={
                "markdown.extensions.codehilite": {"css_class": "highlight"},
            }
        )
    ).tag(attr=False)

    #: Disallow raw HTMl
    safe_mode = d_(Bool()).tag(attr=False)

    #: Output format
    output_format = d_(Enum("xhtml", "html5")).tag(attr=False)

    #: Tab size
    tab_length = d_(Int(4)).tag(attr=False)

    #: Reference to the proxy
    proxy = Typed(ProxyMarkdown)

    @observe(
        "extensions", "extension_configs", "safe_mode", "output_format", "tab_length"
    )
    def _update_proxy(self, change: ChangeDict):
        """The superclass implementation is sufficient."""
        super()._update_proxy(change)

    def _notify_modified(self, root: Optional[Tag], change: ChangeDict):
        """Update the notification"""
        if change["type"] == "update" and change["name"] == "source":
            change["value"] = self.render()
        super()._notify_modified(root, change)
