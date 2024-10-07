import rednsfinal as redns
import time

port = 4887
(a,b) = redns.start(port=port, algorithm=redns.resolve)
res = redns.resolve("4n1.dev","a",f"127.0.0.1:{port}", timeout=10)
#print(res)
redns.stop(a)
redns.stop(b)