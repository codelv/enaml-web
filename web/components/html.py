"""
Copyright (c) 2017, Jairus Martin.

Distributed under the terms of the MIT License.

The full license is in the file COPYING.txt, distributed with this software.

Created on Apr 2, 2017

@author: jrm
"""
from __future__ import print_function
from past.builtins import basestring
from atom.api import (
    Event, Enum, ContainerList, Value, Int, Unicode, Dict, Instance, Bool,
    ForwardTyped, Typed, observe
)

from enaml.core.declarative import d_
from enaml.widgets.toolkit_object import ToolkitObject, ProxyToolkitObject


class ProxyTag(ProxyToolkitObject):
    declaration = ForwardTyped(lambda: Tag)

    def _write_to_websocket(self, websocket, message):
        """ Write the given data to the given websocket using the underlying
        toolkit server implementation.
        """
        raise NotImplementedError


class Tag(ToolkitObject):
    #: Reference to the proxy object
    proxy = Typed(ProxyTag)

    #: Object ID
    id = d_(Unicode())

    #: Object ID
    ref = d_(Unicode())
    
    #: Tag name (leave blank for class name)
    tag = d_(Unicode())
    
    #: CSS classes
    cls = d_(Instance((list, basestring)))
    
    #: CSS styles
    style = d_(Instance((dict, basestring)))
    
    #: Node text
    text = d_(Unicode())
    
    #: Node tail text
    tail = d_(Unicode())
    
    #: Alt attribute
    alt = d_(Unicode())    
    
    #: Custom attributes not explicitly defined
    attrs = d_(Dict())
    
    #:  Event from JS
    clicked = d_(Event())
    
    def _default_tag(self):
        return self.__class__.__name__.lower()

    def _default_ref(self):
        return u"{}".format(id(self))
    
    @observe('id', 'tag', 'cls', 'style', 'text', 'tail', 'alt', 'attrs')
    def _update_proxy(self, change):
        """ Update the proxy widget when the Widget data 
        changes.
        """
        #: Try default handler
        if change['type'] == 'update' and self.proxy_is_active:
            self._update_clients(change)
            handler = getattr(self.proxy, 'set_' + change['name'], None)
            if handler is not None:
                handler(change['value'])
            else:
                self.proxy.set_attribute(change['name'], change['value'])

    @observe('websockets')
    def _update_websockets(self, change):
        """ When the websocket is set, update all children
        to have the same websocket.
        """
        if change['value'] and self.parent is not None:
            raise RuntimeError("Cannot set websocket on non parent node")
    
    def _update_clients(self, change):
        """  If a change occurs when we have a websocket connection active
        notify the websocket client of the change. 
        """
        root = self.root_object()
        if isinstance(root, Html) and root.websockets:
            msg = {
                'ref': u'{}'.format(self.ref),
                'type': change['type'],
                'name': change['name'],
                'value': change['value']
            }
            for ws in root.websockets:
                self.proxy._write_to_websocket(ws, msg)
            
    def child_added(self, child):
        super(Tag, self).child_added(child)
        if isinstance(child, Tag) and self.proxy_is_active:
            change = {
                'type': 'added',
                'name': 'children',
                #'before':self.ch #: TODO: Handle placement?
                'value': child.render()
            }
            self._update_clients(change)
    
    def child_removed(self, child):
        super(Tag, self).child_removed(child)
        if isinstance(child, Tag) and self.proxy_is_active:
            change = {
                'type': 'removed',
                'name': 'children',
                'value': u'{}'.format(self.ref),
            }
            self._update_clients(change)
                    
    def xpath(self, query, first=False, last=False):
        """ Find nodes matching the given xpath query """
        if not self.proxy:
            return
        nodes = self.proxy.find(query)
        if first:
            return nodes[0].declaration if nodes else None
        elif last:
            return nodes[-1].declaration if nodes else None
        return [n.declaration for n in nodes] if nodes else []
    
    def render(self, **kwargs):
        """ Render to a string"""
        for k, v in kwargs.items():
            setattr(self, k, v)
        if not self.is_initialized:
            self.initialize()
        if not self.proxy_is_active:
            self.activate_proxy()
        return self.proxy.render()


class Html(Tag):
    #: Websocket clients observing changes
    #: Only to on the root of the tree
    websockets = d_(ContainerList())

    #: Request object
    request = d_(Value(), writable=False)

    #: Handler object
    handler = d_(Value())


class Head(Tag):
    pass    


class Body(Tag):
    pass    


class Title(Tag):
    pass    


class P(Tag):
    pass


class H1(Tag):
    pass


class H2(Tag):
    pass           


class H3(Tag):
    pass


class H4(Tag):
    pass


class H5(Tag):
    pass


class H6(Tag):
    pass


class Hr(Tag):
    pass


class Br(Tag):
    pass


class Pre(Tag):
    pass


#class Code(Tag):
#    pass


class Kbd(Tag):
    pass


class Samp(Tag):
    pass


class Var(Tag):
    pass


class Div(Tag):
    pass


class Span(Tag):
    pass                    


class A(Tag):
    href = d_(Unicode())
    target = d_(Enum("", "_blank", "_self", "_parent", "_top", "framename"))
    
    @observe('href', 'target')
    def _update_proxy(self, change):
        super(A, self)._update_proxy(change)


class B(Tag):
    pass


class I(Tag):
    pass


class Strong(Tag):
    pass


class Em(Tag):
    pass


class Mark(Tag):
    pass


class Small(Tag):
    pass


class Del(Tag):
    pass


class Ins(Tag):
    pass


class Sub(Tag):
    pass


class Sup(Tag):
    pass


class Q(Tag):
    pass


class Blockquote(Tag):
    cite = d_(Unicode())
    
    @observe('cite')
    def _update_proxy(self, change):
        super(Blockquote, self)._update_proxy(change)


class Abbr(Tag):
    pass


class Address(Tag):
    pass


class Cite(Tag):
    pass


class Bdo(Tag):
    dir = d_(Unicode())


class Img(Tag):
    src = d_(Unicode())
    width = d_(Unicode())
    height = d_(Unicode())
    
    @observe('src', 'width', 'height')
    def _update_proxy(self, change):
        super(Img, self)._update_proxy(change)            


class Style(Tag):
    pass


class Link(Tag):
    type = d_(Unicode())
    rel = d_(Unicode())
    href = d_(Unicode())
    media = d_(Unicode())
    
    @observe('type', 'rel', 'href', 'media')
    def _update_proxy(self, change):
        super(Link, self)._update_proxy(change)


class Map(Tag):
    name = d_(Unicode())
    
    @observe('name')
    def _update_proxy(self, change):
        super(Map, self)._update_proxy(change)


class Area(Tag):
    shape = d_(Unicode())
    coords = d_(Unicode())
    href = d_(Unicode())
    
    @observe('shape', 'coords', 'href')
    def _update_proxy(self, change):
        super(Area, self)._update_proxy(change)


class Table(Tag):
    pass


class Tr(Tag):
    pass


class Td(Tag):
    colspan = d_(Unicode())
    rowspan = d_(Unicode())

    @observe('colspan', 'rowspan')
    def _update_proxy(self, change):
        super(Td, self)._update_proxy(change)


class Th(Tag):
    colspan = d_(Unicode())
    rowspan = d_(Unicode())
    
    @observe('colspan', 'rowspan')
    def _update_proxy(self, change):
        super(Th, self)._update_proxy(change)


class THead(Tag):
    pass


class TBody(Tag):
    pass


class TFoot(Tag):
    pass


class Caption(Tag):
    pass
    

class Ul(Tag):
    pass


class Ol(Tag):
    type = d_(Enum("", "1", "A", "a", "I", "i"))
    
    @observe('type')
    def _update_proxy(self, change):
        super(Ol, self)._update_proxy(change)


class Li(Tag):
    pass


class Dl(Tag):
    pass


class Dt(Tag):
    pass


class Dd(Tag):
    pass


class IFrame(Tag):
    src = d_(Unicode())
    height = d_(Unicode())
    width = d_(Unicode())
    target = d_(Unicode())
    
    @observe('src', 'height', 'width', 'target')
    def _update_proxy(self, change):
        super(IFrame, self)._update_proxy(change)


class Script(Tag):
    src = d_(Unicode())
    type = d_(Unicode())
    
    @observe('type', 'src')
    def _update_proxy(self, change):
        super(Script, self)._update_proxy(change)


class NoScript(Tag):
    pass


class Meta(Tag):
    name = d_(Unicode())
    content = d_(Unicode())
    
    @observe('name', 'content')
    def _update_proxy(self, change):
        super(Meta, self)._update_proxy(change)
    

class Base(Tag):
    href = d_(Unicode())
    target = d_(Enum("", "_blank", "_self", "_parent", "_top", "framename"))
    
    @observe('href', 'target')
    def _update_proxy(self, change):
        super(Base, self)._update_proxy(change)


class Header(Tag):
    pass


class Nav(Tag):
    pass


class Section(Tag):
    pass


class Aside(Tag):
    pass


class Article(Tag):
    pass


class Footer(Tag):
    pass


class Summary(Tag):
    pass


class Details(Tag):
    pass


class Form(Tag):
    action = d_(Unicode())
    method = d_(Enum("post", "get"))
    
    @observe('action', 'method')
    def _update_proxy(self, change):
        super(Form, self)._update_proxy(change)
    

class Fieldset(Tag):
    pass


class Legend(Tag):
    pass


class Label(Tag):
    pass


class Select(Tag):
    name = d_(Unicode())
    value = d_(Unicode())

    def _default_name(self):
        return u'{}'.format(self.ref)

    @observe('name', 'value')
    def _update_proxy(self, change):
        super(Select, self)._update_proxy(change)
    

class Option(Tag):
    value = d_(Unicode())
    selected = d_(Bool())
    
    @observe('value', 'selected')
    def _update_proxy(self, change):
        super(Option, self)._update_proxy(change)
    

class Input(Tag):
    name = d_(Unicode())
    type = d_(Unicode())
    disabled = d_(Bool())
    checked = d_(Unicode())
    value = d_(Value())

    def _default_name(self):
        return u'{}'.format(self.ref)
    
    @observe('name', 'type', 'disabled', 'checked', 'value')
    def _update_proxy(self, change):
        super(Input, self)._update_proxy(change)


class Textarea(Tag):
    name = d_(Unicode())
    rows = d_(Unicode())
    cols = d_(Unicode())

    def _default_name(self):
        return u'{}'.format(self.ref)
    
    @observe('name', 'rows', 'cols')
    def _update_proxy(self, change):
        super(Textarea, self)._update_proxy(change)


class Button(Tag):
    name = d_(Unicode())
    type = d_(Unicode())
    value = d_(Unicode('1'))
    
    def _default_name(self):
        return u'{}'.format(self.ref)
    
    @observe('type')
    def _update_proxy(self, change):
        super(Button, self)._update_proxy(change)


class Video(Tag):
    controls = d_(Bool())
    
    @observe('controls')
    def _update_proxy(self, change):
        super(Video, self)._update_proxy(change)


class Source(Tag):
    src = d_(Unicode())
    type = d_(Unicode())
    
    @observe('src', 'type')
    def _update_proxy(self, change):
        super(Source, self)._update_proxy(change)
