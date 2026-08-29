import socket
import dnslib
import utils

listen_address = ("0.0.0.0", 8000)
listen_socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
listen_socket.bind(listen_address)
print(f"Servidor escuchando en {listen_address[0]}:{listen_address[1]}")

try:
    while True:
        data, addr = listen_socket.recvfrom(4096)
        print(f"Mensaje recibido desde {addr}:")
        print(data)

        parsed_data = utils.parse_dns_message(data)
        print("Estructura del mensaje DNS:")
        for key, value in parsed_data.items():
            print(f"{key}: {value}")

except KeyboardInterrupt:
    print("\nServidor detenido.")
finally:
    listen_socket.close() 


