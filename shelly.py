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

    logging.info(f'Found {len(shellys)} shellys')
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
        res = requests.get(f"http://{ip}/relay/{relay}?turn=on&timer={on_for}")
        if res.status_code == 200:
            logging.info(f'Turned on shelly - {res.json()}')
        else:
            logging.error(f'Failed to runs on shelly {shelly}, response={res}')


def get_shelly_status(ip):
    try:
        res = requests.get(
                f'http://{ip}/status',
                timeout=config.http_timeout
            )
    except requests.exceptions.Timeout:
        logging.debug(f"No HTTP response from {ip}")
    except OSError:
        logging.error(f"OSError querying {ip}", exc_info=True)
    else:
        if res.status_code == 200:
            return res.json()