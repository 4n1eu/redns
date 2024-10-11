import redns
import dns.query
import dns.message


def resolve(domain:str, rtype:str, nameserver:str="1.1.1.1:53", timeout=1, retries=1):
    if ":" in nameserver:
        ns_ip, ns_port = nameserver.split(":")
    else:
        ns_ip = nameserver
        ns_port = 53
	
    dns_req = dns.message.make_query(domain, rtype)
    try:
        resp = dns.query.tcp(dns_req, where=ns_ip, port=int(ns_port), timeout=timeout, one_rr_per_rrset=True)
    except:
        print(":(")
        exit()

    if not resp or not resp.answer:
        return 0
    else:
        return resp.answer
    



print(resolve("4n1.eu","a","127.0.0.1:53535"))