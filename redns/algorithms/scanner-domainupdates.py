import redns
import majVote
import time
import threading
import nameservers


scannercount = 30 # num of threads
domains = ["redns.4n1.dev"]
scaninterval = 0.1 # in seconds, per thread
ns = nameservers.get('ns3', max=200)
me = "0.0.0.0:53535"


def sleepmost(interval, lasttime):
    diff = lasttime+interval-time.time()
    if (diff > 0):
        time.sleep(diff)
    return time.time()

def scanner(id, scaninterval, domains):
    lasttime = 0
    for domain in domains:
        lasttime = sleepmost(scaninterval, lasttime)
        redns.resolve(domain, "A", me)
    return

(a,b) = redns.start(port=int(me.split(':')[1]), algorithm=majVote.majVote, opt={
    'ns_list': ns,
})

threads = []
for i in range(scannercount):
    t = threading.Thread(target=scanner, args=[i, scaninterval, domains[i:len(domains):scannercount]])
    t.start()
    threads.append(t)
    
for thread in threads:
    thread.join()
    
redns.stop(a)
redns.stop(b)

# times to scan 1000 domains at home, 10 ns each, using one middle-server:
# using 30 scanners, 0.1s interval: 47s
# using 20 scanners, 0.1s interval: 58s
# using 10 scanners, 0.1s interval: 76s
# using 10 scanners, 0.01s interval: 77s