import dns.message
import dns.query
import json

nameserver_host = "127.0.0.1"
nameserver_port = 8444

domain1 = "4n1.eu"
domain2 = "google.de"

try:
    dns_req = dns.message.make_query(domain1, "A")
    dns_req2 = dns.message.make_query(domain2, "AAAA")
    #print(dns_req.question)
    dns_req.question = [dns_req.question[0], dns_req2.question[0]]
    print(dns_req.question)
    resp, wasTCP = dns.query.udp_with_fallback(dns_req, where=nameserver_host, port=int(nameserver_port), timeout=2)
except Exception as e:
    print(f"Error for request: {json.dumps({'error': str(e)})}")

print(resp.answer)
	