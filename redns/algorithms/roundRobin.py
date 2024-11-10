import redns
import nameservers
import logging

log = logging.getLogger('redns.rr')

log2_formatter = logging.Formatter("%(asctime)s.%(msecs)06d: %(message)s",
                                "%Y-%m-%d %H:%M:%S")
log2 = logging.getLogger('rrLog')
log2.setLevel(logging.DEBUG)
log2_fhandler = logging.FileHandler("log/roundrobin.log")
log2_fhandler.setFormatter(log2_formatter)
log2.addHandler(log2_fhandler)


ns = nameservers.get("ns1")
i = 0
def getns():
    global i
    i = (i+1)%len(ns)
    return ns[i]

def roundRobin(domain, rtype):
    usens = getns()
    res = redns.resolve(domain, rtype, nameserver=usens, timeout=2, retries=2)
    if res:
        log2.debug(f"valid response for '{domain} IN {rtype}' from {usens}: {res}")
    else:
        log2.debug(f"got empty / no response for '{domain} IN {rtype}' from {usens}")
    return res


if __name__ == "__main__":
    redns.start(port=53535, algorithm=roundRobin)
