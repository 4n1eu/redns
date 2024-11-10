import redns
import dns.dnssec

def simpleServ(domain, rtype):
    ans = redns.resolve(domain, rtype, '1.1.1.1', timeout=2, retries=1)
    return ans

redns.start(ip="127.0.0.1", port=53535, algorithm=simpleServ)