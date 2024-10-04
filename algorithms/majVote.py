import redns
import dns.rrset
import nameservers
import logging
import concurrent.futures
import time

log = logging.getLogger('redns.majvote')

log2_formatter = logging.Formatter("%(asctime)s.%(msecs)06d: %(message)s",
                                "%Y-%m-%d %H:%M:%S")
log2 = logging.getLogger('majVoteLog')
log2.setLevel(getattr(logging, 'INFO'))
log2_fhandler = logging.FileHandler("log/majVote.log")
log2_fhandler.setFormatter(log2_formatter)
log2.addHandler(log2_fhandler)

def find_rrset_in_list(rrSet1: dns.rrset.RRset, rrSets: dns.rrset.RRset):
    for i, rrSet2 in enumerate(rrSets):
        if redns.isEqualRR(rrSet1, rrSet2):
            return i
    return -1

def majVote(domain, rtype, opt={
        'ns_list': nameservers.get('ns1'),
        'timeout': 2,
        'retries': 1,
        'majThreshold': 0.5
    }):

    rrSets: list[dns.rrset.RRset] = []
    rrSetCounts = {}

    with concurrent.futures.ThreadPoolExecutor(max_workers=10) as executor:
        futures = []
        for ns in opt["ns_list"]:
            print("ns")
            futures.append(executor.submit(redns.resolve, domain, rtype, ns, opt['timeout'], opt['retries']))
        print(3)
        for future in futures:
            ans = future.result()

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


if __name__ == "__main__":
    redns.start(algorithm=majVote, port=53535)
    log2.info("majVote wurde gestartet")