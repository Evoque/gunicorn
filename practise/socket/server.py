
import socket

ss = socket.socket()
# get the according IP address
ip = socket.gethostbyname(socket.gethostname())
ss.bind((ip, 12345))
# listen for incoming connections (server mode) with 3 connection at a time
ss.listen(3)
print("[LISTENED] Server ip address:", ip)
print("[SS] ", ss)

while True:
    # waiting for a connection establishment
    print("Waiting for a connection")
    conn, client_address = ss.accept()
    try:
        print("Connect from ", client_address)
        print("[Conn] ", conn)
        # sending to the client
        conn.send(b"Now You are connected")
        
        # receiving the message
        while True:
            data = conn.recv(1024).decode("utf-8")
            if data:
                # print(list(client_address)[0], end="")
                print(client_address, end="")
                print(": %s" % data)
                
                # new_data = input("You: ").encode()
                # conn.send(new_data)
        
    finally:
        conn.close()