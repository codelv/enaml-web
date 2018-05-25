"""
Copyright (c) 2017, Jairus Martin.

Distributed under the terms of the MIT License.

The full license is in the file COPYING.txt, distributed with this software.

Created on Apr 12, 2017

@author: jrm
"""
from past.builtins import basestring
import weakref
from atom.api import Typed,  Constant,  Event
from web.components.html import ProxyTag
from lxml.html import tostring
from lxml.etree import _Element, Element, SubElement
from .lxml_app import LxmlApplication
CACHE = weakref.WeakValueDictionary()


class WebComponent(ProxyTag):
    """ An lxml implementation of an Enaml ProxyToolkitObject.

    """
    __slots__ = ('__weakref__',)
    
    #: A reference to the toolkit widget created by the proxy.
    widget = Typed(_Element)
    
    #: Attributes to exclude from passing to the element
    #: These are either used internally or manually set
    excluded = Constant(default=('tag', 'attrs', 'cls', 'class',
                                 'style', 'activated', 'initialized',
                                 'text', 'tail', 'websocket'))

    # -------------------------------------------------------------------------
    # Initialization API
    # -------------------------------------------------------------------------
    def create_widget(self):
        """ Create the toolkit widget for the proxy object.

        This method is called during the top-down pass, just before the
        'init_widget()' method is called. This method should create the
        toolkit widget and assign it to the 'widget' attribute.

        """
        parent = self.parent_widget()
        if parent is None:
            self.widget = Element('html')
        else:
            self.widget = SubElement(parent, self.declaration.tag)
        
    def init_widget(self):
        """ Initialize the state of the toolkit widget.

        This method is called during the top-down pass, just after the
        'create_widget()' method is called. This method should init the
        state of the widget. The child widgets will not yet be created.

        """
        widget = self.widget
        if widget is not None:
            d = self.declaration
            
            #: Save ref id
            ref = u'{}'.format(d.ref)
            CACHE[ref] = self
            widget.set('ref', ref)
            
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
            if d.id:
                widget.set('id', d.id)
            
            #: Set any attributes that may be defined
            for name, member in d.members().items():
                if not member.metadata:
                    continue
                elif not (member.metadata.get('d_member') and
                          member.metadata.get('d_final')):
                    continue
                elif name in self.excluded:
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
        super(WebComponent, self).destroy()

    def child_added(self, child):
        """ Handle the child added event from the declaration.

        This handler will insert the child toolkit widget in the correct. 
        position. Subclasses which need more control should reimplement this 
        method.

        """
        super(WebComponent, self).child_added(child)
        if child.widget is not None:
            #: Use insert to put in the correct spot
            for i, c in enumerate(self.children()):
                if c == child:
                    self.widget.insert(i, child.widget)
                    break

    def child_removed(self, child):
        """ Handle the child removed event from the declaration.

        This handler will unparent the child toolkit widget. Subclasses
        which need more control should reimplement this method.

        """
        super(WebComponent, self).child_removed(child)
        if child.widget is not None:
            for i, c in enumerate(self.children()):
                if c == child:
                    del self.widget[i]
                    break

    # -------------------------------------------------------------------------
    # Public API
    # -------------------------------------------------------------------------
    def render(self):
        """ Render the widget tree into a string """
        return tostring(self.widget, pretty_print=True, method='html')
    
    def find(self, query):
        """ Get the node(s) matching the query"""
        nodes = self.widget.xpath(query)
        if nodes:
            refs = [node.attrib.get('ref') for node in nodes
                    if node.attrib.get('ref')]
            return [CACHE[ref] for ref in refs if ref in CACHE]

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
        """ Set any attributes not explicitly defined"""
        self.widget.attrib.update(attrs)
        
    def set_cls(self, cls):
        self.widget.set('class',
                        cls if isinstance(cls, basestring) else " ".join(cls))
        
    def set_style(self, style):
        self.widget.set('style', style if isinstance(style,basestring)
                        else ";".join(["{}:{};".format(k, v)
                                       for k, v in style.items()]))
    
    def set_attribute(self, name, value):
        """ Default handler for those not explicitly defined"""
        if isinstance(value, bool):
            if value: 
                self.widget.set(name, name)
            else:
                del self.widget.attrib[name]
            return
        self.widget.set(name, '{}'.format(value))
        
    # -------------------------------------------------------------------------
    # Event triggers
    # -------------------------------------------------------------------------
    def _write_to_websocket(self, websocket, message):
        """ Defer to the current application instance """
        LxmlApplication.instance().write_to_websocket(websocket, message)
