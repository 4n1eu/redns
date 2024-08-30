reDNS
===============

To start reDNS with majority vote run 'python majVote.py'
All algorithms:
 - majVote.py
 - simpleServer.py
 - badActor.py
 - roundRobin.py

To implement your own algorithm:
- write a function func(domain: str, rType: dns.rdatatype.RdataType) -> list[dns.rrset.RRset]
- use redns.resolve() -> list[dns.rrset.RRset] to resolve a domain name
- use redns.start(ip, port, algorithm) to submit your function and start reDNS on the given ip and port