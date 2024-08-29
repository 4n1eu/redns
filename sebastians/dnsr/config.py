
from itertools import cycle
import os
import yaml
import re
import socket

class Config():
	CONFIG = None

def hostname2ip(hostname):
	host_or_ip, port = hostname.split(":")
	if re.match(r'[^\d\.]', host_or_ip):
		host_or_ip = socket.gethostbyname(host_or_ip)
	return f"{host_or_ip}:{port}"


def parseConfig(config_file):
	yaml_config = yaml.safe_load(open(os.path.join("/app/configs/", config_file)))
	our_config = Config()
	for k in yaml_config.keys():
		setattr(our_config,k,yaml_config[k])

	if our_config.DEFAULT_DNS_SERVER:
		our_config.DEFAULT_DNS_SERVER = hostname2ip(our_config.DEFAULT_DNS_SERVER)
	if our_config.UPSTREAM_SERVERS:
		our_config.UPSTREAM_SERVERS = [ hostname2ip(upstream) for upstream in our_config.UPSTREAM_SERVERS]
		setattr(our_config, 'UPSTREAM_SERVERS_CYCLE', cycle(our_config.UPSTREAM_SERVERS))

	return our_config

def getConfig():
	if not Config.CONFIG:
		Config.CONFIG = parseConfig(os.environ['DNSR_CONFIG'] if os.environ['DNSR_CONFIG'] else 'default.yml')
	return Config.CONFIG
