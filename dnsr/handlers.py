import socketserver
import os
from datetime import datetime

import dns.message
import dns.query
import dns.rrset

import json
import logging

from itertools import cycle
from collections import Counter
from config import getConfig

logs_folder = getConfig().LOGS_FOLDER
if not os.path.exists(logs_folder):
	os.makedirs(logs_folder, exist_ok=True)

log_symlink = os.path.join(logs_folder, 'current')
if os.path.exists(log_symlink):
    os.unlink(log_symlink)

log_dir_name = datetime.now().strftime("%Y-%m-%d-%H:%M:%S")
os.makedirs(os.path.join(logs_folder, log_dir_name), exist_ok=True)
os.symlink(log_dir_name, log_symlink)

setattr(getConfig(),'LOG_SYMLINK',log_symlink)

formatter = logging.Formatter("%(asctime)s.%(msecs)06d: %(message)s",
                              "%Y-%m-%d %H:%M:%S")
dnsr_logger = logging.getLogger('dnsr')
dnsr_logger.setLevel(getattr(logging, 'INFO'))
dnsr_fhandler = logging.FileHandler(os.path.join(getConfig().LOG_SYMLINK, "dnsr.log"))
dnsr_fhandler.setFormatter(formatter)
dnsr_logger.addHandler(dnsr_fhandler)


class BaseDNSRequestHandler(socketserver.DatagramRequestHandler):


	def handle_request(self, dns_req, *args, **kwargs):
		response = dns.message.make_response(dns_req, **kwargs)
		return response
	
	def handle(self):
		data = self.request[0]
		req = dns.message.from_wire(wire=data, question_only=True, ignore_trailing=True, one_rr_per_rrset=True)

		try:
			dnsr_logger.info(f"Received request: {json.dumps({'id': str(req.id), 'question': str(req.question)})}")
			response = self.handle_request(req)

			dnsr_logger.info(f"Sending response: {json.dumps({'id': str(response.id), 'response': str(response.answer)})}")

			return self.wfile.write(response.to_wire())
		except Exception as e:
			dnsr_logger.info(f"Error for request: {json.dumps({'id': str(req.id), 'question': str(req.question), 'error': str(e)})}")

class SimpleDNSRequestHandler(BaseDNSRequestHandler):
	def handle_request(self, dns_req, *args, **kwargs):
		retries = getConfig().QUERY_RETRIES
		timeout = getConfig().QUERY_TIMEOUT/retries

		upstream_resolver_host, upstream_resolver_port = getConfig().DEFAULT_DNS_SERVER.split(":")
		
		resp = None
		error = None
		for i in range(retries):
			try:
				resp = dns.query.udp(dns_req, where=upstream_resolver_host, port=int(upstream_resolver_port), timeout=timeout)
				break
			except Exception as e:
				error = e
				continue
		if not resp:
			raise error
		

		answer = dns.message.make_response(dns_req, **kwargs)
		answer.answer = resp.answer
		return answer

class RoundRobinDNSRequestHandler(BaseDNSRequestHandler):
	def __init__(self, *args, **kwargs):
		super(BaseDNSRequestHandler, self).__init__(*args, **kwargs)

	def handle_request(self, dns_req, *args, **kwargs):
		resolver = next(getConfig().UPSTREAM_SERVERS_CYCLE)
		upstream_resolver_host, upstream_resolver_port = resolver.split(":")
		dnsr_logger.info(f"Resolving request: {json.dumps({'id': str(dns_req.id), 'question': str(dns_req.question), 'resolver': str(resolver)})}")
		retries = getConfig().QUERY_RETRIES
		timeout = getConfig().QUERY_TIMEOUT/retries
		resp = None
		error = None
		for i in range(retries):
			try:
				resp = dns.query.udp(dns_req, where=upstream_resolver_host, port=int(upstream_resolver_port), timeout=timeout)
				break
			except Exception as e:
				error = e
				continue
		if not resp:
			raise error
		answer = dns.message.make_response(dns_req, **kwargs)
		answer.answer = resp.answer
		return answer

class MajorityVoteDNSRequestHandler(BaseDNSRequestHandler):
	def __init__(self, *args, **kwargs):
		self.upstream_servers = getConfig().UPSTREAM_SERVERS
		super(BaseDNSRequestHandler, self).__init__(*args, **kwargs)

	def get_upstream_servers(self):
		return sorted(self.upstream_servers)

	def handle_request(self, dns_req, *args, **kwargs):
		answer = dns.message.make_response(dns_req, **kwargs)

		timeout = getConfig().QUERY_TIMEOUT/len(self.upstream_servers)
		answer_rrsets = {}
		ttls = set()
		for upstream_server in self.get_upstream_servers():
			upstream_resolver_host, upstream_resolver_port = upstream_server.split(":")

			try:
				response = dns.query.udp(dns_req, where=upstream_resolver_host, port=int(upstream_resolver_port), timeout=timeout)
			
				for i, rrset in enumerate(response.answer):
					if not i in answer_rrsets:
						answer_rrsets[i] = Counter()
					answer_rrsets[i].update([record for record in rrset])
					ttls.update([rrset.ttl])
			except Exception as e:
				continue

		answer.answer = []
		for k, rrset in answer_rrsets.items():
			majority_rrset = list(filter(lambda x: rrset[x] >= len(self.upstream_servers)/2, rrset))
			if not majority_rrset:
				continue
			answer.answer.append(dns.rrset.from_rdata_list(name=answer.question[0].name, rdatas=majority_rrset,ttl=min(ttls)))

		return answer