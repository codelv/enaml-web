
def server_factory():
    from .twisted.tx_server import TxServer
    return TxServer

def site_factory():
    from .twisted.tx_site import TxSite
    return TxSite

def resource_factory():
    from .twisted.tx_resource import TxResource
    return TxResource

WEB_FACTORIES = {
    'Server': server_factory,
    'Site': site_factory,
    'Resource': resource_factory,
}