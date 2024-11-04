import sys

def app(environ, start_response):
    # TODO 
    # data必须是byte
    data = b"Hello, Fuck!!!\n" 

    start_response("200 OK", [
        ("Content-Type", "text/plain"),
        ("Content-Length", str(len(data)))
    ])

    return iter([data])