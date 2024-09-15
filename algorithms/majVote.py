import redns
import dns.rrset
import nameservers


def find_rrset_in_list(rrSet1: dns.rrset.RRset, rrSets: dns.rrset.RRset):
    for i, rrSet2 in enumerate(rrSets):
        if redns.isEqualRR(rrSet1, rrSet2):
            return i
    return -1

def majVote(domain, rtype, opt={}):

    redns.stdOptions(opt, {
        'ns_list': nameservers.get('ns1'),
        'timeout': 2,
        'retries': 1,
        'majThreshold': 0.5
    })

    rrSets: list[dns.rrset.RRset] = []
    rrSetCounts = {}

    for ns in opt['ns_list']:
        print(ns)
        ans = redns.resolve(domain, rtype, ns, opt['timeout'], opt['retries'])

        if not ans:
            continue

        for rrAns in ans:
            print(rrAns)
            i = find_rrset_in_list(rrAns, rrSets)
            if (i==-1): # rrset is new
                rrSetCounts.update({len(rrSets): 1})
                rrSets.append(rrAns)
            else: # rrset already exists
                rrSetCounts.update({i: rrSetCounts.get(i) + 1})
                rrSets[i].update_ttl(min(rrSets[i].ttl, rrAns.ttl))

    answer = []
    for i, rrSet in enumerate(rrSets):
        if (rrSetCounts.get(i) >= len(opt['ns_list'])*opt['majThreshold']):
            answer.append(rrSet)

    return answer


redns.start(algorithm=majVote, port=53335)