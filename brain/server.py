import asyncio
from os import environ
from distutils.log import ERROR
from flask import Flask, request, redirect, url_for
from db.db import JarvisStatus
from services.kasa_devices import lights_on

from models.status import Status
from models.appliances import Appliance

unauth_routes = ['default', 'status']

def create_app(test_config=None):
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
        print('auth attempt', environ['AUTH_TOKEN'], first_param)
        if first_param != environ['AUTH_TOKEN'] and first_param not in unauth_routes:
            return redirect(url_for('default'))
    
    @app.route('/default')
    def default():
        return 'Nothing to see here, sir ;)'

    @app.route('/status')
    def status():
        status = JarvisStatus.select().get().status
        if status == Status.ON.value:
            return 'Jarvis is awake'
        elif status == Status.OFF.value:
            return 'Jarvis is asleep'
        elif status == Status.ERROR.value:
            return 'Jarvis is having issues'
        else:
            return 'Jarvis doesn\'nt know wtf is happening'
    
    @app.route('/<auth>/on/<variable>', methods=['GET'])
    def on(auth, variable):
        print('running on!', auth, variable)
        valid_appliances = ['all', *[appliance.value for appliance in Appliance]]
        if variable == 'all':
            asyncio.run(lights_on([], True))
        elif variable in valid_appliances:
            asyncio.run(lights_on([variable]))
        else:
            return f'''Sorry sir, I couldn\'t find that appliance.<br>
                Your attempt: {variable} <br>
                Appliances I know: <strong>{", ".join(valid_appliances)}</strong>
            '''
        return '<h1>Lights have been turned on!</h1>'
    


    return app