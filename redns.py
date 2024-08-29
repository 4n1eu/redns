import socketserver

import dns.message
import dns.query
import dns.rrset

import json
from typing import Callable

from resolver import resolve_domain as resolve

class BaseDNSRequestHandler(socketserver.DatagramRequestHandler):
	def handle_request(self, dns_req, *args, **kwargs):
		response = dns.message.make_response(dns_req, **kwargs)
		return response
	
	def handle(self):
		data = self.request[0]
		req = dns.message.from_wire(wire=data, question_only=True, ignore_trailing=True, one_rr_per_rrset=True)

		try:
			response = self.handle_request(req)
			return self.wfile.write(response.to_wire())
		except Exception as e:
			print(f"Error for request: {json.dumps({'id': str(req.id), 'question': str(req.question), 'error': str(e)})}")

class SimpleDNSRequestHandler(BaseDNSRequestHandler):
	def handle_request(self, dns_req:dns.message.Message, *args, **kwargs):
		msg = dns.message.make_response(dns_req, **kwargs)
		# maybe todo: support multiple rrsets
		rrset = dns_req.question[0]

		ans = resolve(rrset.name, rrset.rdtype)
		if ans:
			msg.answer = ans
		return msg
	
class CustomDNSRequestHandler(BaseDNSRequestHandler):
	customAlgorithm = staticmethod(resolve)

	def handle_request(self, dns_req:dns.message.Message, *args, **kwargs):
		msg = dns.message.make_response(dns_req, **kwargs)
		# todo: support multiple rrsets
		rrset = dns_req.question[0]

		ans = self.customAlgorithm(rrset.name, rrset.rdtype)
		if ans:
			msg.answer = ans
		return msg

def start(ip:str="127.0.0.1", port:int=53535, algorithm:Callable[[str, str], any]=resolve):
	dnsserver = socketserver.ThreadingUDPServer((ip, port), CustomDNSRequestHandler)
	dnsserver.RequestHandlerClass.customAlgorithm = staticmethod(algorithm)
	print(f"your dns resolver is now available on {ip}:{port}")
	dnsserver.serve_forever()
	return dnsserver
