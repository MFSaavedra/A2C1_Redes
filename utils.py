import socket
from dnslib import DNSRecord

def parse_dns_message(raw_bytes: bytes) -> dict:
    """
    Parse a raw DNS message in bytes and return a dictionary with its components.
    """
    try:
        d = DNSRecord.parse(raw_bytes)
        return {
            "Qname": str(d.q.qname).rstrip('.'),
            "ANCOUNT": d.header.a,
            "NSCOUNT": d.header.auth,
            "ARCOUNT": d.header.ar,
            "Answer": [str(rr) for rr in d.rr],
            "Authority": [str(rr) for rr in d.auth],
            "Additional": [str(rr) for rr in d.ar]
        }
    except Exception as e:
        return {"error": f"No se pudo parsear el mensaje: {e}"}

def send_udp_message(message: bytes, ip: str, port=53, timeout=3) -> bytes:
    """
    Send a UDP message to the specified IP and port, and return the response.
    """
    sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    sock.settimeout(timeout)
    try:
        sock.sendto(message, (ip, port))
        data, _ = sock.recvfrom(4096)
        return data
    except socket.timeout:
        return b""
    finally:
        sock.close()