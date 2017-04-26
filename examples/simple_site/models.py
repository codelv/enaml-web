'''
Created on Apr 15, 2017

@author: jrm
'''
import cyclone.web
from atom.api import Atom, Enum, Bool, Subclass,  Instance, Unicode, List

class Link(Atom):
    url = Unicode()
    text = Unicode()
    menus = List()

class Message(Atom):
    #: Contact form message
    name = Unicode().tag(order=1)
    email = Unicode().tag(order=2)
    message = Unicode().tag(order=3)
    options = Enum('Email','Text','Phone').tag(order=4)
    sign_up = Bool().tag(order=5)
    
class Page(Atom):
    #: Top of page
    title = Unicode()
    
    #: Link to this page
    link = Instance(Link)
    
    #: Js to include
    scripts = List(default= [
        "https://code.jquery.com/jquery-2.1.1.min.js",
        "/static/materialize/js/materialize.min.js",
        "/static/materialize/js/init.js"
    ])
    
    #: Request handler class for this page
    handler = Subclass(cyclone.web.RequestHandler)
    
    #: Dotted path to page view class
    view = Unicode()
    

