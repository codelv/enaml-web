'''
Created on Apr 12, 2017

@author: jrm
'''
import inspect
from web.components import html

def generic_factory():
    from .lxml_toolkit_object import WebComponent
    return WebComponent 

FACTORIES = {
    name:generic_factory 
        for name,obj in inspect.getmembers(html) 
            if inspect.isclass(obj)
}





    
    
    