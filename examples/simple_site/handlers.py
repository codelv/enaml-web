'''
Created on Apr 16, 2017

@author: jrm
'''
import enaml
import cyclone.web 
import pydoc
    
class BaseHandler(cyclone.web.RequestHandler):
    view = None # Holds the View
    site = None # Set by Site model to Site instance
    page = None # Set by Site model to Page instance
    
    def initialize(self,*args,**kwargs):
        super(BaseHandler, self).initialize(*args,**kwargs)
        self.init_view()
        
    def init_view(self):
        """ Load the view on first load """
        if self.__class__.view:
            return
        
        #: Load the View class from the dotted view name
        with enaml.imports():
            View = pydoc.locate(self.page.view)
        assert View, "Failed to import View: {}".format(self.page.view)
        
        #: Set initial view properties
        self.__class__.view = View(
            site=self.site,
            page=self.page,
            request=self.request,
        )
            
        
    def get(self):
        #: Update view
        self.view.request = self.request
        #: Update any view models here
        self.write(self.view.render())
        

class MainHandler(BaseHandler):
    pass

class AboutHandler(BaseHandler):
    pass

class ServicesHandler(BaseHandler):
    pass

class ContactHandler(BaseHandler):
    pass
