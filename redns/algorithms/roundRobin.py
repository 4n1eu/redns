import redns
import logging

log = logging.getLogger('redns.rr')

log2_formatter = logging.Formatter("%(asctime)s.%(msecs)06d: %(message)s",
                                "%Y-%m-%d %H:%M:%S")
log2 = logging.getLogger('rrLog')
log2.setLevel(logging.DEBUG)
log2_fhandler = logging.FileHandler("log/roundrobin.log")
log2_fhandler.setFormatter(log2_formatter)
log2.addHandler(log2_fhandler)

i = 0
def getns(ns):
    global i
    i = i+1
    return ns[i%len(ns)]

def roundRobin(domain, rtype, opt={
      'retries' = 2,
      'timeout' = 2,
      'ns_list' = nameservers.get('ns2')
    }):
    
    usens = getns(opt['ns_list'])

    for i in range(opt['retries']):
        res = redns.resolve(domain, rtype, nameserver=usens, timeout=opt['timeout'], retries=1)
        if res != False:
            continue
        break
    if res:
        log2.debug(f"valid response for '{domain} IN {rtype}' from {usens}: {res}")
    else:
        log2.debug(f"got empty / no response for '{domain} IN {rtype}' from {usens}")
    return res


if __name__ == "__main__":
    redns.start(port=53535, algorithm=roundRobin)
