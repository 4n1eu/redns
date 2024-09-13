import yaml

def get(file):
    try:
        return yaml.safe_load(open(file))
    except:
        pass
    try:
        return yaml.safe_load(open(file+".yaml"))
    except:
        return yaml.safe_load(open(file+".yml"))
