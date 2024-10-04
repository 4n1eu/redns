import redns

print(redns.resolve("4n1.eu","txt","127.0.0.1:53535", timeout=3))