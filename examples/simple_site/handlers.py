'''
Created on Apr 16, 2017

@author: jrm
'''
import pydoc
import enaml
import atom.api
import cyclone.web
from models import Message


class BaseHandler(cyclone.web.RequestHandler):
    view = None # Holds the View
    site = None # Set by Site model to Site instance
    page = None # Set by Site model to Page instance
    
    def prepare(self):
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

class ModelHandler(BaseHandler):
    model = atom.api.Atom
    
    def get(self, model=None):
        self.view.model = model or self.model()
        super(ModelHandler, self).get()
        
    def is_valid(self,obj):
        return True
        
    def post(self, model=None):
        # Update the message
        obj = model or self.model()
        for k,v in self.request.arguments.items():
            m =  obj.get_member(k)
            if m:
                if isinstance(m,(atom.api.Tuple, atom.api.List)):
                    setattr(obj,k,v)
                elif isinstance(m,atom.api.Bool):
                    setattr(obj,k,bool(v[0]))
                elif isinstance(m,atom.api.Int):
                    setattr(obj,k,int(v[0]))
                elif isinstance(m,atom.api.Float):
                    setattr(obj,k,float(v[0]))
                else:
                    setattr(obj,k,v[0])
        #: TODO: Validate
        if self.is_valid(obj):
            self.save(obj)
            obj = None
        
        return self.get(obj)
    
    def save(self,obj):
        raise NotImplementedError

class ContactHandler(ModelHandler):
    model = Message
    
    def save(self,obj):
        msgs = self.site.messages[:]
        msgs.append(obj)
        self.site.messages = msgs
        
