import threading
from ipaddress import ip_network
import requests
import logging
import config
import pickle
import os
from flask import jsonify
import tempfile

CACHE_PATH = os.path.join(tempfile.gettempdir(), 'shellys.pickle')
logging.basicConfig(level=logging.INFO)

def get_shellys(subnet):
    try:
        with open(CACHE_PATH, 'rb') as f:
            shellys = pickle.load(f)
    except FileNotFoundError:
        shellys = find_shellys(subnet)
        # save_shellys(shellys)
    return jsonify(shellys)

def get_shelly_status(ip):
    try:
        res = requests.get(
            'http://%s/status' % ip,
            timeout=config.http_timeout
        )
    except requests.exceptions.Timeout:
        logging.debug("No HTTP response from %s" % ip)
    except OSError:
        logging.error("OSError querying %s" % ip, exc_info=True)
    else:
        if res.status_code == 200:
            return res.json()

def save_shellys(shellys):
    with open(CACHE_PATH, 'wb') as f:
        pickle.dump(shellys, f)

def find_shellys(subnet):
    shellys = []
    threads = [threading.Thread(
        target=store_if_shelly,
        args=(ip, shellys)
    ) for ip in ip_network(subnet).hosts()]

    for t in threads:
        t.start()
    for t in threads:
        t.join()

    logging.info('Scanned for and found %s shellys' % len(shellys))
    return shellys


def lookup_shelly_config(mac):
    try:
        return config.shellymac2name[mac[6:]]
    except KeyError:
        return None


def store_if_shelly(ip,shellys):
    shelly = get_shelly_status(ip)
    if shelly:
        shellys.append(shelly)
        enrich_shelly(shelly)

def enrich_shelly(shelly):
    '''Get added data from settings & shelly API'''
    #Warning - this might create a namespace clash!
    for function in ('shelly','settings'):
        shelly[function]=requests.get(
                'http://%s/%s'%(shelly['wifi_sta']['ip'],function),
                #timeout=config.http_timeout
                timeout=5
            ).json()

def log_response(res, ip):
    if res.status_code == 200:
        logging.info('Turned on shelly - %s' % res.json())
    else:
        logging.error('Failed to runs on shelly %s, response=%s' % (ip, res))


def on(ip, relay=0):
    res = requests.get("http://%s/relay/%s?turn=on" % (ip, relay))
    if res.status_code == 200:
        logging.info('Turned on shelly - %s' % res.json())
    else:
        logging.error('Failed to runs on shelly %s, response=%s' % (ip, res))


def off(ip, relay=0):
    res = requests.get("http://%s/relay/%s?turn=off" % (ip, relay))
    if res.status_code == 200:
        logging.info('Turned on shelly - %s' % res.json())
    else:
        logging.error('Failed to runs on shelly %s, response=%s' % (ip, res))


def set_timer(shelly, ip, relay, on_for):
    if shelly['shelly']['type'] in ('SHDM-1', 'SHBLB-1'):
        req_template = 'http://%s/light/%s?turn=on&timer=%s&brightness=100'
    else:
        req_template = 'http://%s/relay/%s?turn=on&timer=%s'

    res = requests.get(req_template % (ip, relay, on_for))
    if res.status_code == 200:
        logging.info('Turned on shelly - %s' % res.json())
    else:
        logging.error('Failed to runs on shelly %s %s, response=%s' % (shelly['shelly']['type'], ip, res))