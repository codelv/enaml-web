"""
Copyright (c) 2017-2019, Jairus Martin.

Distributed under the terms of the MIT License.

The full license is in the file LICENSE.txt, distributed with this software.

Created on Apr 2, 2017

@author: jrm
"""
from __future__ import print_function
from atom.api import (
    Atom, Event, Enum, ContainerList, Value, Int, Unicode, Dict, Instance,
    ForwardTyped, Typed, Coerced, observe
)

from enaml.core.declarative import d_
from enaml.widgets.toolkit_object import ToolkitObject, ProxyToolkitObject


class ProxyTag(ProxyToolkitObject):
    declaration = ForwardTyped(lambda: Tag)

    def xpath(self, *args, **kwargs):
        """ Perform an xpath lookup on the node """
        raise NotImplementedError


class SuperProxy(Atom):
    """ A proxy for accessing overridden members. This requires a modification
    to enaml at the moment.

    """

    #: Object of which to find the super node
    owner = Typed(Atom)

    def __getattr__(self, attr):
        owner = self.owner
        node = owner._d_node
        engine = node.engine
        while node and engine == node.engine:
            node = node.super_node
        if node is None or node == owner._d_node:
            raise AttributeError('%s has no super node' % owner)
        return node.engine.read(self.owner, attr)


class Tag(ToolkitObject):
    #: Reference to the proxy object
    proxy = Typed(ProxyTag)

    #: Enables accessing overridden expressions
    base = Typed(SuperProxy)

    #: Object ID
    id = d_(Unicode())

    #: Object ID
    ref = d_(Unicode())

    #: Tag name (leave blank for class name)
    tag = d_(Unicode()).tag(attr=False)

    #: CSS classes
    cls = d_(Instance((list, object))).tag(attr=False)

    #: CSS styles
    style = d_(Instance((dict, object))).tag(attr=False)

    #: Node text
    text = d_(Unicode()).tag(attr=False)

    #: Node tail text
    tail = d_(Unicode()).tag(attr=False)

    #: Alt attribute
    alt = d_(Unicode())

    #: Custom attributes not explicitly defined
    attrs = d_(Dict()).tag(attr=False)

    #: Event from JS
    onclick = d_(Unicode())

    #: Whether this is clickable via websockets
    clickable = d_(Coerced(bool))

    #:  Event from JS
    clicked = d_(Event())

    def _default_tag(self):
        return self.__class__.__name__.lower()

    def _default_ref(self):
        return u"{}".format(id(self))

    def _default_base(self):
        return SuperProxy(owner=self)

    @observe('id', 'tag', 'cls', 'style', 'text', 'tail', 'alt', 'attrs',
             'onclick', 'clickable')
    def _update_proxy(self, change):
        """ Update the proxy widget when the Widget data
        changes.
        """
        #: Try default handler
        if change['type'] == 'update' and self.proxy_is_active:
            handler = getattr(self.proxy, 'set_' + change['name'], None)
            if handler is not None:
                handler(change['value'])
            else:
                self.proxy.set_attribute(change['name'], change['value'])
            self._notify_modified(change)

    def _notify_modified(self, change):
        """  If a change occurs when we have a websocket connection active
        notify the websocket client of the change.
        """
        root = self.root_object()
        if isinstance(root, Html):
            name = change['name']
            change = {
                'ref': self.ref,
                'type': change['type'],
                'name': change['name'],
                'value': change['value']
            }
            root.modified(change)

    def child_added(self, child):
        super(Tag, self).child_added(child)
        if isinstance(child, Tag) and self.proxy_is_active:
            change = {
                'type': 'added',
                'name': 'children',
                #'before':self.ch #: TODO: Handle placement?
                'value': child.render().decode()
            }
            self._notify_modified(change)

    def child_removed(self, child):
        super(Tag, self).child_removed(child)
        if isinstance(child, Tag) and self.proxy_is_active:
            change = {
                'type': 'removed',
                'name': 'children',
                'value': child.ref,
            }
            self._notify_modified(change)

    def xpath(self, *args, **kwargs):
        if not nodes:
            return []
        refs = [node.attrib.get('ref') for node in nodes]
        if not refs:
            return []
        return [CACHE[ref] for ref in refs if ref and ref in CACHE]

    def xpath(self, query, **kwargs):
        """ Find nodes matching the given xpath query """
        if not self.proxy:
            return
        nodes = self.proxy.find(query, **kwargs)
        return [n.declaration for n in nodes]

    def prepare(self, **kwargs):
        """ Prepare for rendering """
        for k, v in kwargs.items():
            setattr(self, k, v)
        if not self.is_initialized:
            self.initialize()
        if not self.proxy_is_active:
            self.activate_proxy()

    def render(self, **kwargs):
        """ Render to a string"""
        self.prepare(**kwargs)
        return self.proxy.render()


class Html(Tag):
    #: Dom modified event. This will fire when any child node is updated, added
    #: or removed. Observe this event to handle updating websockets.
    modified = d_(Event(dict), writable=False).tag(attr=False)

    def _default_tag(self):
        return 'html'


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
    selected = d_(Coerced(bool))

    @observe('value', 'selected')
    def _update_proxy(self, change):
        super(Option, self)._update_proxy(change)


class Input(Tag):
    name = d_(Unicode())
    type = d_(Unicode())
    disabled = d_(Coerced(bool))
    checked = d_(Coerced(bool))
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
    controls = d_(Coerced(bool))

    @observe('controls')
    def _update_proxy(self, change):
        super(Video, self)._update_proxy(change)


class Source(Tag):
    src = d_(Unicode())
    type = d_(Unicode())

    @observe('src', 'type')
    def _update_proxy(self, change):
        super(Source, self)._update_proxy(change)
