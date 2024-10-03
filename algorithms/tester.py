import rednsfinal as redns
import time
import majVote

port = 4887
(a,b) = redns.start(port=port, algorithm=majVote.majVote)
time.sleep(1)
print(redns.resolve("4n1.eu","txt",f"127.0.0.1:{port}", timeout=10))
redns.stop(a)
redns.stop(b)