import pychromecast
import logging

#devices, browser = pychromecast.discovery.discover_chromecasts()

def all_chromecasts():
    chromecasts, browser = pychromecast.get_chromecasts()
    for cc in chromecasts:
        cc.__class__ = chromecast
        yield cc
    pychromecast.discovery.stop_discovery(browser)

    #casts, browser = pychromecast.get_chromecasts()
    #for cast in casts:
    #    cast.__class__ = chromecast
    #    yield cast

def find_by_name(name):
    devices, browser = pychromecast.get_listed_chromecasts(friendly_names=[name])
    try:
        devices[0].__class__ = chromecast
        return devices[0]
    except IndexError:
        raise Exception('No Chromecast called %s found'%name)

class chromecast(pychromecast.Chromecast):

    def play_mp3(self, mp3_url, volume=None):
        self.wait()
        if volume:
            old_vol = self.set_volume_if_diff(volume)
        logging.info('Playing mp3 %s'%mp3_url)
        self.media_controller.play_media(mp3_url, 'audio/mp3')
        if volume and old_vol != volume:
            logging.info('Setting volume back to %s'%old_vol)
            self.set_volume_if_diff(old_vol) #reset volume back to what it was!

    def set_volume_if_diff(self, volume):
        self.wait()
        old_vol = round(self.status.volume_level, 2)
        if old_vol == volume:
            logging.info('Not changing vol already %s' % old_vol)
        else:
            logging.info('Set vol from %s to %s' % (old_vol, volume))
            self.set_volume(volume)
            self.wait()  # hopefully this waits for volume to stick
        return old_vol

if __name__ == "__main__":
    pass