import sys
from copy import deepcopy
from importlib import import_module

import config.config_sys as cfg_sys

__serviceSet = deepcopy(getattr(import_module(cfg_sys.TOPO), '__serviceSet'))
__nodeSet = deepcopy(getattr(import_module(cfg_sys.TOPO), '__nodeSet'))
__edgeList = deepcopy(getattr(import_module(cfg_sys.TOPO), '__edgeList'))
__distanceMat = deepcopy(getattr(import_module(cfg_sys.TOPO), '__distanceMat'))

# prepocessing, to control cl num, service num, etc.
_serviceList = sorted([serviceName for serviceName in __serviceSet])

assert cfg_sys.NUM_SERVICE <= len(_serviceList)

for serviceName in _serviceList[cfg_sys.NUM_SERVICE:]:
    __serviceSet.pop(serviceName)

_clList = sorted([
    (nodeIp, node['alias'])
    for nodeIp, node in __nodeSet.items()
    if node['typee'] == cfg_sys.TYPEE_CL_USER
], key=lambda x: x[1])

_clAliasList = [__nodeSet[clIp]['alias'] for clIp, _ in _clList]

assert cfg_sys.NUM_CL <= len(_clList)

for clIp, _ in _clList[cfg_sys.NUM_CL:]:
    print(clIp)
    __nodeSet.pop(clIp)

__edgeList = [
    edge
    for edge in __edgeList
    if edge['src'] not in _clAliasList[cfg_sys.NUM_CL:] and
       edge['dst'] not in _clAliasList[cfg_sys.NUM_CL:]
]
clIp = serviceName = _ = None
del _clList, _clAliasList, _serviceList, clIp, serviceName

__tmp = {node['alias']: ip for ip, node in __nodeSet.items()}
__topo = {
    'nodeSet': __nodeSet,
    'edgeList': [
        {'src': __tmp[e['src']], 'dst': __tmp[e['dst']], 'price': e['price'], 'priceReverse': e['priceReverse']}
        for e in __edgeList
    ],
    'distanceMat': __distanceMat
}

# config for ctlr
cfg_ctlr = {
    'ip': None,
    'state': None,
    'algorithm': cfg_sys.ALGORITHM,
    'topo': __topo,
    'budget': cfg_sys.AVG_BUDGET * cfg_sys.NUM_REQ,
    'resetSet': {i: False for i in __topo['nodeSet']},
    'registerSet': {i: False for i in __topo['nodeSet']},
    'delayMat': {i: None for i in __topo['nodeSet']},
    'distributeMat': {i: 2 if __topo['nodeSet'][i]['typee'] == cfg_sys.TYPEE_CL_USER else 1 for i in __topo['nodeSet']},
    'resultUploadSet': {i: False for i in __topo['nodeSet'] if __topo['nodeSet'][i]['typee'] == cfg_sys.TYPEE_CL_USER},
    'resultSet': {},
    'serviceSet': __serviceSet,
    'userSet': None,
    'dcSet': None,
    'assignment': None
}

# config to distribute to CL and DC
cfg_cldc = {
    'topo': cfg_ctlr['topo'],
    'reqThreading': cfg_sys.REQ_THREADING
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
    import networkx as nx
    from numpy import random
    import matplotlib.pyplot as plt

    output()

    random.seed(cfg_sys.RANDOM_SEED)

    plt.figure(figsize=(8, 8))

    nxG = nx.Graph([(e['src'], e['dst']) for e in __edgeList])
    nx.draw_networkx(nxG)
    plt.show()
    pass
