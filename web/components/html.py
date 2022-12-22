"""
Copyright (c) 2017-2019, Jairus Martin.

Distributed under the terms of the MIT License.

The full license is in the file LICENSE.txt, distributed with this software.

Created on Apr 2, 2017

@author: jrm
"""
from __future__ import annotations

from typing import Any, Generator, Optional
from atom.api import (
    Atom,
    Event,
    Bool,
    Enum,
    ContainerList,
    Value,
    Int,
    Str,
    Dict,
    Instance,
    ForwardTyped,
    Typed,
    Coerced,
    observe,
    set_default,
)
from enaml.core.declarative import d_, Declarative
from enaml.widgets.toolkit_object import ToolkitObject, ProxyToolkitObject

ChangeDict = dict[str, Any]

try:
    from web.core.speedups import gen_id
except ImportError as e:

    def gen_id(tag, id=id, mod=divmod):
        """Generate a short id for the tag"""
        number = id(tag)
        output = ""
        alpha = "0123456789ABCDEFGHJKLMNPQRSTUVWXYZabcdefghijkmnopqrstuvwxyz"
        while number:
            number, digit = mod(number, 59)
            output += alpha[digit]
        return output


class ProxyTag(ProxyToolkitObject):
    #: Reference to the declaration
    declaration = ForwardTyped(lambda: Tag)

    #: A cached reference to the root element.
    #: WARNING: If the root is changed this becomes invalid
    root = ForwardTyped(lambda: ProxyTag)

    def xpath(self, query: str, **kwargs) -> Generator[ProxyToolkitObject, None, None]:
        """Perform an xpath lookup on the node"""
        raise NotImplementedError

    def render(self, method: str = "html", encoding: str = "unicode", **kwargs) -> str:
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
    tag = d_(Str()).tag(attr=False)

    #: CSS classes
    cls = d_(Instance((list, tuple, str))).tag(attr=False)

    #: CSS styles
    style = d_(Instance((dict, str))).tag(attr=False)

    #: Node text
    text = d_(Str()).tag(attr=False)

    #: Node tail text
    tail = d_(Str()).tag(attr=False)

    #: Alt attribute
    alt = d_(Str()).tag(attr=False)

    #: Custom attributes not explicitly defined
    attrs = d_(Dict()).tag(attr=False)

    #: JS onclick definition
    onclick = d_(Str()).tag(attr=False)

    #: Used to tell js to send click events back to the server
    clickable = d_(Coerced(bool)).tag(attr=False)

    #: Used to tell js to send drag events back to the server and sets the
    #: draggable attribute. Must be used with ondragstart.
    draggable = d_(Coerced(bool)).tag(attr=False)

    #: JS ondragstart definition
    ondragstart = d_(Str()).tag(attr=False)

    #: JS ondragover definition
    ondragover = d_(Str()).tag(attr=False)

    #: JS ondragend definition
    ondragend = d_(Str()).tag(attr=False)

    #: JS ondragenter definition
    ondragenter = d_(Str()).tag(attr=False)

    #: JS ondragleave definition
    ondragleave = d_(Str()).tag(attr=False)

    #: JS ondrop definition
    ondrop = d_(Str()).tag(attr=False)

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
        "tag",
        "cls",
        "style",
        "text",
        "tail",
        "alt",
        "attrs",
        "clickable",
        "draggable",
        "onclick",
        "ondragstart",
        "ondragover",
        "ondragend",
        "ondragenter",
        "ondragleave",
        "ondrop",
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
            handler = getattr(proxy, f"set_{name}", None)
            if handler is not None:
                handler(value)
            else:
                proxy.set_attribute(name, value)
            root = proxy.root
            if root is not None and root.rendered:
                self._notify_modified(
                    root.declaration,
                    {
                        "id": self.id,
                        "type": change["type"],
                        "name": name,
                        "value": value,
                    },
                )

    # =========================================================================
    # Object API
    # =========================================================================

    def child_added(self, child: Declarative):
        super().child_added(child)
        if self.proxy_is_active and isinstance(child, Tag):
            proxy = self.proxy
            assert proxy is not None
            root = proxy.root
            assert root is not None
            if root.rendered:
                self._notify_modified(
                    root.declaration,
                    {
                        "id": self.id,
                        "type": "added",
                        "name": "children",
                        "value": child.render(),
                        "index": self._child_index(child),
                        "before": self._next_child_id(child),
                    },
                )

    def child_moved(self, child: Declarative):
        super().child_moved(child)
        if self.proxy_is_active and isinstance(child, Tag):
            proxy = self.proxy
            assert proxy is not None
            root = proxy.root
            assert root is not None
            if root.rendered and proxy.child_moved(child.proxy):
                self._notify_modified(
                    root.declaration,
                    {
                        "id": self.id,
                        "type": "moved",
                        "name": "children",
                        "value": child.id,
                        "index": self._child_index(child),
                        "before": self._next_child_id(child),
                    },
                )

    def child_removed(self, child: Declarative):
        """Handles the child removed event.

        This will generate a modified event indicating which child was removed.

        """
        super().child_removed(child)
        if self.proxy_is_active and isinstance(child, Tag):
            proxy = self.proxy
            assert proxy is not None
            root = proxy.root
            assert root is not None
            if root.rendered:
                self._notify_modified(
                    root.declaration,
                    {
                        "id": self.id,
                        "type": "removed",
                        "name": "children",
                        "value": child.id,
                    },
                )

    def _notify_modified(self, root: Optional[Tag], change: ChangeDict):
        """Trigger a modified event on the root node. Subclasses may override
        this to update change parameters if needed.

        """
        if root is not None:
            root.modified(change)

    def _child_index(self, child: Tag) -> int:
        """Find the index of the child ignoring any pattern nodes"""
        i = 0
        for c in self.children:
            if c is child:
                return i
            elif isinstance(c, Tag):
                i += 1
        raise ValueError("Child not found")

    def _next_child_id(self, child: Tag) -> Optional[str]:
        """Find the id of the node after this child."""
        # Indicate where it was added
        children = self.children
        i = children.index(child) + 1
        for c in children[i:]:
            if isinstance(c, Tag):  # Ignore pattern nodes
                return c.id
        return None

    # =========================================================================
    # Tag API
    # =========================================================================
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
        return [n.declaration for n in proxy.xpath(query, **kwargs)]

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
    ) -> str:
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
    __slots__ = "__weakref__"

    #: Set the tag name
    tag = set_default("html")

    #: Dom modified event. This will fire when any child node is updated, added
    #: or removed. Observe this event to handle updating websockets.
    modified = d_(Event(dict), writable=False).tag(attr=False)

    def _default_tag(self):
        return "html"


class Head(Tag):
    #: Set the tag name
    tag = set_default("head")


class Body(Tag):
    #: Set the tag name
    tag = set_default("body")


class Title(Tag):
    #: Set the tag name
    tag = set_default("title")


class P(Tag):
    #: Set the tag name
    tag = set_default("p")


class H1(Tag):
    #: Set the tag name
    tag = set_default("h1")


class H2(Tag):
    #: Set the tag name
    tag = set_default("h2")


class H3(Tag):
    #: Set the tag name
    tag = set_default("h3")


class H4(Tag):
    #: Set the tag name
    tag = set_default("h4")


class H5(Tag):
    #: Set the tag name
    tag = set_default("h5")


class H6(Tag):
    #: Set the tag name
    tag = set_default("h6")


class Hr(Tag):
    #: Set the tag name
    tag = set_default("hr")


class Br(Tag):
    #: Set the tag name
    tag = set_default("br")


class Pre(Tag):
    #: Set the tag name
    tag = set_default("pre")


class Kbd(Tag):
    #: Set the tag name
    tag = set_default("kbd")


class Samp(Tag):
    #: Set the tag name
    tag = set_default("samp")


class Var(Tag):
    #: Set the tag name
    tag = set_default("var")


class Div(Tag):
    #: Set the tag name
    tag = set_default("div")


class Span(Tag):
    #: Set the tag name
    tag = set_default("span")


class A(Tag):
    #: Set the tag name
    tag = set_default("a")

    #: Set the url
    href = d_(Str())

    #: Set the target options
    target = d_(Enum("", "_blank", "_self", "_parent", "_top", "framename"))

    @observe("href", "target")
    def _update_proxy(self, change: ChangeDict):
        super()._update_proxy(change)


class B(Tag):
    #: Set the tag name
    tag = set_default("b")


class I(Tag):
    #: Set the tag name
    tag = set_default("i")


class Strong(Tag):
    #: Set the tag name
    tag = set_default("strong")


class Em(Tag):
    #: Set the tag name
    tag = set_default("em")


class Mark(Tag):
    #: Set the tag name
    tag = set_default("mark")


class Small(Tag):
    #: Set the tag name
    tag = set_default("small")


class Del(Tag):
    #: Set the tag name
    tag = set_default("del")


class Ins(Tag):
    #: Set the tag name
    tag = set_default("ins")


class Sub(Tag):
    #: Set the tag name
    tag = set_default("sub")


class Sup(Tag):
    #: Set the tag name
    tag = set_default("sup")


class Q(Tag):
    #: Set the tag name
    tag = set_default("q")


class Blockquote(Tag):
    #: Set the tag name
    tag = set_default("blockquote")

    cite = d_(Str())

    @observe("cite")
    def _update_proxy(self, change: ChangeDict):
        super()._update_proxy(change)


class Abbr(Tag):
    #: Set the tag name
    tag = set_default("abbr")


class Address(Tag):
    #: Set the tag name
    tag = set_default("address")


class Cite(Tag):
    #: Set the tag name
    tag = set_default("cite")


class Bdo(Tag):
    #: Set the tag name
    tag = set_default("bdo")

    dir = d_(Str())


class Img(Tag):
    #: Set the tag name
    tag = set_default("img")

    src = d_(Str())
    width = d_(Str())
    height = d_(Str())

    @observe("src", "width", "height")
    def _update_proxy(self, change: ChangeDict):
        super()._update_proxy(change)


class Style(Tag):
    #: Set the tag name
    tag = set_default("style")


class Link(Tag):
    #: Set the tag name
    tag = set_default("link")

    type = d_(Str())
    rel = d_(Str())
    href = d_(Str())
    media = d_(Str())

    @observe("type", "rel", "href", "media")
    def _update_proxy(self, change: ChangeDict):
        super()._update_proxy(change)


class Map(Tag):
    #: Set the tag name
    tag = set_default("map")

    name = d_(Str())

    @observe("name")
    def _update_proxy(self, change: ChangeDict):
        super()._update_proxy(change)


class Area(Tag):
    #: Set the tag name
    tag = set_default("area")

    shape = d_(Str())
    coords = d_(Str())
    href = d_(Str())

    @observe("shape", "coords", "href")
    def _update_proxy(self, change: ChangeDict):
        super()._update_proxy(change)


class Table(Tag):
    #: Set the tag name
    tag = set_default("table")


class Tr(Tag):
    #: Set the tag name
    tag = set_default("tr")


class Td(Tag):
    #: Set the tag name
    tag = set_default("td")

    colspan = d_(Str())
    rowspan = d_(Str())

    @observe("colspan", "rowspan")
    def _update_proxy(self, change: ChangeDict):
        super()._update_proxy(change)


class Th(Tag):
    #: Set the tag name
    tag = set_default("th")

    colspan = d_(Str())
    rowspan = d_(Str())

    @observe("colspan", "rowspan")
    def _update_proxy(self, change: ChangeDict):
        super()._update_proxy(change)


class THead(Tag):
    #: Set the tag name
    tag = set_default("thead")


class TBody(Tag):
    #: Set the tag name
    tag = set_default("tbody")


class TFoot(Tag):
    #: Set the tag name
    tag = set_default("tfoot")


class Caption(Tag):
    #: Set the tag name
    tag = set_default("caption")


class Ul(Tag):
    #: Set the tag name
    tag = set_default("ul")


class Ol(Tag):
    #: Set the tag name
    tag = set_default("ol")

    type = d_(Enum("", "1", "A", "a", "I", "i"))

    @observe("type")
    def _update_proxy(self, change: ChangeDict):
        super()._update_proxy(change)


class Li(Tag):
    #: Set the tag name
    tag = set_default("li")


class Dl(Tag):
    #: Set the tag name
    tag = set_default("dl")


class Dt(Tag):
    #: Set the tag name
    tag = set_default("dt")


class Dd(Tag):
    #: Set the tag name
    tag = set_default("dd")


class IFrame(Tag):
    #: Set the tag name
    tag = set_default("iframe")

    src = d_(Str())
    height = d_(Str())
    width = d_(Str())
    target = d_(Str())

    @observe("src", "height", "width", "target")
    def _update_proxy(self, change: ChangeDict):
        super()._update_proxy(change)


class Script(Tag):
    #: Set the tag name
    tag = set_default("script")
    src = d_(Str())
    type = d_(Str())

    @observe("type", "src")
    def _update_proxy(self, change: ChangeDict):
        super()._update_proxy(change)


class NoScript(Tag):
    #: Set the tag name
    tag = set_default("noscript")


class Meta(Tag):
    #: Set the tag name
    tag = set_default("meta")

    name = d_(Str())
    content = d_(Str())

    @observe("name", "content")
    def _update_proxy(self, change: ChangeDict):
        super()._update_proxy(change)


class Base(Tag):
    #: Set the tag name
    tag = set_default("base")

    href = d_(Str())
    target = d_(Enum("", "_blank", "_self", "_parent", "_top", "framename"))

    @observe("href", "target")
    def _update_proxy(self, change: ChangeDict):
        super()._update_proxy(change)


class Header(Tag):
    #: Set the tag name
    tag = set_default("header")


class Nav(Tag):
    #: Set the tag name
    tag = set_default("nav")


class Section(Tag):
    #: Set the tag name
    tag = set_default("section")


class Aside(Tag):
    #: Set the tag name
    tag = set_default("aside")


class Article(Tag):
    #: Set the tag name
    tag = set_default("article")


class Footer(Tag):
    #: Set the tag name
    tag = set_default("footer")


class Summary(Tag):
    #: Set the tag name
    tag = set_default("summary")


class Details(Tag):
    #: Set the tag name
    tag = set_default("details")


class Form(Tag):
    #: Set the tag name
    tag = set_default("form")

    action = d_(Str())
    method = d_(Enum("post", "get"))

    @observe("action", "method")
    def _update_proxy(self, change: ChangeDict):
        super()._update_proxy(change)


class Fieldset(Tag):
    #: Set the tag name
    tag = set_default("fieldset")


class Legend(Tag):
    #: Set the tag name
    tag = set_default("legend")


class Label(Tag):
    #: Set the tag name
    tag = set_default("label")


class Select(Tag):
    #: Set the tag name
    tag = set_default("select")

    name = d_(Str())
    value = d_(Str())

    def _default_name(self):
        return "{}".format(self.id)

    @observe("name", "value")
    def _update_proxy(self, change: ChangeDict):
        super()._update_proxy(change)


class Option(Tag):
    #: Set the tag name
    tag = set_default("option")

    value = d_(Str())
    selected = d_(Coerced(bool))

    @observe("value", "selected")
    def _update_proxy(self, change: ChangeDict):
        super()._update_proxy(change)


class OptGroup(Tag):
    #: Set the tag name
    tag = set_default("optgroup")

    label = d_(Str())
    disabled = d_(Coerced(bool))

    @observe("label", "disabled")
    def _update_proxy(self, change: ChangeDict):
        super()._update_proxy(change)


class Input(Tag):
    #: Set the tag name
    tag = set_default("input")

    name = d_(Str())
    type = d_(Str())
    placeholder = d_(Str())
    disabled = d_(Coerced(bool))
    checked = d_(Coerced(bool))
    value = d_(Value())

    def _default_name(self):
        return f"{self.id}"

    @observe("name", "type", "disabled", "checked", "value", "placeholder")
    def _update_proxy(self, change: ChangeDict):
        super()._update_proxy(change)


class Textarea(Tag):
    #: Set the tag name
    tag = set_default("textarea")

    name = d_(Str())
    rows = d_(Str())
    cols = d_(Str())

    def _default_name(self):
        return f"{self.id}"

    @observe("name", "rows", "cols")
    def _update_proxy(self, change: ChangeDict):
        super()._update_proxy(change)


class Button(Tag):
    #: Set the tag name
    tag = set_default("button")

    name = d_(Str())
    type = d_(Str())
    value = d_(Str("1"))

    def _default_name(self):
        return f"{self.id}"

    @observe("type")
    def _update_proxy(self, change: ChangeDict):
        super()._update_proxy(change)


class Video(Tag):
    #: Set the tag name
    tag = set_default("video")

    controls = d_(Coerced(bool))

    @observe("controls")
    def _update_proxy(self, change: ChangeDict):
        super()._update_proxy(change)


class Source(Tag):
    #: Set the tag name
    tag = set_default("source")

    src = d_(Str())
    type = d_(Str())

    @observe("src", "type")
    def _update_proxy(self, change: ChangeDict):
        super()._update_proxy(change)
