import sys

def app(environ, start_response):
    # TODO 
    # data必须是byte
    data = b"Hello, World!!!\n" 

    start_response("200 OK", [
        ("Content-Type", "text/plain"),
        ("Content-Length", str(len(data)))
    ])

    return iter([data])

# def warn(msg):
#     print("!!!", file=sys.stderr)

#     lines = msg.splitlines()
#     for i, line in enumerate(lines):
#         if i == 0:
#             line = "WARNING: %s" % line
#         print("!!! %s" % line, file=sys.stderr)

#     print("!!!\n", file=sys.stderr)
#     sys.stderr.flush()
    
# warn('warn msg1\nwarn msg2\nwarn msg3')
# import os

# print('ready to print sys.argv')
# print(sys.argv[0])

# print(os.path.basename(sys.argv[0]))