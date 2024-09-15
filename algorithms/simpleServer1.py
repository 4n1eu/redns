import redns

def simpleServ(domain, rtype):
    return redns.resolve(domain, rtype, '1.1.1.1', timeout=2, retries=1)

redns.start(ip="127.0.0.1", port="53553", algorithm=simpleServ)