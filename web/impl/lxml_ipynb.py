"""
Copyright (c) 2018, Jairus Martin.

Distributed under the terms of the MIT License.

The full license is in the file LICENSE.text, distributed with this software.

Created on Jul 8, 2018

@author: jrm
"""
import nbformat
from atom.api import Instance, Value
from nbconvert import HTMLExporter
from web.components.ipynb import ProxyNotebook
from .lxml_raw import RawComponent, SourceType


class NotebookComponent(RawComponent, ProxyNotebook):
    """A component for rendering Jupyter Notebooks."""

    #: Exporter
    exporter = Instance(HTMLExporter, ())

    #: Resources from the node
    resources = Value()

    def set_source(self, source: SourceType):
        # Parse md and put in a root node
        d = self.declaration
        assert d is not None
        source = d.source
        if isinstance(source, str):
            source, self.resources = self.exporter.from_notebook_node(
                nbformat.reads(source, as_version=d.version)
            )
            source = f"<div>{source}</div>"
        super().set_source(source)

    def set_version(self, version: int):
        d = self.declaration
        assert d is not None
        self.set_source(d.source)
