from flask import Flask, request, url_for, jsonify
import logging
from gtts import gTTS
from slugify import slugify
from pathlib import Path
from urllib.parse import urlparse
import os

import nesthome
import shelly
import config
import requests

app = Flask(__name__)

@app.route('/all')
def all():
    shellys = {}
    for s in shelly.get_shellys(config.subnet):
        ip = str(s.ip)
        shellys[s.name or ip] = {
            'ip': ip,
            'hostname': s.settings['device']['hostname'],
            'mac': s.mac,
            'class': str(s.__class__),
        }

    return jsonify(shellys)

@app.route('/p/<name>/<path:p>')
def proxy(name, p):
    '''Allows you to reference shellys by the name defined in app not IP'''
    url = '/'.join(('http:/', str(shelly.find_by_name(name).ip), p))
    r = requests.get(url, params=request.args)
    return jsonify(r.json())

@app.route('/shelly/<name>/<funcname>')
def shelly_func(name, funcname):
    '''Call any function on a given shelly object'''
    s = shelly.find_by_name(name)
    return getattr(s, funcname)(**request.args)

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

    mp3_url=url_for('static', filename='/'.join(('cache', filename)), _external=True)
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
