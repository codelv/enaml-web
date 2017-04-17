'''
Created on Apr 15, 2017

@author: jrm
'''
import os
import cyclone.web
from atom.api import Atom, Enum, Bool, Subclass,  Instance, Unicode, List, observe
from handlers import MainHandler, AboutHandler, ServicesHandler, ContactHandler

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
    
class Site(Atom):
    """ Model representing our site
          this could be serialized to a db using jsonpickle, pickle, etc..  
    """
    
    #: App under which this site runs
    app = Instance(cyclone.web.Application)
    
    #: Url and handlers to add to the application
    handlers = List()
    
    #: Site title
    title = Unicode("Enaml Web")
    theme_color = Unicode("teal")
    theme_color2 = Unicode("brown")
    
    #: Footer title
    footer_title = Unicode("About")
    footer_desc = Unicode("We are a team of college students working on this project like it's our full time job. Any amount would help support and continue development on this project and is greatly appreciated.")
    
    #: Generic links to anywhere
    links = List(Link,default=[
        Link(url="https://github.com/",text="Github",menus=['connect']),
        Link(url="http://stackoverflow.com/",text="Stack overflow",menus=['connect']),
        Link(url="https://www.facebook.com/",text="Facebook",menus=['connect']),
        Link(url="https://github.com/nucleic/enaml",text="Enaml",menus=['dependencies']),
        Link(url="http://www.tornadoweb.org/en/stable/",text="Tornado",menus=['dependencies']),
        Link(url="https://twistedmatrix.com/trac/",text="Twisted",menus=['dependencies']),
    ])
    
    #: Site pages
    pages = List(Page,default = [
        Page(
            title="Home",
            link=Link(url=r'/',text="Home",menus=['nav','footer']),
            view='views.index.Index',
            handler=MainHandler
        ),
        Page(
            title="Services",
            link=Link(url=r"/services/",text="Services",menus=['nav','footer']),
            view='views.services.Services',
            handler=ServicesHandler
        ),
        Page(
            title="About",
            link=Link(url=r"/about/",text="About",menus=['nav','footer']),
            view='views.about.About',
            handler=AboutHandler
        ),
        Page(
            title="Contact",
            link=Link(url=r"/contact/",text="Contact",menus=['nav','footer']),
            view='views.contact.Contact',
            handler=ContactHandler
        ),
    ])
    
    #: Messages
    messages = List(Message)
    
    #: Menus
    nav_menu = List(Link)
    footer_menu = List(Link)
    dependencies_menu = List(Link)
    connect_menu = List(Link)
    
    @observe('links','pages','clients')
    def _update_menus(self,change):
        """ When pages change, update the menus"""
        menus = {}
        
        #: Get all links
        links = [p.link for p in self.pages if p.link] + self.links 
        
        #: Put all links in the correct menu
        for link in links:
            for menu in link.menus:
                if menu not in menus:
                    menus[menu] = []
                menus[menu].append(link)
         
        #: Update the menus
        for name,menu in menus.items():
            k = '{}_menu'.format(name)
            if hasattr(self,k):
                setattr(self,k,menu)        
    
    def _default_handlers(self):
        """ Generate the handlers for this site """
        static_path = os.path.abspath(os.path.join(os.path.dirname(__file__),"static"))
        urls = [
            (r"/static/(.*)", cyclone.web.StaticFileHandler, {"path": static_path}),
        ]
        for p in self.pages:
            handler = p.handler
            handler.site = self
            handler.page = p
            urls.append((p.link.url,handler))
        return urls

