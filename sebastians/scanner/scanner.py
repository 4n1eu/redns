import socket
import dns.resolver
import dns.query
import dns.exception
import time
import threading
import logging
import json
import os
from datetime import datetime

from multiprocessing.pool import ThreadPool

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
scanner_logger = logging.getLogger('scanner')
scanner_logger.setLevel(getattr(logging, 'INFO'))
scanner_fhandler = logging.FileHandler(os.path.join(getConfig().LOG_SYMLINK, "scanner.log"))
scanner_fhandler.setFormatter(formatter)
scanner_logger.addHandler(scanner_fhandler)

def resolve_domain(domain):
	global scanner_logger
	result_obj = {
		'start': time.time(),
		'domain': domain,
		'rr': 'A',
		'results': {}
	}

	for resolver_key in getConfig().RESOLVERS.keys():
		result_obj['results'][resolver_key] = {}
		result_obj['results'][resolver_key]['start'] = time.time()
		try:
			dns_req = dns.message.make_query(domain, result_obj['rr'])
			resolver = getConfig().RESOLVERS[resolver_key]

			if (not 'ip'in resolver or not resolver['ip']) and resolver['hostname']:
				resolver['ip'] = socket.gethostbyname(resolver['hostname'])

			response = dns.query.udp(dns_req, where=resolver['ip'], port=int(resolver['port']), timeout=getConfig().QUERY_TIMEOUT)

			records = [rr.to_text() for rr in response.answer]
			result_obj['results'][resolver_key]['success'] = True
			result_obj['results'][resolver_key]['records'] = records
		except Exception as e:
			result_obj['results'][resolver_key]['success'] = False
			result_obj['results'][resolver_key]['error'] = str(e)
		result_obj['results'][resolver_key]['stop'] = time.time()
		result_obj['results'][resolver_key]['duration'] = result_obj['results'][resolver_key]['stop'] - result_obj['results'][resolver_key]['start'] 

	result_obj['stop'] = time.time()
	result_obj['duration'] = result_obj['stop'] - result_obj['start']

	scanner_logger.info(json.dumps(result_obj))

thread_pool = ThreadPool(processes=getConfig().QUERIES_PER_SECOND*3)

print("Waiting 5s before starting")
time.sleep(5)
print("Let's go!")

for line in open(getConfig().DOMAIN_FILE):
	domain = line.strip()
	thread_pool.apply_async(resolve_domain, args=(domain,))
	time.sleep(1.0/getConfig().QUERIES_PER_SECOND)

thread_pool.close()
thread_pool.join()
