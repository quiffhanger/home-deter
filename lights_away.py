import random
from shelly import *

logging.basicConfig(level=logging.INFO)

shellys = find_shellys(config.subnet)
for shelly in shellys:
    try:
        name, relays = lookup_shelly_config(shelly['mac'])
    except TypeError:
        logging.info(f'Found shelly not in config: {shelly}')
    else:
        ip = shelly['wifi_sta']['ip']
        logging.debug(f'Found known shelly {name}, {ip}, {shelly["mac"]}, including relays {relays}')
        for relay in relays:
            if random.random() < config.prob:
                on_for = random.randint(config.min_on,config.max_on)
                logging.info(f'Turning on relay {relay} for shelly {name} for {on_for} seconds')
                set_timer(ip, relay, on_for)
            else:
                logging.info(f'NOT turning on relay {relay} for shelly {name}')
