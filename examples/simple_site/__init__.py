from .models import Site

def load(app):
    """ Load the site """
    return Site(app=app)