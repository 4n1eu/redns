import socketserver

import dns.message
import dns.query
import dns.rrset

import json
from collections import Counter

from resolver import resolve_domain

me = ("127.0.0.1", 53535)

class BaseDNSRequestHandler(socketserver.DatagramRequestHandler):
	def handle_request(self, dns_req, *args, **kwargs):
		response = dns.message.make_response(dns_req, **kwargs)
		return response
	
	def handle(self):
		data = self.request[0]
		print(data)
		req = dns.message.from_wire(wire=data, question_only=True, ignore_trailing=True, one_rr_per_rrset=True)
		print(req)
		print("")

		try:
			response = self.handle_request(req)
			return self.wfile.write(response.to_wire())
		except Exception as e:
			print(f"Error for request: {json.dumps({'id': str(req.id), 'question': str(req.question), 'error': str(e)})}")

class SimpleDNSRequestHandler(BaseDNSRequestHandler):
	def handle_request(self, dns_req:dns.message.Message, *args, **kwargs):
		msg = dns.message.make_response(dns_req, **kwargs)
		print()
		print(msg)
		# maybe todo: support multiple rrsets
		rrset = dns_req.question[0]

		print("")
		ans = resolve_domain(rrset.name, rrset.rdtype)
		print(ans)
		if ans:
			msg.answer = ans
			print(msg)
		return msg
	


if __name__ == "__main__":
	dnsserver = socketserver.ThreadingUDPServer(me, SimpleDNSRequestHandler)
	dnsserver.serve_forever()