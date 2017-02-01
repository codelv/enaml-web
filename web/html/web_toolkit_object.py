'''
Created on Jan 31, 2017

@author: jrm
@author: nucotec
'''
from atom.api import Typed

from enaml.widgets.toolkit_object import ProxyToolkitObject

from lxml.html import builder, HtmlElement

class WebToolkitObject(ProxyToolkitObject):
    """ An lxml implementation of an Enaml ProxyToolkitObject.

    """
    #: A reference to the toolkit widget created by the proxy.
    widget = Typed(HtmlElement)

    #--------------------------------------------------------------------------
    # Initialization API
    #--------------------------------------------------------------------------
    def create_widget(self):
        """ Create the toolkit widget for the proxy object.

        This method is called during the top-down pass, just before the
        'init_widget()' method is called. This method should create the
        toolkit widget and assign it to the 'widget' attribute.

        """
        self.widget = builder.HTML()

    def init_widget(self):
        """ Initialize the state of the toolkit widget.

        This method is called during the top-down pass, just after the
        'create_widget()' method is called. This method should init the
        state of the widget. The child widgets will not yet be created.

        """
        widget = self.widget
        if widget is not None:
            # Each Qt object gets a name. If one is not provided by the
            # widget author, one is generated. This is required so that
            # Qt stylesheet cascading can be prevented (Enaml's styling
            # engine applies the cascade itself). Names provided by the
            # widget author are assumed to be unique.
            d = self.declaration
            name = d.name or u'obj-%d' % id(d)
            widget.set('id',name)

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
        super(WebToolkitObject, self).destroy()

    def child_removed(self, child):
        """ Handle the child removed event from the declaration.

        This handler will unparent the child toolkit widget. Subclasses
        which need more control should reimplement this method.

        """
        super(WebToolkitObject, self).child_removed(child)
        if child.widget is not None:
            child.widget.getparent().remove(child.widget)

    #--------------------------------------------------------------------------
    # Public API
    #--------------------------------------------------------------------------
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
