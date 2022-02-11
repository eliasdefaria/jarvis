from os import environ
import asyncio

from flask import Flask
from db.db import JarvisStatus

from models.status import Status
from services.kasa_devices import init_kasa_devices, lights_on

def init_jarvis(test_config=None):
    init_brain()
    # create and configure the app
    app = Flask(__name__, instance_relative_config=True)
    app.config.from_mapping(SECRET_KEY='dev')

    if test_config is None:
        # load the instance config, if it exists, when not testing
        app.config.from_pyfile('config.py', silent=True)
    else:
        # load the test config if passed in
        app.config.from_mapping(test_config)
    
    # a simple page that says hello
    @app.route('/status')
    def status():
        return 'Hello, World!'

    return app

def init_brain():
    if JarvisStatus.select().count() > 0:
        return
    
    print('Initializing brain...')
    JarvisStatus.create(status=Status.OFF.value)

    print('Brain initialized... \nHello sir. Give me just a moment check in on the house...')
    init_devices()
    
def init_devices():
    asyncio.run(init_kasa_devices())
    asyncio.run(lights_on([],True))

if __name__ == '__main__':
    init_jarvis()    