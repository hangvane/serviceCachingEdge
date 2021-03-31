import networkx as nx
from networkx.algorithms import all_pairs_dijkstra_path_length

import code_utils.lpsolve_wrapper as lw
import config.config_sys as cfg_sys
from code_utils.utils import getLogger, shutdown, addEdge

logger = getLogger()


def transferCost(nodeSet, edgeList):
    logger.info('start calculating transfer cost')
    input = {}
    for e in edgeList:
        addEdge(input, e['src'], e['dst'], e['price'])
        addEdge(input, e['dst'], e['src'], e['priceReverse'])

    nxG = nx.DiGraph(input)
    pass

    for i in nodeSet:
        if i not in nxG.nodes:
            logger.error('nodeSet not connected: %s have no edge', i)
            shutdown()

    if not nx.is_strongly_connected(nxG):
        logger.error('nodeSet not connected: not strongly connected')
        shutdown()

    return dict(all_pairs_dijkstra_path_length(nxG))


def totalCost(userSet, dcSet, nodeSet, edgeList, serviceSet):
    clSet = {
        nodeIp: node for nodeIp, node in nodeSet.items()
        if node['typee'] == cfg_sys.TYPEE_CL_USER
    }

    transferCostMat = transferCost(nodeSet, edgeList)

    costMat = {}
    for userIp, user in userSet.items():
        for reqName, req in user['reqSet'].items():
            service = req['service']
            originalDc = [dcIp for dcIp, dc in dcSet.items() if service in dc['serviceList']][0]
            speed = req['speed']

            costMat[reqName] = {}
            for nodeIp, node in clSet.items():
                price = node['price']

                costMat[reqName][nodeIp] = 0
                # cost service instantiation
                costMat[reqName][nodeIp] += serviceSet[service]['cost']
                # cost processing
                costMat[reqName][nodeIp] += price * speed
                # cost transfer
                costMat[reqName][nodeIp] += transferCostMat[userIp][nodeIp] * speed
                # cost update
                costMat[reqName][nodeIp] += transferCostMat[nodeIp][originalDc] * speed * cfg_sys.THETA
            pass
        pass

    return costMat


def uckm(distances, numClient, numFacility):
    # since capacity == 1, no need to determine the open facilities set,
    # so degrade into algorithm in chapter 3.1 of UCKM reference
    logger.info('UCKM algorithm, %d clients, %d facilities', numClient, numFacility)
    model = lw.Model(
        notations={
            'x': lw.notation(
                shape=(numClient, numFacility),
                lower_bound=0,
            )
        })
    for i in range(numClient):
        model.add_constr_callback(
            callbacks={
                'x': lambda x: x[i, :].fill(1)
            },
            right_value=1,
            constr_type=lw.EQ
        )
    for i in range(numFacility):
        model.add_constr_callback(
            callbacks={
                'x': lambda x: x[:, i].fill(1)
            },
            right_value=1,
            constr_type=lw.LEQ
        )
    objective, notation_list = model.lp_solve(
        obj_func={
            'x': distances,
        },
        minimize=True
    )
    return objective, notation_list['x']


def statistic(assignment, nodeSet):
    count = {
        cfg_sys.TYPEE_CL_USER: 0,
        cfg_sys.TYPEE_DC: 0
    }
    for target in assignment.values():
        count[nodeSet[target]['typee']] += 1
    return count


def totalDelay(assignment, delayMat, userSet):
    reqLocationSet = {
        reqName: userIp
        for userIp, user in userSet.items()
        for reqName, req in user['reqSet'].items()
    }
    delaySet = {
        reqName: delayMat[userIp][assignment[reqName]]
        for reqName, userIp in reqLocationSet.items()
    }
    logger.info('theoretical total delay: %.2f', sum(delaySet.values()))
    return sum(delaySet.values()) / len(assignment)


def totalBudget(assignment, userSet, dcSet, nodeSet, edgeList, serviceSet):
    costMat = totalCost(userSet, dcSet, nodeSet, edgeList, serviceSet)
    assignmentCostSet = {
        reqName: costMat[reqName][location]
        for reqName, location
        in assignment.items()
        if location not in dcSet
    }
    logger.info('total budget: %.2f', sum(assignmentCostSet.values()))
    return sum(assignmentCostSet.values())


if __name__ == '__main__':
    pass
