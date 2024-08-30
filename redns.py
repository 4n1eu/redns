import socketserver

import dns.message
import dns.query
import dns.rrset
import dns.exception
import dns.rdatatype

import json
from typing import Callable


def isEqualRR(rrSet1: dns.rrset.RRset, rrSet2: dns.rrset.RRset):
    # rrSetX[0] müsste funktionieren, da one_rr_per_rrset=True
    return rrSet1.full_match(rrSet2.name, rrSet2.rdclass, rrSet2.rdtype, rrSet2.covers, rrSet2.deleting) and rrSet1[0] == rrSet2[0]

def resolve(domain:str, rtype:str, nameserver:str="1.1.1.1:53", timeout=2, retries=1):

    if ":" in nameserver:
        nameserver_host, nameserver_port = nameserver.split(":")
    else:
        nameserver_host = nameserver
        nameserver_port = 53

    try:
        dns_req = dns.message.make_query(domain, rtype)
        resp, wasTCP = dns.query.udp_with_fallback(dns_req, where=nameserver_host, port=int(nameserver_port), timeout=timeout, one_rr_per_rrset=True)
    except Exception as e:
        print(f"Error for request: {json.dumps({'error': str(e)})}")
        return 0
    
    # answer is a list of rrsets
    # rrset is a set containing the resource records

    if not resp or not resp.answer:
        return 0
    else:
        return resp.answer
	
class CustomDNSRequestHandler(socketserver.DatagramRequestHandler):
	customAlgorithm = staticmethod(resolve)
      
	def handle_request(self, dns_req:dns.message.Message, *args, **kwargs):
		msg = dns.message.make_response(dns_req, **kwargs)
		# todo: support multiple rrsets
		rrset = dns_req.question[0]

		ans = self.customAlgorithm(rrset.name, rrset.rdtype)
		if ans:
			msg.answer = ans
		return msg

	def handle(self):
		data = self.request[0]
		req = dns.message.from_wire(wire=data, question_only=True, ignore_trailing=True, one_rr_per_rrset=True)

		try:
			response = self.handle_request(req)
			return self.wfile.write(response.to_wire())
		except Exception as e:
			print(f"Error for request: {json.dumps({'id': str(req.id), 'question': str(req.question), 'error': str(e)})}")



def start(ip:str="127.0.0.1", port:int=53535, algorithm:Callable[[str, dns.rdatatype.RdataType], any]=resolve):
	dnsserver = socketserver.ThreadingUDPServer((ip, port), CustomDNSRequestHandler)
	dnsserver.RequestHandlerClass.customAlgorithm = staticmethod(algorithm)
	print(f"reDNS is now available on {ip}:{port}")
	dnsserver.serve_forever()
	return dnsserver


if __name__ == "__main__":
    start()