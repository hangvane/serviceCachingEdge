import numpy as np
from math import floor

import config.config_sys as cfg_sys
from algorithms.utils import totalCost, uckm
from code_utils.utils import getLogger, minN, shutdown

logger = getLogger()


def alg(userSet, dcSet, nodeSet, edgeList, serviceSet, delayMat, budget):
    """
    return assignment: {
        reqName: locationIp
    }
    """
    logger.info('Appro_uni algorithm beginning')

    speedList = [v['speed'] for elm in userSet.values() for v in elm['reqSet'].values()]
    if not speedList or speedList.count(speedList[0]) != len(speedList):
        logger.critical('Appro_uni alg: error: need identical packet rate, current: %s', speedList)
        shutdown()

    if len(serviceSet) != 1:
        logger.critical('Appro_uni alg: error: need single type of service, current: %d types', len(serviceSet))
        shutdown()

    costMat = totalCost(userSet, dcSet, nodeSet, edgeList, serviceSet)

    service = list(serviceSet.values())[0]
    reqList = [
        {'reqName': reqName, **req, 'location': userIp}
        for userIp, user in userSet.items()
        for reqName, req in user['reqSet'].items()
    ]
    clSet = {
        nodeIp: node for nodeIp, node in nodeSet.items()
        if node['typee'] == cfg_sys.TYPEE_CL_USER
    }
    clIpList = list(clSet.keys())
    numReq = len(reqList)

    capacity = reqList[0]['speed'] / service['miu']
    numVirtualClSet = {
        clIp: floor((cl['capacity'] if cl['capacity'] > 0 else 0) / capacity)
        for clIp, cl in clSet.items()
    }
    costList = [cost for subSet in costMat.values() for cost in subSet.values()]
    cMax = max(costList)
    cMin = min(costList)
    rho = reqList[0]['speed']
    beta = cfg_sys.BETA

    Nq = floor(budget / (cMin + beta * (cMax - cMin)))

    Ncl = sum(numVirtualClSet.values())
    K = min(Nq, Ncl)

    logger.info(
        'Appro_uni alg: cMax: %.2f, cMin: %.2f, B: %.2f, rho: %d, miuQ: %.2f, Nq: %d, Ncl: %d, K: %d',
        cMax, cMin, budget, rho, service['miu'], Nq, Ncl, K)

    if K <= 0:
        dcAssignment = {
            req['reqName']: dcIp
            for dcIp, dc in dcSet.items()
            for req in reqList
            if req['service'] in dc['serviceList']
        }
        return dcAssignment

    numVirtualClList = [numVirtualClSet[clIp] for clIp in clIpList]

    virtualClList = []
    for clIp, num in zip(clIpList, numVirtualClList):
        virtualClList += [clIp, ] * num

    numVirtualCl = Ncl
    delayArr = np.zeros(shape=(numReq, numVirtualCl))
    for i in range(numReq):
        for j in range(numVirtualCl):
            delayArr[i][j] = delayMat[reqList[i]['location']][virtualClList[j]]

    if numReq > numVirtualCl:
        addArr = delayArr.max(axis=1)
        addArr = np.tile(
            np.expand_dims(addArr, axis=(1,)),
            (1, numReq - numVirtualCl)
        )
        addArr = cfg_sys.MAX - addArr
        delayArr = np.c_[
            delayArr,
            addArr
        ]

    _, result = uckm(
        distances=delayArr,
        numClient=numReq,
        numFacility=max(numReq, numVirtualCl)
    )

    resultDelay = result * delayArr
    resultDelay[resultDelay == 0] = np.inf
    reqIdxes, virtualClIdxes = minN(resultDelay, min(numReq, numVirtualCl, K))

    assignment = {reqList[i]['reqName']: virtualClList[j] for i, j in zip(reqIdxes, virtualClIdxes)}

    dcAssignment = {req['reqName']: req for req in reqList if req['reqName'] not in assignment}

    dcAssignment = {
        reqName: dcIp
        for dcIp, dc in dcSet.items()
        for reqName, req in dcAssignment.items()
        if req['service'] in dc['serviceList']
    }

    assignment.update(dcAssignment)

    for req in reqList:
        if req['reqName'] not in assignment:
            logger.critical(
                'request not assigned: reqName: %s, userIp: %s, assignment: %s',
                req['reqName'],
                req['location'],
                str(assignment)
            )
            shutdown()

    return assignment
