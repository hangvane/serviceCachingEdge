import colorlog
import json
import numpy as np
import requests
import subprocess
import sys
import time
import urllib3
from pythonping import ping
from requests.adapters import HTTPAdapter
from requests.packages.urllib3.util.retry import Retry

from config import config_sys as cfg_sys

urllib3.disable_warnings()

session = requests.session()
adapter = HTTPAdapter(
    max_retries=Retry(
        total=cfg_sys.HTTP_MAX_RETRY,
        connect=5,
        read=1,
        backoff_factor=0.1,
        method_whitelist=('POST', 'GET')
    ))
session.mount('http://', adapter)
session.mount('https://', adapter)


def getLogger(name=cfg_sys.LOGGER_NAME):
    logger = colorlog.getLogger(name)
    if not logger.hasHandlers():
        handler = colorlog.StreamHandler()
        handler.setFormatter(
            colorlog.ColoredFormatter(
                fmt=cfg_sys.LOG_FORMAT,
                datefmt=cfg_sys.LOG_DATE_FORMAT,
                log_colors=cfg_sys.LOG_COLOR_MAP
            )
        )
        logger.addHandler(handler)
        logger.setLevel('INFO')
    return logger


logger = getLogger()


def post(url, data=None, timeout=5):
    """do post and get receipt sync"""
    try:
        r = session.post(url, json=data, timeout=timeout)
        r.raise_for_status()
        result = (True, r.text, None)
    except requests.exceptions.HTTPError as e:
        result = (False, None, repr(e))
    except requests.exceptions.ConnectionError as e:
        result = (False, None, repr(e))
    except requests.exceptions.Timeout as e:
        result = (False, None, repr(e))
    except Exception as e:
        result = (False, None, repr(e))
    finally:
        return result


def ipPing(ip):
    """ping ip for multiple times"""
    delay = ping(ip, timeout=5, count=cfg_sys.TIMES_PING).rtt_avg_ms
    logger.info('delay test %s: %.2fms', ip, delay)
    return delay


def getIp():
    while True:
        status, response, errInfo = post('https://jsonip.com/')
        if status:
            break
        else:
            logger.critical('get ip failed: %s', errInfo)
    ip = json.loads(response)['ip']
    logger.info('self IP: %s', ip)
    return ip


def getState(ipCtlr, ipSelf):
    """
    fetch state from ctlr, for state sync
    ipCtlr
    ipSelf
    """
    while True:
        status, response, errInfo = post('http://%s:%d/getState' % (ipCtlr, cfg_sys.HTTP_PORT), data={'ip': ipSelf})
        if status:
            break
        else:
            logger.warning('get state failed: %s', errInfo)
    result = json.loads(response)['result']
    if result != cfg_sys.RETURN_SUCCEED:
        logger.error('get state: problems occurred, exit: %s', result)
        shutdown()
    state = json.loads(response)['state']
    logger.info('state fetched: %s', state)
    return state


def getConfig(ipCtlr, ipSelf):
    while True:
        status, response, errInfo = post('http://%s:%d/getConfig' % (ipCtlr, cfg_sys.HTTP_PORT), data={'ip': ipSelf})
        if status:
            break
        else:
            logger.warning('get config failed: %s', errInfo)
    remoteCfg = json.loads(response)
    logger.info('config fetched: %s', remoteCfg)
    return remoteCfg


def register(ipCtlr, ipSelf, typee, capacity):
    """node registration, upload the information of itself"""
    while True:
        status, response, errInfo = post(
            'http://%s:%d/register' % (ipCtlr, cfg_sys.HTTP_PORT),
            data={
                'ip': ipSelf,
                'typee': typee,
                'capacity': capacity
            }
        )
        if status:
            break
        else:
            logger.warning('node registration failed: %s', errInfo)
    result = json.loads(response)['result']
    if result != cfg_sys.RETURN_SUCCEED:
        logger.critical('node registration: problems occurred, exit: %s', result)
        shutdown()
    logger.info('node registration result: %s', result)
    return result


def delayTest(nodeList):
    """
    delay test
    nodeList: ['1.1.1.1','2.2.2.2']
    """
    delaySet = {ip: ipPing(ip) for ip in nodeList}
    logger.warning('delay test completed')
    return delaySet


def uploadDelay(ipCtlr, ipSelf, delaySet):
    """upload delay test result"""
    while True:
        status, response, errInfo = post(
            'http://%s:%d/uploadDelay' % (ipCtlr, cfg_sys.HTTP_PORT),
            data={
                'ip': ipSelf,
                'delaySet': delaySet
            }
        )
        if status:
            break
        else:
            logger.warning('upload delay test result failed: %s', errInfo)
    result = json.loads(response)['result']
    logger.warning('upload delay test result: %s', result)
    return result


def cmd(cmdStr):
    subprocess.Popen(
        cmdStr,
        shell=True,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE
    )


def iperfSender(port, serviceName, reqName):
    """create iperf sender container (server)"""
    containerName = 'sc-server-%s-%s' % (reqName, serviceName)
    logger.info(
        'create iperf sender, serviceName: %s, reqName: %s, containerName: %s, port: %d',
        serviceName,
        reqName,
        containerName,
        port
    )
    cmd(
        'docker run --rm --name=%s --net=host networkstatic/iperf3 -s -p%d -1'
        % (containerName, port)
    )
    return containerName


def iperfReceiver(ip, port, reqName, serviceName, bandwidth, duration):
    """create iperf receiver container (client)"""
    containerName = 'sc-client-%s-%s' % (reqName, serviceName)
    logger.info(
        'create iperf receiver, serviceName: %s, reqName: %s, containerName: %s, IP: %s, port: %d, bandwidth: %.3f, duration: %d',
        serviceName,
        reqName,
        containerName,
        ip,
        port,
        bandwidth,
        duration
    )
    cmd(
        'docker run --rm --name=%s --net=host networkstatic/iperf3 -c %s -p%d -R -b%.2fM -t%d -u'
        % (containerName, ip, port, bandwidth, duration),
    )
    return containerName


def dockerDelete(name='No', delAll=False):
    """delete a single container or all containers (`docker stop' in actual)"""
    if delAll:
        cmd('docker stop $(docker ps | awk \'{print $NF}\' | sed 1d | grep ^sc-)')
        logger.info('all containers deleted')
        pass
    else:
        cmd('docker stop %s' % name)
        logger.info('container deleted: %s', name)
        pass
    pass


def minN(arr, n):
    flat_indices = np.argpartition(arr.ravel(), n - 1)[:n]
    row_indices, col_indices = np.unravel_index(flat_indices, arr.shape)
    return row_indices, col_indices


def shutdown():
    cmd('pkill -9 python')
    sys.exit()


def addEdge(graph_dict, src, dst, weight):
    if src in graph_dict:
        graph_dict[src][dst] = {'weight': weight}
    else:
        graph_dict[src] = {dst: {'weight': weight}}


if __name__ == '__main__':
    getState('127.0.0.1', '1.1.1.1')
    pass
