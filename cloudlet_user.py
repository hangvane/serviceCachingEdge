import json
import logging
import threading
import time
from flask import Flask, request, jsonify
from importlib import reload
from multiprocessing.dummy import Pool as ThreadPool
from random_open_port import random_port

import config.config_cl_user
import config.config_sys as cfg_sys
from code_utils.utils import getIp, getState, getConfig, register, delayTest, uploadDelay, iperfSender, dockerDelete, \
    post, iperfReceiver, getLogger

logging.getLogger('werkzeug').setLevel(logging.ERROR)
logger = getLogger()

cfg = config.config_cl_user.cfg


def controlThread():
    """start lifecycle of CL, main thread is for flask"""
    logger.critical('lifecycle thread of CL opened')
    while True:
        for _ in lifecycle():
            time.sleep(2)
            if cfg['state'] == cfg_sys.STATE_RESET:
                logger.info('lifecycle reset: reset state detected')
                reset()
                time.sleep(5)
                break


def init():
    logger.info('CL init is beginning')
    t = threading.Thread(target=controlThread)
    t.start()
    pass


def getReqSet(ipCtlr, ipSelf):
    """for user, fetch request list"""
    logger.info('fetch reqSet')
    while True:
        status, response, errInfo = post(
            'http://%s:%d/getReqSet' % (ipCtlr, cfg_sys.HTTP_PORT),
            data={'ip': ipSelf}
        )
        if status:
            break
        else:
            logger.warning('fetch reqSet failed: %s', errInfo)
    reqSet = json.loads(response)['reqSet']
    logger.info('reqSet: %s', str(reqSet))
    return reqSet


def getDcSet(ipCtlr, ipSelf):
    """for user, fetch service list"""
    logger.info('fetch dcSet')
    while True:
        status, response, errInfo = post(
            'http://%s:%d/getDcSet' % (ipCtlr, cfg_sys.HTTP_PORT),
            data={'ip': ipSelf}
        )
        if status:
            break
        else:
            logger.warning('fetch dcSet failed: %s', errInfo)
    dcSet = json.loads(response)['dcSet']
    serviceList = json.loads(response)['serviceList']
    logger.info('dcSet: %s, serviceList: %s', str(dcSet), str(serviceList))
    return dcSet, serviceList


def uploadResult(ipCtlr, ipSelf, resultSet):
    """result upload"""
    logger.warning('result upload')
    while True:
        status, response, errInfo = post(
            'http://%s:%d/uploadResult' % (ipCtlr, cfg_sys.HTTP_PORT),
            data={
                'ip': ipSelf,
                'resultSet': resultSet
            }
        )
        if status:
            break
        else:
            logger.warning('result upload failed: %s', errInfo)
    logger.info('result upload succeed')
    return


def reset():
    logger.warning('reset is beginning')

    global cfg
    cfg = reload(config.config_cl_user).cfg
    dockerDelete(delAll=True)
    pass


def lifecycle():
    """lifecycle of CLUser"""
    cfg['ip'] = getIp()
    yield

    while cfg['state'] != cfg_sys.STATE_REGISTER:
        logger.info('the state trying to fetch: %s', cfg_sys.STATE_REGISTER)
        cfg['state'] = getState(
            ipCtlr=cfg['ctlrIp'],
            ipSelf=cfg['ip']
        )
        yield

    cfg['remoteCfg'] = getConfig(
        ipCtlr=cfg['ctlrIp'],
        ipSelf=cfg['ip']
    )
    yield

    register(
        ipCtlr=cfg['ctlrIp'],
        ipSelf=cfg['ip'],
        typee=cfg['remoteCfg']['topo']['nodeSet'][cfg['ip']]['typee'],
        capacity=cfg['remoteCfg']['topo']['nodeSet'][cfg['ip']]['capacity']
    )
    yield

    while cfg['state'] != cfg_sys.STATE_DELAY_TEST:
        logger.info('the state trying to fetch: %s', cfg_sys.STATE_DELAY_TEST)
        cfg['state'] = getState(
            ipCtlr=cfg['ctlrIp'],
            ipSelf=cfg['ip']
        )
        yield

    delaySet = delayTest(
        nodeList=list(cfg['remoteCfg']['topo']['nodeSet'])
    )
    yield

    uploadDelay(
        ipCtlr=cfg['ctlrIp'],
        ipSelf=cfg['ip'],
        delaySet=delaySet
    )
    yield

    while cfg['state'] != cfg_sys.STATE_DISTRIBUTE:
        logger.info('the state trying to fetch: %s', cfg_sys.STATE_DISTRIBUTE)
        cfg['state'] = getState(
            ipCtlr=cfg['ctlrIp'],
            ipSelf=cfg['ip']
        )
        yield

    cfg['remoteCfg']['reqSet'] = getReqSet(ipCtlr=cfg['ctlrIp'], ipSelf=cfg['ip'])
    yield

    cfg['remoteCfg']['dcSet'], cfg['remoteCfg']['serviceList'] = getDcSet(ipCtlr=cfg['ctlrIp'], ipSelf=cfg['ip'])
    yield

    while cfg['state'] != cfg_sys.STATE_BEGIN:
        logger.info('the state trying to fetch: %s', cfg_sys.STATE_BEGIN)
        cfg['state'] = getState(
            ipCtlr=cfg['ctlrIp'],
            ipSelf=cfg['ip']
        )
        yield

    resultSet = userExecute(reqSet=cfg['remoteCfg']['reqSet'])
    yield

    uploadResult(resultSet=resultSet, ipCtlr=cfg['ctlrIp'], ipSelf=cfg['ip'])
    yield

    while cfg['state'] != cfg_sys.STATE_RESET:
        logger.info('the state trying to fetch: %s', cfg_sys.STATE_RESET)
        cfg['state'] = getState(
            ipCtlr=cfg['ctlrIp'],
            ipSelf=cfg['ip']
        )
        yield


def userExecute(reqSet):
    """begin requesting from each req in reqSet"""
    logger.warning('user start requesting, %d requests in total', len(reqSet))

    pool = ThreadPool(cfg['remoteCfg']['reqThreading'])
    resultList = pool.map(
        lambda req: (req[0], sendRequest(
            reqName=req[0],
            serviceName=req[1]['service'],
            speed=req[1]['speed'],
            duration=req[1]['duration'],
            targetIp=req[1]['instance'],
            alias=cfg['remoteCfg']['topo']['nodeSet'][req[1]['instance']]['alias'],
            typee=cfg['remoteCfg']['topo']['nodeSet'][req[1]['instance']]['typee'],
            timeout=cfg_sys.REQ_TIMEOUT
        )),
        reqSet.items()
    )
    pool.close()
    pool.join()

    resultSet = {i[0]: i[1] for i in resultList}
    return resultSet


def sendRequest(reqName, serviceName, speed, duration, alias, targetIp, typee, timeout):
    """send a request"""
    # user start timing
    # user initialize iperf server
    # user call for DC or CL
    # DC or CL initialize iperf client, connect to server for reverse transmission
    # return request to user
    # user receive receipt
    # user stop timing
    # user close iperf server
    # return delay
    port = random_port()
    logger.info(
        'user start a request, reqName: %s, serviceName: %s, speed: %.2f, duration: %d, port: %d, target alias:%s , targetIp: %s, target typee: %s',
        reqName,
        serviceName,
        speed,
        duration,
        port,
        alias,
        targetIp,
        typee,
    )
    startTime = time.time()
    iperfSender(port, serviceName, reqName)

    while True:
        status, response, errInfo = post(
            'http://%s:%d/req' % (targetIp, cfg_sys.HTTP_PORT),
            data={
                'ip': cfg['ip'],
                'reqName': reqName,
                'serviceName': serviceName,
                'speed': speed,
                'duration': duration,
                'port': port,
            },
            timeout=timeout + duration
        )
        if status:
            break
        else:
            logger.critical(
                'user requesting failed, reqName: %s, serviceName: %s, port: %d, target alias:%s , targetIp: %s, target typee: %s, err info: %s',
                reqName,
                serviceName,
                port,
                alias,
                targetIp,
                typee,
                errInfo,
            )
    endTime = time.time()

    time.sleep(duration + cfg_sys.OFFSET_DELETE)
    return endTime - startTime


app = Flask(__name__)


@app.route('/req', methods=['POST'])
def req():
    """
    for user, receive request from user
    ip
    reqName,
    serviceName,
    speed,
    duration,
    port,
    """
    params = request.json
    ip = params['ip']
    alias = cfg['remoteCfg']['topo']['nodeSet'][ip]
    reqName = params['reqName']
    serviceName = params['serviceName']
    speed = params['speed']
    duration = params['duration']
    port = params['port']

    logger.info(
        'receive request from user, user alias: %s, IP: %s, reqName: %s, serviceName: %s, speed: %.2f, duration: %d, port: %d',
        alias,
        ip,
        reqName,
        serviceName,
        speed,
        duration,
        port
    )
    iperfReceiver(
        ip=ip,
        port=port,
        reqName=reqName,
        serviceName=serviceName,
        bandwidth=speed,
        duration=duration
    )
    return jsonify({'result': cfg_sys.RETURN_SUCCEED})


@app.route('/shutdown')
def shutdown1():
    shutdown = request.environ.get('werkzeug.server.shutdown')
    shutdown()
    return 'shuting down'


if __name__ == '__main__':
    init()
    app.run(host='0.0.0.0', port=cfg_sys.HTTP_PORT)
