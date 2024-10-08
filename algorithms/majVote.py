import redns
import dns.rrset
import nameservers
import logging
import json
import threading

log = logging.getLogger('redns.majvote')

log2_formatter = logging.Formatter("%(asctime)s.%(msecs)06d: %(message)s",
                                "%Y-%m-%d %H:%M:%S")
log2 = logging.getLogger('majVoteLog')
log2.setLevel(logging.DEBUG)
log2_fhandler = logging.FileHandler("log/majVote.log")
log2_fhandler.setFormatter(log2_formatter)
log2.addHandler(log2_fhandler)

def find_rrset_in_list(rrSet1: dns.rrset.RRset, rrSets: dns.rrset.RRset):
    for i, rrSet2 in enumerate(rrSets):
        if redns.isEqualRR(rrSet1, rrSet2):
            return i
    return -1

def singleResolve(results, i, domain, rtype, ns, timeout, retries):
    results[i] = redns.resolve(domain, rtype, ns, timeout, retries)

def majVote(domain, rtype, opt={
        'ns_list': nameservers.get('ns1'),
        'timeout': 2,
        'retries': 1,
        'majThreshold': 0.5
    }):

    rrSets: list[dns.rrset.RRset] = []
    rrSetCounts = {}

    
    ns_len = len(opt["ns_list"])
    results = [None]*ns_len
    threads = [None]*ns_len
    for i, ns in enumerate(opt['ns_list']):
        threads[i] = threading.Thread(target=singleResolve, args=[results, i, domain, rtype, ns, opt['timeout'], opt['retries']])
        threads[i].start()
    for t in threads:
        t.join()

    log2.debug(f"beginn voting for '{domain} IN {rtype}'")
    for i, ans in enumerate(results):
        if not ans:
            continue
        log2.debug(f"result for '{domain} IN {rtype}' by {opt["ns_list"][i]}")
        for rrAns in ans:
            log2.debug(rrAns)

            i = find_rrset_in_list(rrAns, rrSets)
            if (i==-1): # rrset is new
                rrSetCounts.update({len(rrSets): 1})
                rrSets.append(rrAns)
            else: # rrset already exists
                rrSetCounts.update({i: rrSetCounts.get(i) + 1})
                rrSets[i].update_ttl(min(rrSets[i].ttl, rrAns.ttl))

    answer = []
    
    log2.debug(f"final result for '{domain} IN {rtype}':")
    for i, rrSet in enumerate(rrSets):
        if (rrSetCounts.get(i) >= len(opt['ns_list'])*opt['majThreshold']):
            answer.append(rrSet)
            log2.debug(rrSet)
    for rrSet in rrSets:
        if (rrSetCounts.get(i) < ns_len):
            log2.debug(f"MajVote actually did something for '{domain} IN {rtype}'!")
            break

    return answer


if __name__ == "__main__":
    redns.start(algorithm=majVote, port=53535)
    log.info("majVote wurde gestartet")