import threading
from ipaddress import ip_network
import requests
import logging
import config
import pickle
import os
from flask import jsonify
import tempfile
import datetime

CACHE_PATH = os.path.join(tempfile.gettempdir(), 'shellys.pickle')
logging.basicConfig(level=logging.INFO)

class Shelly:

    def __init__(self, ip):
        '''Instantiate a shelly by IP, throws an Exception if given IP is not accessible or doesn't look like a shelly'''

        res = requests.get(
            'http://%s/status' % ip,
            timeout=config.http_timeout
        )

        if res.status_code == 200:
            self.ip = ip
            self.__settings = None
            self.__shelly = None
            self.status = None
        else:
            raise Exception('Status code %s getting status from %s'%(res.status_code,ip))

    def load(self):
        self.shelly
        self.settings

    @property
    def shelly(self, use_cache=True):
        if not self.__shelly or not use_cache:
            self.__shelly = requests.get(
                'http://%s/%s' % (self.ip, 'shelly'),
            ).json()
        return self.__shelly

    def is_light(self):
        return True

    @property
    def settings(self, use_cache=True):
        if not self.__settings or not use_cache:
            self.__settings = requests.get(
                'http://%s/%s' % (self.ip, 'settings'),
            ).json()
        return self.__settings

    @property
    def type(self):
        return self.shelly['type']

    @property
    def name(self):
        return self.settings['name']

    @property
    def names(self):
        return (self.settings['name'],)

    @property
    def mac(self):
        return self.shelly['mac']

    def is_on(self, relay=0):
        return self.req("http://%s/relay/%s" % (self.ip, relay))['ison']

    def on(self, relay=0):
        return self.req("http://%s/relay/%s?turn=on" % (self.ip, relay))

    def off(self, relay=0):
        return self.req("http://%s/relay/%s?turn=off" % (self.ip, relay))

    def set_timer(self, on_for):
        return self.req('http://%s/relay/0?turn=on&timer=%s' % (self.ip, on_for))

    def __str__(self):
        return "%s(name=%s ip=%s mac=%s)"%(self.__class__,self.name,self.ip,self.mac)

    def req(self, url):
        r = requests.get(url)
        r.raise_for_status()
        return r.json()

    def old(self):
        if res.status_code == 200:
            logging.info('Turned on shelly - %s' % res.json())
        else:
            logging.error('Failed to runs on shelly %s, response=%s' % (ip, res))

class Shelly25(Shelly):
    @property
    def names(self):
        for relay in self.settings['relays']:
            yield relay['name']

class ShellyBulb(Shelly):

    def is_light(self):
        return True

    def on(self):
        return self.req("http://%s/color/0?turn=on" % self.ip)

    def off(self):
        return self.req("http://%s/color/0?turn=off" % self.ip)

    def set_timer(self, on_for):
        return self.req('http://%s/color/0?turn=on&timer=%s&brightness=100' % (self.ip, on_for))

class ShellyDimmer(Shelly):

    def is_light(self):
        return True

    def on(self):
        return self.req("http://%s/light/0?turn=on" % self.ip)

    def off(self):
        return self.req("http://%s/light/0?turn=off" % self.ip)

    def set_timer(self, on_for):
        return self.req('http://%s/light/0?turn=on&timer=%s&brightness=100' % (self.ip, on_for))

def get_shellys(subnet, max_cache=config.max_cache_age_seconds):
    '''Return all shellies on a given subnet, using the cache if it's not timed out'''
    try:
        cache_age = (datetime.datetime.now() - datetime.datetime.fromtimestamp(os.path.getmtime(CACHE_PATH))).seconds
        if cache_age > max_cache:
            logging.info("max cache age %ss expired as file is %ss old" % (max_cache, cache_age))
            os.remove(CACHE_PATH)
        with open(CACHE_PATH, 'rb') as f:
            shellys = pickle.load(f)
        logging.info('Succesfully loaded pickled shelly cache from %s cache age: %s' % (CACHE_PATH, cache_age))
    except FileNotFoundError:
        shellys = scan_for_shellys(subnet)
        save_shellys(shellys)
    return shellys


def save_shellys(shellys):
    with open(CACHE_PATH, 'wb') as f:
        pickle.dump(shellys, f)

def find_by_name(name):
    '''Find a shelly by it's name
        Parameters:
            a (str): Name of the device (if settings, sync name is turned on this will match name in Shelly App)
            b (list): List of Shelly objects to search

        Returns:
            shelly (Shelly): first matching shelly device. None if no match
    '''
    for shelly in shellys:
        if shelly.name == name:
            return shelly

def scan_for_shellys(subnet):
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

class_map = {
    'SHDM-1': ShellyDimmer,
    'SHBLB-1': ShellyBulb,
    'SHSW-25': Shelly25,
}

def store_if_shelly(ip, shellys):
    try:
        shelly = Shelly(ip)
    except:
        logging.debug('IP: %s not a shelly'%ip, exc_info=True)
    else:
        shelly.load()
        shelly.__class__ = class_map.setdefault(shelly.type,Shelly)
        shellys.append(shelly)

# Old functions!
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


def lookup_shelly_config(mac):
    try:
        return config.shellymac2name[mac[6:]]
    except KeyError:
        return None


def name_to_mac(name):
    for k, v in config.shellymac2name.items():
        if v[0] == name:
            return k


def mac_to_ip(mac, shellys):
    for shelly in shellys:
        if shelly['mac'].endswith(mac):
            return shelly['wifi_sta']['ip']


def enrich_shelly(shelly):
    '''Get added data from settings & shelly API'''
    # Warning - this might create a namespace clash!
    for function in ('shelly', 'settings'):
        shelly[function] = requests.get(
            'http://%s/%s' % (shelly['wifi_sta']['ip'], function),
            # timeout=config.http_timeout
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
        logging.info('Turned off shelly - %s' % res.json())
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
