import argparse
from multiprocessing import Process
import sys
from os import environ

from db.db import init_db
from jarvis import init_jarvis
from waitress import serve
from services.server import create_app

if __name__ == '__main__':

    [ DEV, PROD ] = [ 'development', 'production' ]
    TEST_AUTH_TOKEN = 'test-auth'

    parser = argparse.ArgumentParser(description='Process some integers.')
    parser.add_argument('--env', 
        choices=['production', 'development'], 
        help='The environment to run the server in (production or development)',
        required=True
    )
    parser.add_argument('--no-server', dest='server', action='store_false')
    parser.add_argument('--only-server', dest='only_server', action='store_true')
    parser.set_defaults(server=True)

    args = parser.parse_args()

    if 'AUTH_TOKEN' not in environ:
        if args.env == DEV:
            environ['AUTH_TOKEN'] = TEST_AUTH_TOKEN
        else:
            sys.exit('Invalid auth token configuration for production server environment')    

    environ['FLASK_ENV'] = environ['ENV'] = PROD if args.env == PROD else DEV

    init_db()
    
    if not args.server:
        init_jarvis()
        sys.exit('No server argument passed in. Skipping server initialization')
    
    flask_app = create_app()
    
    if args.only_server:
        flask_app.run()
        sys.exit('Only server argument passed in. Skipping jarvis initialization')

    jarvis_process = Process(target=init_jarvis)
    jarvis_process.start()

    serve(flask_app, port=8000)
