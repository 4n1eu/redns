import redns
import dns.rrset
import dns.rdatatype
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

#returns index if found, -1 if not found
def find_rrset_in_list(rrSet1: dns.rrset.RRset, rrSets: list[dns.rrset.RRset]):
    for i, rrSet2 in enumerate(rrSets):
        if redns.isEqualRR(rrSet1, rrSet2):
            return i
    return -1

def resolveStoreResult(results, i, domain, rtype, ns, timeout, retries):
    results[i] = redns.resolve(domain, rtype, ns, timeout, retries)

def vote_winner(rrSets, rrSetCounts:list, opt):
    answer = []
    winnercount = max(rrSetCounts)

    for i,rrset in enumerate(rrSets):
        if rrSetCounts[i] == winnercount:
            answer.append(rrset)
    return answer



def vote_majority(rrSets, rrSetCounts, opt):
    answer = []
    
    for i, rrSet in enumerate(rrSets):
        if (rrSetCounts[i] > len(opt['ns_list'])*opt['majThreshold']):
            answer.append(rrSet)

    return answer

def majVote(domain, rtype, opt={
        'ns_list': redns.getList('ns1'),
        'timeout': 2,
        'retries': 1,
        'majThreshold': 0.5,
        'weightMultiple': False, # when one ns returns n rrsets, weight them 1/n
        'voteWinnerWhenReasonable': True,
        'alwaysVoteWinner': False
    }):

    if type(rtype)!=str: rtype = dns.rdatatype.to_text(rtype)

    results = [None] * len(opt["ns_list"])
    threads = []
    for i, ns in enumerate(opt['ns_list']):
        threads.append(threading.Thread(target=resolveStoreResult, args=[results, i, domain, rtype, ns, opt['timeout'], opt['retries']]))
        threads[-1].start()
    for thread in threads:
        thread.join()

    rrSets: list[dns.rrset.RRset] = []
    rrSetCounts = []

    anyAnswerExists = False

    # combine results and store the amounts of different rrsets
    for i, ans in enumerate(results):
        if not ans: continue
        anyAnswerExists = True
        ns = opt["ns_list"][i]
        log2.debug(f"'{domain} IN {rtype}': result {i+1}/{len(results)} by {ns+' '*(16-len(ns))} ready: {ans}")

        weight = 1/len(ans) if opt['weightMultiple'] else 1 

        for rrAns in ans:
            i = find_rrset_in_list(rrAns, rrSets)
            if (i==-1):
                rrSetCounts.append(weight)
                rrSets.append(rrAns)
            else:
                rrSetCounts[i] = rrSetCounts[i] + weight
                rrSets[i].update_ttl(min(rrSets[i].ttl, rrAns.ttl))

    if not anyAnswerExists:
        log2.debug(f"'{domain} IN {rtype}': No answers")
        return 0

    if opt['alwaysVoteWinner']:
        answer = vote_winner(rrSets, rrSetCounts, opt)
    elif opt['voteWinnerWhenReasonable']:
        answer = vote_majority(rrSets, rrSetCounts, opt)
        if len(answer)==0: answer = vote_winner(rrSets, rrSetCounts, opt)
    else:
        answer = vote_majority(rrSets, rrSetCounts, opt)

    log2.debug(f"'{domain} IN {rtype}': final result is: {answer}")
    return answer


if __name__ == "__main__":
    redns.start(algorithm=majVote, port=53535, ip="0.0.0.0")
    log.info("majVote wurde gestartet")