import socketserver

import dns.message
import dns.query
import dns.rrset
import dns.exception
import dns.rdatatype
import dns.dnssec
import dns.resolver
import dns.name

import threading
import signal
import atexit
import json
import logging
from typing import Callable, Optional # technically typing.callable is deprecated
import inspect

log_formatter = logging.Formatter("%(asctime)s.%(msecs)06d: %(message)s",
                              "%Y-%m-%d %H:%M:%S")
log = logging.getLogger('redns')
log.setLevel(logging.INFO)
log_fhandler = logging.FileHandler("log/redns.log")
log_fhandler.setFormatter(log_formatter)
log.addHandler(log_fhandler)

def error(txt):
	log.error(txt)
	print("ERROR: " + txt)

def isEqualRR(rrSet1: dns.rrset.RRset, rrSet2: dns.rrset.RRset):
    # rrSetX[0] müsste funktionieren, da one_rr_per_rrset=True
    return rrSet1.full_match(rrSet2.name, rrSet2.rdclass, rrSet2.rdtype, rrSet2.covers, rrSet2.deleting) and rrSet1[0] == rrSet2[0]

def resolve(domain:str, rtype:str, nameserver:str="1.1.1.1:53", timeout=3, retries=2):

	# ERROR-CODES
	# 0 = no error
	# 1 = no response
	# 2 = nxdomain

	if ":" in nameserver:
		ns_ip, ns_port = nameserver.split(":")
	else:
		ns_ip = nameserver
		ns_port = 53

	resp = None
	for i in range(retries):
		try:
			dns_req = dns.message.make_query(domain, rtype)
			resp, wasTCP = dns.query.udp_with_fallback(dns_req, where=ns_ip, port=int(ns_port), timeout=timeout, one_rr_per_rrset=True)
			break
		except Exception as e:
			if (i==retries-1): log.warning(f"Error for request: {e}")
			continue

	#print(resp)
	# answer is a list of rrsets
	# rrset is a set containing the resource records
	if not resp:
		return False
	else:
		return resp.answer



def handle_request(self, dns_req:dns.message.Message, *args, **kwargs):
	log.info("handling new dns request")
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

	try:
		if (has_options):
			ans = self.customAlgorithm(rrset.name, rrset.rdtype, opt=opt)
		else:
			ans = self.customAlgorithm(rrset.name, rrset.rdtype)
	except Exception as e:
		error("exception in custom Algorithm: " + str(e))
		ans = 0
	
	if ans != False:
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
			error(f"Error for udp request: {json.dumps({'id': str(req.id), 'question': str(req.question), 'error': str(e)})}")

class DNSHandlerTCP(socketserver.StreamRequestHandler):
	customAlgorithm = staticmethod(resolve)
	customOptions = {}

	def handle(self):
		try:
			req, timestamp = dns.query.receive_tcp(self.request, one_rr_per_rrset=True, ignore_trailing=True)
			response = handle_request(self, req)
			return dns.query.send_tcp(self.request, response)
		except Exception as e:
			error(f"Error for tcp request: {json.dumps({'id': str(req.id), 'question': str(req.question), 'error': str(e)})}")
 

serverlist = []

def start(ip:str="0.0.0.0", port:int=53535, algorithm:Callable[[str, dns.rdatatype.RdataType], any]=resolve, opt:Optional[any]={}, udp:bool=True, tcp:bool=True):
	if udp: udpserver = start_udp(ip, port, algorithm, opt)
	if tcp: tcpserver = start_tcp(ip, port, algorithm, opt)

	if (tcp and udp): return (udpserver, tcpserver)
	if tcp: return tcpserver
	if udp: return udpserver
	log.warning("starting a server requires at least one of tcp, udp to be set to True")

def start_udp(ip:str="0.0.0.0", port:int=53535, algorithm:Callable[[str, dns.rdatatype.RdataType], any]=resolve, opt:Optional[any]={}):

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
		return False

def start_tcp(ip:str="0.0.0.0", port:int=53535, algorithm:Callable[[str, dns.rdatatype.RdataType], any]=resolve, opt:Optional[any]={}):
	log.debug(f"TCP Server is starting")
	try:
		dnsserver = socketserver.ThreadingTCPServer((ip, port), DNSHandlerTCP)
		dnsserver.RequestHandlerClass.customAlgorithm = staticmethod(algorithm)
		dnsserver.RequestHandlerClass.customOptions = opt
		thread = threading.Thread(target=dnsserver.serve_forever)
		thread.start()
		serverlist.append(dnsserver)
		log.info(f"reDNS (TCP) is now available on {ip}:{port}")
		return dnsserver
	except Exception as e:
		log.error(f"Couldn't start TCP Server: {e}")
		return False
	

def stop(server):
	try:
		server.shutdown()
		serverlist.remove(server)
		if (server.socket_type == 1):
			log.info("Stopped TCP server.")
		else:
			log.info("Stopped UDP server.")
	except:
		error("error while stopping server")

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