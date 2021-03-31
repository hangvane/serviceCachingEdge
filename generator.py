from numpy.random import choice, seed, uniform

from code_utils.utils import getLogger
from config import config_sys as cfg_sys
from config.config_ctlr import cfg_ctlr

logger = getLogger()


def req(service, speed, duration):
    return {'service': service, 'speed': int(speed), 'duration': int(duration)}


def generator(nodeSet, serviceSet, fixedSpeed=False):
    """
    generate request and service assignment
    :return: userSet: {
        ip:{
            'alias':alias,
            'reqSet':{
                reqName:{
                    'service': service,
                    'speed': speed,
                    'duration': duration
                }
            }
        }
    }
    dcSet: {
        ip:{
            'alias':alias,
            'serviceList': [
                'service0',
                'service1',
            ]
        }
    }
    """
    seed(cfg_sys.RANDOM_SEED)

    userSet = {i: {'alias': nodeSet[i]['alias'], 'reqSet': {}} for i in nodeSet if
               nodeSet[i]['typee'] == cfg_sys.TYPEE_CL_USER}

    nameList = ['req' + str(i) for i in range(cfg_sys.NUM_REQ)]

    serviceList = choice(list(serviceSet), size=cfg_sys.NUM_REQ)
    minSpeedList = [
        serviceSet[serviceName]['speed'][0]
        for serviceName in serviceList
    ]
    maxSpeedList = [
        serviceSet[serviceName]['speed'][0 if fixedSpeed else 1]
        for serviceName in serviceList
    ]
    speedList = uniform(low=minSpeedList, high=maxSpeedList, size=cfg_sys.NUM_REQ)

    durationList = choice(cfg_sys.DURATION, size=cfg_sys.NUM_REQ)

    reqSet = {i: req(j, k, l) for i, j, k, l in zip(nameList, serviceList, speedList, durationList)}
    for i in reqSet:
        user = choice(list(userSet))
        userSet[user]['reqSet'][i] = reqSet[i]

    dcSet = {
        i: {'alias': nodeSet[i]['alias'], 'serviceList': []}
        for i in nodeSet if nodeSet[i]['typee'] == cfg_sys.TYPEE_DC
    }
    for i in serviceSet:
        minServiceNum = min([len(dc['serviceList']) for dc in dcSet.values()])
        dc = choice([
            dcIp
            for dcIp, dc in dcSet.items()
            if len(dc['serviceList']) == minServiceNum
        ])
        dcSet[dc]['serviceList'].append(i)
    logger.info('generation complete: userSet: %s, dcSet: %s', str(userSet), str(dcSet))
    return userSet, dcSet


if __name__ == '__main__':
    u, d = generator(cfg_ctlr['topo']['nodeSet'], cfg_ctlr['serviceSet'])
    print(u)
    print(d)
