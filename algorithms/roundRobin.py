import redns
import nameservers

ns = nameservers.get("ns1")

print(ns)

def roundRobin(domain, rtype):
    print("using nameserver ",ns[0])
    return redns.resolve(domain, rtype, nameserver=ns[0], timeout=2, retries=2)


redns.start(ip="127.0.0.1", port=53553, algorithm=roundRobin)