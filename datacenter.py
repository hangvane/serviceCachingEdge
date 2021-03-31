import json
import logging
import threading
import time
from flask import Flask, request, jsonify
from importlib import reload

import config.config_dc
import config.config_sys as cfg_sys
from code_utils.utils import getIp, getState, getConfig, register, delayTest, uploadDelay, iperfReceiver, post, \
    dockerDelete, getLogger

logging.getLogger('werkzeug').setLevel(logging.ERROR)
logger = getLogger()

cfg = config.config_dc.cfg


def controlThread():
    """start lifecycle of DC, main thread is for flask"""
    logger.critical('lifecycle thread of DC opened')
    while True:
        for _ in lifecycle():
            time.sleep(2)
            if cfg['state'] == cfg_sys.STATE_RESET:
                logger.info('lifecycle reset: reset state detected')
                reset()
                time.sleep(5)
                break


def init():
    logger.info('DC init is beginning')
    t = threading.Thread(target=controlThread)
    t.start()

    pass


def getServiceSetSingle(ipCtlr, ipSelf):
    """for dc, fetch service list of the original instance"""
    logger.info('fetch service instance set')
    while True:
        status, response, errInfo = post(
            'http://%s:%d/getServiceSetSingle' % (ipCtlr, cfg_sys.HTTP_PORT),
            data={'ip': ipSelf}
        )
        if status:
            break
        else:
            logger.warning('fetch service instance set failed: %s', errInfo)
    serviceSet = json.loads(response)['serviceSet']
    logger.info('service instance set fetched: %s', str(serviceSet))
    return serviceSet


def reset():
    logger.warning('reset is beginning')

    global cfg
    cfg = reload(config.config_dc).cfg
    dockerDelete(delAll=True)
    pass


def lifecycle():
    """lifecycle of DC"""
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

    cfg['remoteCfg']['serviceSet'] = getServiceSetSingle(ipCtlr=cfg['ctlrIp'], ipSelf=cfg['ip'])
    yield

    """begin state ignored"""

    while cfg['state'] != cfg_sys.STATE_RESET:
        logger.info('the state trying to fetch: %s', cfg_sys.STATE_RESET)
        cfg['state'] = getState(
            ipCtlr=cfg['ctlrIp'],
            ipSelf=cfg['ip']
        )
        yield
    # yield reset()


app = Flask(__name__)


@app.route('/req', methods=['POST'])
def req():
    """
    accept requests from user
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
        'accept requests from user, alias: %s, IP: %s, reqName: %s, serviceName: %s, speed: %.2f, duration: %d, port: %d',
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
