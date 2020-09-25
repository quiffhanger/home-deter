#!/usr/bin/env python3
import random
import shelly
import logging
import config
import pprint

logging.basicConfig(level=logging.INFO)

shellies = shelly.get_shellys(config.subnet, max_cache=0)

def main():
    for s in shellies:
        for name in s.names:
            if name == 'Away': #shortcut - relies on away being the second relay on the 2.5
                if s.is_on(1):
                    set_lights()
                else:
                    logging.info('Not away - not setting any relays!')

def set_lights():
    for s in shellies:
        if s.name not in config.lights_away_ignore_list:
            if random.random() < config.prob:
                on_for = random.randint(config.min_on, config.max_on)
                logging.info('Turning on shelly %s for %s seconds' % (s, on_for))
                s.set_timer(on_for)
            else:
                logging.info('NOT turning on relay shelly %s' % (s))

if __name__ == '__main__':
    main()