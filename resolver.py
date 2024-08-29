import dns.message
import dns.query
import dns.rrset
import dns.exception
import dns.rdatatype

import json

def resolve_domain(domain:str, rtype:str, nameserver:str="1.1.1.1:53", timeout=2, retries=1):

    if ":" in nameserver:
        nameserver_host, nameserver_port = nameserver.split(":")
    else:
        nameserver_host = nameserver
        nameserver_port = 53

    try:
        dns_req = dns.message.make_query(domain, rtype)
        resp, wasTCP = dns.query.udp_with_fallback(dns_req, where=nameserver_host, port=int(nameserver_port), timeout=timeout, one_rr_per_rrset=True)
    except Exception as e:
        print(f"Error for request: {json.dumps({'error': str(e)})}")
        return 0
    
    # answer is a list of rrsets
    # rrset is a set containing the resource records

    if not resp or not resp.answer:
        return 0
    else:
        return resp.answer



if __name__ == "__main__":
    x = resolve_domain("4n1.eu", "txt", "127.0.0.1:53535")
    if not x:
        print(0)
        exit()
    for y in x:
        print(y)