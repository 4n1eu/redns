import redns
from majVote import majVote
import time
import nameservers
import math


port_majvote = 53535
port_vanilla = 53536
domains = nameservers.get("tranco1m", max=10000)
ns_majvote = nameservers.get('ns2',max=10)
ns_vanilla = ns_majvote
scan_interval = 0.01


times = []
for i in range(len(ns_vanilla)+1):
    times.append([])


# scan majVote
a,b = redns.start(port=port_majvote, algorithm=majVote, opt={'ns_list': ns_majvote})
for di, domain in enumerate(domains):
    print(f"{di+1}/{2*len(domains)}",end="\r")
    start = time.time()
    result = redns.resolve(domain, "A", f"127.0.0.1:{port_majvote}")
    duration = time.time()-start
    times[0].append(duration)
    #print(domain, duration)
    if duration<scan_interval: time.sleep(scan_interval-duration)
redns.stop(a)
redns.stop(b)

# scan vanilla
for di, domain in enumerate(domains):
    print(f"{di+1+len(domains)}/{2*len(domains)}",end="\r")
    for i, ns in enumerate(ns_vanilla):
        start = time.time()
        result = redns.resolve(domain, "A", ns)
        duration = time.time()-start
        times[i+1].append(duration)
        #print(domain, ns, duration)
        if duration<scan_interval: time.sleep(scan_interval-duration)

log = open("log/timing/times.log","w")
for t in times:
    log.write(str(t)+"\n")

# for i, t in enumerate(times):
#     y = [0]*700
#     x = []
#     for val in range(700):
#         x.append(val/100)

#     for val in t:
#         a = math.floor(val*100)
#         if a>=0.4: a=0.39
#         y[a] = y[a]+1
#     plt.stem(x[0:40],y[0:40])
#     plt.show()
#     plt.savefig(f'log/timing/plt-times-{i}.png')
