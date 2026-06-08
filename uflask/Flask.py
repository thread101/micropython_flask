import utime
import network
import socket
import pHeader
import json
import os

html = '''
<!DOCTYPE html>
<html lang="en">
<head>
  <meta charset="UTF-8">
  <meta name="viewport" content="width=device-width, initial-scale=1.0">
  <title>{}</title>
</head>
<body>
  {}
</body>
</html>
'''

class Endpoint:
    def __init__(self, route: str, methods: list, handler, variables: list=[]):
        self.route = route
        self.methods = methods
        self.handler = handler
        self.variables = variables

class Flask:
    def __init__(self, path: str):
        assert self.exists(path) == 1, f"invalid path {path} specified"
        self.path = path
        self.log = False
        self.endpoints = []
        self.server = "uflask pico W"
        self.request = None
        self.static_route = "/static"
        self.mime = {
            "txt": "text/plain",
            "html": "text/html",
            "css": "text/css",
            "js": "application/javascript",
            "json": "application/json",
            "py": "x-python"
        }
        self.valid_variables = {
            "<str>": str,
            "<int>": int,
            "<float>": float,
        }

    def _log(self, msg: str) -> None:
        if not self.log: return
        tym = utime.localtime(utime.time())
        stamp = f"{tym[0]}-{tym[1]}-{tym[2]} {tym[3]}:{tym[4]}:{tym[5]}"
        print(f"[{stamp:<19}] {msg}")
        
    def route(self, route: str, methods: list=['GET']):
        def wrapper_func(func):
            def f(sock: socket.socket, request:pHeader.Packet, *args, **kwargs):
                self.request = request
                response = func(*args, **kwargs)
                assert type(response) in [dict, str, list, tuple], f"Unsupported return type {type(response)}"
                if type(response) == tuple: response, code = response
                else: code = 200
                assert type(response) in [dict, str, list], f"Unsupported return type {type(response)}"
                assert type(code) == int, "return code must be of type <class: int>"
                self.request = None
                if type(response) == list:
                    path, options = tuple(response)
                    self.serve_file(path, sock, code, options)
                    return
                elif type(response) == dict:
                    content_type = "application/json"
                    content = json.dumps(response)
                else:
                    content_type = "text/html"
                    content = str(response)
                pkt = pHeader.Packet()
                pkt.header.version = "HTTP/1.1"
                pkt.header.options = [{"Content-Type": content_type}, {"Server": self.server}]
                pkt.code = code
                pkt.content = content
                sock.send(str(pkt))
            if "<" not in route or ">" not in route:
                assert route != self.static_route, f"endpoint {route} is for static files"
                self.endpoints.append(Endpoint(route, methods, f))
            else:
                _route = route[:route.index("/<")]
                variables = route[len(_route):].split("/")[1:]
                _variables = []
                valid_variables = list(self.valid_variables.keys())
                for var in variables:
                    assert var in valid_variables, f"invalid variable {var} type specified"
                    _variables.append(self.valid_variables[var])
                assert _route != self.static_route, f"endpoint {_route} is for static files"
                self.endpoints.append(Endpoint(_route, methods, f, _variables))
        return wrapper_func
    
    def unknown_endpoint(self, sock: socket.socket):
        self._log("\033[31;1mE - unknown endpoint \033[0m")
        pkt = pHeader.Packet()
        pkt.header.version = "HTTP/1.1"
        pkt.header.options = [{"Content-Type": "text/html"}, {"Server": self.server}]
        pkt.code = 404
        title = "Error response"
        page = "<h1>File not found</h1>"
        pkt.content = html.format(title, page)
        sock.send(str(pkt))
        
    def unsupported_method(self, sock: socket.socket):
        self._log("\033[31;1mE - unsupported method \033[0m")
        pkt = pHeader.Packet()
        pkt.header.version = "HTTP/1.1"
        pkt.header.options = [{"Content-Type": "text/html"}, {"Server": self.server}]
        pkt.code = 501
        title = "Error response"
        page = "<h1>Unsupported method</h1>"
        pkt.content = html.format(title, page)
        sock.send(str(pkt))
        
    def run(self, log: bool=False, port: int=8080, host: str="0.0.0.0"):
        net = network.WLAN(network.STA_IF)
        assert net.isconnected(), "No interface connected"
        self.log = log
        s = socket.socket()
        s.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        saddr = socket.getaddrinfo(host, port)[0][-1]
        s.bind(saddr)
        s.listen(1)
        ip = net.ifconfig()[0]
        self._log(f"App running on \033[34;1mhttp://{ip}:{port}/\033[0m, press ctrl+c to close")
        running = True
        while running:
            addr = "unknown:0000"
            try:
                cl, _addr = s.accept()
                addr = f"{_addr[0]}:{_addr[1]}"
                request = pHeader.parse(cl.recv(1024))
                route = request.header.route
                method = request.header.method
                routes = [i.route for i in self.endpoints]
                self._log(f"{addr:<23} {method:<5} {route}")
                if self.static_route == route[:min([len(self.static_route), len(route)])]:
                    header_options = [list(i.keys())[0] for i in request.header.options]
                    if "Referer" not in header_options:
                        self._log("\033[33;1mW - (referer) illegal access\033[0m")
                        self.unknown_endpoint(cl)
                    else:
                        referer = request.header.options[header_options.index("Referer")]["Referer"]
                        try:
                            r = referer.split("/")[3:]
                            for ref in range(len(r), 0, -1):
                                _route = "/" + "/".join(r[:ref])
                                if _route in routes:
                                    self._log(f"I - (referer) route: {_route}")
                                    self.serve_file(self.get_path(f"{self.path}{route}"), cl, 200)
                                    break
                            else:
                                assert False, f"unknown referer {referer}"
                        except Exception as e:
                            self._log(f"\033[33;1mW - (referer) {e}\033[0m")
                            self.unknown_endpoint(cl)
                else:
                    for endpoint in self.endpoints:
                        _route = endpoint.route
                        args = []
                        if _route not in route or route == "*": continue
                        if len(endpoint.variables) == 0:
                            if _route != route: continue
                        else:
                            if _route != route[:min([len(_route), len(route)])]: continue
                            values = route[len(_route):].split("/")[1:]
                            try:
                                assert len(values) == len(endpoint.variables), "incomplete uri input"
                                args = [dtype(inp) for inp, dtype in zip(values, endpoint.variables)]
                            except Exception as e:
                                self._log(f"{addr:<23}\033[31;1m E - {e} \033[0m")
                                continue

                        if method in endpoint.methods: endpoint.handler(cl, request, *args)
                        else: self.unsupported_method(cl)
                        break
                    else:
                        for endpoint in self.endpoints:
                            _route = endpoint.route
                            if '*' not in _route: continue 
                            _route = _route[:_route.index('*')]
                            if _route == route[:len(_route)]:
                                if method in endpoint.methods:
                                    endpoint.handler(cl, request)
                                    break
                        else:
                            if "*" in routes:
                                endpoint = self.endpoints[routes.index("*")]
                                if method in endpoint.methods: endpoint.handler(cl, request)
                                else: self.unsupported_method(cl)                         
                            else: self.unknown_endpoint(cl)

            except KeyboardInterrupt: running = False
            except Exception as e: self._log(f"{addr:<23}\033[31;1m E - {e} \033[0m")
            finally:
                try: cl.close()
                except Exception: pass
                
        s.close()
        self._log(f"\033[1mExiting ...\033[0m")

    def exists(self, path: str):
        try:
            p = os.getcwd()
            os.chdir(path)
            os.chdir(p)
            return 1
        except Exception:
            try:
                with open(path, "r") as f: f.read(1)
                return 2
            except Exception: return False

    def render_template(self, location: str, **kwargs):
        path = f"{self.path}/templates/{location}"
        assert self.exists(path) == 2, f"template {path} does not exist"
        return [path, kwargs]
    
    def serve_file(self, path: str, sock: socket.socket, code: int, options: dict=None):
        if self.exists(path) != 2:
            self._log(f"\033[31;1mFile not found {path}\033[0m")
            self.unknown_endpoint(sock)
            return
        ext = path.rsplit(".")[-1]
        if ext in list(self.mime.keys()): mime = self.mime[ext]
        else: mime = self.mime['txt']
        with open(path, "rb") as f:
            f.seek(0, 2)
            size = f.tell()
        if options is not None:
            for key, value in options.items():
                size -= (len(key) + 2)
                size += len(str(value))
            
        pkt = pHeader.Packet()
        pkt.header.version = "HTTP/1.1"
        pkt.header.options = [{"Content-Type": mime}, {"Server": self.server}, {"Content-Length": size}]
        pkt.code = code
        data = ""
        with open(path, "r") as f:
            iterration = 0
            while True:
                line = f.readline()
                if len(line) == 0 or (len(data) + len(line)) > 4096:
                    if options is not None:
                        kwargs = {}
                        for key, value in options.items():
                            option = "{" + key + "}"
                            if option in data: kwargs.update({key: value})
                        data = data.format(**kwargs)
                    if iterration == 0:
                        pkt.content = data
                        sock.sendall(str(pkt))
                    else:
                        sock.sendall(data)
                    iterration += 1
                    data = ""
                if len(line) == 0: break
                data += line
    
    def get_path(self, route: str):
        route = route.replace("\\", "", route.count("\\"))
        route = route.replace("../", "", route.count("../"))
        route = route.replace("%20", " ", route.count("%20"))
        return route


if __name__ == "__main__":
    app = Flask("/lib/uflask")

    @app.route('/')
    def home():
        return "Hello, World", 200
    
    @app.route('/login/<str>/<int>')
    def login(name, key):
        print("name:", name)
        print("key:", key)
        return app.render_template("index.html", name=name, key=key)
    
    @app.route("/api", methods=["POST", "GET"])
    def api():
        if app.request.header.method.lower() == "post":
            data = json.loads(app.request.content)
            print(data)

        return {"name": "Joe Doe"}
    
    @app.route("/make/*")
    def wildcard():
        return "<p>this is a wildcard endpoint</p>"
    
    app.run(log=True, port=80, host="0.0.0.0")
