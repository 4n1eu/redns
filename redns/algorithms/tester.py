import rednsfinal as redns
import majVote
from time import sleep


port = 4887
(a,b) = redns.start(port=port, algorithm=majVote.majVote)
res = redns.resolve("4n1.dev","a",f"127.0.0.1:{port}", timeout=10)



redns.stop(a)
redns.stop(b)