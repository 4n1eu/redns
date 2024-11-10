import redns

bad_domain = input("Domain: ")
port = int(input("listen on port: "))

def baddie(domain, rtype):
    return redns.resolve(bad_domain,"txt")

redns.start(port=port, algorithm=baddie)