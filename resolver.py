import socket
from dnslib import DNSRecord, QTYPE
from utils import parse_dns_message, send_udp_message

ROOT_IP = "198.41.0.4"

def resolver(mensaje_consulta: bytes, ip_addr=ROOT_IP) -> bytes:
    """
    Resolver function that sends a DNS query to the specified IP address and handles the response.
    """
    response = send_udp_message(mensaje_consulta, ip_addr)
    if not response:
        return b""
    
    dns_response = DNSRecord.parse(response)

    for rr in dns_response.rr: # Caso 1: Answer tiene la respuesta
        if rr.rtype == QTYPE.A:
            return response

    has_ns = any(rr.rtype == QTYPE.NS for rr in dns_response.auth) 
    
    if has_ns: # Caso 2: Delegación a otro NS
        for rr in dns_response.ar:
            if rr.rtype == QTYPE.A:
                ip_next = str(rr.rdata)
                return resolver(mensaje_consulta, ip_addr=ip_next)

        for rr in dns_response.auth:
            if rr.rtype == QTYPE.NS:
                ns_domain = str(rr.rdata)
                ns_query = DNSRecord.question(ns_domain).pack()
                ns_ip_bytes = resolver(ns_query, ROOT_IP)
                
                if ns_ip_bytes:
                    ns_dns_ans = DNSRecord.parse(ns_ip_bytes)
                    for ns_rr in ns_dns_ans.rr:
                        if ns_rr.rtype == QTYPE.A:
                            ip_next = str(ns_rr.rdata)
                            return resolver(mensaje_consulta, ip_addr=ip_next)

    return b""

if __name__ == "__main__":
    listen_address = ("0.0.0.0", 8000)
    listen_socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    listen_socket.bind(listen_address)
    print(f"Resolver escuchando en {listen_address[0]}:{listen_address[1]}")

    try:
        while True:
            data, addr = listen_socket.recvfrom(4096)
            print(f"Mensaje recibido desde {addr}:")
            print(data)

            response = resolver(data)
            if not response:
                print("No se pudo obtener una respuesta del resolver.")
                continue

            listen_socket.sendto(response, addr)
            print(f"Respuesta enviada a {addr}:")
            print(response)

            parsed_data = parse_dns_message(data)
            print("Estructura del mensaje DNS:")
            for key, value in parsed_data.items():
                print(f"{key}: {value}")

    except KeyboardInterrupt:
        print("\nServidor detenido.")
    finally:
        listen_socket.close() 


