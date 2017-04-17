# Enaml Web Components #

Using enaml as a declarative  "templating engine" for building dynamic component based websites in python.

_Note: this is still in alpha currently it cannot bind data between the browser and server_

### Servers ###

Currently supports the following webservers:

1. Tornado
2. Twisted
3. Cyclone

### Examples ###

See the examples folder.

#### Tutorial ####

 A page is defined as an enaml view directly in python as shown below. Simply replace html tags with the enaml component (eg. the capitalized tag name). 

```python
from web.components.api import *

enamldef Index(Html):
    Head:
        Title:
            text = "Hello world"
    Body:
        H1:
            text = "Hello world"

```

The enaml view then generates the an xml tree (using lxml) based on the models and variables passed to the template. Finally, the toolkit implementation renders the lxml and writes the response.  


```python

import enaml
import cyclone.web

class IndexHandler(cyclone.web.RequestHandler):
    view = None # Set statically so it's only loaded once
    def get(self):
        if self.view is None:
            with enaml.imports():
                from index import Index
            self.__class__.view = Index()
        self.write(self.view.render()) 


```

Next simply pass the app for your server to the corresponding implemenation of the enaml application.

```python

import cyclone.web

class Application(cyclone.web.Application,object):
    def __init__(self):
        super(Application, self).__init__([
                (r'/',IndexHandler) 
           ],
            xheaders=False
        )
        
if __name__ == "__main__":
    from web.impl.cyclone_app import CycloneApplication
    app = CycloneApplication(port=8888,app=Application())
    app.start()

```


#### Speed ####

The initial load of a page takes some time to build the lxml tree and template. However, subsequent loads only have to change the tree based on the different variables passed and are thus significantly faster often < 1ms.





 



