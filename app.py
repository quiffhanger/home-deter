from flask import Flask, request, url_for
import logging
from gtts import gTTS
from slugify import slugify
from pathlib import Path
from urllib.parse import urlparse
import os

import nesthome
import shelly
import config

app = Flask(__name__)

@app.route('/')
def hello_world():
    return shelly.get_shellys(config.subnet)

def play_tts(text, device, lang='en', slow=False, volume=None):
    cc = nesthome.find_by_name(device)
    tts = gTTS(text=text, lang=lang, slow=slow)
    filename = slugify(text+"-"+lang+"-"+str(slow)) + ".mp3"
    path = os.path.join('.', 'static', 'cache')
    cache_filename = os.path.join(path, filename)
    tts_file = Path(cache_filename)
    if not tts_file.is_file():
        logging.info(tts)
        tts.save(cache_filename)

    #urlparts = urlparse(request.url)
    #mp3_url = "http://" +urlparts.netloc + path + filename

    mp3_url=url_for('static', filename='/'.join(('cache',filename)), _external=True)
    logging.info(mp3_url)
    cc.play_mp3(mp3_url, volume=volume)

@app.route('/say/')
def say():
    text = request.args.get("text")
    lang = request.args.get("lang")
    device = request.args.get("device")
    try:
        volume = float(request.args.get('volume'))
    except:
        logging.error("Couldn't parse volume", exc_info=True)
        volume = None
    if not text or not device:
        return False
    if not lang:
        lang = "en"
    play_tts(text, device, lang=lang, volume=volume)
    return text

if __name__ == '__main__':
    app.run()
