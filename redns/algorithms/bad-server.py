import redns

bad_domain = input("Domain: ")
port = int(input("listen on port: "))

def baddie(domain, rtype):
    return redns.resolve(bad_domain,"txt")

redns.start(ip="127.0.0.1", port=port, algorithm=baddie)