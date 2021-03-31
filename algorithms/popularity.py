import config.config_sys as cfg_sys
from algorithms.utils import totalCost
from code_utils.utils import getLogger, shutdown

logger = getLogger()


def alg(userSet, dcSet, nodeSet, edgeList, serviceSet, delayMat, budget):
    """
    return assignment: {
        reqName: locationIp
    }
    """
    logger.warning('Popularity algorithm beginning')

    costMat = totalCost(userSet, dcSet, nodeSet, edgeList, serviceSet)
    logger.info('Popularity alg: costMat: %s', str(costMat))

    residualCapacity = {
        k: v['capacity'] for k, v in nodeSet.items()
        if v['typee'] == cfg_sys.TYPEE_CL_USER or
           v['typee'] == cfg_sys.TYPEE_DC
    }

    popularitySet = {
        serviceName: {
            nodeIp: 0
            for nodeIp, node in nodeSet.items()
            if node['typee'] == cfg_sys.TYPEE_CL_USER
        }
        for serviceName in serviceSet
    }
    assignment = {}

    for userIp, user in userSet.items():
        for reqName, req in user['reqSet'].items():
            serviceName = req['service']
            capacity = req['speed'] / serviceSet[serviceName]['miu']

            maxDelay = max(delayMat[userIp].values())
            popularitySubset = {
                clIp: pop - delayMat[userIp][clIp] / maxDelay / 2
                for clIp, pop in popularitySet[serviceName].items()
            }

            popularityList = sorted(
                zip(popularitySubset.keys(), popularitySubset.values()),
                key=lambda x: x[1],
                reverse=True,
            )

            for clIp, _ in popularityList:
                if residualCapacity[clIp] < capacity:
                    continue

                popularitySet[serviceName][clIp] += 1
                assignment[reqName] = clIp
                residualCapacity[clIp] -= capacity
                break

            if reqName not in assignment:
                for dcIp in dcSet:
                    if serviceName not in dcSet[dcIp]['serviceList']:
                        continue

                    assignment[reqName] = dcIp
                    residualCapacity[dcIp] -= capacity
                    break


            if reqName not in assignment:
                logger.error(
                    'request not assigned: reqName: %s, userIp: %s, assignment: %s', reqName, userIp, str(assignment)
                )
                shutdown()
    logger.warning('Popularity algorithm finished, assignment: %s', str(assignment))
    return assignment
