"""
Benchmark different servers

"""
import os
import time
import pytest
import requests
import subprocess
from multiprocessing import Process

BASE = os.path.dirname(__file__)
HELLO_WORLD = 'Hello World!'
with open(os.path.join(BASE, 'templates', 'landing.html'), 'r') as f:
    LANDING_PAGE = f.read()


STATIC_PATH = os.path.join(BASE, '..', 'docs')
with open(os.path.join(STATIC_PATH, 'data-binding.gif'), 'rb') as f:
    STATIC_FILE = f.read()

# Expected responses
RESPONSES = {
    '/': HELLO_WORLD,
    '/landing': LANDING_PAGE,
    '/static/data-binding.gif':  STATIC_FILE
}

def aiohttp_app(port):
    """ Without logging...
    
    Running 30s test @ http://127.0.0.1:8888/
      12 threads and 400 connections
      Thread Stats   Avg      Stdev     Max   +/- Stdev
        Latency    89.37ms    6.68ms 290.76ms   89.18%
        Req/Sec   369.61     80.32   666.00     83.37%
      132444 requests in 30.04s, 20.59MB read
    Requests/sec:   4408.86
    Transfer/sec:    701.81KB
    """
    from web.apps.aiohttp_app import AiohttpApplication
    from aiohttp.web import Response

    async def home(request):
        return Response(text=HELLO_WORLD)

    async def landing(request):
        return Response(text=LANDING_PAGE)

    app = AiohttpApplication()
    app.add_route('/', home)
    app.add_route('/landing', landing)
    app.add_static_route('/static/', STATIC_PATH)
    app.start(port=port)


def sanic_app(port):
    """ With logging
    
    Running 30s test @ http://127.0.0.1:8888/
      12 threads and 400 connections
      Thread Stats   Avg      Stdev     Max   +/- Stdev
        Latency    62.65ms   10.04ms 189.96ms   87.87%
        Req/Sec   526.93    159.98     1.00k    64.25%
      188860 requests in 30.06s, 23.41MB read
    Requests/sec:   6283.35
    Transfer/sec:    797.69KB
    """
    from web.apps.sanic_app import SanicApplication
    from sanic import Sanic, response
    
    app = SanicApplication()

    async def home(request):
        return response.html(HELLO_WORLD)

    async def landing(request):
        return response.html(LANDING_PAGE)
    
    app.add_route('/', home)
    app.add_route('/landing', landing)
    app.add_static_route('/static', STATIC_PATH)
    app.start(port=port)


def falcon_app(port):
    """ With logging
    
    Running 30s test @ http://127.0.0.1:8888/
      12 threads and 400 connections
      Thread Stats   Avg      Stdev     Max   +/- Stdev
        Latency    62.65ms   10.04ms 189.96ms   87.87%
        Req/Sec   526.93    159.98     1.00k    64.25%
      188860 requests in 30.06s, 23.41MB read
    Requests/sec:   6283.35
    Transfer/sec:    797.69KB
    """
    from web.apps.falcon_app import FalconApplication

    app = FalconApplication()

    class HomeResource(object):
        def on_get(self, req, resp):
            resp.body = HELLO_WORLD
    
    class LandingResource(object):
        def on_get(self, req, resp):
            resp.body = LANDING_PAGE
    
    app.add_route('/', HomeResource())
    app.add_route('/landing', LandingResource())
    app.add_static_route('/static', STATIC_PATH)
    app.start(port=port)


def flask_app(port):
    """ With logging
    
    Running 30s test @ http://127.0.0.1:8888/
      12 threads and 400 connections
      Thread Stats   Avg      Stdev     Max   +/- Stdev
        Latency    62.65ms   10.04ms 189.96ms   87.87%
        Req/Sec   526.93    159.98     1.00k    64.25%
      188860 requests in 30.06s, 23.41MB read
    Requests/sec:   6283.35
    Transfer/sec:    797.69KB
    """
    from web.apps.flask_app import FlaskApplication
    from flask import Flask

    app = FlaskApplication()

    def home():
        return HELLO_WORLD
    
    def landing():
        return LANDING_PAGE
    
    app.add_route('/', home)
    app.add_route('/landing', landing)
    app.add_static_route('/static', STATIC_PATH)
    app.start(port=port)

def tornado_app(port):
    """ Even without logging it's slower!
    
    Running 30s test @ http://127.0.0.1:8888/
      12 threads and 400 connections
      Thread Stats   Avg      Stdev     Max   +/- Stdev
        Latency   179.14ms   26.19ms 464.63ms   92.60%
        Req/Sec   184.55    107.47   560.00     57.59%
      64871 requests in 30.10s, 12.87MB read
    Requests/sec:   2155.42
    Transfer/sec:    437.82KB
    
    with logging
    
    Running 30s test @ http://127.0.0.1:8888/
      12 threads and 400 connections
      Thread Stats   Avg      Stdev     Max   +/- Stdev
        Latency   209.77ms   28.48ms 320.47ms   91.43%
        Req/Sec   156.14     79.60   500.00     63.72%
      55415 requests in 30.10s, 10.99MB read
    Requests/sec:   1841.04
    Transfer/sec:    373.96KB


    """
    import tornado.web
    from web.apps.tornado_app import TornadoApplication
    from tornado.log import enable_pretty_logging
    enable_pretty_logging()
    
    app = TornadoApplication()

    class MainHandler(tornado.web.RequestHandler):
        def get(self):
            self.write(HELLO_WORLD)
    
    class LandingHandler(tornado.web.RequestHandler):
        def get(self):
            self.write(LANDING_PAGE)
    
    app.add_route('/', MainHandler)
    app.add_route('/landing', LandingHandler)
    app.add_static_route('/static', STATIC_PATH)
    app.start(port=port)


def twisted_app(port):
    """ With logging
    
    Running 30s test @ http://127.0.0.1:8888/
      12 threads and 400 connections
      Thread Stats   Avg      Stdev     Max   +/- Stdev
        Latency   124.17ms   24.74ms 492.40ms   85.64%
        Req/Sec   245.94     80.01     0.86k    66.42%
      87585 requests in 30.05s, 11.78MB read
    Requests/sec:   2914.22
    Transfer/sec:    401.27KB

    """
    from twisted.web import server
    from twisted.web.resource import Resource
    from web.apps.twisted_app import TwistedApplication

    class Main(Resource):
        def getChild(self, name, request):
            name = name.decode()
            if name == '':
                return self
            return self.children[name]

        def render_GET(self, request):
            return HELLO_WORLD.encode()

    class Landing(Resource):
        isLeaf = True
        def render_GET(self, request):
            return LANDING_PAGE.encode()

    root = Main()
    root.putChild('landing', Landing())

    site = server.Site(root)
    TwistedApplication(port=port, site=site).start()

def clip(s, n=100):
    if len(s)<=n:
        return s
    return s[:n]

@pytest.mark.parametrize('server, route', [
    (server, route)
        for server in (
                aiohttp_app,
                #sanic_app, # Sanic is a memory hog and keeps killing my laptop
                falcon_app,
                tornado_app,
                #twisted_app,
        )
            for route in RESPONSES.keys()
])
def test_benchmarks(capsys, server, route):
    port = 8888
    url = 'http://127.0.0.1:{}{}'.format(port, route)
    benchmark = 'wrk -t12 -c400 -d30s {}'.format(url)
    p = Process(target=server, args=(port,))
    p.start()
    try:
        time.sleep(1)

        # Make sure the page is actually what we expect
        r = requests.get(url)
        if not r.ok:
            with capsys.disabled():
                print(clip(r.content, 100))
            assert r.ok
        if 'static' in route:
            assert r.content == RESPONSES[route]
        else:
            assert r.content.decode() == RESPONSES[route]

        # Run wrk
        results = subprocess.check_output(benchmark.split())
        with capsys.disabled():
            print("\n---------------------")
            for line in results.split(b"\n"):
                print(line.decode())
            print("---------------------")
    finally:
        p.terminate()
    time.sleep(2)
    

if __name__ == '__main__':
  aiohttp_app(8888)
  
