import sys

from config.config_sys import CTLR_IP

cfg = {
    'ip': None,
    'ctlrIp': CTLR_IP,
    'state': None,
    'remoteCfg': None,
    'serviceCaching': []
}


def state_dict():
    """return config dict"""
    mod = sys.modules[__name__]
    from inspect import isfunction, ismodule
    state = {}
    vrb_names = dir(mod)
    for vrbName in vrb_names:
        if vrbName.startswith('__') or vrbName.endswith('__'):
            continue
        vrb = getattr(mod, vrbName)
        if isfunction(vrb):
            continue
        if ismodule(vrb):
            continue
        state[vrbName] = vrb
    return state


def load(state_dict):
    """load config dict"""
    mod = sys.modules[__name__]
    for vrbName in state_dict:
        setattr(mod, vrbName, state_dict[vrbName])
    print('config loaded')


def output():
    """output config dict"""
    stat = state_dict()
    for vrb_name in stat:
        print(vrb_name + ' = ' + str(stat[vrb_name]))


if __name__ == '__main__':
    output()
