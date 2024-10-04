import socketserver

import dns.message
import dns.query
import dns.rrset
import dns.exception
import dns.rdatatype
import dns.dnssec

import threading
import signal
import atexit
import json
import logging
from typing import Callable, Optional # technically typing.callable is deprecated
import inspect

# neccessary because of https://stackoverflow.com/a/75379243/11030358
import concurrent.futures
thread_pool_ref = concurrent.futures.ThreadPoolExecutor

log_formatter = logging.Formatter("%(asctime)s.%(msecs)06d: %(message)s",
                              "%Y-%m-%d %H:%M:%S")
log = logging.getLogger('redns')
log.setLevel(getattr(logging, 'INFO'))
log_fhandler = logging.FileHandler("log/redns.log")
log_fhandler.setFormatter(log_formatter)
log.addHandler(log_fhandler)
def isEqualRR(rrSet1: dns.rrset.RRset, rrSet2: dns.rrset.RRset):
    # rrSetX[0] müsste funktionieren, da one_rr_per_rrset=True
    return rrSet1.full_match(rrSet2.name, rrSet2.rdclass, rrSet2.rdtype, rrSet2.covers, rrSet2.deleting) and rrSet1[0] == rrSet2[0]

def resolve(domain:str, rtype:str, nameserver:str="1.1.1.1:53", timeout=2, retries=1):
    if ":" in nameserver:
        ns_ip, ns_port = nameserver.split(":")
    else:
        ns_ip = nameserver
        ns_port = 53

    try:
        dns_req = dns.message.make_query(domain, rtype)
        resp, wasTCP = dns.query.udp_with_fallback(dns_req, where=ns_ip, port=int(ns_port), timeout=timeout, one_rr_per_rrset=True)
    except Exception as e:
        print(f"Error for request: {json.dumps({'error': str(e)})}")
        return 0
    
    # answer is a list of rrsets
    # rrset is a set containing the resource records
    if not resp or not resp.answer:
        return 0
    else:
        return resp.answer


def handle_request(self, dns_req:dns.message.Message, *args, **kwargs):
	msg = dns.message.make_response(dns_req, **kwargs)
	rrset = dns_req.question[0]

	# options-dict
	has_options = False
	opt = dict(self.customOptions)
	for name, param in inspect.signature(self.customAlgorithm).parameters.items():
		if (name != "opt"):
			continue
		has_options=True
		for o in param.default:
			if o not in opt:
				opt[o] = param.default[o]
	print(1)
	if (has_options):
		ans = self.customAlgorithm(rrset.name, rrset.rdtype, opt=opt)
	else:
		ans = self.customAlgorithm(rrset.name, rrset.rdtype)
	print(2)
	if ans:
		msg.answer = ans
	return msg
	
class DNSHandlerUDP(socketserver.DatagramRequestHandler):
	customAlgorithm = staticmethod(resolve)
	customOptions = {}
	
	def handle(self):
		try:
			req = dns.message.from_wire(wire=self.request[0], question_only=True, ignore_trailing=True, one_rr_per_rrset=True)
			response = handle_request(self, req)
			return self.wfile.write(response.to_wire())
		except Exception as e:
			print(f"Error for udp request: {json.dumps({'id': str(req.id), 'question': str(req.question), 'error': str(e)})}")

class DNSHandlerTCP(socketserver.StreamRequestHandler):
	customAlgorithm = staticmethod(resolve)
	customOptions = {}

	def handle(self):
		try:
			req, timestamp = dns.query.receive_tcp(self.request, one_rr_per_rrset=True, ignore_trailing=True)
			response = handle_request(self, req)
			return dns.query.send_tcp(self.request, response)
		except Exception as e:
			print(f"Error for tcp request: {json.dumps({'id': str(req.id), 'question': str(req.question), 'error': str(e)})}")


serverlist = []

def start(ip:str="127.0.0.1", port:int=53535, algorithm:Callable[[str, dns.rdatatype.RdataType], any]=resolve, opt:Optional[dict]={}, udp:bool=True, tcp:bool=True):
	if udp: udpserver = start_udp(ip, port, algorithm, opt)
	if tcp: tcpserver = start_tcp(ip, port, algorithm, opt)

	if (tcp and udp): return (udpserver, tcpserver)
	if tcp: return tcpserver
	if udp: return udpserver
	log.warning("starting a server requires at least one of tcp, udp to be set to True")

def start_udp(ip:str="127.0.0.1", port:int=53535, algorithm:Callable[[str, dns.rdatatype.RdataType], any]=resolve, opt:Optional[dict]={}):

	log.debug(f"UDP Server is starting")
	try:
		dnsserver = socketserver.ThreadingUDPServer((ip, port), DNSHandlerUDP)
		dnsserver.RequestHandlerClass.customAlgorithm = staticmethod(algorithm)
		dnsserver.RequestHandlerClass.customOptions = opt
		thread = threading.Thread(target=dnsserver.serve_forever)
		thread.start()
		serverlist.append(dnsserver)
		log.info(f"reDNS (UDP) is now available on {ip}:{port}")
		return dnsserver
	except Exception as e:
		log.error(f"Couldn't start UDP Server: {e}")

def start_tcp(ip:str="127.0.0.1", port:int=53535, algorithm:Callable[[str, dns.rdatatype.RdataType], any]=resolve, opt:Optional[dict]={}):
	log.debug(f"TCP Server is starting")
	try:
		dnsserver = socketserver.TCPServer((ip, port), DNSHandlerTCP)
		dnsserver.RequestHandlerClass.customAlgorithm = staticmethod(algorithm)
		dnsserver.RequestHandlerClass.customOptions = opt
		thread = threading.Thread(target=dnsserver.serve_forever)
		thread.start()
		serverlist.append(dnsserver)
		log.info(f"reDNS (TCP) is now available on {ip}:{port}")
		return dnsserver
	except Exception as e:
		log.error(f"Couldn't start TCP Server: {e}")
	

def stop(server):
	try:
		server.shutdown()
		serverlist.remove(server)
		if (server.socket_type == 1):
			print("Stopped TCP server.")
		else:
			print("Stopped UDP server.")
	except:
		print("error while stopping server")

def handle_exit(*args):
	servers = []
	for s in serverlist:
		servers.append(s)
	print()
	for s in servers:
		stop(s)

atexit.register(handle_exit)
signal.signal(signal.SIGTERM, handle_exit)
signal.signal(signal.SIGINT, handle_exit)

if __name__ == "__main__":
    start(port=8445)