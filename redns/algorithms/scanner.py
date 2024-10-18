import redns
import majVote
import time
import threading
import nameservers


scannercount = 3 # num of threads
domains = nameservers.get('domains1')
scaninterval = 0.1 # in seconds, per thread
ns = nameservers.get('ns2')
me = "127.0.0.1:53535"


def sleepmost(interval, lasttime):
    diff = lasttime+interval-time.time()
    if (diff > 0):
        time.sleep(diff)
    return time.time()

def scanner(id, scaninterval, domains):
    lasttime = 0
    for domain in domains:
        lasttime = sleepmost(scaninterval, lasttime)
        print(redns.resolve(domain, "A", me))
    return

(a,b) = redns.start(port=int(me.split(':')[1]), algorithm=majVote.majVote, opt={'ns_list': ns, "voteWinnerWhenReasonable":True})

threads = []
for i in range(scannercount):
    t = threading.Thread(target=scanner, args=[i, scaninterval, domains[i:len(domains):scannercount]])
    t.start()
    threads.append(t)
    
for thread in threads:
    thread.join()
    
redns.stop(a)
redns.stop(b)