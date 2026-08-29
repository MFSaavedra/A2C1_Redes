import socket
import dnslib

listen_address = ("0.0.0.0", 8000)
listen_socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)

listen_address.bind(listen_address)

try:
    while True:
        data, addr = listen_socket.recvfrom(4096)
        print(f"Mensaje....blabla:")
        print(data)
except..:
    print("\nServidor detenido.")
finally:
    sock.close() 


