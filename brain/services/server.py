import asyncio
from os import environ
from flask import Flask, request, redirect, url_for
from db.db import JarvisStatus
from services.kasa_devices import update_lights_status

from models.status import Status
from models.appliances import Appliance

from typing import Union

unauth_routes = ['default', 'status']

def create_app(test_config=None) -> Flask:
    # create and configure the app
    app = Flask(__name__, instance_relative_config=True)
    app.config.from_mapping(SECRET_KEY='dev')

    if test_config is None:
        # load the instance config, if it exists, when not testing
        app.config.from_pyfile('config.py', silent=True)
    else:
        # load the test config if passed in
        app.config.from_mapping(test_config)
    
    @app.before_request
    def before_request_func():
        first_param = request.path.split('/')[1]
        if first_param != environ['AUTH_TOKEN'] and first_param not in unauth_routes:
            return redirect(url_for('default'))
    
    @app.route('/default')
    def default() -> str:
        return 'Nothing to see here, sir ;)'

    @app.route('/status')
    def status() -> str:
        status = JarvisStatus.select().get().status
        if status == Status.ON.value:
            return 'Jarvis is awake'
        elif status == Status.OFF.value:
            return 'Jarvis is asleep'
        elif status == Status.ERROR.value:
            return 'Jarvis is having issues'
        
        return 'Jarvis doesn\'nt know wtf is happening'
    
    @app.route('/<auth>/on/<variable>', methods=['GET'])
    def on(auth: str, variable: str) -> str:
        valid_appliances = ['all', *[appliance.value for appliance in Appliance]]
        if variable == 'all':
            asyncio.run(update_lights_status(Status.ON, [], True))
        elif variable in valid_appliances:
            asyncio.run(update_lights_status(Status.ON, [variable]))
        else:
            return f'''Sorry sir, I couldn\'t find that appliance.<br>
                Your attempt: {variable} <br>
                Appliances I know: <strong>{", ".join(valid_appliances)}</strong>
            '''
        return '<h1 style="text-align:center;">Lights have been turned on!</h1>'
    
    @app.route('/<auth>/off/<variable>', methods=['GET'])
    def off(auth: str, variable: str) -> str:
        valid_appliances = ['all', *[appliance.value for appliance in Appliance]]
        if variable == 'all':
            asyncio.run(update_lights_status(Status.OFF, [], True))
        elif variable in valid_appliances:
            asyncio.run(update_lights_status(Status.OFF, [variable]))
        else:
            return f'''Sorry sir, I couldn\'t find that appliance.<br>
                Your attempt: {variable} <br>
                Appliances I know: <strong>{", ".join(valid_appliances)}</strong>
            '''
        return '<h1 style="text-align:center;">Lights have been turned off!</h1>'
    


    return app