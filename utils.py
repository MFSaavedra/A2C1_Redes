import socket
from collections import Counter
from dnslib import DNSRecord

historial_consultas = []
cache = {}

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

def update_cache(qname: str, response: bytes):
    """
    Update the cache with the given query name and response.
    """
    if not qname or not response:
        return
    
    historial_consultas.append(qname)
    if len(historial_consultas) > 20:
        historial_consultas.pop(0)
        
    top_3 = {dom for dom, _ in Counter(historial_consultas).most_common(3)}

    if qname in top_3:
        cache[qname] = response

    for k in list(cache.keys()):
        if k not in top_3:
            del cache[k]