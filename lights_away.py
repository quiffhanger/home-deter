<<<<<<< HEAD
#!/usr/bin/env python3
import random
from shelly import *

logging.basicConfig(level=logging.INFO)

shellys = find_shellys(config.subnet)
logging.info('Found %s shellies' % len(shellys))
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
                #set_timer(ip, relay, on_for)
            else:
                logging.info('NOT turning on relay %s for shelly %s'%(relay, name))
=======
#!/usr/bin/env python3
import random
from shelly import *

logging.basicConfig(level=config.log_level)
shellys = find_shellys(config.subnet)

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
>>>>>>> 9f7bdbec2f071d932ab935dae9745f0d2c7dcf10
