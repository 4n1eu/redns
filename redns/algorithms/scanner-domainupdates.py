import redns
import majVote
import time
import math
import nameservers


domain = "redns1.liar.pw"
ns = nameservers.get('actives', max=70000)

stepsize = 100
skip = 45
max = 15

for i in range(math.ceil(len(ns)/stepsize)):
    if (i<skip): continue
    if (i>=skip+max): continue

    majVote.majVote(domain, "A", {
        'ns_list': ns[stepsize*i:stepsize*(i+1)],
        'timeout': 2,
        'retries': 2,
        'majThreshold': 0.5,
        'weightMultiple': False,
        'voteWinnerWhenReasonable': True,
        'alwaysVoteWinner': False
    })
    print(f"\r {i+1}/{math.ceil(len(ns)/stepsize)}", end="")

