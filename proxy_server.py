#!/usr/bin/env python3
import socket
import sys
from multiprocessing import Process

#define address & buffer size
HOST = ""
PORT = 8001
BUFFER_SIZE = 1024

#create a tcp socket
def create_tcp_socket():
    print('Creating socket')
    try:
        s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    except (socket.error, msg):
        print(f'Failed to create socket. Error code: {str(msg[0])} , Error message : {msg[1]}')
        sys.exit()
    print('Socket created successfully')
    return s

#get host information
def get_remote_ip(host):
    print(f'Getting IP for {host}')
    try:
        remote_ip = socket.gethostbyname( host )
    except socket.gaierror:
        print ('Hostname could not be resolved. Exiting')
        sys.exit()

    print (f'Ip address of {host} is {remote_ip}')
    return remote_ip

#send data to server
def send_data(serversocket, payload):
    print("Sending payload")    
    try:
        serversocket.sendall(payload.encode())
    except socket.error:
        print ('Send failed')
        sys.exit()
    print("Payload sent successfully")

def handle_request(conn, client_sock):
    send_full_data = conn.recv(BUFFER_SIZE)
    print(f"Sending incoming data {send_full_data} to google")
    client_sock.sendall(send_full_data)
    client_sock.shutdown(socket.SHUT_WR)
    #continue accepting data until no more left
    full_data = b""
    while True:
        data = client_sock.recv(BUFFER_SIZE)
        if not data:
            break
        full_data += data
    print(f"Sending received data {data} to client")
    #send it back
    conn.send(data)
    conn.close()

def main():
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as server_sock:
    
        server_sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        
        #bind socket to address
        server_sock.bind((HOST, PORT))
        #set to listening mode
        server_sock.listen(2)
        while True:
            conn, addr = server_sock.accept()
            with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as client_sock:
                print("Connecting to Google")
                remote_ip = get_remote_ip("www.google.com")
                client_sock.connect((remote_ip, 80))
                print("Incoming from", addr)
                p = Process(target=handle_request, args=(conn, client_sock))
                p.daemon = True
                p.start()
                print('Started process to handle request', p)
            conn.close()

if __name__ == "__main__":
    main()
