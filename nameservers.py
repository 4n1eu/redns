import yaml

def get(file):
    return yaml.safe_load(open(file))