from copy import deepcopy

import config.config_sys as cfg_sys
from algorithms.appro_diff import alg as algApproDiff
from algorithms.utils import totalCost
from code_utils.utils import getLogger, shutdown

logger = getLogger()


def alg(userSet, dcSet, nodeSet, edgeList, serviceSet, delayMat, budget, w1=None, w2=None, w3=None):
    """
    return assignment: {
        reqName: locationIp
    }
    """
    logger.warning('Heu algorithm beginning')

    serviceList = list(serviceSet)
    logger.info('Heu alg: serviceList: %s', serviceList)
    serviceReqList = [
        {
            reqName: req
            for user in userSet.values()
            for reqName, req in user['reqSet'].items()
            if req['service'] == serviceName
        } for serviceName in serviceList
    ]

    numList = [len(reqSet) for reqSet in serviceReqList]
    logger.info('Heu alg: service req num: %s', numList)

    totalList = [
        sum([req['speed'] for req in reqSet.values()])
        for reqSet in serviceReqList
    ]
    logger.info('Heu alg: service total packet rate: %s', totalList)

    avgList = [total / num for total, num in zip(totalList, numList)]
    logger.info('Heu alg: service avg packet rate: %s', avgList)

    numList = [i / sum(numList) for i in numList]
    avgList = [i / sum(avgList) for i in avgList]
    totalList = [i / sum(totalList) for i in totalList]

    w1 = cfg_sys.WEIGHT_HEU_1 if w1 is None else w1
    w2 = cfg_sys.WEIGHT_HEU_2 if w2 is None else w2
    w3 = cfg_sys.WEIGHT_HEU_3 if w3 is None else w3
    scoreList = [
        w1 * num + w2 * avg + w3 * total
        for num, avg, total in zip(numList, avgList, totalList)
    ]

    rankList = sorted(zip(serviceList, scoreList), key=lambda x: x[1])
    logger.info('Heu alg: service rank: %s', rankList)

    reqList = [
        {'reqName': reqName, **req, 'location': userIp}
        for userIp, user in userSet.items()
        for reqName, req in user['reqSet'].items()
    ]
    costMat = totalCost(userSet, dcSet, nodeSet, edgeList, serviceSet)
    nodeSet = deepcopy(nodeSet)
    budget = deepcopy(budget)
    assignment = {}
    for serviceName in next(zip(*rankList)):
        userSetSplit = deepcopy(userSet)
        userSetSplit = {
            userIp: {
                **user,
                'reqSet': {
                    reqName: req
                    for reqName, req in user['reqSet'].items()
                    if req['service'] == serviceName
                }
            } for userIp, user in userSetSplit.items()
        }

        assignmentDiff = algApproDiff(
            userSetSplit, dcSet, nodeSet, edgeList, {serviceName: serviceSet[serviceName]}, delayMat, budget
        )
        assignment.update(assignmentDiff)

        for req in reqList:
            if req['reqName'] in assignmentDiff:

                target = assignmentDiff[req['reqName']]
                nodeSet[target]['capacity'] -= req['speed'] / serviceSet[req['service']]['miu']

                if target not in dcSet:
                    budget -= costMat[req['reqName']][target]

    logger.info('Heu alg: assignment: %s', str(assignment))

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
