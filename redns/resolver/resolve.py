import redns

print(redns.resolve("4n1.eu","A", nameserver="127.0.0.1:53535"))