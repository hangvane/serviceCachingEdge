from collections import Counter
from copy import deepcopy
from math import ceil

from algorithms.appro_uni import alg as algApproUni
from code_utils.utils import getLogger, shutdown

logger = getLogger()


def alg(userSet, dcSet, nodeSet, edgeList, serviceSet, delayMat, budget):
    """
    return assignment: {
        reqName: locationIp
    }
    """
    logger.info('Appro_uni algorithm beginning')

    if len(serviceSet) != 1:
        logger.critical('Appro_Diffalg: error: need single type of service, current: %d types', len(serviceSet))
        shutdown()

    reqList = [
        {'reqName': reqName, **req, 'location': userIp}
        for userIp, user in userSet.items()
        for reqName, req in user['reqSet'].items()
    ]
    speedList = [v['speed'] for elm in userSet.values() for v in elm['reqSet'].values()]
    minSpeed = min(speedList)

    userSetSplit = deepcopy(userSet)

    for userIp, user in userSetSplit.items():
        tmpReqSet = deepcopy(user['reqSet'])
        user['reqSet'] = {}
        for reqName, req in tmpReqSet.items():
            numVirtualReq = ceil(req['speed'] / minSpeed)

            for i in range(numVirtualReq):
                user['reqSet'][reqName + '_' + str(i)] = {**req, 'speed': minSpeed}
                pass

    assignmentUni = algApproUni(userSetSplit, dcSet, nodeSet, edgeList, serviceSet, delayMat, budget)

    virtualReqNameList = list(assignmentUni.keys())

    assignment = {}

    for req in reqList:
        names = [i for i in virtualReqNameList if i.startswith(req['reqName'] + '_')]
        candidateList = [assignmentUni[name] for name in names]
        candidateCountList = dict(Counter(candidateList))
        maxLocation = max(candidateCountList.items(), key=lambda x: x[1])[0]
        assignment[req['reqName']] = maxLocation
        pass
    logger.info('Appro_diff alg: assignment: %s', str(assignment))

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
