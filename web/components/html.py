'''
Created on Apr 12, 2017

@author: jrm
'''
from atom.api import (
    Event, Enum, Value, Unicode, Dict, Instance, Bool, observe
)

from enaml.core.declarative import d_

from enaml.widgets.toolkit_object import ToolkitObject

class Tag(ToolkitObject):
    #: Object ID
    id = d_(Unicode())
    
    #: Tag name (leave blank for class name)
    tag = d_(Unicode())
    
    #: CSS classes
    cls = d_(Instance((list,basestring)))
    
    #: CSS styles
    style = d_(Instance((dict,basestring)))
    
    #: Node text
    text = d_(Unicode())
    
    #: Node tail text
    tail = d_(Unicode())
    
    #: Alt attribute
    alt = d_(Unicode())    
    
    #: Custom attributes not explicityl defined
    attrs = d_(Dict())
    
    #:  
    on_click = d_(Event())
    
#     on_context_menu = d_(Event())
#     
#     on_dbl_click = d_(Event())
#     
#     on_mouse_down = d_(Event())
#     
#     on_mouse_enter = d_(Event())
#     
#     on_mouse_leave = d_(Event())
#     
#     on_mouse_move = d_(Event())
#     
#     on_mouse_over = d_(Event())
#     
#     on_mouse_out = d_(Event())
#     
#     on_mouse_up = d_(Event())
    
    @observe('id','tag','cls','style','text','tail','alt','attrs')#,'on_click')
    def _update_proxy(self, change):
        """ Update the proxy widget when the Widget data 
         changes."""
        #: Try default handler
        if change['type'] == 'update' and self.proxy_is_active:
            handler = getattr(self.proxy, 'set_' + change['name'],None)
            if handler is not None:
                handler(change['value'])
            else:
                self.proxy.set_attribute(change)
    
    def render(self, parent=None):
        if not self.is_initialized:
            self.initialize()
        if not self.proxy_is_active:
            self.activate_proxy()
        return self.proxy.render()
        
class Html(Tag):
    pass
    
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

class Code(Tag):
    pass

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
    target = d_(Enum("","_blank","_self","_parent","_top","framename"))
    
    @observe('href','target')
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
    
    @observe('src','width','height')
    def _update_proxy(self, change):
        super(Img, self)._update_proxy(change)            

class Style(Tag):
    pass

class Link(Tag):
    type = d_(Unicode())
    rel = d_(Unicode())
    href = d_(Unicode())
    media = d_(Unicode())
    
    @observe('type','rel','href','media')
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
    
    @observe('shape','coords','href')
    def _update_proxy(self, change):
        super(Area, self)._update_proxy(change)
    
class Table(Tag):
    pass

class Tr(Tag):
    pass

class Td(Tag):
    pass

class Th(Tag):
    colspan = d_(Unicode())
    rowspan = d_(Unicode())
    
    @observe('colspan','rowspan')
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
    type = d_(Enum("","1","A","a","I","i"))
    
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
    
    @observe('src','height','width','target')
    def _update_proxy(self, change):
        super(IFrame, self)._update_proxy(change)
    
class Script(Tag):
    src = d_(Unicode())
    type = d_(Unicode())
    
    @observe('type','src')
    def _update_proxy(self, change):
        super(Script, self)._update_proxy(change)

class NoScript(Tag):
    pass

class Meta(Tag):
    name = d_(Unicode())
    content = d_(Unicode())
    
    @observe('name','content')
    def _update_proxy(self, change):
        super(Meta, self)._update_proxy(change)
    
class Base(Tag):
    href = d_(Unicode())
    target = d_(Enum("","_blank","_self","_parent","_top","framename"))
    
    @observe('href','target')
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
    method = d_(Enum("","get","post"))
    
    @observe('action','method')
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
    
    @observe('name','value')
    def _update_proxy(self, change):
        super(Select, self)._update_proxy(change)
    
class Option(Tag):
    value = d_(Unicode())
    selected = d_(Bool())
    
    @observe('value','selected')
    def _update_proxy(self, change):
        super(Option, self)._update_proxy(change)
    

class Input(Tag):
    name = d_(Unicode())
    type = d_(Enum("","radio","checkbox","text","hidden","submit"))
    disabled = d_(Bool())
    checked = d_(Bool())
    value = d_(Value())
    
    @observe('name','type','disabled','checked','value')
    def _update_proxy(self, change):
        super(Input, self)._update_proxy(change)
        
class Textarea(Tag):
    name = d_(Unicode())
    rows = d_(Unicode())
    cols = d_(Unicode())
    
    @observe('name','rows','cols')
    def _update_proxy(self, change):
        super(Textarea, self)._update_proxy(change)
    
class Button(Tag):
    type=d_(Unicode())
    
    @observe('type')
    def _update_proxy(self, change):
        super(Button, self)._update_proxy(change)
