import threading
from ipaddress import ip_network
import requests
import logging
import config

def find_shellys(subnet):
    shellys=[]
    threads = [threading.Thread(
        target=store_if_shelly,
        args=(ip, shellys)
    ) for ip in ip_network(subnet).hosts()]

    for t in threads:
        t.start()
    for t in threads:
        t.join()

    logging.info('Found %s shellys'%len(shellys))
    return shellys


def lookup_shelly_config(mac):
    try:
        return config.shellymac2name[mac[6:]]
    except KeyError:
        return None


def store_if_shelly(ip,shellys):
    status = get_shelly_status(ip)
    if status:
        shellys.append(status)


def set_timer(ip,relay,on_for):
    res = requests.get("http://%s/relay/%s?turn=on&timer=%s"%(ip, relay, on_for))
    if res.status_code == 200:
        logging.info('Turned on shelly - %s'%res.json())
    else:
        logging.error('Failed to runs on shelly %s, response=%s'%(ip, res))


def get_shelly_status(ip):
    try:
        res = requests.get(
                'http://%s/status'%ip,
                timeout=config.http_timeout
            )
    except:
        logging.debug("Error querying %s (probably not a shelly on that IP)"%ip, exc_info=True)
    else:
        if res.status_code == 200:
            return res.json()
