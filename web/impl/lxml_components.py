'''
Created on Apr 12, 2017

@author: jrm
'''
import inspect
from web.components import html
from web.impl.lxml_toolkit_object import WebComponent

FACTORIES = {}

for name, obj in inspect.getmembers(html):
    if inspect.isclass(obj):
        FACTORIES[name] = lambda:WebComponent





    
    
    