"""
Copyright (c) 2017, Jairus Martin.

Distributed under the terms of the MIT License.

The full license is in the file LICENSE.text, distributed with this software.

Created on Apr 12, 2017

@author: jrm
"""
import inspect
from web.components import html


def generic_factory():
    from .lxml_toolkit_object import WebComponent

    return WebComponent


def html_factory():
    from .lxml_toolkit_object import RootWebComponent

    return RootWebComponent


def code_factory():
    from .lxml_code import CodeComponent

    return CodeComponent


def markdown_factory():
    from .lxml_md import MarkdownComponent

    return MarkdownComponent


def notebook_factory():
    from .lxml_ipynb import NotebookComponent

    return NotebookComponent


def raw_factory():
    from .lxml_raw import RawComponent

    return RawComponent


#: Create generic html factories
FACTORIES = {
    name: generic_factory
    for name, obj in inspect.getmembers(html)
    if inspect.isclass(obj)
}

#: Create special widgets
FACTORIES.update(
    {
        "Code": code_factory,
        "Html": html_factory,
        "Markdown": markdown_factory,
        "Notebook": notebook_factory,
        "Raw": raw_factory,
    }
)
