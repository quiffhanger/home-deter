from flask import Flask
import shelly
import config

app = Flask(__name__)


@app.route('/')
def hello_world():
    return shelly.get_shellys(config.subnet)

if __name__ == '__main__':
    app.run()
