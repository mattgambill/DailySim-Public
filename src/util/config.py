import yaml
try:
    from yaml import CLoader as Loader, CDumper as Dumper
except ImportError:
    from yaml import Loader, Dump


def get_config(path):
    config = None
    with open(path, 'r') as f:
        config = yaml.load(f, Loader=Loader)
    return config
