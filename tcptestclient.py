import dns.message
import dns.query
import dns.rrset
import dns.exception
import dns.rdatatype

import json


def resolve(domain:str, rtype:str, nameserver:str="1.1.1.1:53", timeout=2, retries=1):

    if ":" in nameserver:
        nameserver_host, nameserver_port = nameserver.split(":")
    else:
        nameserver_host = nameserver
        nameserver_port = 53

    try:
        dns_req = dns.message.make_query(domain, rtype)
        resp = dns.query.tcp(dns_req, where=nameserver_host, port=int(nameserver_port), timeout=timeout, one_rr_per_rrset=True)
    except Exception as e:
        print(f"Error for request: {json.dumps({'error': str(e)})}")
        return 0
    
    # answer is a list of rrsets
    # rrset is a set containing the resource records

    if not resp or not resp.answer:
        return 0
    else:
        return resp.answer



print(resolve("4n1.dev","txt","127.0.0.1:8444"))
