from dnslib import DNSRecord

def parse_dns_message(raw_bytes: bytes) -> dict:
    """
    Parse a raw DNS message in bytes and return a dictionary with its components.
    """
    try:
        d = DNSRecord.parse(raw_bytes)
        return {
            "Qname": str(d.q.qname).rstrip('.'),
            "ANCOUNT": d.header.ancount,
            "NSCOUNT": d.header.nscount,
            "ARCOUNT": d.header.arcount,
            "Answer": [str(rr) for rr in d.rr],
            "Authority": [str(rr) for rr in d.auth],
            "Additional": [str(rr) for rr in d.ar]
        }
    except Exception as e:
        return {"error": f"No se pudo parsear el mensaje: {e}"}