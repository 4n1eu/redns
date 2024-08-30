import redns
import dns.rrset

majVoteThreshold = 0.5

def find_rrset_in_list(rrSet1: dns.rrset.RRset, rrSets: dns.rrset.RRset):
    for i, rrSet2 in enumerate(rrSets):
        if redns.isEqualRR(rrSet1, rrSet2):
            return i
    return -1

def majVote(domain, rtype):
    rrSets: list[dns.rrset.RRset] = []
    rrSetCounts = {}

    ns_list = ["1.1.1.1", "8.8.8.8", "9.9.9.9"]
    ns_count = len(ns_list)

    for ns in ns_list:
        print(ns)
        ans = redns.resolve(domain, rtype, ns)
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
        if (rrSetCounts.get(i) >= ns_count*majVoteThreshold):
            answer.append(rrSet)

    return answer


redns.start(algorithm=majVote)