import sys

# system config
CTLR_IP = '8.130.167.115'
HTTP_PORT = 5000

# algorithm config
TOPO = 'config.topo.global1'
ALGORITHM = 'algorithms.distance'

FIXED_SPEED = False
NUM_CL = 25
NUM_SERVICE = 5

NUM_REQ = 200

DURATION = [1, 2, 3, 5, 10]

PRICE_CL = 0.007
AVG_BUDGET = 0.3
BETA = 0.1
LAMBDA = 0.3
THETA = 0.1

WEIGHT_HEU_1 = -9.7
WEIGHT_HEU_2 = 0.3
WEIGHT_HEU_3 = 1 - WEIGHT_HEU_1 - WEIGHT_HEU_2

PRICE_LINK_DC_FACTOR = 3

# testbed config
RANDOM_SEED = 4

TIMES_PING = 4

HTTP_MAX_RETRY = 3

REQ_TIMEOUT = 10
REQ_THREADING = 25 // NUM_CL

RESET_DURATION = 10
OFFSET_DELETE = 1.5

# LOG config
LOGGER_NAME = 'testbed'
LOG_FORMAT = '%(log_color)s[%(asctime)s] %(filename)s -> ' \
             '%(funcName)s line:%(lineno)d [%(levelname)s] : %(message)s'
LOG_DATE_FORMAT = '%H:%M:%S'
LOG_COLOR_MAP = {
    'DEBUG': 'white',
    'WARNING': 'yellow',
    'ERROR': 'red',
    'CRITICAL': 'bold_red',
}

# constants
MAX = 99999

STATE_RESET = 'reset'
STATE_REGISTER = 'register'
STATE_DELAY_TEST = 'delayTest'
STATE_DISTRIBUTE = 'distribute'
STATE_BEGIN = 'begin'

TYPEE_CL_USER = 'clUser'
TYPEE_CTLR = 'ctlr'
TYPEE_DC = 'dc'

RETURN_SUCCEED = 'succeed'


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
