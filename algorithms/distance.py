import config.config_sys as cfg_sys
from code_utils.utils import getLogger
from config.config_ctlr import cfg_ctlr

logger = getLogger()


def alg(userSet, dcSet, nodeSet, edgeList, serviceSet, delayMat, budget):
    """
    return assignment: {
        reqName: locationIp
    }
    """
    logger.warning('Distance algorithm beginning')

    distanceMat = cfg_ctlr['topo']['distanceMat']

    residualCapacity = {
        k: v['capacity'] for k, v in nodeSet.items()
        if v['typee'] == cfg_sys.TYPEE_CL_USER
    }
    assignment = {}

    for userIp, user in userSet.items():

        distanceList = sorted(
            [clIp for clIp in residualCapacity],
            key=lambda clIp: distanceMat[user['alias'][-3:]][nodeSet[clIp]['alias'][-3:]]
        )
        for reqName, req in user['reqSet'].items():
            service = req['service']
            capacity = req['speed'] / serviceSet[service]['miu']
            for location in distanceList:

                if location in dcSet:
                    continue

                if residualCapacity[location] < capacity:
                    continue

                if location in dcSet and service not in dcSet[location]['serviceList']:
                    continue

                assignment[reqName] = location
                residualCapacity[location] -= capacity
                break

    dcAssignment = {
        reqName: req
        for userIp, user in userSet.items()
        for reqName, req in user['reqSet'].items()
        if reqName not in assignment
    }

    dcAssignment = {
        reqName: dcIp
        for dcIp, dc in dcSet.items()
        for reqName, req in dcAssignment.items()
        if req['service'] in dc['serviceList']
    }
    assignment.update(dcAssignment)

    logger.warning('Distance alg: assignment: %s', str(assignment))
    return assignment
