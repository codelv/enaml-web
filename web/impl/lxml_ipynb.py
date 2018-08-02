"""
Copyright (c) 2018, Jairus Martin.

Distributed under the terms of the MIT License.

The full license is in the file LICENSE.text, distributed with this software.

Created on Jul 8, 2018

@author: jrm
"""
import nbformat
from atom.api import Instance
from .lxml_raw import RawComponent
from nbconvert import HTMLExporter
from web.components.ipynb import ProxyNotebook


class NotebookComponent(RawComponent, ProxyNotebook):
    """ A component for rendering Jupyter Notebooks. """
    
    #: Exporter
    exporter = Instance(HTMLExporter, ())
    
    def set_source(self, source):
        # Parse md and put in a root node
        source, resources = self.exporter.from_notebook_node(
            nbformat.reads(source, as_version=self.declaration.version))
        # Parse source to html
        super(NotebookComponent, self).set_source(
            "<div>{}</div>".format(source))
        
    def set_version(self, version):
        self.set_source(self.declaration.source)

