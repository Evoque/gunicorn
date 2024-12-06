
import os
import socket 

server = input("Enter Server IP: ")

cs = socket.socket()
cs.connect((server, 12345))
print('[Connect] Connect to server, port:', os.getpid())
print('[CS] ', cs)

data = cs.recv(1024).decode()
print(server + ": " + data)


while True:
    new_data = input("[Client] You: ").encode()
    # cs.sendall(new_data)
    cs.send(new_data)
    # data = cs.recv(1024).decode()
    # print(server + ": " + data)
    

cs.close()
