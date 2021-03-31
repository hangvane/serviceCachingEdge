import logging
import threading
import time
from copy import deepcopy
from flask import Flask, jsonify, request
from importlib import import_module, reload

import config.config_ctlr
import config.config_sys as cfg_sys
from algorithms.utils import statistic
from code_utils.utils import getIp, getLogger, cmd
from generator import generator

logging.getLogger('werkzeug').setLevel(logging.ERROR)
logger = getLogger()

cfg_ctlr = config.config_ctlr.cfg_ctlr
cfg_cldc = config.config_ctlr.cfg_cldc


def init():
    logger.critical('ctlr init is beginning')

    if cfg_ctlr['state'] == cfg_sys.STATE_BEGIN:
        cfg_ctlr['state'] = cfg_sys.STATE_RESET

        for _ in range(cfg_sys.RESET_DURATION):
            time.sleep(cfg_sys.RESET_DURATION)
            cfg_ctlr['resetSet'] = {i: False for i in cfg_ctlr['topo']['nodeSet']}
            logger.critical('waiting for reset, %d/%ds', _, cfg_sys.RESET_DURATION)
    else:
        cfg_ctlr['state'] = cfg_sys.STATE_RESET

    cfg_ctlr['ip'] = getIp()

    cfg_ctlr['userSet'], cfg_ctlr['dcSet'] = generator(
        cfg_ctlr['topo']['nodeSet'],
        cfg_ctlr['serviceSet'],
        fixedSpeed=cfg_sys.FIXED_SPEED
    )

    pass


def startAlg():
    """invoking algorithms for request assignment"""
    logger.warning('begin invoking %s', cfg_ctlr['algorithm'])

    algorithm = getattr(import_module(cfg_ctlr['algorithm']), 'alg')

    cfg_ctlr['assignment'] = algorithm(
        userSet=cfg_ctlr['userSet'],
        dcSet=cfg_ctlr['dcSet'],
        nodeSet=cfg_ctlr['topo']['nodeSet'],
        edgeList=cfg_ctlr['topo']['edgeList'],
        serviceSet=cfg_ctlr['serviceSet'],
        delayMat={
            src: {
                dst: delay * (1 + cfg_sys.LAMBDA)
                for dst, delay in dstSet.items()
            } for src, dstSet in cfg_ctlr['delayMat'].items()
        },
        budget=cfg_ctlr['budget']
    )

    count = statistic(cfg_ctlr['assignment'], cfg_ctlr['topo']['nodeSet'])
    logger.warning('invoke %s completed, assignment: %s', cfg_ctlr['algorithm'], str(count))
    cfg_ctlr['state'] = cfg_sys.STATE_DISTRIBUTE
    pass


def output():
    resultSet = cfg_ctlr['resultSet']
    delayList = [delay for sets in resultSet.values() for delay in sets.values()]
    logger.warning('statistic: resultSet: %s', resultSet)
    logger.warning(
        'statistic: %d requests in total, %.5f delay in avg',
        len(delayList),
        sum(delayList) / len(delayList)
    )
    pass


def reset():
    logger.warning('ctlr reset beginning')

    global cfg_ctlr, cfg_cldc
    cfg_ctlr = reload(config.config_ctlr).cfg_ctlr
    cfg_cldc = reload(config.config_ctlr).cfg_cldc

    init()
    pass


app = Flask(__name__)


@app.route('/register', methods=['POST'])
def register():
    """
    node register
    ip
    typee
    capacity
    """
    params = request.json
    ip = params['ip']
    alias = cfg_ctlr['topo']['nodeSet'][ip]['alias']
    typee = params['typee']
    capacity = params['capacity']
    logger.info('node register: alias: %s, IP: %s, typee: %s, capacity: %.3f', alias, ip, typee, capacity)

    result = {}
    if ip in cfg_ctlr['topo']['nodeSet'] and typee == cfg_ctlr['topo']['nodeSet'][ip]['typee']:

        cfg_ctlr['topo']['nodeSet'][ip]['capacity'] = capacity
        cfg_ctlr['registerSet'][ip] = True

        remains = list(cfg_ctlr['registerSet'].values()).count(False)
        total = len(cfg_ctlr['registerSet'])
        logger.info('node register: completed alias: %s, IP: %s, remaining num: %d/%d', alias, ip, remains, total)

        if remains == 0:
            cfg_ctlr['state'] = cfg_sys.STATE_DELAY_TEST
            logger.warning('node register: all completed, goto delaytest state')
        result['result'] = cfg_sys.RETURN_SUCCEED
    else:
        logger.critical(
            'node register: Info mismatch: alias: %s, IP: %s, typee: %s, capacity: %.3f',
            alias,
            ip,
            typee,
            capacity
        )
        result['result'] = 'Info mismatch'
    return jsonify(result)


@app.route('/getConfig', methods=['POST'])
def getConfig():
    params = request.json
    ip = params['ip']
    alias = cfg_ctlr['topo']['nodeSet'][ip]['alias']
    typee = cfg_ctlr['topo']['nodeSet'][ip]['typee']
    logger.info('get config, alias: %s, IP: %s, typee: %s', alias, ip, typee)

    return jsonify(cfg_cldc)


@app.route('/uploadDelay', methods=['POST'])
def uploadDelay():
    """
    upload delay test result
    ip
    delaySet a single set of a node with all delay with all nodes
    """
    params = request.json
    ip = params['ip']
    delaySet = params['delaySet']
    alias = cfg_ctlr['topo']['nodeSet'][ip]['alias']
    logger.info('uploadDelay: alias: %s, IP: %s', alias, ip)

    if cfg_ctlr['delayMat'][ip] is not None:
        logger.warning('uploadDelay: upload repeated!: alias: %s, IP: %s', alias, ip)

    cfg_ctlr['delayMat'][ip] = delaySet

    remains = list(cfg_ctlr['delayMat'].values()).count(None)
    total = len(cfg_ctlr['delayMat'])
    logger.info('uploadDelay: completed: alias: %s, IP: %s, remaining num: %d/%d', alias, ip, remains, total)

    if remains == 0:
        logger.critical('uploadDelay: all completed, begin invoking alg, delayMat: %s', str(cfg_ctlr['delayMat']))
        cmd('echo "%s" > delayMat.txt' % str(cfg_ctlr['delayMat']))
        t = threading.Thread(target=startAlg)
        t.start()

    return jsonify({'result': cfg_sys.RETURN_SUCCEED})


@app.route('/getState', methods=['POST'])
def getState():
    """
    polling for state sync
    reset:
    register:
    delayTest:
    distribute: waiting for fetching the request and service assignments
    begin:
    ip
    """
    state = cfg_ctlr['state']
    result = {'state': state, 'result': cfg_sys.RETURN_SUCCEED}

    params = request.json
    ip = params['ip']

    if ip not in cfg_ctlr['topo']['nodeSet']:
        logger.critical('getState: IP not in list: IP: %s', ip)
        result['result'] = 'Ip error'
        return jsonify(result)
    alias = cfg_ctlr['topo']['nodeSet'][ip]['alias']
    logger.info('getState: alias: %s, IP: %s', alias, ip)

    if state == cfg_sys.STATE_RESET:
        if cfg_ctlr['resetSet'][ip] == False:
            cfg_ctlr['resetSet'][ip] = True
            remains = list(cfg_ctlr['resetSet'].values()).count(False)
            total = len(cfg_ctlr['resetSet'])
            logger.info('getState: reset: name: %s, IP: %s, remaining num: %d/%d', alias, ip, remains, total)
            if remains == 0:
                logger.critical('getState: all completed, goto register state')
                cfg_ctlr['state'] = cfg_sys.STATE_REGISTER
                pass
        pass
    elif state == cfg_sys.STATE_REGISTER:
        pass
    elif state == cfg_sys.STATE_DELAY_TEST:
        pass
    elif state == cfg_sys.STATE_DISTRIBUTE:
        pass
    elif state == cfg_sys.STATE_BEGIN:
        pass
    else:
        assert False
    return jsonify(result)


@app.route('/getReqSet', methods=['POST'])
def getReqSet():
    """
    for user, fetch the request set assigned to the user
    cfg_ctlr['distributeMat'] each value = 2 at the beginning, getReqSet -> 1, getDcSet -> 0 means completed
    ip
    """
    params = request.json
    ip = params['ip']
    alias = cfg_ctlr['topo']['nodeSet'][ip]['alias']
    logger.info('user getReqSet: alias: %s, IP: %s', alias, ip)
    result = {'reqSet': {}}
    if cfg_ctlr['state'] != cfg_sys.STATE_DISTRIBUTE:
        logger.critical('user getReqSet: state error, state: %s, alias: %s, IP: %s', cfg_ctlr['state'], alias, ip)
        return jsonify(result)
    # assignment for single user, add instance and return
    assignment = cfg_ctlr['assignment']
    result['reqSet'] = deepcopy(cfg_ctlr['userSet'][ip]['reqSet'])
    for reqName, req in result['reqSet'].items():
        req['instance'] = assignment[reqName]

    cfg_ctlr['distributeMat'][ip] = 1

    return jsonify(result)


@app.route('/getDcSet', methods=['POST'])
def getDcSet():
    """
    for user, fetch the dcSet
    cfg_ctlr['distributeMat'] each value = 2 at the beginning, getReqSet -> 1, getDcSet -> 0 means completed
    user fetch the whole dcSet but only with serviceName
    ip
    """
    params = request.json
    ip = params['ip']
    alias = cfg_ctlr['topo']['nodeSet'][ip]['alias']
    logger.info('user getDcSet: alias: %s, IP: %s', alias, ip)

    result = {'dcSet': {}, 'reqThreading': 0}
    if cfg_ctlr['state'] != cfg_sys.STATE_DISTRIBUTE:
        logger.critical('user getDcSet: state error, state: %s, alias: %s, IP: %s', cfg_ctlr['state'], alias, ip)
        return jsonify(result)

    result['dcSet'] = cfg_ctlr['dcSet']

    if cfg_ctlr['distributeMat'][ip] == 1:
        cfg_ctlr['distributeMat'][ip] = 0
        total = len(cfg_ctlr['distributeMat'])
        remains = total - list(cfg_ctlr['distributeMat'].values()).count(0)
        logger.info('state distribute: remaining num: %d/%d', remains, total)
        if remains == 0:
            logger.critical('state distribute: all completed, goto begin state')
            cfg_ctlr['state'] = cfg_sys.STATE_BEGIN

    return jsonify(result)


@app.route('/getServiceSetSingle', methods=['POST'])
def getServiceSetSingle():
    """
    for dc, fetch serviceSet
    serviceSet only contains services in dc, but includes the whole information
    ip
    """
    params = request.json
    ip = params['ip']
    alias = cfg_ctlr['topo']['nodeSet'][ip]['alias']
    logger.info('dc getServiceSetSingle, alias: %s, IP: %s', alias, ip)

    result = {'serviceSet': {}}
    if cfg_ctlr['state'] != cfg_sys.STATE_DISTRIBUTE:
        logger.critical(
            'dc getServiceSetSingle: state error, state:%s, alias: %s, IP: %s',
            cfg_ctlr['state'],
            alias,
            ip
        )
        return jsonify(result)

    result['serviceSet'] = {i: cfg_ctlr['serviceSet'][i] for i in cfg_ctlr['dcSet'][ip]['serviceList']}

    if cfg_ctlr['distributeMat'][ip] == 1:
        cfg_ctlr['distributeMat'][ip] = 0
        total = len(cfg_ctlr['distributeMat'])
        remains = total - list(cfg_ctlr['distributeMat'].values()).count(0)
        logger.info('state distribute: remaining num: %d/%d', remains, total)
        if remains == 0:
            logger.critical('state distribute: all completed, goto begin state')
            cfg_ctlr['state'] = cfg_sys.STATE_BEGIN

    return jsonify(result)


@app.route('/uploadResult', methods=['POST'])
def uploadResult():
    """
    for user, result upload
    ip
    resultSet: the delay for each request
    """
    params = request.json
    resultSet = params['resultSet']
    ip = params['ip']
    alias = cfg_ctlr['topo']['nodeSet'][ip]['alias']
    typee = cfg_ctlr['topo']['nodeSet'][ip]['typee']

    if typee != cfg_sys.TYPEE_CL_USER:
        logger.critical('result upload: typee error, typee: %s, alias: %s, IP: %s', typee, alias, ip)
        return jsonify({'result': 'typee error'})

    if cfg_ctlr['state'] != cfg_sys.STATE_BEGIN:
        logger.critical('result upload: state error, state: %s, alias: %s, IP: %s', cfg_ctlr['state'], alias, ip)
        return jsonify({'result': 'state error'})

    logger.info('result upload: alias: %s, IP: %s', alias, ip)
    cfg_ctlr['resultSet'][ip] = resultSet

    if cfg_ctlr['resultUploadSet'][ip] == False:
        cfg_ctlr['resultUploadSet'][ip] = True
        total = len(cfg_ctlr['resultUploadSet'])
        remains = list(cfg_ctlr['resultUploadSet'].values()).count(False)
        logger.info('result upload: remaining num: %d/%d', remains, total)
        if remains == 0:
            logger.critical('result upload: all completed, output and reset')
            output()
            t = threading.Thread(target=reset)
            t.start()

    return jsonify({'result': cfg_sys.RETURN_SUCCEED})


@app.route('/shutdown')
def shutdown1():
    shutdown = request.environ.get('werkzeug.server.shutdown')
    shutdown()
    return 'shuting down'


if __name__ == '__main__':
    init()
    app.run(host='0.0.0.0', port=cfg_sys.HTTP_PORT)
