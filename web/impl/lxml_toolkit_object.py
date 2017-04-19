'''
Created on Apr 12, 2017

@author: jrm
'''

from atom.api import Typed, Tuple, Event

from enaml.widgets.toolkit_object import ProxyToolkitObject

import lxml.html
from lxml.etree import _Element, Element, SubElement


class WebComponent(ProxyToolkitObject):
    """ An lxml implementation of an Enaml ProxyToolkitObject.

    """
    #: A reference to the toolkit widget created by the proxy.
    widget = Typed(_Element)
    
    #: Attributes to exclude from passing to the element
    excluded = Tuple(default=('tag','attrs','cls','class','style','activated','initialized','text')) 

    #--------------------------------------------------------------------------
    # Initialization API
    #--------------------------------------------------------------------------
    def create_widget(self):
        """ Create the toolkit widget for the proxy object.

        This method is called during the top-down pass, just before the
        'init_widget()' method is called. This method should create the
        toolkit widget and assign it to the 'widget' attribute.

        """
        d = self.declaration
        attrs = {}
        if d.cls:
            attrs['class'] = d.cls  if isinstance(d.cls,basestring) else " ".join(d.cls)
        if d.style:
            attrs['style'] = d.style if isinstance(d.style,basestring) else  ";".join(["{}:{};".format(k,v) for k,v in d.style.items()])
             
        for name,member in d.members().items():
            if name in self.excluded:
                continue
            elif not member.metadata:
                continue
            elif not (member.metadata.get('d_member') and member.metadata.get('d_final')):
                continue
            
            if isinstance(member, Event):
                #: TODO: Handle triggers??
                #if not d.id: #: Force an ID
                 #   d.id = u'obj-%d' % id(d)
                #attrs[name.replace("_","")] = "Enaml.trigger('{}','{}')".format(d.id,name)
                pass
            else:
                #: TODO: Handle updates?? 
                v = getattr(d,name)
                if v:
                    attrs[name] = unicode(v)
                
        attrs.update(d.attrs)
        
        parent = self.parent_widget()
        if parent is None:
            node = Element('html',attrs)
        else:
            tag = d.tag or d.__class__.__name__.lower()
            node = SubElement(parent,tag,attrs)
        self.widget = node

    def init_widget(self):
        """ Initialize the state of the toolkit widget.

        This method is called during the top-down pass, just after the
        'create_widget()' method is called. This method should init the
        state of the widget. The child widgets will not yet be created.

        """
        widget = self.widget
        if widget is not None:
            d = self.declaration
            if d.text:
                widget.text = d.text
            if d.id:
                widget.set('id',d.id)
            #widget.set('id',d.id or u'obj-%d' % id(d))

    def init_layout(self):
        """ Initialize the layout of the toolkit widget.

        This method is called during the bottom-up pass. This method
        should initialize the layout of the widget. The child widgets
        will be fully initialized and layed out when this is called.

        """
        pass

    #--------------------------------------------------------------------------
    # ProxyToolkitObject API
    #--------------------------------------------------------------------------
    def activate_top_down(self):
        """ Activate the proxy for the top-down pass.

        """
        self.create_widget()
        self.init_widget()

    def activate_bottom_up(self):
        """ Activate the proxy tree for the bottom-up pass.

        """
        self.init_layout()

    def destroy(self):
        """ A reimplemented destructor.

        This destructor will clear the reference to the toolkit widget
        and set its parent to None.

        """
        widget = self.widget
        if widget is not None:
            widget.getparent().remove(widget)
            del self.widget
        super(WebComponent, self).destroy()

    def child_removed(self, child):
        """ Handle the child removed event from the declaration.

        This handler will unparent the child toolkit widget. Subclasses
        which need more control should reimplement this method.

        """
        super(WebComponent, self).child_removed(child)
        if child.widget is not None:
            self.widget.remove(child.widget)

    #--------------------------------------------------------------------------
    # Public API
    #--------------------------------------------------------------------------
    def render(self):
        """ Render the widget tree into a string """
        return lxml.html.tostring(self.widget,pretty_print=True)

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
                
    #--------------------------------------------------------------------------
    # Change handlers
    #--------------------------------------------------------------------------
    def update_attribute(self,change):
        if isinstance(change['value'],dict):
            self.widget.attrib.update(change['value'])
        else:
            self.widget.set(change['name'],change['value'])
    
    