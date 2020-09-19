#!/usr/bin/env python3
import random
import shelly
import logging
import config
import pprint

logging.basicConfig(level=logging.INFO)

for s in shelly.get_shellys(config.subnet, max_cache=0):
    if s.name not in config.lights_away_ignore_list:
        if random.random() < config.prob:
            on_for = random.randint(config.min_on, config.max_on)
            logging.info('Turning on shelly %s for %s seconds' % (s, on_for))
            s.set_timer(on_for)
        else:
            logging.info('NOT turning on relay shelly %s' % (s))

shellys=[]
#shellys = find_shellys(config.subnet)

for shelly in shellys:
    try:
        name, relays = lookup_shelly_config(shelly['mac'])
    except TypeError:
        logging.info('Found shelly not in config: %s'%shelly)
    else:
        ip = shelly['wifi_sta']['ip']
        logging.debug('Found known shelly %s, %s, %s, including relays %s'%(name, ip, shelly["mac"], relays))
        for relay in relays:
            if random.random() < config.prob:
                on_for = random.randint(config.min_on,config.max_on)
                logging.info('Turning on relay %s for shelly %s for %s seconds'%(relay, name, on_for))
                set_timer(ip, relay, on_for)
            else:
                logging.info('NOT turning on relay %s for shelly %s'%(relay, name))
