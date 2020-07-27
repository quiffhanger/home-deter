import threading
from ipaddress import ip_network
import requests
import logging
import config
import pickle
import os
from flask import jsonify

CACHE_PATH=os.path.join(os.environ['tmp'], 'shellys.pickle')
logging.basicConfig(level=logging.INFO)

def get_shellys(subnet):
    try:
        with open(CACHE_PATH,'rb') as f:
            shellys = pickle.load(f)
    except FileNotFoundError:
        shellys = find_shellys(subnet)
        #save_shellys(shellys)
    return jsonify(shellys)

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


def store_if_shelly(ip, shellys):
    status = get_shelly_status(ip)
    if status:
        shellys.append(status)


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


def set_timer(ip, relay, on_for):
    res = requests.get("http://%s/relay/%s?turn=on&timer=%s" % (ip, relay, on_for))
    if res.status_code == 200:
        logging.info('Turned on shelly - %s' % res.json())
    else:
        logging.error('Failed to runs on shelly %s, response=%s' % (ip, res))


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
