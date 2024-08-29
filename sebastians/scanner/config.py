
from itertools import cycle
import os
import yaml

class Config():
	CONFIG = None

def parseConfig(config_file):
	yaml_config = yaml.safe_load(open(os.path.join("/app/configs/", config_file)))
	our_config = Config()
	for k in yaml_config.keys():
		setattr(our_config,k,yaml_config[k])
	return our_config

def getConfig():
	if not Config.CONFIG:
		Config.CONFIG = parseConfig(os.environ['SCANNER_CONFIG'] if os.environ['SCANNER_CONFIG'] else 'default.yml')
	return Config.CONFIG
