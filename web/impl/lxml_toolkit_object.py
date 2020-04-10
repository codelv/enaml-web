"""
Copyright (c) 2017, Jairus Martin.

Distributed under the terms of the MIT License.

The full license is in the file LICENSE.txt, distributed with this software.

Created on Apr 12, 2017

@author: jrm
"""
from atom.api import Typed,  Constant, Event, Property, Dict, atomref
from lxml.html import tostring
from lxml.etree import _Element, Element, SubElement
from web.components.html import ProxyTag
from web.core.app import WebApplication


class WebComponent(ProxyTag):
    """ An lxml implementation of an Enaml ProxyToolkitObject.

    """

    #: A reference to the toolkit widget created by the proxy.
    widget = Typed(_Element)

    #: A cached reference to the root element.
    #: WARNING: If the root is changed this becomes invalid
    root = Property(lambda self: self.parent().root, cached=True)

    # -------------------------------------------------------------------------
    # Initialization API
    # -------------------------------------------------------------------------
    def create_widget(self):
        """ Create the toolkit widget for the proxy object.

        This method is called during the top-down pass, just before the
        'init_widget()' method is called. This method should create the
        toolkit widget and assign it to the 'widget' attribute.

        """
        self.widget = SubElement(self.parent_widget(), self.declaration.tag)

    def init_widget(self):
        """ Initialize the state of the toolkit widget.

        This method is called during the top-down pass, just after the
        'create_widget()' method is called. This method should init the
        state of the widget. The child widgets will not yet be created.

        """
        widget = self.widget
        d = self.declaration

        #: Save ref id
        self.root.cache[d.id] = atomref(self)
        widget.set('id', d.id)

        if d.text:
            self.set_text(d.text)
        if d.tail:
            self.set_tail(d.tail)
        if d.style:
            self.set_style(d.style)
        if d.cls:
            self.set_cls(d.cls)
        if d.attrs:
            self.set_attrs(d.attrs)
        if d.draggable:
            self.set_draggable(d.draggable)

        # Set any attributes that may be defined
        for name, member in d.members().items():
            meta = member.metadata
            if not meta:
                continue

            # Exclude any attr tags
            if not (meta.get('d_member') and meta.get('d_final')):
                continue

            # Skip any items tagged with attr=false
            elif not meta.get('attr', True):
                continue

            elif isinstance(member, Event):
                continue

            value = getattr(d, name)
            if value:
                self.set_attribute(name, value)

    def init_layout(self):
        """ Initialize the layout of the toolkit widget.

        This method is called during the bottom-up pass. This method
        should initialize the layout of the widget. The child widgets
        will be fully initialized and layed out when this is called.

        """
        pass

    def init_events(self):
        """ Initialize the event handlers of the toolkit widget.

        This method is called during the bottom-up pass. This method
        should initialize the event handlers for the widget. The child widgets
        will be fully initialized and layed out when this is called.

        """
        pass

    # -------------------------------------------------------------------------
    # ProxyToolkitObject API
    # -------------------------------------------------------------------------
    def activate_top_down(self):
        """ Activate the proxy for the top-down pass.

        """
        self.create_widget()
        self.init_widget()

    def activate_bottom_up(self):
        """ Activate the proxy tree for the bottom-up pass.

        """
        self.init_layout()
        self.init_events()

    def destroy(self):
        """ A reimplemented destructor.

        This destructor will clear the reference to the toolkit widget
        and set its parent to None.

        """
        widget = self.widget
        if widget is not None:
            parent = widget.getparent()
            if parent is not None:
                parent.remove(widget)
            del self.widget

            # Remove from cache
            self.root.cache.pop(self.declaration.id, None)

        super(WebComponent, self).destroy()

    def child_added(self, child):
        """ Handle the child added event from the declaration.

        This handler will insert the child toolkit widget in the correct.
        position. Subclasses which need more control should reimplement this
        method.

        """
        super(WebComponent, self).child_added(child)
        if isinstance(child, WebComponent):
            # Use insert to put in the correct spot
            for i, c in enumerate(self.children()):
                if c is child:
                    self.widget.insert(i, child.widget)
                    break

    def child_moved(self, child):
        """ Handle the child moved event from the declaration.

        This handler will pop the child and insert it in the correct position
        if it isn't already there.

        Subclasses which need more control should reimplement this method.

        Returns
        -------
        was_moved: Bool
            Whether a move was performed or not

        """
        # There is no super child_moved method
        if isinstance(child, WebComponent):
            # Determine the new index
            for i, c in enumerate(self.children()):
                if c is child:
                    w = self.widget
                    j = w.index(child.widget)
                    if j != i:
                        # Delete and re-insert at correct position
                        del w[j]
                        w.insert(i, child.widget)
                        return True
                    break
        return False

    def child_removed(self, child):
        """ Handle the child removed event from the declaration.

        This handler will unparent the child toolkit widget. Subclasses
        which need more control should reimplement this method.

        """
        super(WebComponent, self).child_removed(child)
        if isinstance(child, WebComponent):
            self.widget.remove(child.widget)

    # -------------------------------------------------------------------------
    # Public API
    # -------------------------------------------------------------------------
    def render(self, method='html', encoding='unicode', **kwargs):
        """ Render the widget tree into a string """
        return tostring(self.widget, method=method, encoding=encoding, **kwargs)

    def xpath(self, query, **kwargs):
        """ Get the node(s) matching the query"""
        nodes = self.widget.xpath(query, **kwargs)
        if not nodes:
            return []
        matches = []
        cache = self.root.cache
        for node in nodes:
            aref = cache.get(node.attrib.get('id'))
            obj = aref() if aref else None
            if obj is None:
                continue
            matches.append(obj)
        return matches

    def parent_widget(self):
        """ Get the parent toolkit widget for this object.

        Returns
        -------
        result : QObject or None
            The toolkit widget declared on the declaration parent, or
            None if there is no such parent.

        """
        parent = self.parent()
        if parent is not None:
            return parent.widget

    def child_widgets(self):
        """ Get the child toolkit widgets for this object.

        Returns
        -------
        result : iterable of QObject
            The child widgets defined for this object.

        """
        for child in self.children():
            w = child.widget
            if w is not None:
                yield w

    # -------------------------------------------------------------------------
    # Change handlers
    # -------------------------------------------------------------------------
    def set_text(self, text):
        self.widget.text = text

    def set_tail(self, text):
        self.widget.tail = text

    def set_tag(self, tag):
        self.widget.tag = tag

    def set_attrs(self, attrs):
        """ Set any attributes not explicitly defined """
        self.widget.attrib.update(attrs)

    def set_cls(self, cls):
        if isinstance(cls, (tuple, list)):
            cls = " ".join(cls)
        else:
            cls = str(cls)
        self.widget.set('class', cls)

    def set_style(self, style):
        if isinstance(style, dict):
            style = ";".join("%s:%s" % s for s in style.items())
        else:
            style = str(style)
        self.widget.set('style', style)

    def set_attribute(self, name, value):
        """ Default handler for those not explicitly defined """
        if value is True:
            self.widget.set(name, name)
        elif value is False:
            del self.widget.attrib[name]
        else:
            self.widget.set(name, str(value))

    def set_draggable(self, draggable):
        """ The draggable attr must be explicitly set to true or false """
        self.widget.set('draggable', 'true' if draggable else 'false')


class RootWebComponent(WebComponent):
    """ A root component """

    #: Components are cached for lookup by id so xpath queries from lxml
    #: can retrieve their declaration component
    cache = Dict()

    #: Return a reference to self since this is the root
    root = Property(lambda self: self, cached=True)

    def create_widget(self):
        self.widget = Element(self.declaration.tag)
