


import socket

clientSocket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

clientSocket.connect(("www.python.org", 80))

serverSocket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

'''
bind the socket to a public host, and a well-known port
`socket.gethostname()`: the socket would be visible to the outside world.
`bind(('localhost',80))` or `bind(('127.0.0.1',80))`: we will have a 'server' that only visible within the same machine.
`bind(('',80))`: specifies that the socket is reachable by any adress the machine happens to have.
'''
serverSocket.bind((socket.gethostname(), 80))
# become a server socket
serverSocket.listen(5)

while True:
    # accept connections from outside
    (cs, addr) = serverSocket.accept()
    # now do something with the clientsocket
    # in this case, we'll 
    ct = client_thread(clientSocket)
    ct.run()



