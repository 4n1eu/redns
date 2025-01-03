import redns
import majVote
import redns.redns

# customizable:
nsCountPerMajvoter = 5
all_ns = redns.getList('ns3', max=24)
nsCount = len(all_ns)

# if nsCount is not divisble by nsCountPerMajvoter, just ignore trailing nameservers
majvoterCount = int(nsCount/nsCountPerMajvoter)
usableNsCount = majvoterCount*nsCountPerMajvoter

# starting MajVoters
rrPort = 1024
majvoterPort = rrPort
majVoterPortlist = []
for i in range(majvoterCount):
    a = b = False
    while not a or not b:
        majvoterPort = majvoterPort+1
        a,b = redns.start(ip="0.0.0.0", port=majvoterPort, algorithm=majVote.majVote, opt={"ns_list":all_ns[i*nsCountPerMajvoter:(i+1)*nsCountPerMajvoter]})
    majVoterPortlist.append(majvoterPort)
    print(f"started MajVoter #{majvoterPort}")

# server which distributes queries to majVoters
portindex = 0
def roundRobin(domain, rtpye):
    global portindex
    port = majVoterPortlist[portindex]
    portindex = (portindex+1)%majvoterCount
    return redns.resolve(domain, rtpye, ns=f"0.0.0.0:{port}")

a,b = redns.start(ip="0.0.0.0", port=rrPort, algorithm=roundRobin)
if a and b:
    print(f"The round robin majority Voter is now available on port {rrPort}")
else:
    print("error starting main server")
    