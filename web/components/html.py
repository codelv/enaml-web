"""
Copyright (c) 2017-2019, Jairus Martin.

Distributed under the terms of the MIT License.

The full license is in the file LICENSE.txt, distributed with this software.

Created on Apr 2, 2017

@author: jrm
"""

from __future__ import annotations

from typing import Any, Generator, Optional, Union
from atom.api import (
    Event,
    Enum,
    Instance,
    Value,
    Str,
    ForwardTyped,
    Typed,
    Coerced,
    ChangeDict,
)
from enaml.core.declarative import d_, Declarative, observe
from enaml.widgets.toolkit_object import ToolkitObject, ProxyToolkitObject
from web.core.utils import InternStr

try:
    from web.core.speedups import gen_id, lookup_child_index
except ImportError:

    def lookup_child_index(parent: "Tag", child: "Tag") -> int:
        """Find the index of the child ignoring any pattern nodes"""
        i = 0
        for c in parent.children:
            if c is child:
                return i
            elif isinstance(c, Tag):
                i += 1
        raise KeyError("Child not found")

    def gen_id(tag, id=id, mod=divmod):
        """Generate a short id for the tag"""
        number = id(tag)
        output = ""
        alpha = "0123456789ABCDEFGHJKLMNPQRSTUVWXYZabcdefghijkmnopqrstuvwxyz-+.:!"
        while number:
            number, digit = mod(number, 59)
            output += alpha[digit]
        return output


class ProxyTag(ProxyToolkitObject):
    #: Reference to the declaration
    declaration = ForwardTyped(lambda: Tag)

    def xpath(self, query: str, **kwargs) -> Generator["ProxyTag", None, None]:
        """Perform an xpath lookup on the node"""
        raise NotImplementedError

    def render(
        self, method: str = "html", encoding: str = "unicode", **kwargs
    ) -> Union[str, bytes]:
        """Render the node and all children"""
        raise NotImplementedError

    def set_attribute(self, name: str, value: Any):
        raise NotImplementedError


class Tag(ToolkitObject):
    #: Reference to the proxy object
    proxy = Typed(ProxyTag)

    #: Object ID
    id = d_(Str()).tag(attr=False)

    #: Tag name
    tag = "tag"

    #: CSS classes.
    cls = d_(InternStr()).tag(attr=False)

    #: CSS styles
    style = d_(Instance((dict, str))).tag(attr=False)

    #: Node text
    text = d_(Str()).tag(attr=False)

    #: Node tail text
    tail = d_(Str()).tag(attr=False)

    #: Custom attributes not explicitly defined
    attrs = d_(Typed(dict)).tag(attr=False)

    #: Event triggered on click
    clicked = d_(Event())

    #: Event triggered when a drag starts
    dragstart = d_(Event())

    #: Event triggered when a drag ends
    dragend = d_(Event())

    #: Event triggered when a node is dragged over a valid drop target
    dragenter = d_(Event(ToolkitObject))

    #: Event triggered when a node leaves a valid drop target
    dragleave = d_(Event(ToolkitObject))

    #: Event triggered when a drop occurs
    dropped = d_(Event(ToolkitObject))

    def _default_id(self):
        return gen_id(self)

    @observe(
        "id",
        "cls",
        "style",
        "text",
        "tail",
        "attrs",
    )
    def _update_proxy(self, change: ChangeDict):
        """Update the proxy widget when the Widget data changes.

        This also notifies the root that the dom has been modified.

        """
        if self.proxy_is_active and change["type"] == "update":
            name = change["name"]
            value = change["value"]
            proxy = self.proxy
            assert proxy is not None
            if handler := getattr(proxy, f"set_{name}", None):
                handler(value, change["oldvalue"])
            else:
                proxy.set_attribute(name, value)
            self._notify_modified(
                {
                    "id": self.id,
                    "type": change["type"],
                    "name": name,
                    "value": value,
                    "oldvalue": change["oldvalue"],
                },
            )

    # =========================================================================
    # Object API
    # =========================================================================

    def child_added(self, child: Declarative):
        super().child_added(child)
        if self.proxy_is_active and isinstance(child, Tag):
            self._notify_modified(
                {
                    "id": self.id,
                    "type": "added",
                    "name": "children",
                    "value": child.render(),
                    "index": self._child_index(child),
                },
            )

    def child_moved(self, child: Declarative):
        super().child_moved(child)
        if self.proxy_is_active and isinstance(child, Tag):
            proxy = self.proxy
            assert proxy is not None
            if proxy.child_moved(child.proxy):
                self._notify_modified(
                    {
                        "id": self.id,
                        "type": "moved",
                        "name": "children",
                        "value": child.id,
                        "index": self._child_index(child),
                    },
                )

    def child_removed(self, child: Declarative):
        """Handles the child removed event.

        This will generate a modified event indicating which child was removed.

        """
        super().child_removed(child)
        if self.proxy_is_active and isinstance(child, Tag):
            self._notify_modified(
                {
                    "id": self.id,
                    "type": "removed",
                    "name": "children",
                    "value": child.id,
                },
            )

    def _notify_modified(self, change: dict[str, Any]):
        """Trigger a modified event on the root node. Subclasses may override
        this to update change parameters if needed.

        """
        root = self.root_object()
        if isinstance(root, Html):
            proxy = root.proxy
            assert proxy is not None
            if proxy.rendered:
                root.modified(change)

    def _child_index(self, child: Tag) -> int:
        """Find the index of the child ignoring any pattern nodes"""
        return lookup_child_index(self, child)

    # =========================================================================
    # Tag API
    # =========================================================================
    def find_by_id(self, id: str) -> Optional[Tag]:
        """Find a child node with the given id.

        Parameters
        ----------
        id: str
            The id to look for.

        Returns
        -------
        results: Optional[Tag]
            The first node with the given id or None.

        """
        for child in self.traverse():
            if isinstance(child, Tag) and child.id == id:
                return child
        return None

    def xpath(self, query: str, **kwargs) -> list[Tag]:
        """Find nodes matching the given xpath query

        Parameters
        ----------
        query: str
            The xpath query to run
        kwargs: dict
            Parameters to xpath.

        Returns
        -------
        nodes: List[Tag]
            List of tags matching the xpath query.

        """
        proxy = self.proxy
        assert proxy is not None
        return [n for n in proxy.xpath(query, **kwargs)]

    def prepare(self, **kwargs: dict[str, Any]):
        """Prepare this node for rendering.

        This sets any attributes given, initializes and actives the proxy
        as needed.

        """
        for k, v in kwargs.items():
            setattr(self, k, v)
        if not self.is_initialized:
            self.initialize()
        if not self.proxy_is_active:
            self.activate_proxy()

    def render(
        self, render_options: Optional[dict] = None, **kwargs: dict[str, Any]
    ) -> Union[str, bytes]:
        """Render this tag and all children to a string.

        Parameters
        -------
        render_options: dict
            Options to pass to render
        kwargs: dict
            Attributes to set on the view

        Returns
        -------
        html: str
            The rendered html content of the node.

        """
        self.prepare(**kwargs)
        proxy = self.proxy
        assert proxy is not None
        if render_options:
            return proxy.render(**render_options)
        return proxy.render()


class Html(Tag):
    """Html is a root tag. It can be created without a parent and handles all modified events"""

    __slots__ = ("__weakref__",)

    #: The xml tag of the root node.
    tag = d_(Str("html"))

    #: Dom modified event. This will fire when any child node is updated, added
    #: or removed. Observe this event to handle updating websockets.
    modified = d_(Event(dict), writable=False).tag(attr=False)


class Head(Tag):
    tag = "head"


class Body(Tag):
    tag = "body"


class Title(Tag):
    tag = "title"


class P(Tag):
    tag = "p"


class H1(Tag):
    tag = "h1"


class H2(Tag):
    tag = "h2"


class H3(Tag):
    tag = "h3"


class H4(Tag):
    tag = "h4"


class H5(Tag):
    tag = "h5"


class H6(Tag):
    tag = "h6"


class Hr(Tag):
    tag = "hr"


class Br(Tag):
    tag = "br"


class Pre(Tag):
    tag = "pre"


class Kbd(Tag):
    tag = "kbd"


class Samp(Tag):
    tag = "samp"


class Var(Tag):
    tag = "var"


class Div(Tag):
    tag = "div"


class Span(Tag):
    tag = "span"


class A(Tag):
    tag = "a"

    #: Set the url
    href = d_(Str())

    #: Alt attribute
    alt = d_(Str())

    #: Set the target options
    target = d_(Enum("", "_blank", "_self", "_parent", "_top", "framename"))

    @observe("href", "target", "alt")
    def _update_proxy(self, change: ChangeDict):
        super()._update_proxy(change)


class B(Tag):
    tag = "b"


class I(Tag):  # noqa: E742
    tag = "i"


class Strong(Tag):
    tag = "strong"


class Em(Tag):
    tag = "em"


class Mark(Tag):
    tag = "mark"


class Small(Tag):
    tag = "small"


class Del(Tag):
    tag = "del"


class Ins(Tag):
    tag = "ins"


class Sub(Tag):
    tag = "sub"


class Sup(Tag):
    tag = "sup"


class Q(Tag):
    tag = "q"


class Blockquote(Tag):
    tag = "blockquote"
    cite = d_(Str())

    @observe("cite")
    def _update_proxy(self, change: ChangeDict):
        super()._update_proxy(change)


class Abbr(Tag):
    tag = "abbr"


class Address(Tag):
    tag = "address"


class Cite(Tag):
    tag = "cite"


class Bdo(Tag):
    tag = "bdo"
    dir = d_(Str())


class Img(Tag):
    tag = "img"

    #: Alt attribute
    alt = d_(Str())
    src = d_(Str())
    width = d_(Str())
    height = d_(Str())

    @observe("src", "width", "height", "alt")
    def _update_proxy(self, change: ChangeDict):
        super()._update_proxy(change)


class Style(Tag):
    tag = "style"


class Link(Tag):
    tag = "link"
    type = d_(Str())
    rel = d_(Str())
    href = d_(Str())
    media = d_(Str())

    @observe("type", "rel", "href", "media")
    def _update_proxy(self, change: ChangeDict):
        super()._update_proxy(change)


class Map(Tag):
    tag = "map"

    @observe("name")
    def _update_proxy(self, change: ChangeDict):
        super()._update_proxy(change)


class Area(Tag):
    tag = "area"

    shape = d_(Str())
    coords = d_(Str())
    href = d_(Str())

    @observe("shape", "coords", "href")
    def _update_proxy(self, change: ChangeDict):
        super()._update_proxy(change)


class Table(Tag):
    tag = "table"


class Tr(Tag):
    tag = "tr"


class Td(Tag):
    tag = "td"
    colspan = d_(Str())
    rowspan = d_(Str())

    @observe("colspan", "rowspan")
    def _update_proxy(self, change: ChangeDict):
        super()._update_proxy(change)


class Th(Tag):
    tag = "th"
    colspan = d_(Str())
    rowspan = d_(Str())

    @observe("colspan", "rowspan")
    def _update_proxy(self, change: ChangeDict):
        super()._update_proxy(change)


class THead(Tag):
    tag = "thead"


class TBody(Tag):
    tag = "tbody"


class TFoot(Tag):
    tag = "tfoot"


class Caption(Tag):
    tag = "caption"


class Ul(Tag):
    tag = "ul"


class Ol(Tag):
    tag = "ol"
    type = d_(Enum("", "1", "A", "a", "I", "i"))

    @observe("type")
    def _update_proxy(self, change: ChangeDict):
        super()._update_proxy(change)


class Li(Tag):
    tag = "li"


class Dl(Tag):
    tag = "dl"


class Dt(Tag):
    tag = "dt"


class Dd(Tag):
    tag = "dd"


class IFrame(Tag):
    tag = "iframe"
    src = d_(Str())
    height = d_(Str())
    width = d_(Str())
    target = d_(Str())

    @observe("src", "height", "width", "target")
    def _update_proxy(self, change: ChangeDict):
        super()._update_proxy(change)


class Script(Tag):
    tag = "script"
    src = d_(Str())
    type = d_(Str())

    @observe("type", "src")
    def _update_proxy(self, change: ChangeDict):
        super()._update_proxy(change)


class NoScript(Tag):
    tag = "noscript"


class Meta(Tag):
    tag = "meta"
    content = d_(Str())

    @observe("name", "content")
    def _update_proxy(self, change: ChangeDict):
        super()._update_proxy(change)


class Base(Tag):
    tag = "base"

    href = d_(Str())
    target = d_(Enum("", "_blank", "_self", "_parent", "_top", "framename"))

    @observe("href", "target")
    def _update_proxy(self, change: ChangeDict):
        super()._update_proxy(change)


class Header(Tag):
    tag = "header"


class Nav(Tag):
    tag = "nav"


class Section(Tag):
    tag = "section"


class Aside(Tag):
    tag = "aside"


class Article(Tag):
    tag = "article"


class Footer(Tag):
    tag = "footer"


class Font(Tag):
    tag = "font"


class Summary(Tag):
    tag = "summary"


class Details(Tag):
    tag = "details"


class Form(Tag):
    tag = "form"
    action = d_(Str())
    method = d_(Enum("post", "get"))

    @observe("action", "method")
    def _update_proxy(self, change: ChangeDict):
        super()._update_proxy(change)


class Fieldset(Tag):
    tag = "fieldset"


class Legend(Tag):
    tag = "legend"


class Label(Tag):
    tag = "label"


class Select(Tag):
    tag = "select"
    value = d_(Str())
    disabled = d_(Coerced(bool))

    def _default_name(self):
        return self.id

    @observe("name", "value", "disabled")
    def _update_proxy(self, change: ChangeDict):
        super()._update_proxy(change)


class Option(Tag):
    tag = "option"
    value = d_(Str())
    selected = d_(Coerced(bool))

    @observe("value", "selected")
    def _update_proxy(self, change: ChangeDict):
        super()._update_proxy(change)


class OptGroup(Tag):
    tag = "optgroup"
    label = d_(Str())
    disabled = d_(Coerced(bool))

    @observe("label", "disabled")
    def _update_proxy(self, change: ChangeDict):
        super()._update_proxy(change)


class Input(Tag):
    tag = "input"
    type = d_(Str())
    placeholder = d_(Str())
    disabled = d_(Coerced(bool))
    checked = d_(Coerced(bool))
    value = d_(Value())

    def _default_name(self):
        return self.id

    @observe("name", "type", "disabled", "checked", "value", "placeholder")
    def _update_proxy(self, change: ChangeDict):
        super()._update_proxy(change)


class Textarea(Tag):
    tag = "textarea"
    rows = d_(Str())
    cols = d_(Str())
    disabled = d_(Coerced(bool))

    def _default_name(self):
        return self.id

    @observe("name", "rows", "cols", "disabled")
    def _update_proxy(self, change: ChangeDict):
        super()._update_proxy(change)


class Button(Tag):
    tag = "button"
    type = d_(Str())
    value = d_(Str("1"))

    def _default_name(self):
        return self.id

    @observe("type")
    def _update_proxy(self, change: ChangeDict):
        super()._update_proxy(change)


class Canvas(Tag):
    tag = "canvas"


class Video(Tag):
    tag = "video"
    controls = d_(Coerced(bool))

    @observe("controls")
    def _update_proxy(self, change: ChangeDict):
        super()._update_proxy(change)


class Source(Tag):
    tag = "source"
    src = d_(Str())
    type = d_(Str())

    @observe("src", "type")
    def _update_proxy(self, change: ChangeDict):
        super()._update_proxy(change)
